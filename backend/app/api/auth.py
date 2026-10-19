from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.security import (
    create_session_token,
    hash_password,
    hash_session_token,
    verify_password,
)
from app.db.database import get_db
from app.models import User, UserSession
from app.schemas import LoginRequest, SignupRequest, UserResponse


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, database: Session = Depends(get_db)) -> User:
    existing_user = database.scalar(
        select(User).where(
            or_(User.email == payload.email, User.nickname == payload.nickname),
        )
    )
    if existing_user is not None:
        if existing_user.email == payload.email:
            detail = "이미 사용 중인 이메일입니다."
        else:
            detail = "이미 사용 중인 닉네임입니다."
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        nickname=payload.nickname,
    )
    database.add(user)
    try:
        database.commit()
    except IntegrityError as error:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 이메일 또는 닉네임입니다.",
        ) from error
    database.refresh(user)
    return user


@router.post("/login", response_model=UserResponse)
def login(
    payload: LoginRequest,
    response: Response,
    database: Session = Depends(get_db),
) -> User:
    user = database.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 맞지 않습니다.",
        )

    token = create_session_token()
    now = datetime.now(UTC).replace(tzinfo=None)
    database.add(
        UserSession(
            token_hash=hash_session_token(token),
            user_id=user.id,
            expires_at=now + timedelta(seconds=settings.session_max_age_seconds),
        )
    )
    database.commit()

    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=settings.session_max_age_seconds,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )
    return user


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user
