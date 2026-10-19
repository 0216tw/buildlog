"""remove redundant unique constraints

Revision ID: 20261020_03
Revises: 20261020_02
Create Date: 2026-10-20
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20261020_03"
down_revision: str | None = "20261020_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # The initial migration created both a unique index and an equivalent
    # PostgreSQL unique constraint. Models use the named unique indexes, so the
    # duplicate constraints are removed without weakening uniqueness.
    op.drop_constraint("users_email_key", "users", type_="unique")
    op.drop_constraint("users_nickname_key", "users", type_="unique")
    op.drop_constraint("user_sessions_token_hash_key", "user_sessions", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint("user_sessions_token_hash_key", "user_sessions", ["token_hash"])
    op.create_unique_constraint("users_nickname_key", "users", ["nickname"])
    op.create_unique_constraint("users_email_key", "users", ["email"])
