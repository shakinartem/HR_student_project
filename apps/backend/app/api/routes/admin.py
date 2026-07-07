from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_db_session, require_admin
from app.core.enums import ComplaintStatus, HRStatus, ModerationResult, PaymentStatus, UserRole, VacancyStatus
from app.models import Application, Complaint, HRProfile, ModerationLog, Payment, User, Vacancy
from app.schemas.admin import (
    AdminCompanyMiniResponse,
    AdminComplaintListResponse,
    AdminComplaintResponse,
    AdminComplaintUpdateRequest,
    AdminHRProfileListResponse,
    AdminHRProfileResponse,
    AdminHRProfileStatusUpdateRequest,
    AdminModerationRejectRequest,
    AdminModerationVacancyListResponse,
    AdminModerationVacancyResponse,
    AdminPaymentListResponse,
    AdminPaymentResponse,
    AdminStatsResponse,
    AdminUserListResponse,
    AdminUserMiniResponse,
    AdminUserResponse,
    AdminUserUpdateRequest,
)
from app.services.student_finance import log_event

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _serialize_user(user: User) -> AdminUserResponse:
    return AdminUserResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        role=user.role.value,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        email=user.email,
        is_blocked=user.is_blocked,
        mute_until=user.mute_until,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def _serialize_user_mini(user: User) -> AdminUserMiniResponse:
    return AdminUserMiniResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
    )


def _serialize_hr_profile(profile: HRProfile) -> AdminHRProfileResponse:
    return AdminHRProfileResponse(
        id=profile.id,
        position=profile.position,
        verified_status=profile.verified_status.value,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
        user=_serialize_user_mini(profile.user),
        company=AdminCompanyMiniResponse(
            id=profile.company.id,
            name=profile.company.name,
            status=profile.company.status,
        ),
    )


def _latest_moderation_reason(vacancy: Vacancy, session: Session) -> str | None:
    return session.scalar(
        select(ModerationLog.reason)
        .where(ModerationLog.entity_type == "vacancy", ModerationLog.entity_id == str(vacancy.id))
        .order_by(ModerationLog.created_at.desc())
        .limit(1)
    )


def _serialize_moderation_vacancy(vacancy: Vacancy, session: Session) -> AdminModerationVacancyResponse:
    return AdminModerationVacancyResponse(
        id=vacancy.id,
        title=vacancy.title,
        status=vacancy.status.value,
        moderation_status=vacancy.moderation_status,
        category=vacancy.category,
        salary_text=vacancy.salary_text,
        company_name=vacancy.company.name if vacancy.company else None,
        hr_user_id=vacancy.hr_user_id,
        published_at=vacancy.published_at,
        created_at=vacancy.created_at,
        moderation_reason=_latest_moderation_reason(vacancy, session),
    )


def _serialize_complaint(complaint: Complaint) -> AdminComplaintResponse:
    return AdminComplaintResponse(
        id=complaint.id,
        reporter_user_id=complaint.reporter_user_id,
        target_user_id=complaint.target_user_id,
        vacancy_id=complaint.vacancy_id,
        application_id=complaint.application_id,
        reason=complaint.reason,
        status=complaint.status.value,
        admin_comment=complaint.admin_comment,
        created_at=complaint.created_at,
        updated_at=complaint.updated_at,
    )


def _serialize_payment(payment: Payment) -> AdminPaymentResponse:
    return AdminPaymentResponse(
        id=payment.id,
        user_id=payment.user_id,
        amount=str(Decimal(str(payment.amount)).quantize(Decimal("0.01"))),
        currency=payment.currency,
        provider=payment.provider,
        provider_payment_id=payment.provider_payment_id,
        status=payment.status.value,
        purpose=payment.purpose,
        entity_type=payment.entity_type,
        entity_id=payment.entity_id,
        created_at=payment.created_at,
        paid_at=payment.paid_at,
        user=_serialize_user_mini(payment.user),
    )


@router.get("/users", response_model=AdminUserListResponse)
def get_admin_users(
    _admin: User = Depends(require_admin),
    session: Session = Depends(get_db_session),
) -> AdminUserListResponse:
    users = session.scalars(select(User).order_by(User.created_at.desc())).all()
    return AdminUserListResponse(items=[_serialize_user(user) for user in users])


@router.get("/users/{user_id}", response_model=AdminUserResponse)
def get_admin_user(
    user_id: UUID,
    _admin: User = Depends(require_admin),
    session: Session = Depends(get_db_session),
) -> AdminUserResponse:
    user = session.get(User, user_id)
    if user is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _serialize_user(user)


