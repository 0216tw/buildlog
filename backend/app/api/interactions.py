from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.record_helpers import get_public_interaction_record, get_record
from app.db.database import get_db
from app.models import Comment, RecordLike, User
from app.schemas import CommentResponse, CommentWrite, LikeResponse


router = APIRouter(tags=["comments and likes"])


def normalize_record_type(record_type: str) -> str:
    normalized = {"study": "study", "studies": "study", "error": "error", "errors": "error"}.get(record_type)
    if normalized is None:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다.")
    return normalized


def target_filter(model, record_type: str, record_id: int):
    return model.study_log_id == record_id if record_type == "study" else model.error_log_id == record_id


def target_values(record_type: str, record_id: int) -> dict:
    return {"study_log_id": record_id} if record_type == "study" else {"error_log_id": record_id}


def comment_response(comment: Comment) -> CommentResponse:
    return CommentResponse(id=comment.id, author_id=comment.author_id, author_nickname=comment.author.nickname, content=comment.content, created_at=comment.created_at, updated_at=comment.updated_at)


@router.get("/{record_type}/{record_id}/comments", response_model=list[CommentResponse])
def list_comments(record_type: str, record_id: int, _current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    record_type = normalize_record_type(record_type)
    get_public_interaction_record(database, record_type, record_id)
    comments = database.scalars(select(Comment).where(target_filter(Comment, record_type, record_id)).order_by(Comment.created_at.asc(), Comment.id.asc())).all()
    return [comment_response(comment) for comment in comments]


@router.post("/{record_type}/{record_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(record_type: str, record_id: int, payload: CommentWrite, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    record_type = normalize_record_type(record_type)
    get_public_interaction_record(database, record_type, record_id)
    comment = Comment(author_id=current_user.id, content=payload.content, **target_values(record_type, record_id))
    database.add(comment)
    database.commit()
    database.refresh(comment)
    return comment_response(comment)


@router.put("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(comment_id: int, payload: CommentWrite, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    comment = database.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="이 댓글을 수정할 권한이 없습니다.")
    record_type = "study" if comment.study_log_id is not None else "error"
    record_id = comment.study_log_id or comment.error_log_id
    get_public_interaction_record(database, record_type, record_id)
    comment.content = payload.content
    comment.updated_at = datetime.now(UTC).replace(tzinfo=None)
    database.commit()
    database.refresh(comment)
    return comment_response(comment)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    comment = database.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    record_type = "study" if comment.study_log_id is not None else "error"
    record_id = comment.study_log_id or comment.error_log_id
    record = get_record(database, record_type, record_id)
    if comment.author_id != current_user.id and record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="이 댓글을 삭제할 권한이 없습니다.")
    database.delete(comment)
    database.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def like_result(database: Session, record_type: str, record_id: int, user_id: int) -> LikeResponse:
    condition = target_filter(RecordLike, record_type, record_id)
    liked = database.scalar(select(RecordLike.id).where(condition, RecordLike.user_id == user_id)) is not None
    count = database.scalar(select(func.count()).select_from(RecordLike).where(condition)) or 0
    return LikeResponse(liked=liked, count=count)


@router.get("/{record_type}/{record_id}/like", response_model=LikeResponse)
def read_like(record_type: str, record_id: int, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    record_type = normalize_record_type(record_type)
    get_public_interaction_record(database, record_type, record_id)
    return like_result(database, record_type, record_id, current_user.id)


@router.post("/{record_type}/{record_id}/like", response_model=LikeResponse)
def create_like(record_type: str, record_id: int, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    record_type = normalize_record_type(record_type)
    get_public_interaction_record(database, record_type, record_id)
    existing = database.scalar(select(RecordLike).where(target_filter(RecordLike, record_type, record_id), RecordLike.user_id == current_user.id))
    if existing is None:
        database.add(RecordLike(user_id=current_user.id, **target_values(record_type, record_id)))
        try:
            database.commit()
        except IntegrityError:
            database.rollback()
    return like_result(database, record_type, record_id, current_user.id)


@router.delete("/{record_type}/{record_id}/like", response_model=LikeResponse)
def delete_like(record_type: str, record_id: int, current_user: User = Depends(get_current_user), database: Session = Depends(get_db)):
    record_type = normalize_record_type(record_type)
    get_public_interaction_record(database, record_type, record_id)
    existing = database.scalar(select(RecordLike).where(target_filter(RecordLike, record_type, record_id), RecordLike.user_id == current_user.id))
    if existing is not None:
        database.delete(existing)
        database.commit()
    return like_result(database, record_type, record_id, current_user.id)
