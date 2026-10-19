from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models import User
from app.schemas import NicknameUpdateRequest, UserResponse


router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/me/nickname", response_model=UserResponse)
def update_my_nickname(
    payload: NicknameUpdateRequest,
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
) -> User:
    duplicate = database.scalar(
        select(User).where(
            User.nickname == payload.nickname,
            User.id != current_user.id,
        )
    )
    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 닉네임입니다.",
        )

    current_user.nickname = payload.nickname
    try:
        database.commit()
    except IntegrityError as error:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 닉네임입니다.",
        ) from error
    database.refresh(current_user)
    return current_user
