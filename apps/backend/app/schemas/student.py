from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StudentProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    university: str | None
    course: int | None
    speciality: str | None
    preferred_job_types: list[str] | None
    preferred_schedule: list[str] | None
    preferred_districts: list[str] | None
    experience_text: str | None
    profile_completed: bool


class StudentProfileUpdateRequest(BaseModel):
    university: str | None = None
    course: int | None = Field(default=None, ge=1)
    speciality: str | None = None
    preferred_job_types: list[str] | None = None
    preferred_schedule: list[str] | None = None
    preferred_districts: list[str] | None = None
    experience_text: str | None = None


class BalanceTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    amount: Decimal
    type: str
    reason: str
    payment_id: UUID | None
    created_at: datetime


class StudentBalanceResponse(BaseModel):
    balance: Decimal
    currency: str
    transactions: list[BalanceTransactionResponse]


class StudentSubscriptionResponse(BaseModel):
    status: str
    starts_at: datetime | None
    expires_at: datetime | None


class RefundRequestCreate(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class RefundRequestResponse(BaseModel):
    id: UUID
    status: str
    type: str
    subject: str
    message: str
