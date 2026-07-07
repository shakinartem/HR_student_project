from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.enums import PaymentStatus, SubscriptionStatus, SupportTicketStatus
from app.models import BalanceTransaction, Event, Payment, StudentProfile, Subscription, SupportTicket, Tariff, User

STUDENT_MONTHLY_ACCESS_CODE = "student_monthly_access"
STUDENT_BALANCE_TOPUP_PURPOSE = "student_balance_topup"


@dataclass(frozen=True)
class TariffSnapshot:
    amount: Decimal
    duration_days: int


def ensure_student_profile(session: Session, *, user: User) -> StudentProfile:
    profile = user.student_profile
    if profile is None:
        profile = StudentProfile(user_id=user.id, profile_completed=False)
        session.add(profile)
        session.commit()
        session.refresh(profile)
    return profile


def is_profile_completed(profile: StudentProfile) -> bool:
    return all(
        [
            bool(profile.university),
            profile.course is not None,
            bool(profile.speciality),
            bool(profile.preferred_job_types),
            bool(profile.preferred_schedule),
            bool(profile.preferred_districts),
            bool(profile.experience_text),
        ]
    )


def get_student_tariff(session: Session, settings: Settings) -> TariffSnapshot:
    tariff = session.scalar(
        select(Tariff).where(Tariff.code == STUDENT_MONTHLY_ACCESS_CODE, Tariff.is_active.is_(True))
    )
    if tariff is not None:
        return TariffSnapshot(amount=Decimal(str(tariff.amount)), duration_days=tariff.duration_days)
    return TariffSnapshot(amount=Decimal(str(settings.student_monthly_tariff_rub)), duration_days=30)


def get_balance(session: Session, *, user_id: object) -> Decimal:
    total = session.scalar(select(func.coalesce(func.sum(BalanceTransaction.amount), 0)).where(BalanceTransaction.user_id == user_id))
    return Decimal(str(total)).quantize(Decimal("0.01"))


def get_balance_transactions(session: Session, *, user_id: object) -> list[BalanceTransaction]:
    return list(
        session.scalars(
            select(BalanceTransaction)
            .where(BalanceTransaction.user_id == user_id)
            .order_by(BalanceTransaction.created_at.desc())
        ).all()
    )


def get_active_subscription(session: Session, *, user_id: object, now: datetime | None = None) -> Subscription | None:
    current_time = now or datetime.now(UTC)
    return session.scalar(
        select(Subscription)
        .where(Subscription.user_id == user_id)
        .where(Subscription.status == SubscriptionStatus.ACTIVE)
        .where(Subscription.expires_at > current_time)
        .order_by(Subscription.expires_at.desc())
    )


def get_latest_subscription(session: Session, *, user_id: object) -> Subscription | None:
    return session.scalar(
        select(Subscription).where(Subscription.user_id == user_id).order_by(Subscription.expires_at.desc())
    )


def log_event(
    session: Session,
    *,
    user_id: object | None,
    event_name: str,
    entity_type: str | None = None,
    entity_id: UUID | str | None = None,
    metadata: dict | None = None,
) -> None:
    session.add(
        Event(
            user_id=user_id,
            event_name=event_name,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            metadata_json=metadata,
        )
    )


def create_pending_topup_payment(
    session: Session,
    *,
    user: User,
    amount: Decimal,
    settings: Settings,
) -> Payment:
    tariff = get_student_tariff(session, settings)
    if get_active_subscription(session, user_id=user.id) is None and amount < tariff.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="First top-up must be at least the monthly tariff amount",
        )

    payment = Payment(
        user_id=user.id,
        amount=amount.quantize(Decimal("0.01")),
        currency="RUB",
        provider="mock",
        provider_payment_id=f"mock-{uuid4().hex}",
        status=PaymentStatus.PENDING,
        purpose=STUDENT_BALANCE_TOPUP_PURPOSE,
    )
    session.add(payment)
    session.flush()
    log_event(
        session,
        user_id=user.id,
        event_name="payment_created",
        entity_type="payment",
        entity_id=payment.id,
        metadata={"purpose": payment.purpose, "amount": str(payment.amount)},
    )
    session.commit()
    session.refresh(payment)
    return payment


def _create_balance_transaction(
    session: Session,
    *,
    user_id: object,
    payment_id: object | None,
    amount: Decimal,
    transaction_type: str,
    reason: str,
) -> BalanceTransaction:
    transaction = BalanceTransaction(
        user_id=user_id,
        payment_id=payment_id,
        amount=amount.quantize(Decimal("0.01")),
        type=transaction_type,
        reason=reason,
    )
    session.add(transaction)
    session.flush()
    log_event(
        session,
        user_id=user_id,
        event_name="balance_transaction_created",
        entity_type="balance_transaction",
        entity_id=transaction.id,
        metadata={"reason": reason, "amount": str(transaction.amount)},
    )
    return transaction


