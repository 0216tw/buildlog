"""create materials

Revision ID: 20261020_04
Revises: 20261020_03
Create Date: 2026-10-20
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20261020_04"
down_revision: str | None = "20261020_03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "materials",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.Column("original_filename", sa.Text(), nullable=False),
        sa.Column("stored_path", sa.String(length=500), nullable=False),
        sa.Column("media_type", sa.String(length=10), nullable=False),
        sa.Column("content_type", sa.String(length=50), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "media_type IN ('image', 'video')",
            name="ck_materials_media_type",
        ),
        sa.CheckConstraint(
            "(media_type = 'image' AND content_type IN ('image/png', 'image/jpeg')) "
            "OR (media_type = 'video' AND content_type = 'video/mp4')",
            name="ck_materials_content_type",
        ),
        sa.CheckConstraint("size_bytes > 0", name="ck_materials_positive_size"),
        sa.CheckConstraint(
            "(media_type = 'image' AND size_bytes <= 5242880) "
            "OR (media_type = 'video' AND size_bytes <= 31457280)",
            name="ck_materials_size_limit",
        ),
        sa.UniqueConstraint("stored_path", name="uq_materials_stored_path"),
    )
    op.create_index(
        "ix_materials_user_created",
        "materials",
        ["user_id", "created_at", "id"],
    )


def downgrade() -> None:
    op.drop_index("ix_materials_user_created", table_name="materials")
    op.drop_table("materials")
