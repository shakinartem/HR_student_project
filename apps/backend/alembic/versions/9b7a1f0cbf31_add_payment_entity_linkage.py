"""add_payment_entity_linkage

Revision ID: 9b7a1f0cbf31
Revises: c431be6959b2
Create Date: 2026-07-06 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "9b7a1f0cbf31"
down_revision = "c431be6959b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("payments", sa.Column("entity_type", sa.String(length=255), nullable=True))
    op.add_column("payments", sa.Column("entity_id", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("payments", "entity_id")
    op.drop_column("payments", "entity_type")
