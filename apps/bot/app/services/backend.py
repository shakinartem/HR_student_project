from __future__ import annotations

from collections.abc import Mapping

import httpx

from app.models import BackendApplicationPayload, BackendUser


class BotBackendClient:
    """Thin boundary for future bot-safe backend integration.

    Current backend routes rely on user JWT auth and do not expose a service-safe
    lookup for Telegram IDs. Until Task 9/10 adds that contract, these methods
    return safe placeholders instead of guessing around auth.
    """

    def __init__(self, base_url: str | None, timeout_seconds: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/") if base_url else None
        self.timeout_seconds = timeout_seconds

    async def get_me_by_telegram_id(self, telegram_id: int) -> BackendUser | None:
        _ = telegram_id
        return None

    async def get_student_applications(self, telegram_id: int) -> list[BackendApplicationPayload]:
        _ = telegram_id
        return []

    async def get_hr_applications(self, telegram_id: int) -> list[BackendApplicationPayload]:
        _ = telegram_id
        return []

    async def accept_application(self, telegram_id: int, application_id: str) -> BackendApplicationPayload | None:
        _ = (telegram_id, application_id)
        return None

    async def reject_application(self, telegram_id: int, application_id: str) -> BackendApplicationPayload | None:
        _ = (telegram_id, application_id)
        return None

    async def get(self, path: str, params: Mapping[str, str] | None = None) -> httpx.Response:
        if self.base_url is None:
            raise RuntimeError("Backend base URL is not configured.")
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_seconds) as client:
            return await client.get(path, params=params)
