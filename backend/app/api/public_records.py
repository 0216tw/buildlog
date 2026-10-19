from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models import ErrorLog, StudyLog, Todo, User
from app.schemas import PublicRecordResponse


router = APIRouter(prefix="/public-records", tags=["public records"])


@router.get("", response_model=list[PublicRecordResponse])
def list_public_records(
    record_type: Literal["all", "study", "todo", "error"] = "all",
    q: str = "",
    _current_user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
):
    search = q.strip()
    results: list[PublicRecordResponse] = []

    if record_type in {"all", "study"}:
        statement = select(StudyLog, User.nickname).join(User).where(StudyLog.is_public.is_(True))
        if search:
            pattern = f"%{search}%"
            statement = statement.where(or_(StudyLog.title.ilike(pattern), StudyLog.content.ilike(pattern)))
        for record, nickname in database.execute(statement):
            results.append(PublicRecordResponse(type="study", id=record.id, title=record.title, content=record.content, author_nickname=nickname, created_at=record.created_at, updated_at=record.updated_at))

    if record_type in {"all", "todo"}:
        statement = select(Todo, User.nickname).join(User).where(Todo.is_public.is_(True))
        if search:
            statement = statement.where(Todo.title.ilike(f"%{search}%"))
        for record, nickname in database.execute(statement):
            results.append(PublicRecordResponse(type="todo", id=record.id, title=record.title, status="완료" if record.is_completed else "미완료", author_nickname=nickname, created_at=record.created_at, updated_at=record.updated_at))

    if record_type in {"all", "error"}:
        statement = select(ErrorLog, User.nickname).join(User).where(ErrorLog.is_public.is_(True))
        if search:
            pattern = f"%{search}%"
            statement = statement.where(or_(ErrorLog.title.ilike(pattern), ErrorLog.content.ilike(pattern), ErrorLog.resolution.ilike(pattern)))
        for record, nickname in database.execute(statement):
            results.append(PublicRecordResponse(type="error", id=record.id, title=record.title, content=record.content, status="해결" if record.is_resolved else "미해결", author_nickname=nickname, created_at=record.created_at, updated_at=record.updated_at))

    return sorted(results, key=lambda item: (item.created_at, item.id), reverse=True)
