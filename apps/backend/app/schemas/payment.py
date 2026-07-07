from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PaymentCreateRequest(BaseModel):
    amount: Decimal = Field(gt=0, decimal_places=2, max_digits=10)
    purpose: Literal["student_balance_topup"]


class PaymentCreateResponse(BaseModel):
    payment_id: UUID
    status: str
    confirmation_url: str


class MockPaymentConfirmRequest(BaseModel):
    payment_id: UUID


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    amount: Decimal
    currency: str
    provider: str
    provider_payment_id: str | None
    status: str
    purpose: str
    entity_type: str | None
    entity_id: str | None
    created_at: datetime
    paid_at: datetime | None


class PaymentHistoryResponse(BaseModel):
    items: list[PaymentResponse]
