from __future__ import annotations

import json
import warnings
from collections.abc import Generator
from datetime import UTC, datetime
import hashlib
import hmac
from pathlib import Path
from uuid import uuid4
from urllib.parse import urlencode

import pytest
from starlette.exceptions import StarletteDeprecationWarning

warnings.filterwarnings("ignore", category=StarletteDeprecationWarning)

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings
from app.core.enums import UserRole
from app.db.base import metadata
from app.main import app
from app.models import User


def build_init_data(*, bot_token: str, telegram_id: int, username: str = "telegram_user", first_name: str = "Telegram", last_name: str = "User", auth_date: int | None = None) -> str:
    auth_ts = auth_date or int(datetime.now(UTC).timestamp())
    user_payload = {
        "id": telegram_id,
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
    }
    payload = {
        "auth_date": str(auth_ts),
        "query_id": "AAEAAAE",
        "user": json.dumps(user_payload, separators=(",", ":")),
    }
    data_check_string = "\n".join(f"{key}={payload[key]}" for key in sorted(payload))
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    payload["hash"] = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    return urlencode(payload)


@pytest.fixture()
def db_session() -> Generator[Session]:
    tmp_dir = Path("tests/.tmp")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    db_path = tmp_dir / f"test_auth_{uuid4().hex}.db"
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    metadata.create_all(engine)
    with TestingSessionLocal() as session:
        yield session
    metadata.drop_all(engine)
    engine.dispose()
    if db_path.exists():
        db_path.unlink()


@pytest.fixture()
def settings() -> Settings:
    return Settings(
        app_env="test",
        app_debug=False,
        database_url="sqlite:///unused.db",
        telegram_bot_token="test_bot_token_123",
        jwt_secret="super-secret-test-key",
        admin_telegram_ids=[999001],
    )


@pytest.fixture()
def client(db_session: Session, settings: Settings) -> Generator[TestClient]:
    def override_settings() -> Settings:
        return settings

    def override_session() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_settings] = override_settings
    from app.api.dependencies import get_current_settings, get_db_session

    app.dependency_overrides[get_current_settings] = override_settings
    app.dependency_overrides[get_db_session] = override_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client: TestClient, settings: Settings) -> dict[str, str]:
    init_data = build_init_data(bot_token=settings.telegram_bot_token, telegram_id=777001)
    response = client.post("/api/auth/telegram", json={"init_data": init_data})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin_headers(client: TestClient, settings: Settings) -> dict[str, str]:
    init_data = build_init_data(bot_token=settings.telegram_bot_token, telegram_id=999001, username="admin_user")
    response = client.post("/api/auth/telegram", json={"init_data": init_data})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def hr_headers(client: TestClient, db_session: Session, settings: Settings) -> dict[str, str]:
    init_data = build_init_data(bot_token=settings.telegram_bot_token, telegram_id=888001, username="hr_user")
    response = client.post("/api/auth/telegram", json={"init_data": init_data})
    token = response.json()["access_token"]
    user = db_session.query(User).filter(User.telegram_id == 888001).one()
    user.role = UserRole.HR
    db_session.commit()
    return {"Authorization": f"Bearer {token}"}
