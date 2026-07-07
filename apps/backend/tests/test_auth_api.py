from __future__ import annotations

from datetime import UTC, datetime, timedelta
from urllib.parse import urlparse

from fastapi import APIRouter, Depends
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.models import User

from .conftest import build_init_data


def test_healthcheck_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_allows_configured_local_web_origins(client: TestClient, settings) -> None:
    configured_origin = settings.web_app_url
    parsed = urlparse(configured_origin)
    alternate_host = "127.0.0.1" if parsed.hostname == "localhost" else "localhost"
    alternate_origin = parsed._replace(netloc=f"{alternate_host}:{parsed.port}" if parsed.port else alternate_host).geturl()

    for origin in (configured_origin, alternate_origin):
        response = client.options(
            "/api/vacancies",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin


def test_telegram_auth_creates_student_by_default(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    init_data = build_init_data(bot_token=settings.telegram_bot_token, telegram_id=123456, username="fresh_student")

    response = client.post("/api/auth/telegram", json={"init_data": init_data})

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["user"]["role"] == "student"
    user = db_session.query(User).filter(User.telegram_id == 123456).one()
    assert user.role is UserRole.STUDENT


def test_telegram_auth_bootstraps_admin_from_settings(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    init_data = build_init_data(bot_token=settings.telegram_bot_token, telegram_id=999001, username="admin_bootstrap")

    response = client.post("/api/auth/telegram", json={"init_data": init_data})

    assert response.status_code == 200
    assert response.json()["user"]["role"] == "admin"
    user = db_session.query(User).filter(User.telegram_id == 999001).one()
    assert user.role is UserRole.ADMIN


def test_telegram_auth_updates_existing_names_from_fresh_payload(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    original_data = build_init_data(
        bot_token=settings.telegram_bot_token,
        telegram_id=555001,
        username="old_name",
        first_name="Old",
        last_name="Name",
    )
    client.post("/api/auth/telegram", json={"init_data": original_data})
    updated_data = build_init_data(
        bot_token=settings.telegram_bot_token,
        telegram_id=555001,
        username="new_name",
        first_name="New",
        last_name="Profile",
    )

    response = client.post("/api/auth/telegram", json={"init_data": updated_data})

    assert response.status_code == 200
    user = db_session.query(User).filter(User.telegram_id == 555001).one()
    assert user.username == "new_name"
    assert user.first_name == "New"
    assert user.last_name == "Profile"


def test_telegram_auth_rejects_invalid_hash(client: TestClient) -> None:
    response = client.post(
        "/api/auth/telegram",
        json={"init_data": "auth_date=1&user=%7B%7D&hash=invalid"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Telegram initData"


def test_telegram_auth_rejects_expired_init_data(client: TestClient, settings) -> None:
    expired_time = int((datetime.now(UTC) - timedelta(days=2)).timestamp())
    init_data = build_init_data(
        bot_token=settings.telegram_bot_token,
        telegram_id=123321,
        auth_date=expired_time,
    )

    response = client.post("/api/auth/telegram", json={"init_data": init_data})

    assert response.status_code == 401
    assert response.json()["detail"] == "Expired Telegram initData"


def test_get_me_returns_current_user_profile(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/api/me", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["role"] == "student"
    assert payload["telegram_id"] == 777001


def test_patch_me_updates_only_safe_fields(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    response = client.patch(
        "/api/me",
        headers=auth_headers,
        json={
            "first_name": "Updated",
            "last_name": "Profile",
            "phone": "+79998887766",
            "email": "updated@example.com",
            "role": "admin",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["first_name"] == "Updated"
    assert payload["last_name"] == "Profile"
    assert payload["phone"] == "+79998887766"
    assert payload["email"] == "updated@example.com"
    user = db_session.query(User).filter(User.telegram_id == 777001).one()
    assert user.role is UserRole.STUDENT


def test_get_me_rejects_invalid_bearer_token(client: TestClient) -> None:
    response = client.get("/api/me", headers={"Authorization": "Bearer invalid.token"})

    assert response.status_code == 401


def test_role_guards_enforce_student_hr_and_admin(
    client: TestClient,
    auth_headers: dict[str, str],
    hr_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> None:
    response_student = client.get("/api/test/student-only", headers=auth_headers)
    response_hr = client.get("/api/test/hr-only", headers=auth_headers)
    response_admin = client.get("/api/test/admin-only", headers=auth_headers)
    response_hr_ok = client.get("/api/test/hr-only", headers=hr_headers)
    response_admin_ok = client.get("/api/test/admin-only", headers=admin_headers)

    assert response_student.status_code == 200
    assert response_hr.status_code == 403
    assert response_admin.status_code == 403
    assert response_hr_ok.status_code == 200
    assert response_admin_ok.status_code == 200


def test_blocked_user_cannot_use_current_user_endpoint(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    user = db_session.query(User).filter(User.telegram_id == 777001).one()
    user.is_blocked = True
    db_session.commit()

    response = client.get("/api/me", headers=auth_headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "User is blocked"


def test_guard_endpoints_exist() -> None:
    from app.api.dependencies import require_admin, require_hr, require_student

    router = APIRouter()

    @router.get("/student")
    def student_route(user=Depends(require_student)):
        return user

    @router.get("/hr")
    def hr_route(user=Depends(require_hr)):
        return user

    @router.get("/admin")
    def admin_route(user=Depends(require_admin)):
        return user

    assert len(router.routes) == 3
