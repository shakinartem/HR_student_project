from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta


class TokenError(ValueError):
    """Raised when a signed access token is invalid."""


def _urlsafe_b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _urlsafe_b64decode(raw: str) -> bytes:
    padding = "=" * (-len(raw) % 4)
    return base64.urlsafe_b64decode(raw + padding)


def create_access_token(*, subject: str, secret_key: str, ttl_seconds: int) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp()),
    }
    payload_segment = _urlsafe_b64encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signature = hmac.new(secret_key.encode("utf-8"), payload_segment.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload_segment}.{signature}"


def decode_access_token(token: str, secret_key: str) -> dict:
    try:
        payload_segment, signature = token.split(".", 1)
    except ValueError as exc:
        raise TokenError("Malformed token") from exc

    expected_signature = hmac.new(
        secret_key.encode("utf-8"),
        payload_segment.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        raise TokenError("Invalid token signature")

    payload = json.loads(_urlsafe_b64decode(payload_segment))
    now_ts = int(datetime.now(UTC).timestamp())
    if int(payload["exp"]) < now_ts:
        raise TokenError("Token expired")
    return payload
