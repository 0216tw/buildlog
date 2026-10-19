from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.record_helpers import get_owned_record, get_visible_record
from app.db.database import get_db
from app.models import StudyLog, User
from app.schemas import StudyResponse, StudyWrite, VisibilityUpdate


router = APIRouter(prefix="/studies", tags=["studies"])


@router.post("", response_model=StudyResponse, status_code=status.HTTP_201_CREATED)
def create_study(payload: StudyWrite, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    record = StudyLog(user_id=current_user.id, **payload.model_dump())
    database.add(record)
    database.commit()
    database.refresh(record)
    return record


@router.get("", response_model=list[StudyResponse])
def list_studies(q: str = "", current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    statement = select(StudyLog).where(StudyLog.user_id == current_user.id)
    search = q.strip()
    if search:
        pattern = f"%{search}%"
        statement = statement.where(or_(StudyLog.title.ilike(pattern), StudyLog.content.ilike(pattern)))
    return list(database.scalars(statement.order_by(StudyLog.created_at.desc(), StudyLog.id.desc())))


@router.get("/{record_id}", response_model=StudyResponse)
def read_study(record_id: int, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    return get_visible_record(database, "study", record_id, current_user)


@router.put("/{record_id}", response_model=StudyResponse)
def update_study(record_id: int, payload: StudyWrite, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    record = get_owned_record(database, "study", record_id, current_user)
    for key, value in payload.model_dump().items():
        setattr(record, key, value)
    record.updated_at = datetime.now(UTC).replace(tzinfo=None)
    database.commit()
    database.refresh(record)
    return record


@router.patch("/{record_id}/visibility", response_model=StudyResponse)
def update_study_visibility(record_id: int, payload: VisibilityUpdate, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    record = get_owned_record(database, "study", record_id, current_user)
    record.is_public = payload.is_public
    record.updated_at = datetime.now(UTC).replace(tzinfo=None)
    database.commit()
    database.refresh(record)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_study(record_id: int, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    record = get_owned_record(database, "study", record_id, current_user)
    database.delete(record)
    database.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