@router.patch("/users/{user_id}", response_model=AdminUserResponse)
def patch_admin_user(
    user_id: UUID,
    payload: AdminUserUpdateRequest,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_db_session),
) -> AdminUserResponse:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.role is not None:
        try:
            user.role = UserRole(payload.role)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unsupported role") from exc

    if payload.is_blocked is not None:
        user.is_blocked = payload.is_blocked
        log_event(
            session,
            user_id=admin.id,
            event_name="user_blocked" if payload.is_blocked else "user_unblocked",
            entity_type="user",
            entity_id=user.id,
        )

    user.mute_until = payload.mute_until
    if payload.mute_until is not None:
        log_event(
            session,
            user_id=admin.id,
            event_name="user_muted",
            entity_type="user",
            entity_id=user.id,
            metadata={"mute_until": payload.mute_until.isoformat()},
        )

    session.commit()
    session.refresh(user)
    return _serialize_user(user)


@router.get("/hr-profiles", response_model=AdminHRProfileListResponse)
def get_admin_hr_profiles(
    _admin: User = Depends(require_admin),
    session: Session = Depends(get_db_session),
) -> AdminHRProfileListResponse:
    profiles = session.scalars(
        select(HRProfile)
        .options(joinedload(HRProfile.user), joinedload(HRProfile.company))
        .order_by(HRProfile.created_at.desc())
    ).all()
    return AdminHRProfileListResponse(items=[_serialize_hr_profile(profile) for profile in profiles])


@router.patch("/hr-profiles/{profile_id}/status", response_model=AdminHRProfileResponse)
def patch_admin_hr_profile_status(
    profile_id: UUID,
    payload: AdminHRProfileStatusUpdateRequest,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_db_session),
) -> AdminHRProfileResponse:
    profile = session.scalar(
        select(HRProfile)
        .options(joinedload(HRProfile.user), joinedload(HRProfile.company))
        .where(HRProfile.id == profile_id)
    )
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HR profile not found")

    try:
        profile.verified_status = HRStatus(payload.verified_status)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unsupported HR status") from exc

    if profile.verified_status is HRStatus.ACTIVE:
        profile.user.role = UserRole.HR
        event_name = "hr_role_granted"
    elif profile.verified_status is HRStatus.BLOCKED:
        profile.user.role = UserRole.HR
        event_name = "hr_role_blocked"
    else:
        event_name = "hr_role_pending"

    log_event(session, user_id=admin.id, event_name=event_name, entity_type="hr_profile", entity_id=profile.id)
    session.commit()
    session.refresh(profile)
    return _serialize_hr_profile(profile)


@router.get("/moderation/vacancies", response_model=AdminModerationVacancyListResponse)
def get_admin_moderation_vacancies(
    _admin: User = Depends(require_admin),
    session: Session = Depends(get_db_session),
) -> AdminModerationVacancyListResponse:
    vacancies = session.scalars(
        select(Vacancy)
        .options(joinedload(Vacancy.company))
        .where(
            or_(
                Vacancy.status.in_([VacancyStatus.MODERATION, VacancyStatus.MANUAL_REVIEW]),
                Vacancy.moderation_status == "manual_review",
            )
        )
        .order_by(Vacancy.created_at.desc())
    ).all()
    return AdminModerationVacancyListResponse(items=[_serialize_moderation_vacancy(vacancy, session) for vacancy in vacancies])


@router.post("/moderation/vacancies/{vacancy_id}/approve", response_model=AdminModerationVacancyResponse)
def post_admin_approve_vacancy(
    vacancy_id: UUID,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_db_session),
) -> AdminModerationVacancyResponse:
    vacancy = session.scalar(select(Vacancy).options(joinedload(Vacancy.company)).where(Vacancy.id == vacancy_id))
    if vacancy is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")

    vacancy.status = VacancyStatus.ACTIVE
    vacancy.moderation_status = ModerationResult.APPROVED.value
    if vacancy.published_at is None:
        vacancy.published_at = datetime.now(UTC)
    session.add(
        ModerationLog(
            entity_type="vacancy",
            entity_id=str(vacancy.id),
            result=ModerationResult.APPROVED,
            reason=None,
            raw_response="admin_approval",
        )
    )
    log_event(session, user_id=admin.id, event_name="vacancy_approved", entity_type="vacancy", entity_id=vacancy.id)
    session.commit()
    session.refresh(vacancy)
    return _serialize_moderation_vacancy(vacancy, session)


