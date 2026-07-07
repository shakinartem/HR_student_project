from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
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


class UserUpdateRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    email: str | None = None
