from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import PaymentStatus, SubscriptionStatus, SupportTicketStatus, UserRole
from app.models import BalanceTransaction, Payment, StudentProfile, Subscription, SupportTicket, Tariff, User


def ensure_student_monthly_tariff(db_session: Session, amount: Decimal = Decimal("350.00")) -> Tariff:
    tariff = db_session.scalar(select(Tariff).where(Tariff.code == "student_monthly_access"))
    if tariff is None:
        tariff = Tariff(
            code="student_monthly_access",
            title="Student Monthly Access",
            amount=amount,
            duration_days=30,
            is_active=True,
        )
        db_session.add(tariff)
        db_session.commit()
        db_session.refresh(tariff)
    return tariff


def get_current_user(db_session: Session) -> User:
    return db_session.scalar(select(User).where(User.telegram_id == 777001))


def test_student_can_read_empty_profile(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.get("/api/student/profile", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["university"] is None
    assert payload["course"] is None
    assert payload["speciality"] is None
    assert payload["preferred_job_types"] is None
    assert payload["preferred_schedule"] is None
    assert payload["preferred_districts"] is None
    assert payload["experience_text"] is None
    assert payload["profile_completed"] is False


def test_student_can_update_profile(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.patch(
        "/api/student/profile",
        headers=auth_headers,
        json={
            "university": "SGTU",
            "course": 2,
            "speciality": "Computer Science",
            "preferred_job_types": ["part_time", "shift"],
            "preferred_schedule": ["evening"],
            "preferred_districts": ["center"],
            "experience_text": "Worked as a waiter for two months.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["university"] == "SGTU"
    assert payload["course"] == 2
    assert payload["speciality"] == "Computer Science"
    assert payload["preferred_job_types"] == ["part_time", "shift"]
    assert payload["preferred_schedule"] == ["evening"]
    assert payload["preferred_districts"] == ["center"]
    assert payload["experience_text"] == "Worked as a waiter for two months."
    assert payload["profile_completed"] is True


def test_student_cannot_update_role_through_profile_endpoints(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    response = client.patch(
        "/api/student/profile",
        headers=auth_headers,
        json={
            "university": "SGTU",
            "course": 3,
            "speciality": "Law",
            "preferred_job_types": ["part_time"],
            "preferred_schedule": ["day"],
            "preferred_districts": ["center"],
            "experience_text": "Ready to work.",
            "role": "admin",
        },
    )

    assert response.status_code == 200
    user = get_current_user(db_session)
    assert user.role is UserRole.STUDENT


def test_top_up_below_monthly_tariff_is_rejected_if_no_active_subscription(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    ensure_student_monthly_tariff(db_session)

    response = client.post(
        "/api/payments/create",
        headers=auth_headers,
        json={"amount": 349, "purpose": "student_balance_topup"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "First top-up must be at least the monthly tariff amount"


def test_top_up_equal_to_monthly_tariff_creates_pending_payment(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    ensure_student_monthly_tariff(db_session)

    response = client.post(
        "/api/payments/create",
        headers=auth_headers,
        json={"amount": 350, "purpose": "student_balance_topup"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "pending"
    assert payload["confirmation_url"].startswith("mock://payment/")
    payment = db_session.get(Payment, UUID(payload["payment_id"]))
    assert payment is not None
    assert payment.status is PaymentStatus.PENDING
    assert Decimal(payment.amount) == Decimal("350.00")


def test_mock_confirm_succeeded_payment_credits_balance_and_activates_subscription(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    ensure_student_monthly_tariff(db_session)
    create_response = client.post(
        "/api/payments/create",
        headers=auth_headers,
        json={"amount": 350, "purpose": "student_balance_topup"},
    )
    payment_id = UUID(create_response.json()["payment_id"])

    confirm_response = client.post("/api/payments/mock-confirm", headers=auth_headers, json={"payment_id": str(payment_id)})

    assert confirm_response.status_code == 200
    payment = db_session.get(Payment, payment_id)
    assert payment is not None
    assert payment.status is PaymentStatus.SUCCEEDED
    assert payment.paid_at is not None

    balance_response = client.get("/api/student/balance", headers=auth_headers)
    assert balance_response.status_code == 200
    assert Decimal(balance_response.json()["balance"]) == Decimal("0.00")
    assert len(balance_response.json()["transactions"]) == 2

    subscription_response = client.get("/api/student/subscription", headers=auth_headers)
    assert subscription_response.status_code == 200
    assert subscription_response.json()["status"] == "active"


def test_top_up_above_monthly_tariff_leaves_remaining_balance_after_subscription_charge(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    ensure_student_monthly_tariff(db_session)
    create_response = client.post(
        "/api/payments/create",
        headers=auth_headers,
        json={"amount": 700, "purpose": "student_balance_topup"},
    )

    confirm_response = client.post(
        "/api/payments/mock-confirm",
        headers=auth_headers,
        json={"payment_id": create_response.json()["payment_id"]},
    )

    assert confirm_response.status_code == 200
    balance_response = client.get("/api/student/balance", headers=auth_headers)
    assert Decimal(balance_response.json()["balance"]) == Decimal("350.00")


def test_duplicate_mock_confirmation_is_idempotent(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    ensure_student_monthly_tariff(db_session)
    create_response = client.post(
        "/api/payments/create",
        headers=auth_headers,
        json={"amount": 700, "purpose": "student_balance_topup"},
    )
    payment_id = UUID(create_response.json()["payment_id"])

    first_response = client.post("/api/payments/mock-confirm", headers=auth_headers, json={"payment_id": str(payment_id)})
    second_response = client.post("/api/payments/mock-confirm", headers=auth_headers, json={"payment_id": str(payment_id)})

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    payment = db_session.get(Payment, payment_id)
    assert payment is not None
    assert payment.status is PaymentStatus.SUCCEEDED
    transactions = db_session.scalars(
        select(BalanceTransaction).where(BalanceTransaction.payment_id == payment.id).order_by(BalanceTransaction.created_at)
    ).all()
    assert len(transactions) == 2

    subscriptions = db_session.scalars(select(Subscription).where(Subscription.user_id == payment.user_id)).all()
    assert len(subscriptions) == 1
    assert subscriptions[0].status is SubscriptionStatus.ACTIVE


def test_subscription_cannot_activate_from_pending_payment(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    ensure_student_monthly_tariff(db_session)
    client.post(
        "/api/payments/create",
        headers=auth_headers,
        json={"amount": 350, "purpose": "student_balance_topup"},
    )

    response = client.get("/api/student/subscription", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["status"] == "inactive"
    assert db_session.scalar(select(Subscription).limit(1)) is None


def test_existing_active_subscription_is_preserved_correctly(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    ensure_student_monthly_tariff(db_session)
    user = get_current_user(db_session)
    now = datetime.now(UTC)
    subscription = Subscription(
        user_id=user.id,
        starts_at=now - timedelta(days=5),
        expires_at=now + timedelta(days=10),
        status=SubscriptionStatus.ACTIVE,
    )
    db_session.add(subscription)
    db_session.commit()
    original_expires_at = subscription.expires_at

    create_response = client.post(
        "/api/payments/create",
        headers=auth_headers,
        json={"amount": 350, "purpose": "student_balance_topup"},
    )
    confirm_response = client.post(
        "/api/payments/mock-confirm",
        headers=auth_headers,
        json={"payment_id": create_response.json()["payment_id"]},
    )

    assert confirm_response.status_code == 200
    db_session.refresh(subscription)
    assert subscription.expires_at == original_expires_at

    balance_response = client.get("/api/student/balance", headers=auth_headers)
    assert Decimal(balance_response.json()["balance"]) == Decimal("350.00")


def test_balance_endpoint_returns_correct_ledger_derived_balance(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    ensure_student_monthly_tariff(db_session)
    user = get_current_user(db_session)
    db_session.add_all(
        [
            BalanceTransaction(user_id=user.id, amount=Decimal("500.00"), type="credit", reason="manual_topup"),
            BalanceTransaction(user_id=user.id, amount=Decimal("-150.00"), type="debit", reason="monthly_charge"),
        ]
    )
    db_session.commit()

    response = client.get("/api/student/balance", headers=auth_headers)

    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == Decimal("350.00")
    assert len(response.json()["transactions"]) == 2


def test_payment_history_returns_current_user_payments_only(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    ensure_student_monthly_tariff(db_session)
    current_user = get_current_user(db_session)
    other_user = User(
        telegram_id=777002,
        role=UserRole.STUDENT,
        username="other_student",
        first_name="Other",
        last_name="Student",
    )
    db_session.add(other_user)
    db_session.flush()
    db_session.add_all(
        [
            Payment(
                user_id=current_user.id,
                amount=Decimal("350.00"),
                currency="RUB",
                provider="mock",
                provider_payment_id="mock-current",
                status=PaymentStatus.PENDING,
                purpose="student_balance_topup",
            ),
            Payment(
                user_id=other_user.id,
                amount=Decimal("700.00"),
                currency="RUB",
                provider="mock",
                provider_payment_id="mock-other",
                status=PaymentStatus.PENDING,
                purpose="student_balance_topup",
            ),
        ]
    )
    db_session.commit()

    response = client.get("/api/payments/history", headers=auth_headers)

    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["provider_payment_id"] == "mock-current"


def test_refund_request_creates_support_ticket(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    response = client.post(
        "/api/student/refund-request",
        headers=auth_headers,
        json={"message": "Хочу вернуть остаток баланса"},
    )

    assert response.status_code == 201
    user = get_current_user(db_session)
    ticket = db_session.scalar(select(SupportTicket).where(SupportTicket.user_id == user.id))
    assert ticket is not None
    assert ticket.type == "refund_request"
    assert ticket.status is SupportTicketStatus.OPEN


def test_refund_request_does_not_mutate_balance(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    user = get_current_user(db_session)
    db_session.add(BalanceTransaction(user_id=user.id, amount=Decimal("150.00"), type="credit", reason="manual_topup"))
    db_session.commit()

    response = client.post(
        "/api/student/refund-request",
        headers=auth_headers,
        json={"message": "Прошу обработать возврат"},
    )

    assert response.status_code == 201
    balance_response = client.get("/api/student/balance", headers=auth_headers)
    assert Decimal(balance_response.json()["balance"]) == Decimal("150.00")


def test_non_student_role_cannot_use_student_endpoints(
    client: TestClient,
    hr_headers: dict[str, str],
) -> None:
    response = client.get("/api/student/profile", headers=hr_headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Student role required"