@router.post("/moderation/vacancies/{vacancy_id}/reject", response_model=AdminModerationVacancyResponse)
def post_admin_reject_vacancy(
    vacancy_id: UUID,
    payload: AdminModerationRejectRequest,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_db_session),
) -> AdminModerationVacancyResponse:
    vacancy = session.scalar(select(Vacancy).options(joinedload(Vacancy.company)).where(Vacancy.id == vacancy_id))
    if vacancy is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found")

    vacancy.status = VacancyStatus.REJECTED
    vacancy.moderation_status = ModerationResult.REJECTED.value
    session.add(
        ModerationLog(
            entity_type="vacancy",
            entity_id=str(vacancy.id),
            result=ModerationResult.REJECTED,
            reason=payload.reason,
            raw_response="admin_rejection",
        )
    )
    log_event(
        session,
        user_id=admin.id,
        event_name="vacancy_rejected",
        entity_type="vacancy",
        entity_id=vacancy.id,
        metadata={"reason": payload.reason},
    )
    session.commit()
    session.refresh(vacancy)
    return _serialize_moderation_vacancy(vacancy, session)


@router.get("/complaints", response_model=AdminComplaintListResponse)
def get_admin_complaints(
    _admin: User = Depends(require_admin),
    session: Session = Depends(get_db_session),
) -> AdminComplaintListResponse:
    complaints = session.scalars(select(Complaint).order_by(Complaint.created_at.desc())).all()
    return AdminComplaintListResponse(items=[_serialize_complaint(item) for item in complaints])


@router.patch("/complaints/{complaint_id}/status", response_model=AdminComplaintResponse)
def patch_admin_complaint_status(
    complaint_id: UUID,
    payload: AdminComplaintUpdateRequest,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_db_session),
) -> AdminComplaintResponse:
    complaint = session.get(Complaint, complaint_id)
    if complaint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    try:
        complaint.status = ComplaintStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unsupported complaint status") from exc

    complaint.admin_comment = payload.admin_comment
    log_event(
        session,
        user_id=admin.id,
        event_name="complaint_resolved" if complaint.status is ComplaintStatus.RESOLVED else "complaint_updated",
        entity_type="complaint",
        entity_id=complaint.id,
        metadata={"status": complaint.status.value},
    )
    session.commit()
    session.refresh(complaint)
    return _serialize_complaint(complaint)


@router.get("/payments", response_model=AdminPaymentListResponse)
def get_admin_payments(
    _admin: User = Depends(require_admin),
    session: Session = Depends(get_db_session),
) -> AdminPaymentListResponse:
    payments = session.scalars(
        select(Payment).options(joinedload(Payment.user)).order_by(Payment.created_at.desc())
    ).all()
    return AdminPaymentListResponse(items=[_serialize_payment(payment) for payment in payments])


@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    _admin: User = Depends(require_admin),
    session: Session = Depends(get_db_session),
) -> AdminStatsResponse:
    total_users = session.scalar(select(func.count()).select_from(User)) or 0
    students = session.scalar(select(func.count()).select_from(User).where(User.role == UserRole.STUDENT)) or 0
    hr_users = session.scalar(select(func.count()).select_from(User).where(User.role == UserRole.HR)) or 0
    active_vacancies = session.scalar(select(func.count()).select_from(Vacancy).where(Vacancy.status == VacancyStatus.ACTIVE)) or 0
    applications = session.scalar(select(func.count()).select_from(Application)) or 0
    succeeded_payments = session.scalar(
        select(func.count()).select_from(Payment).where(Payment.status == PaymentStatus.SUCCEEDED)
    ) or 0
    open_complaints = session.scalar(
        select(func.count()).select_from(Complaint).where(Complaint.status == ComplaintStatus.OPEN)
    ) or 0
    manual_review_vacancies = session.scalar(
        select(func.count())
        .select_from(Vacancy)
        .where(or_(Vacancy.status == VacancyStatus.MANUAL_REVIEW, Vacancy.moderation_status == "manual_review"))
    ) or 0

    return AdminStatsResponse(
        total_users=total_users,
        students=students,
        hr_users=hr_users,
        active_vacancies=active_vacancies,
        applications=applications,
        succeeded_payments=succeeded_payments,
        open_complaints=open_complaints,
        manual_review_vacancies=manual_review_vacancies,
    )
