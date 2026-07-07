from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_settings, get_current_user, get_db_session, require_student
from app.core.config import Settings
from app.models import User
from app.schemas.payment import (
    MockPaymentConfirmRequest,
    PaymentCreateRequest,
    PaymentCreateResponse,
    PaymentHistoryResponse,
)
from app.services.student_finance import confirm_mock_payment, create_pending_topup_payment, list_user_payments

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.post("/create", response_model=PaymentCreateResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payload: PaymentCreateRequest,
    current_user: Annotated[User, Depends(require_student)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_current_settings)],
) -> PaymentCreateResponse:
    payment = create_pending_topup_payment(
        session,
        user=current_user,
        amount=payload.amount,
        settings=settings,
    )
    return PaymentCreateResponse(
        payment_id=payment.id,
        status=payment.status.value,
        confirmation_url=f"mock://payment/{payment.id}",
    )


@router.post("/mock-confirm", status_code=status.HTTP_200_OK)
def mock_confirm_payment(
    payload: MockPaymentConfirmRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_current_settings)],
) -> dict[str, str]:
    payment = confirm_mock_payment(
        session,
        payment_id=payload.payment_id,
        user=current_user,
        settings=settings,
    )
    return {"payment_id": str(payment.id), "status": payment.status.value}


@router.get("/history", response_model=PaymentHistoryResponse)
def get_payment_history(
    current_user: Annotated[User, Depends(require_student)],
    session: Annotated[Session, Depends(get_db_session)],
) -> PaymentHistoryResponse:
    return PaymentHistoryResponse(items=list_user_payments(session, user_id=current_user.id))
