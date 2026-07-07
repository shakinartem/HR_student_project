from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserResponse


class TelegramAuthRequest(BaseModel):
    init_data: str


class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str
    user: UserResponse
