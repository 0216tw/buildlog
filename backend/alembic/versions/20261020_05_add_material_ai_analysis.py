"""add material ai analysis

Revision ID: 20261020_05
Revises: 20261020_04
Create Date: 2026-10-20
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20261020_05"
down_revision: str | None = "20261020_04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("materials") as batch_op:
        batch_op.add_column(sa.Column("ai_summary", sa.Text(), nullable=True))
        batch_op.add_column(
            sa.Column(
                "ai_status",
                sa.String(length=20),
                server_default="not_requested",
                nullable=False,
            )
        )
        batch_op.add_column(sa.Column("ai_model", sa.String(length=100), nullable=True))
        batch_op.add_column(
            sa.Column("ai_prompt_version", sa.String(length=50), nullable=True)
        )
        batch_op.add_column(
            sa.Column("ai_attempt_count", sa.Integer(), server_default="0", nullable=False)
        )
        batch_op.add_column(sa.Column("ai_started_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("ai_analyzed_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("ai_error_code", sa.String(length=50), nullable=True))
        batch_op.create_check_constraint(
            "ck_materials_ai_status",
            "ai_status IN ('not_requested', 'pending', 'processing', 'completed', 'failed')",
        )
        batch_op.create_check_constraint(
            "ck_materials_ai_attempt_count",
            "ai_attempt_count >= 0 AND ai_attempt_count <= 3",
        )
        batch_op.create_check_constraint(
            "ck_materials_ai_summary_length",
            "ai_summary IS NULL OR (length(ai_summary) >= 1 AND length(ai_summary) <= 1000)",
        )
        batch_op.create_index(
            "ix_materials_ai_work",
            ["ai_status", "created_at", "id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("materials") as batch_op:
        batch_op.drop_index("ix_materials_ai_work")
        batch_op.drop_constraint("ck_materials_ai_summary_length", type_="check")
        batch_op.drop_constraint("ck_materials_ai_attempt_count", type_="check")
        batch_op.drop_constraint("ck_materials_ai_status", type_="check")
        batch_op.drop_column("ai_error_code")
        batch_op.drop_column("ai_analyzed_at")
        batch_op.drop_column("ai_started_at")
        batch_op.drop_column("ai_attempt_count")
        batch_op.drop_column("ai_prompt_version")
        batch_op.drop_column("ai_model")
        batch_op.drop_column("ai_status")
        batch_op.drop_column("ai_summary")