def _get_payment_transactions(session: Session, *, payment_id: object) -> list[BalanceTransaction]:
    return list(session.scalars(select(BalanceTransaction).where(BalanceTransaction.payment_id == payment_id)).all())


def confirm_mock_payment(
    session: Session,
    *,
    payment_id: UUID,
    user: User,
    settings: Settings,
) -> Payment:
    if not (settings.enable_yookassa_test_mode or settings.app_env == "local"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mock payment confirmation is disabled")

    payment = session.get(Payment, payment_id)
    if payment is None or payment.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    log_event(
        session,
        user_id=user.id,
        event_name="webhook_received",
        entity_type="payment",
        entity_id=payment.id,
        metadata={"provider": "mock"},
    )

    if payment.status is PaymentStatus.SUCCEEDED:
        log_event(
            session,
            user_id=user.id,
            event_name="webhook_duplicate_ignored",
            entity_type="payment",
            entity_id=payment.id,
            metadata={"provider": "mock"},
        )
        session.commit()
        session.refresh(payment)
        return payment

    if payment.status is not PaymentStatus.PENDING:
        session.commit()
        session.refresh(payment)
        return payment

    if payment.purpose == "hr_vacancy_publication":
        from app.services.hr_vacancies import handle_hr_publication_payment_success

        if payment.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        return handle_hr_publication_payment_success(session, payment=payment, settings=settings)

    now = datetime.now(UTC)
    payment.status = PaymentStatus.SUCCEEDED
    payment.paid_at = now

    existing_transactions = _get_payment_transactions(session, payment_id=payment.id)
    if not existing_transactions:
        _create_balance_transaction(
            session,
            user_id=user.id,
            payment_id=payment.id,
            amount=Decimal(str(payment.amount)),
            transaction_type="credit",
            reason="student_balance_topup",
        )

    log_event(
        session,
        user_id=user.id,
        event_name="payment_succeeded",
        entity_type="payment",
        entity_id=payment.id,
        metadata={"purpose": payment.purpose, "amount": str(payment.amount)},
    )

    if payment.purpose == STUDENT_BALANCE_TOPUP_PURPOSE and get_active_subscription(session, user_id=user.id, now=now) is None:
        tariff = get_student_tariff(session, settings)
        balance_before_charge = get_balance(session, user_id=user.id)
        if balance_before_charge >= tariff.amount:
            _create_balance_transaction(
                session,
                user_id=user.id,
                payment_id=payment.id,
                amount=-tariff.amount,
                transaction_type="debit",
                reason=STUDENT_MONTHLY_ACCESS_CODE,
            )

            subscription = get_latest_subscription(session, user_id=user.id)
            subscription_started_event = "subscription_activated"
            if subscription is None:
                subscription = Subscription(
                    user_id=user.id,
                    starts_at=now,
                    expires_at=now + timedelta(days=tariff.duration_days),
                    status=SubscriptionStatus.ACTIVE,
                )
                session.add(subscription)
                session.flush()
            else:
                base_start = subscription.expires_at if subscription.expires_at > now else now
                if subscription.expires_at > now:
                    subscription_started_event = "subscription_extended"
                subscription.starts_at = now if subscription.expires_at <= now else subscription.starts_at
                subscription.expires_at = base_start + timedelta(days=tariff.duration_days)
                subscription.status = SubscriptionStatus.ACTIVE
                session.flush()

            log_event(
                session,
                user_id=user.id,
                event_name=subscription_started_event,
                entity_type="subscription",
                entity_id=subscription.id,
                metadata={"expires_at": subscription.expires_at.isoformat()},
            )

    session.commit()
    session.refresh(payment)
    return payment


def list_user_payments(session: Session, *, user_id: object) -> list[Payment]:
    return list(
        session.scalars(
            select(Payment).where(Payment.user_id == user_id).order_by(Payment.created_at.desc())
        ).all()
    )


def create_refund_support_ticket(session: Session, *, user: User, message: str) -> SupportTicket:
    ticket = SupportTicket(
        user_id=user.id,
        type="refund_request",
        subject="Refund request",
        message=message,
        status=SupportTicketStatus.OPEN,
    )
    session.add(ticket)
    session.flush()
    log_event(
        session,
        user_id=user.id,
        event_name="refund_request_created",
        entity_type="support_ticket",
        entity_id=ticket.id,
    )
    session.commit()
    session.refresh(ticket)
    return ticket
