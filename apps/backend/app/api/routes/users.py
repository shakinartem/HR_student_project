from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db_session
from app.models import User
from app.schemas.user import UserResponse, UserUpdateRequest

router = APIRouter(tags=["users"])


@router.get("/api/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.patch("/api/me", response_model=UserResponse)
def patch_me(
    payload: UserUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db_session)],
) -> UserResponse:
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(current_user, field, value)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return UserResponse.model_validate(current_user)
