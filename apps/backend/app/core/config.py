from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    app_debug: bool = True
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/hr_student_project"
    backend_base_url: str = "http://localhost:8000"
    web_app_url: str = "http://localhost:5173"
    telegram_bot_token: str = "TODO_SET_LOCAL_TOKEN"
    telegram_bot_username: str = "TODO_SET_LOCAL_BOT_USERNAME"
    telegram_webapp_url: str = "http://localhost:5173"
    admin_telegram_ids: list[int] = Field(default_factory=list)
    jwt_secret: str = "TODO_SET_LOCAL_SECRET"
    yoo_kassa_shop_id: str = "TODO_NOT_USED_IN_TASK_2"
    yoo_kassa_secret_key: str = "TODO_NOT_USED_IN_TASK_2"
    yoo_kassa_return_url: str = "http://localhost:5173/payments/return"
    yoo_kassa_webhook_secret: str = "TODO_NOT_USED_IN_TASK_2"
    enable_yookassa_test_mode: bool = True
    guest_free_vacancy_views: int = 3
    student_monthly_tariff_rub: int = 350
    vacancy_basic_price_rub: int = 149
    telegram_init_data_max_age_seconds: int = 86400
    access_token_ttl_seconds: int = 86400

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("admin_telegram_ids", mode="before")
    @classmethod
    def parse_admin_telegram_ids(cls, value: object) -> list[int]:
        if value in (None, "", "TODO_SET_COMMA_SEPARATED_IDS"):
            return []
        if isinstance(value, str):
            return [int(item.strip()) for item in value.split(",") if item.strip()]
        if isinstance(value, list):
            return [int(item) for item in value]
        raise TypeError("admin_telegram_ids must be a comma-separated string or list")


@lru_cache
def get_settings() -> Settings:
    return Settings()
