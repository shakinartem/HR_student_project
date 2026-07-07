from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import hmac
import json
from urllib.parse import parse_qsl


class TelegramInitDataError(ValueError):
    """Raised when Telegram initData is invalid."""


@dataclass(slots=True)
class TelegramUserPayload:
    id: int
    first_name: str
    last_name: str | None
    username: str | None


def _parse_init_data(raw_init_data: str) -> dict[str, str]:
    parsed = dict(parse_qsl(raw_init_data, keep_blank_values=True))
    if "hash" not in parsed or "auth_date" not in parsed or "user" not in parsed:
        raise TelegramInitDataError("Invalid Telegram initData")
    return parsed


def _build_data_check_string(parsed: dict[str, str]) -> str:
    return "\n".join(f"{key}={value}" for key, value in sorted(parsed.items()) if key != "hash")


def verify_init_data(raw_init_data: str, *, bot_token: str, max_age_seconds: int) -> dict[str, str]:
    parsed = _parse_init_data(raw_init_data)
    received_hash = parsed["hash"]
    data_check_string = _build_data_check_string(parsed)
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(received_hash, expected_hash):
        raise TelegramInitDataError("Invalid Telegram initData")

    auth_date = int(parsed["auth_date"])
    now_ts = int(datetime.now(UTC).timestamp())
    if now_ts - auth_date > max_age_seconds:
        raise TelegramInitDataError("Expired Telegram initData")
    return parsed


def parse_and_verify_init_data(raw_init_data: str, *, bot_token: str, max_age_seconds: int) -> TelegramUserPayload:
    parsed = verify_init_data(raw_init_data, bot_token=bot_token, max_age_seconds=max_age_seconds)
    user_payload = json.loads(parsed["user"])
    return TelegramUserPayload(
        id=int(user_payload["id"]),
        first_name=user_payload.get("first_name") or "",
        last_name=user_payload.get("last_name"),
        username=user_payload.get("username"),
    )
