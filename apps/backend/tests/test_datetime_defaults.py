from __future__ import annotations

import warnings
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import PaymentStatus
from app.models import BalanceTransaction, Event, Payment, User


def test_model_timestamp_defaults_do_not_emit_datetime_utcnow_warnings(db_session: Session) -> None:
    user = User(
        telegram_id=770001,
        username="datetime_user",
        first_name="Date",
        last_name="Time",
    )
    db_session.add(user)
    db_session.flush()

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        db_session.add_all(
            [
                Payment(
                    user_id=user.id,
                    amount=Decimal("100.00"),
                    currency="RUB",
                    provider="mock",
                    provider_payment_id="mock-datetime-defaults",
                    status=PaymentStatus.PENDING,
                    purpose="student_balance_topup",
                ),
                BalanceTransaction(
                    user_id=user.id,
                    amount=Decimal("100.00"),
                    type="credit",
                    reason="manual_topup",
                ),
                Event(
                    user_id=user.id,
                    event_name="datetime_defaults_checked",
                    entity_type="test",
                    entity_id="datetime-defaults",
                ),
            ]
        )
        db_session.flush()

    utcnow_warnings = [
        warning
        for warning in caught
        if "datetime.datetime.utcnow() is deprecated" in str(warning.message)
    ]
    assert utcnow_warnings == []
