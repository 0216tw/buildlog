from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Material(Base):
    __tablename__ = "materials"
    __table_args__ = (
        CheckConstraint(
            "media_type IN ('image', 'video')",
            name="ck_materials_media_type",
        ),
        CheckConstraint(
            "(media_type = 'image' AND content_type IN ('image/png', 'image/jpeg')) "
            "OR (media_type = 'video' AND content_type = 'video/mp4')",
            name="ck_materials_content_type",
        ),
        CheckConstraint("size_bytes > 0", name="ck_materials_positive_size"),
        CheckConstraint(
            "(media_type = 'image' AND size_bytes <= 5242880) "
            "OR (media_type = 'video' AND size_bytes <= 31457280)",
            name="ck_materials_size_limit",
        ),
        CheckConstraint(
            "ai_status IN ('not_requested', 'pending', 'processing', 'completed', 'failed')",
            name="ck_materials_ai_status",
        ),
        CheckConstraint(
            "ai_attempt_count >= 0 AND ai_attempt_count <= 3",
            name="ck_materials_ai_attempt_count",
        ),
        CheckConstraint(
            "ai_summary IS NULL OR (length(ai_summary) >= 1 AND length(ai_summary) <= 1000)",
            name="ck_materials_ai_summary_length",
        ),
        UniqueConstraint("stored_path", name="uq_materials_stored_path"),
        Index("ix_materials_user_created", "user_id", "created_at", "id"),
        Index("ix_materials_ai_work", "ai_status", "created_at", "id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_filename: Mapped[str] = mapped_column(Text, nullable=False)
    stored_path: Mapped[str] = mapped_column(String(500), nullable=False)
    media_type: Mapped[str] = mapped_column(String(10), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_status: Mapped[str] = mapped_column(
        String(20),
        default="not_requested",
        server_default="not_requested",
        nullable=False,
    )
    ai_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ai_prompt_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ai_attempt_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )
    ai_started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ai_analyzed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ai_error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        server_default=func.current_timestamp(),
        nullable=False,
    )

    author: Mapped["User"] = relationship(back_populates="materials")
