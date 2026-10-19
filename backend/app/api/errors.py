from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.record_helpers import get_owned_record, get_visible_record
from app.db.database import get_db
from app.models import ErrorLog, User
from app.schemas import ErrorResponse, ErrorWrite, VisibilityUpdate


router = APIRouter(prefix="/errors", tags=["errors"])


def apply_error_data(record: ErrorLog, payload: ErrorWrite) -> None:
    now = datetime.now(UTC).replace(tzinfo=None)
    was_resolved = record.is_resolved
    for key, value in payload.model_dump().items():
        setattr(record, key, value)
    if payload.is_resolved and not was_resolved:
        record.resolved_at = now
    elif not payload.is_resolved:
        record.resolved_at = None
    record.updated_at = now


@router.post("", response_model=ErrorResponse, status_code=status.HTTP_201_CREATED)
def create_error(payload: ErrorWrite, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    record = ErrorLog(user_id=current_user.id, title=payload.title, content=payload.content, resolution=payload.resolution, is_resolved=payload.is_resolved, is_public=payload.is_public)
    if payload.is_resolved:
        record.resolved_at = datetime.now(UTC).replace(tzinfo=None)
    database.add(record)
    database.commit()
    database.refresh(record)
    return record


@router.get("", response_model=list[ErrorResponse])
def list_errors(state: Literal["all", "unresolved", "resolved"] = "all", q: str = "", current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    statement = select(ErrorLog).where(ErrorLog.user_id == current_user.id)
    if state == "unresolved":
        statement = statement.where(ErrorLog.is_resolved.is_(False))
    elif state == "resolved":
        statement = statement.where(ErrorLog.is_resolved.is_(True))
    search = q.strip()
    if search:
        pattern = f"%{search}%"
        statement = statement.where(or_(ErrorLog.title.ilike(pattern), ErrorLog.content.ilike(pattern)))
    return list(database.scalars(statement.order_by(ErrorLog.created_at.desc(), ErrorLog.id.desc())))


@router.get("/{record_id}", response_model=ErrorResponse)
def read_error(record_id: int, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    return get_visible_record(database, "error", record_id, current_user)


@router.put("/{record_id}", response_model=ErrorResponse)
def update_error(record_id: int, payload: ErrorWrite, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    record = get_owned_record(database, "error", record_id, current_user)
    apply_error_data(record, payload)
    database.commit()
    database.refresh(record)
    return record


@router.patch("/{record_id}/visibility", response_model=ErrorResponse)
def update_error_visibility(record_id: int, payload: VisibilityUpdate, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    record = get_owned_record(database, "error", record_id, current_user)
    record.is_public = payload.is_public
    record.updated_at = datetime.now(UTC).replace(tzinfo=None)
    database.commit()
    database.refresh(record)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_error(record_id: int, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    database.delete(get_owned_record(database, "error", record_id, current_user))
    database.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
