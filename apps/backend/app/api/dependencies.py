from __future__ import annotations

from collections.abc import Generator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.enums import UserRole
from app.core.security import decode_access_token
from app.db.session import get_session_factory
from app.models import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_db_session() -> Generator[Session]:
    SessionLocal = get_session_factory()
    with SessionLocal() as session:
        yield session


def get_current_settings() -> Settings:
    return get_settings()


def _resolve_current_user(
    credentials: HTTPAuthorizationCredentials | None,
    session: Session,
    settings: Settings,
    *,
    required: bool,
) -> User | None:
    if credentials is None or credentials.scheme.lower() != "bearer":
        if required:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
        return None

    try:
        payload = decode_access_token(credentials.credentials, settings.jwt_secret)
        user_id = UUID(payload["sub"])
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token") from exc

    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")
    if user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is blocked")
    return user


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_current_settings)],
) -> User:
    user = _resolve_current_user(credentials, session, settings, required=True)
    assert user is not None
    return user


def get_optional_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_current_settings)],
) -> User | None:
    return _resolve_current_user(credentials, session, settings, required=False)


def require_student(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role is not UserRole.STUDENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student role required")
    return current_user


def require_hr(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role is not UserRole.HR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="HR role required")
    return current_user


def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role is not UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return current_user
