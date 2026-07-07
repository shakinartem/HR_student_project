from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.core.telegram import TelegramInitDataError, parse_and_verify_init_data, verify_init_data

from .conftest import build_init_data


def test_verify_init_data_accepts_valid_payload() -> None:
    init_data = build_init_data(bot_token="test_bot_token_123", telegram_id=101010, username="valid_user")

    payload = verify_init_data(
        init_data,
        bot_token="test_bot_token_123",
        max_age_seconds=86400,
    )

    assert "hash" in payload
    telegram_user = parse_and_verify_init_data(
        init_data,
        bot_token="test_bot_token_123",
        max_age_seconds=86400,
    )
    assert telegram_user.id == 101010
    assert telegram_user.username == "valid_user"


def test_verify_init_data_rejects_invalid_signature() -> None:
    with pytest.raises(TelegramInitDataError, match="Invalid Telegram initData"):
        verify_init_data(
            "auth_date=1&user=%7B%7D&hash=bad",
            bot_token="test_bot_token_123",
            max_age_seconds=86400,
        )


def test_verify_init_data_rejects_expired_payload() -> None:
    old_timestamp = int((datetime.now(UTC) - timedelta(days=2)).timestamp())
    init_data = build_init_data(
        bot_token="test_bot_token_123",
        telegram_id=202020,
        auth_date=old_timestamp,
    )

    with pytest.raises(TelegramInitDataError, match="Expired Telegram initData"):
        verify_init_data(
            init_data,
            bot_token="test_bot_token_123",
            max_age_seconds=86400,
        )
