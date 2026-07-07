from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import Settings
from app.core.enums import HRStatus, ModerationResult, PaymentStatus, UserRole, VacancyStatus
from app.models import ModerationLog, Payment, Tariff, User, Vacancy
from app.services.student_finance import log_event

HR_VACANCY_PUBLICATION_PURPOSE = "hr_vacancy_publication"
VACANCY_TARIFF_CODE = "vacancy_basic_30d"

REJECT_KEYWORDS = {
    "scam": "Potential scam wording",
    "casino": "Casino-related vacancy",
    "betting": "Betting-related vacancy",
    "adult": "Adult content wording",
    "18+": "Adult content wording",
    "escort": "Escort-related wording",
    "financial pyramid": "Financial pyramid wording",
    "network marketing": "Network marketing wording",
    "prepayment from student": "Requests prepayment from student",
    "illegal work": "Illegal work wording",
}

MANUAL_REVIEW_KEYWORDS = {
    "unclear employer": "Employer identity is unclear",
    "dangerous": "Potentially dangerous work wording",
    "discrimination": "Potential discrimination wording",
    "crypto": "Crypto opportunity needs review",
    "trading": "Trading/get-rich wording needs review",
    "high income": "Suspicious high income wording",
    "get rich": "Get-rich wording needs review",
    "unknown employer": "Employer identity is unclear",
}


@dataclass(frozen=True)
class ModerationDecision:
    result: ModerationResult
    reason: str | None


def _ensure_active_hr(user: User) -> None:
    if user.role is not UserRole.HR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="HR role required")
    if user.hr_profile is None or user.hr_profile.verified_status is not HRStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Active HR role required")


def get_vacancy_publication_price(session: Session, settings: Settings) -> tuple[Decimal, int]:
    tariff = session.scalar(select(Tariff).where(Tariff.code == VACANCY_TARIFF_CODE, Tariff.is_active.is_(True)))
    if tariff is not None:
        return Decimal(str(tariff.amount)).quantize(Decimal("0.01")), tariff.duration_days
    return Decimal(str(settings.vacancy_basic_price_rub)).quantize(Decimal("0.01")), 30


def serialize_hr_vacancy(vacancy: Vacancy) -> dict:
    company = vacancy.company
    payment_required = vacancy.status in {
        VacancyStatus.DRAFT,
        VacancyStatus.AWAITING_PAYMENT,
    }
    return {
        "id": vacancy.id,
        "title": vacancy.title,
        "category": vacancy.category,
        "job_type": vacancy.job_type,
        "schedule": vacancy.schedule,
        "salary_text": vacancy.salary_text,
        "salary_min": vacancy.salary_min,
        "salary_max": vacancy.salary_max,
        "district": vacancy.district,
        "address": vacancy.address,
        "format": vacancy.format,
        "description": vacancy.description,
        "responsibilities": vacancy.responsibilities,
        "requirements": vacancy.requirements,
        "conditions": vacancy.conditions,
        "experience_required": vacancy.experience_required,
        "photo_url": vacancy.photo_url,
        "status": vacancy.status.value,
        "moderation_status": vacancy.moderation_status,
        "payment_required": payment_required,
        "is_promoted": vacancy.is_promoted,
        "published_at": vacancy.published_at,
        "expires_at": vacancy.expires_at,
        "hidden_contacts": {
            "contact_name": company.contact_name if company else None,
            "contact_phone": company.contact_phone if company else None,
            "contact_email": company.contact_email if company else None,
            "contact_telegram": company.contact_telegram if company else None,
        },
    }


def create_hr_vacancy(session: Session, *, hr_user: User, payload: dict) -> Vacancy:
    _ensure_active_hr(hr_user)
    vacancy = Vacancy(
        company_id=hr_user.hr_profile.company_id,
        hr_user_id=hr_user.id,
        status=VacancyStatus.DRAFT,
        moderation_status="manual_review",
        **payload,
    )
    session.add(vacancy)
    session.flush()
    log_event(
        session,
        user_id=hr_user.id,
        event_name="vacancy_created",
        entity_type="vacancy",
        entity_id=vacancy.id,
    )
    session.commit()
    return get_hr_vacancy(session, hr_user=hr_user, vacancy_id=vacancy.id)


def list_hr_vacancies(session: Session, *, hr_user: User) -> list[Vacancy]:
    _ensure_active_hr(hr_user)
    return list(
        session.scalars(
            select(Vacancy)
            .options(joinedload(Vacancy.company))
            .where(Vacancy.hr_user_id == hr_user.id)
            .order_by(Vacancy.created_at.desc())
        ).all()
    )


def get_hr_vacancy(session: Session, *, hr_user: User, vacancy_id: UUID) -> Vacancy:
    _ensure_active_hr(hr_user)
    vacancy = session.scalar(
        select(Vacancy)
        .options(joinedload(Vacancy.company))
        .where(Vacancy.id == vacancy_id, Vacancy.hr_user_id == hr_user.id)
    )
    if vacancy is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    return vacancy


