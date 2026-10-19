"""create records and interactions

Revision ID: 20261020_02
Revises: 20261016_01
Create Date: 2026-10-20
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20261020_02"
down_revision: str | None = "20261016_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "study_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_public", sa.Boolean(), server_default=sa.false(), nullable=False),
        *timestamp_columns(),
    )
    op.create_index("ix_study_logs_user_id", "study_logs", ["user_id"])
    op.create_index("ix_study_logs_created_at", "study_logs", ["created_at"])

    op.create_table(
        "todos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("is_completed", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_public", sa.Boolean(), server_default=sa.false(), nullable=False),
        *timestamp_columns(),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_todos_user_id", "todos", ["user_id"])
    op.create_index("ix_todos_created_at", "todos", ["created_at"])

    op.create_table(
        "error_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("resolution", sa.Text(), nullable=True),
        sa.Column("is_resolved", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_public", sa.Boolean(), server_default=sa.false(), nullable=False),
        *timestamp_columns(),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_error_logs_user_id", "error_logs", ["user_id"])
    op.create_index("ix_error_logs_created_at", "error_logs", ["created_at"])

    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("study_log_id", sa.Integer(), sa.ForeignKey("study_logs.id", ondelete="CASCADE"), nullable=True),
        sa.Column("error_log_id", sa.Integer(), sa.ForeignKey("error_logs.id", ondelete="CASCADE"), nullable=True),
        sa.Column("content", sa.String(length=500), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "(study_log_id IS NOT NULL AND error_log_id IS NULL) OR "
            "(study_log_id IS NULL AND error_log_id IS NOT NULL)",
            name="ck_comments_exactly_one_record",
        ),
    )
    op.create_index("ix_comments_author_id", "comments", ["author_id"])
    op.create_index("ix_comments_study_log_id", "comments", ["study_log_id"])
    op.create_index("ix_comments_error_log_id", "comments", ["error_log_id"])
    op.create_index("ix_comments_created_at", "comments", ["created_at"])

    op.create_table(
        "record_likes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("study_log_id", sa.Integer(), sa.ForeignKey("study_logs.id", ondelete="CASCADE"), nullable=True),
        sa.Column("error_log_id", sa.Integer(), sa.ForeignKey("error_logs.id", ondelete="CASCADE"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint(
            "(study_log_id IS NOT NULL AND error_log_id IS NULL) OR "
            "(study_log_id IS NULL AND error_log_id IS NOT NULL)",
            name="ck_record_likes_exactly_one_record",
        ),
        sa.UniqueConstraint("user_id", "study_log_id", name="uq_like_user_study"),
        sa.UniqueConstraint("user_id", "error_log_id", name="uq_like_user_error"),
    )
    op.create_index("ix_record_likes_user_id", "record_likes", ["user_id"])
    op.create_index("ix_record_likes_study_log_id", "record_likes", ["study_log_id"])
    op.create_index("ix_record_likes_error_log_id", "record_likes", ["error_log_id"])

    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("reporter_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("study_log_id", sa.Integer(), sa.ForeignKey("study_logs.id", ondelete="CASCADE"), nullable=True),
        sa.Column("todo_id", sa.Integer(), sa.ForeignKey("todos.id", ondelete="CASCADE"), nullable=True),
        sa.Column("error_log_id", sa.Integer(), sa.ForeignKey("error_logs.id", ondelete="CASCADE"), nullable=True),
        sa.Column("comment_id", sa.Integer(), sa.ForeignKey("comments.id", ondelete="CASCADE"), nullable=True),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint(
            "(CASE WHEN study_log_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN todo_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN error_log_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN comment_id IS NOT NULL THEN 1 ELSE 0 END) = 1",
            name="ck_reports_exactly_one_target",
        ),
        sa.UniqueConstraint("reporter_id", "study_log_id", name="uq_reporter_study"),
        sa.UniqueConstraint("reporter_id", "todo_id", name="uq_reporter_todo"),
        sa.UniqueConstraint("reporter_id", "error_log_id", name="uq_reporter_error"),
        sa.UniqueConstraint("reporter_id", "comment_id", name="uq_reporter_comment"),
    )
    op.create_index("ix_reports_reporter_id", "reports", ["reporter_id"])
    op.create_index("ix_reports_study_log_id", "reports", ["study_log_id"])
    op.create_index("ix_reports_todo_id", "reports", ["todo_id"])
    op.create_index("ix_reports_error_log_id", "reports", ["error_log_id"])
    op.create_index("ix_reports_comment_id", "reports", ["comment_id"])
    op.create_index("ix_reports_created_at", "reports", ["created_at"])


def downgrade() -> None:
    op.drop_table("reports")
    op.drop_table("record_likes")
    op.drop_table("comments")
    op.drop_table("error_logs")
    op.drop_table("todos")
    op.drop_table("study_logs")
