from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.enums import ApplicationStatus, ComplaintStatus, HRStatus, UserRole, VacancyStatus
from app.models import Application, Complaint, User, Vacancy
from app.services.student_finance import get_active_subscription, log_event
from app.services.vacancies import base_active_vacancies_query
from app.services.visibility import serialize_application_for_hr, serialize_application_for_student


def get_applyable_vacancy_or_404(session: Session, vacancy_id: UUID) -> Vacancy:
    vacancy = session.scalar(base_active_vacancies_query().where(Vacancy.id == vacancy_id))
    if vacancy is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    if vacancy.moderation_status != VacancyStatus.APPROVED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")
    return vacancy


def ensure_student_can_apply(session: Session, *, student_user: User) -> None:
    now = datetime.now(UTC)
    if student_user.role is not UserRole.STUDENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student role required")
    mute_until = student_user.mute_until
    if mute_until is not None and mute_until.tzinfo is None:
        mute_until = mute_until.replace(tzinfo=UTC)
    if mute_until is not None and mute_until > now:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Muted student cannot apply")
    subscription = get_active_subscription(session, user_id=student_user.id, now=now)
    if subscription is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Active subscription required")


def ensure_application_not_exists(session: Session, *, vacancy_id: UUID, student_user_id: object) -> None:
    existing = session.scalar(
        select(Application).where(
            Application.vacancy_id == vacancy_id,
            Application.student_user_id == student_user_id,
        )
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Application already exists")


def create_application_for_student(
    session: Session,
    *,
    vacancy: Vacancy,
    student_user: User,
    student_comment: str | None,
) -> Application:
    ensure_student_can_apply(session, student_user=student_user)
    ensure_application_not_exists(session, vacancy_id=vacancy.id, student_user_id=student_user.id)
    application = Application(
        vacancy_id=vacancy.id,
        student_user_id=student_user.id,
        hr_user_id=vacancy.hr_user_id,
        status=ApplicationStatus.SENT,
        student_comment=student_comment,
    )
    session.add(application)
    session.flush()
    log_event(
        session,
        user_id=student_user.id,
        event_name="application_created",
        entity_type="application",
        entity_id=application.id,
        metadata={"vacancy_id": str(vacancy.id)},
    )
    session.commit()
    return get_application_with_relations(session, application.id)


def get_application_with_relations(session: Session, application_id: UUID) -> Application:
    application = session.scalar(
        select(Application)
        .options(
            joinedload(Application.vacancy).joinedload(Vacancy.company),
            joinedload(Application.student_user).joinedload(User.student_profile),
            joinedload(Application.hr_user).joinedload(User.hr_profile),
        )
        .where(Application.id == application_id)
    )
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return application


def list_student_applications(session: Session, *, student_user_id: object) -> list[Application]:
    return list(
        session.scalars(
            select(Application)
            .options(joinedload(Application.vacancy).joinedload(Vacancy.company))
            .where(Application.student_user_id == student_user_id)
            .order_by(Application.created_at.desc())
        ).all()
    )


def _ensure_active_hr(user: User) -> None:
    if user.role is not UserRole.HR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="HR role required")
    if user.hr_profile is None or user.hr_profile.verified_status is not HRStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Active HR role required")


def list_hr_applications(session: Session, *, hr_user: User) -> list[Application]:
    _ensure_active_hr(hr_user)
    if hr_user.hr_profile is None or hr_user.hr_profile.company_id is None:
        return []
    return list(
        session.scalars(
            select(Application)
            .options(
                joinedload(Application.vacancy).joinedload(Vacancy.company),
                joinedload(Application.student_user).joinedload(User.student_profile),
            )
            .join(Vacancy, Application.vacancy_id == Vacancy.id)
            .where(Vacancy.company_id == hr_user.hr_profile.company_id)
            .order_by(Application.created_at.desc())
        ).all()
    )


def get_hr_application_detail(session: Session, *, hr_user: User, application_id: UUID) -> Application:
    _ensure_active_hr(hr_user)
    application = get_application_with_relations(session, application_id)
    if application.hr_user_id != hr_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    if application.vacancy is not None and hr_user.hr_profile is not None:
        if application.vacancy.company_id != hr_user.hr_profile.company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    if application.status is ApplicationStatus.SENT:
        application.status = ApplicationStatus.VIEWED
        log_event(
            session,
            user_id=hr_user.id,
            event_name="application_viewed",
            entity_type="application",
            entity_id=application.id,
        )
        session.commit()
        application = get_application_with_relations(session, application_id)
    return application


def accept_application(session: Session, *, hr_user: User, application_id: UUID) -> Application:
    application = get_hr_application_detail(session, hr_user=hr_user, application_id=application_id)
    now = datetime.now(UTC)
    application.status = ApplicationStatus.ACCEPTED
    application.accepted_at = now
    application.rejected_at = None
    log_event(
        session,
        user_id=hr_user.id,
        event_name="application_accepted",
        entity_type="application",
        entity_id=application.id,
    )
    session.commit()
    return get_application_with_relations(session, application.id)


def reject_application(session: Session, *, hr_user: User, application_id: UUID) -> Application:
    application = get_hr_application_detail(session, hr_user=hr_user, application_id=application_id)
    now = datetime.now(UTC)
    application.status = ApplicationStatus.REJECTED
    application.rejected_at = now
    application.accepted_at = None
    log_event(
        session,
        user_id=hr_user.id,
        event_name="application_rejected",
        entity_type="application",
        entity_id=application.id,
    )
    session.commit()
    return get_application_with_relations(session, application.id)


def create_application_complaint(
    session: Session,
    *,
    hr_user: User,
    application_id: UUID,
    reason: str,
) -> Complaint:
    application = get_hr_application_detail(session, hr_user=hr_user, application_id=application_id)
    complaint = Complaint(
        reporter_user_id=hr_user.id,
        target_user_id=application.student_user_id,
        vacancy_id=application.vacancy_id,
        application_id=application.id,
        reason=reason,
        status=ComplaintStatus.OPEN,
    )
    application.status = ApplicationStatus.COMPLAINT
    session.add(complaint)
    session.flush()
    log_event(
        session,
        user_id=hr_user.id,
        event_name="complaint_created",
        entity_type="complaint",
        entity_id=complaint.id,
        metadata={"application_id": str(application.id)},
    )
    session.commit()
    session.refresh(complaint)
    return complaint


def serialize_student_application_response(application: Application) -> dict:
    return serialize_application_for_student(application)


def serialize_hr_application_response(application: Application, *, hr_user: User) -> dict:
    return serialize_application_for_hr(application, hr_user)