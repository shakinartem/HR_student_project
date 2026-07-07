from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session, require_student
from app.models import User
from app.schemas.student import (
    RefundRequestCreate,
    RefundRequestResponse,
    StudentBalanceResponse,
    StudentProfileResponse,
    StudentProfileUpdateRequest,
    StudentSubscriptionResponse,
)
from app.schemas.application import StudentApplicationListResponse
from app.services.applications import list_student_applications, serialize_student_application_response
from app.services.student_finance import (
    create_refund_support_ticket,
    ensure_student_profile,
    get_active_subscription,
    get_balance,
    get_balance_transactions,
    is_profile_completed,
)

router = APIRouter(prefix="/api/student", tags=["student"])


@router.get("/profile", response_model=StudentProfileResponse)
def get_student_profile(
    current_user: Annotated[User, Depends(require_student)],
    session: Annotated[Session, Depends(get_db_session)],
) -> StudentProfileResponse:
    profile = ensure_student_profile(session, user=current_user)
    return StudentProfileResponse.model_validate(profile)


@router.patch("/profile", response_model=StudentProfileResponse)
def patch_student_profile(
    payload: StudentProfileUpdateRequest,
    current_user: Annotated[User, Depends(require_student)],
    session: Annotated[Session, Depends(get_db_session)],
) -> StudentProfileResponse:
    profile = ensure_student_profile(session, user=current_user)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(profile, field, value)
    profile.profile_completed = is_profile_completed(profile)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return StudentProfileResponse.model_validate(profile)


@router.get("/balance", response_model=StudentBalanceResponse)
def get_student_balance(
    current_user: Annotated[User, Depends(require_student)],
    session: Annotated[Session, Depends(get_db_session)],
) -> StudentBalanceResponse:
    transactions = get_balance_transactions(session, user_id=current_user.id)
    return StudentBalanceResponse(
        balance=get_balance(session, user_id=current_user.id),
        currency="RUB",
        transactions=transactions,
    )


@router.get("/subscription", response_model=StudentSubscriptionResponse)
def get_student_subscription(
    current_user: Annotated[User, Depends(require_student)],
    session: Annotated[Session, Depends(get_db_session)],
) -> StudentSubscriptionResponse:
    subscription = get_active_subscription(session, user_id=current_user.id)
    if subscription is None:
        return StudentSubscriptionResponse(status="inactive", starts_at=None, expires_at=None)
    return StudentSubscriptionResponse(
        status=subscription.status.value,
        starts_at=subscription.starts_at,
        expires_at=subscription.expires_at,
    )


@router.get("/applications", response_model=StudentApplicationListResponse)
def get_student_applications(
    current_user: Annotated[User, Depends(require_student)],
    session: Annotated[Session, Depends(get_db_session)],
) -> StudentApplicationListResponse:
    items = [
        serialize_student_application_response(application)
        for application in list_student_applications(session, student_user_id=current_user.id)
    ]
    return StudentApplicationListResponse(items=items)


@router.post("/refund-request", response_model=RefundRequestResponse, status_code=status.HTTP_201_CREATED)
def create_refund_request(
    payload: RefundRequestCreate,
    current_user: Annotated[User, Depends(require_student)],
    session: Annotated[Session, Depends(get_db_session)],
) -> RefundRequestResponse:
    ticket = create_refund_support_ticket(session, user=current_user, message=payload.message)
    return RefundRequestResponse(
        id=ticket.id,
        status=ticket.status.value,
        type=ticket.type,
        subject=ticket.subject,
        message=ticket.message,
    )
