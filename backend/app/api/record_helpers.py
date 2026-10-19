from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import ErrorLog, StudyLog, Todo, User


RECORD_MODELS = {
    "study": StudyLog,
    "todo": Todo,
    "error": ErrorLog,
}


def get_record(database: Session, record_type: str, record_id: int):
    model = RECORD_MODELS.get(record_type)
    if model is None:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다.")
    record = database.get(model, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다.")
    return record


def get_owned_record(
    database: Session,
    record_type: str,
    record_id: int,
    current_user: User,
):
    record = get_record(database, record_type, record_id)
    if record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 기록을 변경할 권한이 없습니다.",
        )
    return record


def get_visible_record(
    database: Session,
    record_type: str,
    record_id: int,
    current_user: User,
):
    record = get_record(database, record_type, record_id)
    if record.user_id != current_user.id and not record.is_public:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다.")
    return record


def get_public_interaction_record(database: Session, record_type: str, record_id: int):
    if record_type not in {"study", "error"}:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다.")
    record = get_record(database, record_type, record_id)
    if not record.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="공개 기록에서만 사용할 수 있습니다.",
        )
    return record
