from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = Field(alias="BOT_TOKEN")
    telegram_webapp_url: str = Field(alias="TELEGRAM_WEBAPP_URL")
    backend_base_url: str | None = Field(default=None, alias="BACKEND_BASE_URL")
    backend_timeout_seconds: float = Field(default=5.0, alias="BACKEND_TIMEOUT_SECONDS")


@lru_cache(maxsize=1)
def get_settings() -> BotSettings:
    return BotSettings()
