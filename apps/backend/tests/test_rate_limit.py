from __future__ import annotations

import time
from collections.abc import Generator
from datetime import UTC, datetime
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.db.base import metadata
from app.models import User


def _make_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    metadata.create_all(engine)
    session = TestingSessionLocal()
    return session


@pytest.fixture()
def rate_limited_settings() -> Settings:
    settings = Settings(
        app_env="test",
        app_debug=False,
        database_url="sqlite:///unused.db",
        telegram_bot_token="test_bot_token_123",
        jwt_secret="super-secret-test-key",
        admin_telegram_ids=[999001],
        rate_limit_auth_per_minute=3,
        rate_limit_apply_per_minute=2,
        rate_limit_payment_per_minute=2,
        rate_limit_webhook_per_minute=2,
        rate_limit_admin_per_minute=2,
        rate_limit_general_per_minute=100,
    )
    return settings


@pytest.fixture()
def rl_client(rate_limited_settings: Settings, db_session: Session, monkeypatch) -> Generator[TestClient, None, None]:
    import app.core.config as config_module
    from app.core.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setattr(config_module, "get_settings", lambda: rate_limited_settings)
    import app.main as main_module

    monkeypatch.setattr(main_module, "get_settings", lambda: rate_limited_settings)

    def override_settings() -> Settings:
        return rate_limited_settings

    app = main_module.create_app()
    app.dependency_overrides[get_settings] = override_settings
    from app.api.dependencies import get_current_settings, get_db_session

    app.dependency_overrides[get_current_settings] = override_settings
    app.dependency_overrides[get_db_session] = lambda: db_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    session = _make_session()
    try:
        yield session
    finally:
        session.close()


def _auth_init_data(telegram_id: int, bot_token: str) -> str:
    from tests.conftest import build_init_data

    return build_init_data(bot_token=bot_token, telegram_id=telegram_id)


def _login(rl_client: TestClient, rate_limited_settings: Settings, telegram_id: int) -> str:
    init_data = _auth_init_data(telegram_id, rate_limited_settings.telegram_bot_token)
    response = rl_client.post("/api/auth/telegram", json={"init_data": init_data})
    return response.json()["refresh_token"]


def test_auth_endpoint_is_rate_limited(rl_client: TestClient, rate_limited_settings: Settings) -> None:
    bot_token = rate_limited_settings.telegram_bot_token
    for _ in range(rate_limited_settings.rate_limit_auth_per_minute):
        response = rl_client.post(
            "/api/auth/telegram",
            json={"init_data": _auth_init_data(700001, bot_token)},
        )
        assert response.status_code == 200
    blocked = rl_client.post(
        "/api/auth/telegram",
        json={"init_data": _auth_init_data(700002, bot_token)},
    )
    assert blocked.status_code == 429
    assert blocked.json()["detail"]
    assert "Retry-After" in blocked.headers


def test_payments_endpoint_is_rate_limited(rl_client: TestClient, rate_limited_settings: Settings) -> None:
    token = _login(rl_client, rate_limited_settings, 700010)
    headers = {"Authorization": f"Bearer {token}"}
    limit = rate_limited_settings.rate_limit_payment_per_minute

    for _ in range(limit):
        response = rl_client.post("/api/payments/mock-confirm", headers=headers, json={"payment_id": "test-payment-id"})
        # 404 is OK - payment not found, but rate limit is checked before endpoint logic
        assert response.status_code in (200, 404, 422)
    blocked = rl_client.post("/api/payments/mock-confirm", headers=headers, json={"payment_id": "test-payment-id"})
    assert blocked.status_code == 429


def test_apply_endpoint_rate_limit_skipped_for_invalid_vacancy(rl_client: TestClient, rate_limited_settings: Settings) -> None:
    # Test that apply path is matched for rate limiting by using invalid vacancy id
    token = _login(rl_client, rate_limited_settings, 700020)
    headers = {"Authorization": f"Bearer {token}"}
    limit = rate_limited_settings.rate_limit_apply_per_minute

    for _ in range(limit):
        response = rl_client.post("/api/vacancies/00000000-0000-0000-0000-000000000000/apply", headers=headers, json={})
        assert response.status_code in (404, 403, 422)
    blocked = rl_client.post("/api/vacancies/00000000-0000-0000-0000-000000000000/apply", headers=headers, json={})
    assert blocked.status_code == 429


def test_limit_resets_after_window(
    rl_client: TestClient,
    rate_limited_settings: Settings,
    monkeypatch,
) -> None:
    bot_token = rate_limited_settings.telegram_bot_token
    limit = rate_limited_settings.rate_limit_auth_per_minute
    for _ in range(limit):
        response = rl_client.post(
            "/api/auth/telegram",
            json={"init_data": _auth_init_data(700030, bot_token)},
        )
        assert response.status_code == 200
    blocked = rl_client.post(
        "/api/auth/telegram",
        json={"init_data": _auth_init_data(700031, bot_token)},
    )
    assert blocked.status_code == 429

    import app.core.rate_limit as rl_module

    state = {"offset": 0.0}

    original_monotonic = time.monotonic

    def fake_monotonic() -> float:
        return original_monotonic() + state["offset"]

    monkeypatch.setattr(rl_module.time, "monotonic", fake_monotonic)
    state["offset"] = 61.0

    after_window = rl_client.post(
        "/api/auth/telegram",
        json={"init_data": _auth_init_data(700032, bot_token)},
    )
    assert after_window.status_code == 200


def test_different_ips_are_counted_separately(
    rl_client: TestClient,
    rate_limited_settings: Settings,
) -> None:
    bot_token = rate_limited_settings.telegram_bot_token
    limit = rate_limited_settings.rate_limit_auth_per_minute
    for _ in range(limit):
        response = rl_client.post(
            "/api/auth/telegram",
            json={"init_data": _auth_init_data(700040, bot_token)},
            headers={"X-Forwarded-For": "1.1.1.1"},
        )
        assert response.status_code == 200
    blocked_same_ip = rl_client.post(
        "/api/auth/telegram",
        json={"init_data": _auth_init_data(700041, bot_token)},
        headers={"X-Forwarded-For": "1.1.1.1"},
    )
    assert blocked_same_ip.status_code == 429

    different_ip = rl_client.post(
        "/api/auth/telegram",
        json={"init_data": _auth_init_data(700042, bot_token)},
        headers={"X-Forwarded-For": "2.2.2.2"},
    )
    assert different_ip.status_code == 200


def test_different_users_do_not_affect_each_other(
    rl_client: TestClient,
    rate_limited_settings: Settings,
) -> None:
    user_a = _login(rl_client, rate_limited_settings, 700050)
    user_b = _login(rl_client, rate_limited_settings, 700051)
    limit = rate_limited_settings.rate_limit_auth_per_minute

    for _ in range(limit):
        response = rl_client.post("/api/auth/refresh", json={"refresh_token": user_a})
        assert response.status_code == 200
    blocked_a = rl_client.post("/api/auth/refresh", json={"refresh_token": user_a})
    assert blocked_a.status_code == 429

    response_b = rl_client.post("/api/auth/refresh", json={"refresh_token": user_b})
    assert response_b.status_code == 200