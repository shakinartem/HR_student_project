from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class HRVacancyCreateRequest(BaseModel):
    title: str
    category: str
    job_type: str
    schedule: str
    salary_text: str
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    district: str | None = None
    address: str | None = None
    format: str | None = None
    description: str | None = None
    responsibilities: str | None = None
    requirements: str | None = None
    conditions: str | None = None
    experience_required: bool = False
    photo_url: str | None = None


class HRVacancyUpdateRequest(BaseModel):
    title: str | None = None
    category: str | None = None
    job_type: str | None = None
    schedule: str | None = None
    salary_text: str | None = None
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    district: str | None = None
    address: str | None = None
    format: str | None = None
    description: str | None = None
    responsibilities: str | None = None
    requirements: str | None = None
    conditions: str | None = None
    experience_required: bool | None = None
    photo_url: str | None = None


class HRVacancyHiddenContacts(BaseModel):
    contact_name: str | None
    contact_phone: str | None
    contact_email: str | None
    contact_telegram: str | None


class HRVacancyResponse(BaseModel):
    id: UUID
    title: str
    category: str
    job_type: str
    schedule: str
    salary_text: str
    salary_min: int | None
    salary_max: int | None
    district: str | None
    address: str | None
    format: str | None
    description: str | None
    responsibilities: str | None
    requirements: str | None
    conditions: str | None
    experience_required: bool
    photo_url: str | None
    status: str
    moderation_status: str
    payment_required: bool
    is_promoted: bool
    published_at: datetime | None
    expires_at: datetime | None
    hidden_contacts: HRVacancyHiddenContacts


class HRVacancyListResponse(BaseModel):
    items: list[HRVacancyResponse]
