from datetime import UTC, datetime

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_session_token
from app.db.database import get_db
from app.models import User, UserSession


def get_current_user(
    session_token: str | None = Cookie(
        default=None,
        alias=settings.session_cookie_name,
    ),
    database: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="로그인이 필요합니다.",
    )

    if not session_token:
        raise unauthorized

    stored_session = database.scalar(
        select(UserSession).where(
            UserSession.token_hash == hash_session_token(session_token),
        )
    )
    if stored_session is None:
        raise unauthorized

    now = datetime.now(UTC).replace(tzinfo=None)
    if stored_session.expires_at <= now:
        database.delete(stored_session)
        database.commit()
        raise unauthorized

    user = database.get(User, stored_session.user_id)
    if user is None:
        raise unauthorized
    return user
