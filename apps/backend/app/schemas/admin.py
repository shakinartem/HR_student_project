from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    telegram_id: int | None
    role: str
    username: str | None
    first_name: str
    last_name: str | None
    phone: str | None
    email: str | None
    is_blocked: bool
    mute_until: datetime | None
    created_at: datetime
    updated_at: datetime


class AdminUserListResponse(BaseModel):
    items: list[AdminUserResponse]


class AdminUserUpdateRequest(BaseModel):
    role: str | None = None
    is_blocked: bool | None = None
    mute_until: datetime | None = None


class AdminUserMiniResponse(BaseModel):
    id: UUID
    telegram_id: int | None
    username: str | None
    first_name: str
    last_name: str | None
    role: str


class AdminCompanyMiniResponse(BaseModel):
    id: UUID
    name: str
    status: str


class AdminHRProfileResponse(BaseModel):
    id: UUID
    position: str | None
    verified_status: str
    created_at: datetime
    updated_at: datetime
    user: AdminUserMiniResponse
    company: AdminCompanyMiniResponse


class AdminHRProfileListResponse(BaseModel):
    items: list[AdminHRProfileResponse]


class AdminHRProfileStatusUpdateRequest(BaseModel):
    verified_status: str


class AdminModerationVacancyResponse(BaseModel):
    id: UUID
    title: str
    status: str
    moderation_status: str
    category: str
    salary_text: str
    company_name: str | None
    hr_user_id: UUID
    published_at: datetime | None
    created_at: datetime
    moderation_reason: str | None = None


class AdminModerationVacancyListResponse(BaseModel):
    items: list[AdminModerationVacancyResponse]


class AdminModerationRejectRequest(BaseModel):
    reason: str | None = None


class AdminComplaintResponse(BaseModel):
    id: UUID
    reporter_user_id: UUID
    target_user_id: UUID
    vacancy_id: UUID | None
    application_id: UUID | None
    reason: str
    status: str
    admin_comment: str | None
    created_at: datetime
    updated_at: datetime


class AdminComplaintListResponse(BaseModel):
    items: list[AdminComplaintResponse]


class AdminComplaintUpdateRequest(BaseModel):
    status: str
    admin_comment: str | None = None


class AdminPaymentResponse(BaseModel):
    id: UUID
    user_id: UUID
    amount: str
    currency: str
    provider: str
    provider_payment_id: str | None
    status: str
    purpose: str
    entity_type: str | None
    entity_id: str | None
    created_at: datetime
    paid_at: datetime | None
    user: AdminUserMiniResponse


class AdminPaymentListResponse(BaseModel):
    items: list[AdminPaymentResponse]


class AdminStatsResponse(BaseModel):
    total_users: int
    students: int
    hr_users: int
    active_vacancies: int
    applications: int
    succeeded_payments: int
    open_complaints: int
    manual_review_vacancies: int
