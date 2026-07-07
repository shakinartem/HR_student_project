from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class AppRole(StrEnum):
    GUEST = "guest"
    STUDENT = "student"
    HR = "hr"
    ADMIN = "admin"


class BackendUser(BaseModel):
    telegram_id: int | None = None
    role: str
    first_name: str | None = None
    username: str | None = None


class BackendApplicationContactPayload(BaseModel):
    phone: str | None = None
    email: str | None = None
    telegram_username: str | None = None


class BackendApplicationPayload(BaseModel):
    id: str
    status: str
    vacancy_title: str | None = None
    student: dict[str, Any] | None = None
    contacts: BackendApplicationContactPayload | None = None
