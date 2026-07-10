"""add_p2_models

Revision ID: 2b3c4d5e6f7g
Revises: 1a2b3c4d5e6f
Create Date: 2026-07-06 13:30:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2b3c4d5e6f7g"
down_revision = "1a2b3c4d5e6f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "role_audit",
        sa.Column("changed_by_user_id", sa.String(length=255), nullable=False),
        sa.Column("target_user_id", sa.String(length=255), nullable=False),
        sa.Column("old_role", sa.String(), nullable=True),
        sa.Column("new_role", sa.String(), nullable=False),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_role_audit")),
    )
    op.add_column("complaints", sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("complaints", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("complaints", "deleted_at")
    op.drop_column("complaints", "is_deleted")
    op.drop_table("role_audit")