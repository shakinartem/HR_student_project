from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.enums import UserRole
from app.models import Company, GuestVacancyView, User, Vacancy, VacancyView

GUEST_VIEW_LIMIT = 3


def serialize_vacancy_list_item(vacancy: Vacancy) -> dict:
    return {
        "id": vacancy.id,
        "title": vacancy.title,
        "company_name": vacancy.company.name if vacancy.company else None,
        "category": vacancy.category,
        "job_type": vacancy.job_type,
        "salary_text": vacancy.salary_text,
        "salary_min": vacancy.salary_min,
        "salary_max": vacancy.salary_max,
        "district": vacancy.district,
        "schedule": vacancy.schedule,
        "format": vacancy.format,
        "is_promoted": vacancy.is_promoted,
        "published_at": vacancy.published_at,
    }


def serialize_vacancy_detail_for_student(vacancy: Vacancy) -> dict:
    payload = serialize_vacancy_list_item(vacancy)
    payload.update(
        {
            "address": vacancy.address,
            "description": vacancy.description,
            "requirements": vacancy.requirements,
            "conditions": vacancy.conditions,
            "experience_required": vacancy.experience_required,
        }
    )
    return payload


def base_active_vacancies_query() -> Select[tuple[Vacancy]]:
    now = datetime.now(UTC)
    return (
        select(Vacancy)
        .options(joinedload(Vacancy.company))
        .where(Vacancy.status == "active")
        .where(Vacancy.moderation_status == "approved")
        .where(Vacancy.published_at.is_not(None))
        .where(or_(Vacancy.expires_at.is_(None), Vacancy.expires_at > now))
    )


def list_active_vacancies(
    session: Session,
    *,
    category: str | None = None,
    job_type: str | None = None,
    district: str | None = None,
    salary_min: int | None = None,
    vacancy_format: str | None = None,
    schedule: str | None = None,
    experience_required: bool | None = None,
    promoted_first: bool = True,
) -> list[Vacancy]:
    query = base_active_vacancies_query()
    if category:
        query = query.where(Vacancy.category == category)
    if job_type:
        query = query.where(Vacancy.job_type == job_type)
    if district:
        query = query.where(Vacancy.district == district)
    if salary_min is not None:
        query = query.where(Vacancy.salary_min.is_not(None)).where(Vacancy.salary_min >= salary_min)
    if vacancy_format:
        query = query.where(Vacancy.format == vacancy_format)
    if schedule:
        query = query.where(Vacancy.schedule == schedule)
    if experience_required is not None:
        query = query.where(Vacancy.experience_required == experience_required)

    if promoted_first:
        query = query.order_by(Vacancy.is_promoted.desc(), Vacancy.published_at.desc())
    else:
        query = query.order_by(Vacancy.published_at.desc())
    return list(session.scalars(query).all())


def get_active_vacancy_or_404(session: Session, vacancy_id: UUID) -> Vacancy:
    vacancy = session.scalar(base_active_vacancies_query().where(Vacancy.id == vacancy_id))
    if vacancy is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    return vacancy


def _existing_user_view(session: Session, *, user_id, vacancy_id: UUID) -> VacancyView | None:
    return session.scalar(
        select(VacancyView).where(
            VacancyView.user_id == user_id,
            VacancyView.vacancy_id == vacancy_id,
        )
    )


def _existing_guest_view(session: Session, *, guest_id: str, vacancy_id: UUID) -> GuestVacancyView | None:
    return session.scalar(
        select(GuestVacancyView).where(
            GuestVacancyView.guest_id == guest_id,
            GuestVacancyView.vacancy_id == vacancy_id,
        )
    )


def _count_user_views(session: Session, *, user_id) -> int:
    return int(session.scalar(select(func.count(VacancyView.id)).where(VacancyView.user_id == user_id)) or 0)


def _count_guest_views(session: Session, *, guest_id: str) -> int:
    return int(session.scalar(select(func.count(GuestVacancyView.id)).where(GuestVacancyView.guest_id == guest_id)) or 0)


def ensure_view_allowed_and_record(
    session: Session,
    *,
    vacancy: Vacancy,
    user: User | None,
    guest_id: str | None,
) -> tuple[int, str]:
    if user is None and not guest_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Anonymous vacancy preview requires X-Guest-Id header",
        )

    if user is not None:
        if user.role is UserRole.STUDENT:
            existing = _existing_user_view(session, user_id=user.id, vacancy_id=vacancy.id)
            if existing is not None:
                return _count_user_views(session, user_id=user.id), "user"
            session.add(VacancyView(user_id=user.id, vacancy_id=vacancy.id))
            session.commit()
            return _count_user_views(session, user_id=user.id) + 1, "user"

        view_count = _count_user_views(session, user_id=user.id)
        if view_count >= GUEST_VIEW_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "GUEST_VIEW_LIMIT_REACHED",
                    "message": "Guest preview limit reached",
                },
            )
        existing = _existing_user_view(session, user_id=user.id, vacancy_id=vacancy.id)
        if existing is not None:
            return view_count, "user"
        session.add(VacancyView(user_id=user.id, vacancy_id=vacancy.id))
        session.commit()
        return view_count + 1, "user"

    assert guest_id is not None
    existing_guest = _existing_guest_view(session, guest_id=guest_id, vacancy_id=vacancy.id)
    if existing_guest is not None:
        return _count_guest_views(session, guest_id=guest_id), "guest"

    guest_view_count = _count_guest_views(session, guest_id=guest_id)
    if guest_view_count >= GUEST_VIEW_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "GUEST_VIEW_LIMIT_REACHED",
                "message": "Guest preview limit reached",
            },
        )
    session.add(GuestVacancyView(guest_id=guest_id, vacancy_id=vacancy.id))
    session.commit()
    return guest_view_count + 1, "guest"
