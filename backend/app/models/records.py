from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, false, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class StudyLog(Base):
    __tablename__ = "study_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, server_default=func.current_timestamp(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, server_default=func.current_timestamp()
    )

    author = relationship("User")


class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(100))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, server_default=func.current_timestamp(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, server_default=func.current_timestamp()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    author = relationship("User")


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, server_default=func.current_timestamp(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, server_default=func.current_timestamp()
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    author = relationship("User")
