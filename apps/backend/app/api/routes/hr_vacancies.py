from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_settings, get_db_session, require_hr
from app.core.config import Settings
from app.models import User
from app.schemas.hr_vacancy import HRVacancyCreateRequest, HRVacancyListResponse, HRVacancyResponse, HRVacancyUpdateRequest
from app.schemas.payment import PaymentCreateResponse
from app.services.hr_vacancies import (
    create_hr_vacancy,
    create_publish_payment,
    get_hr_vacancy,
    list_hr_vacancies,
    serialize_hr_vacancy,
    update_hr_vacancy,
)

router = APIRouter(prefix="/api/hr/vacancies", tags=["hr-vacancies"])


@router.get("", response_model=HRVacancyListResponse)
def get_vacancies(
    current_user: Annotated[User, Depends(require_hr)],
    session: Annotated[Session, Depends(get_db_session)],
) -> HRVacancyListResponse:
    items = [serialize_hr_vacancy(vacancy) for vacancy in list_hr_vacancies(session, hr_user=current_user)]
    return HRVacancyListResponse(items=items)


@router.post("", response_model=HRVacancyResponse, status_code=status.HTTP_201_CREATED)
def post_vacancy(
    payload: HRVacancyCreateRequest,
    current_user: Annotated[User, Depends(require_hr)],
    session: Annotated[Session, Depends(get_db_session)],
) -> HRVacancyResponse:
    vacancy = create_hr_vacancy(session, hr_user=current_user, payload=payload.model_dump())
    return HRVacancyResponse(**serialize_hr_vacancy(vacancy))


@router.get("/{vacancy_id}", response_model=HRVacancyResponse)
def get_vacancy(
    vacancy_id: UUID,
    current_user: Annotated[User, Depends(require_hr)],
    session: Annotated[Session, Depends(get_db_session)],
) -> HRVacancyResponse:
    vacancy = get_hr_vacancy(session, hr_user=current_user, vacancy_id=vacancy_id)
    return HRVacancyResponse(**serialize_hr_vacancy(vacancy))


@router.patch("/{vacancy_id}", response_model=HRVacancyResponse)
def patch_vacancy(
    vacancy_id: UUID,
    payload: HRVacancyUpdateRequest,
    current_user: Annotated[User, Depends(require_hr)],
    session: Annotated[Session, Depends(get_db_session)],
) -> HRVacancyResponse:
    vacancy = update_hr_vacancy(
        session,
        hr_user=current_user,
        vacancy_id=vacancy_id,
        payload=payload.model_dump(exclude_unset=True),
    )
    return HRVacancyResponse(**serialize_hr_vacancy(vacancy))


@router.post("/{vacancy_id}/publish-payment", response_model=PaymentCreateResponse, status_code=status.HTTP_201_CREATED)
def post_publish_payment(
    vacancy_id: UUID,
    current_user: Annotated[User, Depends(require_hr)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_current_settings)],
) -> PaymentCreateResponse:
    payment = create_publish_payment(session, hr_user=current_user, vacancy_id=vacancy_id, settings=settings)
    return PaymentCreateResponse(
        payment_id=payment.id,
        status=payment.status.value,
        confirmation_url=f"mock://payment/{payment.id}",
    )
