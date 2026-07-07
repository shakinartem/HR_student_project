from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session, require_hr
from app.models import User
from app.schemas.application import (
    ApplicationComplaintRequest,
    ApplicationComplaintResponse,
    HRApplicationListResponse,
    HRApplicationResponse,
)
from app.services.applications import (
    accept_application,
    create_application_complaint,
    get_hr_application_detail,
    list_hr_applications,
    reject_application,
    serialize_hr_application_response,
)

router = APIRouter(prefix="/api/hr", tags=["hr"])


@router.get("/applications", response_model=HRApplicationListResponse)
def get_hr_applications(
    current_user: Annotated[User, Depends(require_hr)],
    session: Annotated[Session, Depends(get_db_session)],
) -> HRApplicationListResponse:
    items = [
        serialize_hr_application_response(application, hr_user=current_user)
        for application in list_hr_applications(session, hr_user=current_user)
    ]
    return HRApplicationListResponse(items=items)


@router.get("/applications/{application_id}", response_model=HRApplicationResponse)
def get_hr_application(
    application_id: UUID,
    current_user: Annotated[User, Depends(require_hr)],
    session: Annotated[Session, Depends(get_db_session)],
) -> HRApplicationResponse:
    application = get_hr_application_detail(session, hr_user=current_user, application_id=application_id)
    return HRApplicationResponse(**serialize_hr_application_response(application, hr_user=current_user))


@router.post("/applications/{application_id}/accept", response_model=HRApplicationResponse)
def post_accept_application(
    application_id: UUID,
    current_user: Annotated[User, Depends(require_hr)],
    session: Annotated[Session, Depends(get_db_session)],
) -> HRApplicationResponse:
    application = accept_application(session, hr_user=current_user, application_id=application_id)
    return HRApplicationResponse(**serialize_hr_application_response(application, hr_user=current_user))


@router.post("/applications/{application_id}/reject", response_model=HRApplicationResponse)
def post_reject_application(
    application_id: UUID,
    current_user: Annotated[User, Depends(require_hr)],
    session: Annotated[Session, Depends(get_db_session)],
) -> HRApplicationResponse:
    application = reject_application(session, hr_user=current_user, application_id=application_id)
    return HRApplicationResponse(**serialize_hr_application_response(application, hr_user=current_user))


@router.post(
    "/applications/{application_id}/complain",
    response_model=ApplicationComplaintResponse,
    status_code=status.HTTP_201_CREATED,
)
def post_application_complaint(
    application_id: UUID,
    payload: ApplicationComplaintRequest,
    current_user: Annotated[User, Depends(require_hr)],
    session: Annotated[Session, Depends(get_db_session)],
) -> ApplicationComplaintResponse:
    complaint = create_application_complaint(
        session,
        hr_user=current_user,
        application_id=application_id,
        reason=payload.reason,
    )
    return ApplicationComplaintResponse(
        id=complaint.id,
        application_id=complaint.application_id,
        status=complaint.status.value,
        reason=complaint.reason,
    )
