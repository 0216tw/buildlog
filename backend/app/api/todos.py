from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.record_helpers import get_owned_record, get_visible_record
from app.db.database import get_db
from app.models import Todo, User
from app.schemas import TodoCompletionUpdate, TodoResponse, TodoWrite, VisibilityUpdate


router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoWrite, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    record = Todo(user_id=current_user.id, **payload.model_dump())
    database.add(record)
    database.commit()
    database.refresh(record)
    return record


@router.get("", response_model=list[TodoResponse])
def list_todos(state: Literal["all", "pending", "completed"] = "all", current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    statement = select(Todo).where(Todo.user_id == current_user.id)
    if state == "pending":
        statement = statement.where(Todo.is_completed.is_(False))
    elif state == "completed":
        statement = statement.where(Todo.is_completed.is_(True))
    return list(database.scalars(statement.order_by(Todo.is_completed.asc(), Todo.created_at.desc(), Todo.id.desc())))


@router.get("/{record_id}", response_model=TodoResponse)
def read_todo(record_id: int, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    return get_visible_record(database, "todo", record_id, current_user)


@router.put("/{record_id}", response_model=TodoResponse)
def update_todo(record_id: int, payload: TodoWrite, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    record = get_owned_record(database, "todo", record_id, current_user)
    record.title = payload.title
    record.is_public = payload.is_public
    record.updated_at = datetime.now(UTC).replace(tzinfo=None)
    database.commit()
    database.refresh(record)
    return record


@router.patch("/{record_id}/completion", response_model=TodoResponse)
def update_todo_completion(record_id: int, payload: TodoCompletionUpdate, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    record = get_owned_record(database, "todo", record_id, current_user)
    now = datetime.now(UTC).replace(tzinfo=None)
    record.is_completed = payload.is_completed
    record.completed_at = now if payload.is_completed else None
    record.updated_at = now
    database.commit()
    database.refresh(record)
    return record


@router.patch("/{record_id}/visibility", response_model=TodoResponse)
def update_todo_visibility(record_id: int, payload: VisibilityUpdate, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    record = get_owned_record(database, "todo", record_id, current_user)
    record.is_public = payload.is_public
    record.updated_at = datetime.now(UTC).replace(tzinfo=None)
    database.commit()
    database.refresh(record)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(record_id: int, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    database.delete(get_owned_record(database, "todo", record_id, current_user))
    database.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