def update_hr_vacancy(session: Session, *, hr_user: User, vacancy_id: UUID, payload: dict) -> Vacancy:
    vacancy = get_hr_vacancy(session, hr_user=hr_user, vacancy_id=vacancy_id)
    if vacancy.status not in {VacancyStatus.DRAFT, VacancyStatus.REJECTED, VacancyStatus.MANUAL_REVIEW}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Vacancy cannot be edited in current status")
    for field, value in payload.items():
        setattr(vacancy, field, value)
    session.commit()
    return get_hr_vacancy(session, hr_user=hr_user, vacancy_id=vacancy.id)


def create_publish_payment(session: Session, *, hr_user: User, vacancy_id: UUID, settings: Settings) -> Payment:
    vacancy = get_hr_vacancy(session, hr_user=hr_user, vacancy_id=vacancy_id)
    if vacancy.status not in {VacancyStatus.DRAFT, VacancyStatus.AWAITING_PAYMENT, VacancyStatus.REJECTED, VacancyStatus.MANUAL_REVIEW}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Vacancy cannot request publication payment")
    amount, _duration_days = get_vacancy_publication_price(session, settings)
    payment = Payment(
        user_id=hr_user.id,
        amount=amount,
        currency="RUB",
        provider="mock",
        provider_payment_id=f"mock-{uuid4().hex}",
        status=PaymentStatus.PENDING,
        purpose=HR_VACANCY_PUBLICATION_PURPOSE,
        entity_type="vacancy",
        entity_id=str(vacancy.id),
    )
    session.add(payment)
    vacancy.status = VacancyStatus.AWAITING_PAYMENT
    session.flush()
    log_event(
        session,
        user_id=hr_user.id,
        event_name="vacancy_payment_created",
        entity_type="payment",
        entity_id=payment.id,
        metadata={"vacancy_id": str(vacancy.id), "amount": str(payment.amount)},
    )
    session.commit()
    session.refresh(payment)
    return payment


def moderate_vacancy(vacancy: Vacancy) -> ModerationDecision:
    haystack = " ".join(
        filter(
            None,
            [
                vacancy.title,
                vacancy.description,
                vacancy.responsibilities,
                vacancy.requirements,
                vacancy.conditions,
            ],
        )
    ).lower()
    for keyword, reason in REJECT_KEYWORDS.items():
        if keyword in haystack:
            return ModerationDecision(result=ModerationResult.REJECTED, reason=reason)
    for keyword, reason in MANUAL_REVIEW_KEYWORDS.items():
        if keyword in haystack:
            return ModerationDecision(result=ModerationResult.MANUAL_REVIEW, reason=reason)
    return ModerationDecision(result=ModerationResult.APPROVED, reason=None)


def handle_hr_publication_payment_success(session: Session, *, payment: Payment, settings: Settings) -> Payment:
    if payment.entity_type != "vacancy" or payment.entity_id is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Payment is not linked to a vacancy")
    vacancy = session.scalar(select(Vacancy).where(Vacancy.id == UUID(payment.entity_id)).options(joinedload(Vacancy.company)))
    if vacancy is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    if payment.status is PaymentStatus.SUCCEEDED and vacancy.status in {
        VacancyStatus.ACTIVE,
        VacancyStatus.REJECTED,
        VacancyStatus.MANUAL_REVIEW,
    }:
        return payment

    now = datetime.now(UTC)
    payment.status = PaymentStatus.SUCCEEDED
    payment.paid_at = now
    log_event(
        session,
        user_id=payment.user_id,
        event_name="vacancy_payment_succeeded",
        entity_type="payment",
        entity_id=payment.id,
        metadata={"vacancy_id": str(vacancy.id)},
    )

    vacancy.status = VacancyStatus.MODERATION
    log_event(
        session,
        user_id=payment.user_id,
        event_name="vacancy_submitted_to_moderation",
        entity_type="vacancy",
        entity_id=vacancy.id,
    )

    decision = moderate_vacancy(vacancy)
    session.add(
        ModerationLog(
            entity_type="vacancy",
            entity_id=str(vacancy.id),
            result=decision.result,
            reason=decision.reason,
            raw_response=None,
        )
    )
    vacancy.moderation_status = decision.result.value
    _amount, duration_days = get_vacancy_publication_price(session, settings)

    if decision.result is ModerationResult.APPROVED:
        vacancy.status = VacancyStatus.ACTIVE
        vacancy.published_at = now
        vacancy.expires_at = now + timedelta(days=duration_days)
        log_event(
            session,
            user_id=payment.user_id,
            event_name="vacancy_approved",
            entity_type="vacancy",
            entity_id=vacancy.id,
        )
    elif decision.result is ModerationResult.REJECTED:
        vacancy.status = VacancyStatus.REJECTED
        log_event(
            session,
            user_id=payment.user_id,
            event_name="vacancy_rejected",
            entity_type="vacancy",
            entity_id=vacancy.id,
            metadata={"reason": decision.reason},
        )
    else:
        vacancy.status = VacancyStatus.MANUAL_REVIEW
        log_event(
            session,
            user_id=payment.user_id,
            event_name="vacancy_manual_review",
            entity_type="vacancy",
            entity_id=vacancy.id,
            metadata={"reason": decision.reason},
        )

    session.commit()
    session.refresh(payment)
    return payment
