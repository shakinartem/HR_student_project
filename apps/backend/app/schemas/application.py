from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ApplicationCreateRequest(BaseModel):
    student_comment: str | None = Field(default=None, max_length=4000)


class StudentApplicationResponse(BaseModel):
    id: UUID
    vacancy_id: UUID
    vacancy_title: str | None
    company_name: str | None
    status: str
    created_at: datetime | None


class StudentApplicationListResponse(BaseModel):
    items: list[StudentApplicationResponse]


class HRApplicationStudentSummary(BaseModel):
    first_name: str | None
    university: str | None
    course: int | None
    speciality: str | None
    preferred_schedule: list[str] | None
    experience_text: str | None
    student_comment: str | None


class HRApplicationContacts(BaseModel):
    phone: str | None
    email: str | None
    telegram_username: str | None


class HRApplicationResponse(BaseModel):
    id: UUID
    vacancy_id: UUID
    vacancy_title: str | None
    status: str
    student: HRApplicationStudentSummary
    contacts: HRApplicationContacts | None
    created_at: datetime | None


class HRApplicationListResponse(BaseModel):
    items: list[HRApplicationResponse]


class ApplicationComplaintRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=4000)


class ApplicationComplaintResponse(BaseModel):
    id: UUID
    application_id: UUID
    status: str
    reason: str
