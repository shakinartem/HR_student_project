from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import PaymentStatus, VacancyStatus
from app.models import HRProfile, Payment, User, Vacancy
from app.services.student_finance import get_student_tariff, log_event


def list_hr_vacancies(session: Session, *, hr_user: User) -> list[Vacancy]:
    return list(
        session.scalars(
            select(Vacancy).where(Vacancy.hr_user_id == hr_user.id).order_by(Vacancy.created_at.desc())
        ).all()
    )


def _ensure_hr_owns_company(session: Session, *, hr_user: User, company_id: UUID) -> HRProfile:
    hr_profile = session.scalar(
        select(HRProfile).where(HRProfile.user_id == hr_user.id, HRProfile.company_id == company_id)
    )
    if hr_profile is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="HR does not own company")
    return hr_profile


def create_hr_vacancy(session: Session, *, hr_user: User, payload: dict) -> Vacancy:
    company_id = UUID(payload["company_id"])
    _ensure_hr_owns_company(session, hr_user=hr_user, company_id=company_id)
    vacancy = Vacancy(
        company_id=company_id,
        hr_user_id=hr_user.id,
        title=payload["title"],
        category=payload["category"],
        job_type=payload["job_type"],
        schedule=payload["schedule"],
        salary_text=payload.get("salary_text") or "",
        salary_min=payload.get("salary_min"),
        salary_max=payload.get("salary_max"),
        district=payload.get("district"),
        address=payload.get("address"),
        format=payload.get("format"),
        description=payload.get("description"),
        responsibilities=payload.get("responsibilities"),
        requirements=payload.get("requirements"),
        conditions=payload.get("conditions"),
        experience_required=bool(payload.get("experience_required")),
        status=VacancyStatus.DRAFT,
        moderation_status="manual_review",
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
    session.refresh(vacancy)
    return vacancy


def get_hr_vacancy(session: Session, *, hr_user: User, vacancy_id: UUID) -> Vacancy:
    vacancy = session.scalar(select(Vacancy).where(Vacancy.id == vacancy_id, Vacancy.hr_user_id == hr_user.id))
    if vacancy is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    return vacancy


def update_hr_vacancy(session: Session, *, hr_user: User, vacancy_id: UUID, payload: dict) -> Vacancy:
    vacancy = get_hr_vacancy(session, hr_user=hr_user, vacancy_id=vacancy_id)
    if "company_id" in payload:
        company_id = UUID(payload["company_id"])
        _ensure_hr_owns_company(session, hr_user=hr_user, company_id=company_id)
        vacancy.company_id = company_id
    for field in [
        "title",
        "category",
        "job_type",
        "schedule",
        "salary_text",
        "district",
        "address",
        "format",
        "description",
        "responsibilities",
        "requirements",
        "conditions",
    ]:
        if field in payload:
            setattr(vacancy, field, payload[field])
    if "salary_min" in payload:
        vacancy.salary_min = payload.get("salary_min")
    if "salary_max" in payload:
        vacancy.salary_max = payload.get("salary_max")
    if "experience_required" in payload:
        vacancy.experience_required = bool(payload.get("experience_required"))
    session.commit()
    session.refresh(vacancy)
    return vacancy


def create_publish_payment(session: Session, *, hr_user: User, vacancy_id: UUID, settings) -> Payment:
    vacancy = get_hr_vacancy(session, hr_user=hr_user, vacancy_id=vacancy_id)
    tariff = get_student_tariff(session, settings)
    payment = Payment(
        user_id=hr_user.id,
        amount=Decimal(str(tariff.amount)),
        currency="RUB",
        provider="mock",
        provider_payment_id=f"mock-{uuid4().hex}",
        status=PaymentStatus.PENDING,
        purpose="hr_vacancy_publication",
    )
    session.add(payment)
    session.flush()
    log_event(
        session,
        user_id=hr_user.id,
        event_name="vacancy_payment_started",
        entity_type="vacancy",
        entity_id=vacancy.id,
    )
    session.commit()
    session.refresh(payment)
    return payment


def handle_hr_publication_payment_success(session: Session, *, payment: Payment, settings) -> Payment:
    now = datetime.now(UTC)
    payment.status = PaymentStatus.SUCCEEDED
    payment.paid_at = now
    vacancy = session.scalar(select(Vacancy).where(Vacancy.id == payment.vacancy_id))
    if vacancy is not None:
        vacancy.status = VacancyStatus.ACTIVE
        vacancy.published_at = now
    log_event(
        session,
        user_id=payment.user_id,
        event_name="vacancy_payment_succeeded",
        entity_type="vacancy",
        entity_id=vacancy.id if vacancy else None,
    )
    session.commit()
    session.refresh(payment)
    return payment