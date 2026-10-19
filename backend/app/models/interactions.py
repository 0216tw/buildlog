from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (
        CheckConstraint(
            "(study_log_id IS NOT NULL AND error_log_id IS NULL) OR "
            "(study_log_id IS NULL AND error_log_id IS NOT NULL)",
            name="ck_comments_exactly_one_record",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    study_log_id: Mapped[int | None] = mapped_column(
        ForeignKey("study_logs.id", ondelete="CASCADE"), nullable=True, index=True
    )
    error_log_id: Mapped[int | None] = mapped_column(
        ForeignKey("error_logs.id", ondelete="CASCADE"), nullable=True, index=True
    )
    content: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, server_default=func.current_timestamp(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, server_default=func.current_timestamp()
    )

    author = relationship("User")


class RecordLike(Base):
    __tablename__ = "record_likes"
    __table_args__ = (
        CheckConstraint(
            "(study_log_id IS NOT NULL AND error_log_id IS NULL) OR "
            "(study_log_id IS NULL AND error_log_id IS NOT NULL)",
            name="ck_record_likes_exactly_one_record",
        ),
        UniqueConstraint("user_id", "study_log_id", name="uq_like_user_study"),
        UniqueConstraint("user_id", "error_log_id", name="uq_like_user_error"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    study_log_id: Mapped[int | None] = mapped_column(
        ForeignKey("study_logs.id", ondelete="CASCADE"), nullable=True, index=True
    )
    error_log_id: Mapped[int | None] = mapped_column(
        ForeignKey("error_logs.id", ondelete="CASCADE"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, server_default=func.current_timestamp()
    )


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (
        CheckConstraint(
            "(CASE WHEN study_log_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN todo_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN error_log_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN comment_id IS NOT NULL THEN 1 ELSE 0 END) = 1",
            name="ck_reports_exactly_one_target",
        ),
        UniqueConstraint("reporter_id", "study_log_id", name="uq_reporter_study"),
        UniqueConstraint("reporter_id", "todo_id", name="uq_reporter_todo"),
        UniqueConstraint("reporter_id", "error_log_id", name="uq_reporter_error"),
        UniqueConstraint("reporter_id", "comment_id", name="uq_reporter_comment"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    reporter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    study_log_id: Mapped[int | None] = mapped_column(
        ForeignKey("study_logs.id", ondelete="CASCADE"), nullable=True, index=True
    )
    todo_id: Mapped[int | None] = mapped_column(
        ForeignKey("todos.id", ondelete="CASCADE"), nullable=True, index=True
    )
    error_log_id: Mapped[int | None] = mapped_column(
        ForeignKey("error_logs.id", ondelete="CASCADE"), nullable=True, index=True
    )
    comment_id: Mapped[int | None] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True
    )
    reason: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, server_default=func.current_timestamp(), index=True
    )

    reporter = relationship("User")
