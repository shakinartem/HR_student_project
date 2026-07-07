from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class VacancyListItemResponse(BaseModel):
    id: UUID
    title: str
    company_name: str | None
    category: str
    job_type: str
    salary_text: str
    salary_min: int | None
    salary_max: int | None
    district: str | None
    schedule: str
    format: str | None
    is_promoted: bool
    published_at: datetime | None


class VacancyListResponse(BaseModel):
    items: list[VacancyListItemResponse]


class VacancyDetailResponse(VacancyListItemResponse):
    address: str | None
    description: str | None
    requirements: str | None
    conditions: str | None
    experience_required: bool


class VacancyViewResponse(BaseModel):
    vacancy_id: UUID
    view_count: int
    viewer_type: str
