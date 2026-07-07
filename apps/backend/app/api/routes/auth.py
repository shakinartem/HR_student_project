from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_settings, get_db_session
from app.core.config import Settings
from app.core.enums import UserRole
from app.core.security import create_access_token
from app.core.telegram import TelegramInitDataError, parse_and_verify_init_data
from app.models import User
from app.schemas.auth import TelegramAuthRequest, TokenResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/telegram", response_model=TokenResponse)
def authenticate_telegram(
    payload: TelegramAuthRequest,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_current_settings)],
) -> TokenResponse:
    try:
        telegram_user = parse_and_verify_init_data(
            payload.init_data,
            bot_token=settings.telegram_bot_token,
            max_age_seconds=settings.telegram_init_data_max_age_seconds,
        )
    except TelegramInitDataError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user = session.scalar(select(User).where(User.telegram_id == telegram_user.id))
    if user is None:
        role = UserRole.ADMIN if telegram_user.id in settings.admin_telegram_ids else UserRole.STUDENT
        user = User(
            telegram_id=telegram_user.id,
            role=role,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
        )
        session.add(user)
    else:
        user.username = telegram_user.username
        user.first_name = telegram_user.first_name
        user.last_name = telegram_user.last_name
        if user.telegram_id in settings.admin_telegram_ids:
            user.role = UserRole.ADMIN

    session.commit()
    session.refresh(user)

    access_token = create_access_token(
        subject=str(user.id),
        secret_key=settings.jwt_secret,
        ttl_seconds=settings.access_token_ttl_seconds,
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )
