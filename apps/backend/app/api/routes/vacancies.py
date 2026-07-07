from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session, get_optional_current_user
from app.api.dependencies import require_student
from app.schemas.application import ApplicationCreateRequest, StudentApplicationResponse
from app.models import User
from app.schemas.vacancy import VacancyDetailResponse, VacancyListResponse, VacancyViewResponse
from app.services.vacancies import (
    ensure_view_allowed_and_record,
    get_active_vacancy_or_404,
    list_active_vacancies,
    serialize_vacancy_detail_for_student,
    serialize_vacancy_list_item,
)
from app.services.applications import (
    create_application_for_student,
    get_applyable_vacancy_or_404,
    serialize_student_application_response,
)

router = APIRouter(prefix="/api/vacancies", tags=["vacancies"])


@router.get("", response_model=VacancyListResponse)
def get_vacancies(
    session: Annotated[Session, Depends(get_db_session)],
    category: str | None = None,
    job_type: str | None = None,
    district: str | None = None,
    salary_min: int | None = Query(default=None, ge=0),
    format: str | None = None,
    schedule: str | None = None,
    experience_required: bool | None = None,
    promoted_first: bool = True,
) -> VacancyListResponse:
    vacancies = list_active_vacancies(
        session,
        category=category,
        job_type=job_type,
        district=district,
        salary_min=salary_min,
        vacancy_format=format,
        schedule=schedule,
        experience_required=experience_required,
        promoted_first=promoted_first,
    )
    return VacancyListResponse(items=[serialize_vacancy_list_item(vacancy) for vacancy in vacancies])


@router.get("/{vacancy_id}", response_model=VacancyDetailResponse)
def get_vacancy_detail(
    vacancy_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
    guest_id: Annotated[str | None, Header(alias="X-Guest-Id")] = None,
) -> VacancyDetailResponse:
    vacancy = get_active_vacancy_or_404(session, vacancy_id)
    ensure_view_allowed_and_record(session, vacancy=vacancy, user=current_user, guest_id=guest_id)
    return VacancyDetailResponse(**serialize_vacancy_detail_for_student(vacancy))


@router.post("/{vacancy_id}/view", response_model=VacancyViewResponse)
def create_vacancy_view(
    vacancy_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
    guest_id: Annotated[str | None, Header(alias="X-Guest-Id")] = None,
) -> VacancyViewResponse:
    vacancy = get_active_vacancy_or_404(session, vacancy_id)
    view_count, viewer_type = ensure_view_allowed_and_record(
        session,
        vacancy=vacancy,
        user=current_user,
        guest_id=guest_id,
    )
    return VacancyViewResponse(vacancy_id=vacancy.id, view_count=view_count, viewer_type=viewer_type)


@router.post("/{vacancy_id}/apply", response_model=StudentApplicationResponse, status_code=201)
def create_vacancy_application(
    vacancy_id: UUID,
    payload: ApplicationCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_student)],
) -> StudentApplicationResponse:
    vacancy = get_applyable_vacancy_or_404(session, vacancy_id)
    application = create_application_for_student(
        session,
        vacancy=vacancy,
        student_user=current_user,
        student_comment=payload.student_comment,
    )
    return StudentApplicationResponse(**serialize_student_application_response(application))
