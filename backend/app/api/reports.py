from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.record_helpers import get_record
from app.db.database import get_db
from app.models import Comment, Report, User
from app.schemas import ReportCreate, ReportResponse


router = APIRouter(tags=["reports"])


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="운영자만 확인할 수 있습니다.")
    return user


def target_values(target_type: str, target_id: int) -> dict:
    return {f"{target_type}_log_id" if target_type in {"study", "error"} else f"{target_type}_id": target_id}


def validate_public_target(database: Session, target_type: str, target_id: int) -> None:
    if target_type == "comment":
        comment = database.get(Comment, target_id)
        if comment is None:
            raise HTTPException(status_code=404, detail="신고 대상을 찾을 수 없습니다.")
        record_type = "study" if comment.study_log_id is not None else "error"
        record_id = comment.study_log_id or comment.error_log_id
        record = get_record(database, record_type, record_id)
    else:
        record = get_record(database, target_type, target_id)
    if not record.is_public:
        raise HTTPException(status_code=403, detail="공개된 대상만 신고할 수 있습니다.")


def report_response(report: Report) -> ReportResponse:
    for target_type, value in (("study", report.study_log_id), ("todo", report.todo_id), ("error", report.error_log_id), ("comment", report.comment_id)):
        if value is not None:
            return ReportResponse(id=report.id, target_type=target_type, target_id=value, reporter_id=report.reporter_id, reporter_nickname=report.reporter.nickname, reason=report.reason, created_at=report.created_at)
    raise RuntimeError("신고 대상이 없습니다.")


@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(payload: ReportCreate, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    validate_public_target(database, payload.target_type, payload.target_id)
    report = Report(reporter_id=current_user.id, reason=payload.reason, **target_values(payload.target_type, payload.target_id))
    database.add(report)
    try:
        database.commit()
    except IntegrityError as error:
        database.rollback()
        raise HTTPException(status_code=409, detail="이미 신고한 대상입니다.") from error
    database.refresh(report)
    return report_response(report)


@router.get("/admin/reports", response_model=list[ReportResponse])
def list_reports(_admin: User = Depends(require_admin), database: Session = Depends(get_db)):
    reports = database.scalars(select(Report).order_by(Report.created_at.desc(), Report.id.desc())).all()
    return [report_response(report) for report in reports]


@router.get("/admin/reports/{report_id}", response_model=ReportResponse)
def read_report(report_id: int, _admin: User = Depends(require_admin), database: Session = Depends(get_db)):
    report = database.get(Report, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="신고를 찾을 수 없습니다.")
    return report_response(report)
