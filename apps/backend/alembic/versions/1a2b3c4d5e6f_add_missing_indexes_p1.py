"""add_missing_indexes_p1

Revision ID: 1a2b3c4d5e6f
Revises: 6282e6a58832
Create Date: 2026-07-06 13:06:00.000000
"""
from __future__ import annotations

from alembic import op


# revision identifiers, used by Alembic.
revision = "1a2b3c4d5e6f"
down_revision = "6282e6a58832"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_vacancies_company_id", "vacancies", ["company_id"], unique=False)
    op.create_index("ix_vacancies_hr_user_id", "vacancies", ["hr_user_id"], unique=False)
    op.create_index("ix_vacancies_status", "vacancies", ["status"], unique=False)
    op.create_index("ix_vacancies_moderation_status", "vacancies", ["moderation_status"], unique=False)
    op.create_index("ix_vacancies_published_at", "vacancies", ["published_at"], unique=False)
    op.create_index("ix_vacancies_expires_at", "vacancies", ["expires_at"], unique=False)
    op.create_index("ix_payments_user_id", "payments", ["user_id"], unique=False)
    op.create_index("ix_balance_transactions_user_id", "balance_transactions", ["user_id"], unique=False)
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"], unique=False)
    op.create_index("ix_subscriptions_status", "subscriptions", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_subscriptions_status", table_name="subscriptions")
    op.drop_index("ix_subscriptions_user_id", table_name="subscriptions")
    op.drop_index("ix_balance_transactions_user_id", table_name="balance_transactions")
    op.drop_index("ix_payments_user_id", table_name="payments")
    op.drop_index("ix_vacancies_expires_at", table_name="vacancies")
    op.drop_index("ix_vacancies_published_at", table_name="vacancies")
    op.drop_index("ix_vacancies_moderation_status", table_name="vacancies")
    op.drop_index("ix_vacancies_status", table_name="vacancies")
    op.drop_index("ix_vacancies_hr_user_id", table_name="vacancies")
    op.drop_index("ix_vacancies_company_id", table_name="vacancies")