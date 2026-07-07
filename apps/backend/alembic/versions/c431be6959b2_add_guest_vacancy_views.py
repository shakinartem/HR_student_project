"""add_guest_vacancy_views

Revision ID: c431be6959b2
Revises: 6282e6a58832
Create Date: 2026-07-06 15:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "c431be6959b2"
down_revision = "6282e6a58832"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "guest_vacancy_views",
        sa.Column("guest_id", sa.String(length=255), nullable=False),
        sa.Column("vacancy_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["vacancy_id"],
            ["vacancies.id"],
            name=op.f("fk_guest_vacancy_views_vacancy_id_vacancies"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_guest_vacancy_views")),
    )
    op.create_index(op.f("ix_guest_vacancy_views_guest_id"), "guest_vacancy_views", ["guest_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_guest_vacancy_views_guest_id"), table_name="guest_vacancy_views")
    op.drop_table("guest_vacancy_views")
