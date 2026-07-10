from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from typing import Final

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import Settings
from app.core.security import decode_access_token, TokenError

# Sliding window buckets keyed by group.
# Each bucket maps a composite identity key -> deque of timestamps (seconds).
_WINDOW_SECONDS: Final[int] = 60

# Mapping of request path prefixes to configuration keys in Settings.
_PATH_GROUP_RULES: Final[list[tuple[str, str]]] = [
    ("/api/auth/telegram", "rate_limit_auth_per_minute"),
    ("/api/auth/refresh", "rate_limit_auth_per_minute"),
    ("/api/applications", "rate_limit_apply_per_minute"),
    ("/api/payments", "rate_limit_payment_per_minute"),
    ("/api/webhook", "rate_limit_webhook_per_minute"),
    ("/api/admin", "rate_limit_admin_per_minute"),
]


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _resolve_limit_per_minute(path: str, settings: Settings) -> int:
    for prefix, attr in _PATH_GROUP_RULES:
        if path.startswith(prefix):
            return int(getattr(settings, attr))
    return settings.rate_limit_general_per_minute


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Centralized sliding-window rate limiter.

    Limits apply per (group, identity) where identity is the authenticated
    user id when available, otherwise the client IP. The same backend storage
    is reused for every protected endpoint, so no per-endpoint duplication
    is required.
    """

    def __init__(self, app, settings: Settings) -> None:
        super().__init__(app)
        self._settings = settings
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    def _resolve_user_id(self, request: Request) -> object | None:
        user_id = getattr(request.state, "user_id", None)
        if user_id is not None:
            return user_id
        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:]
            try:
                payload = decode_access_token(token, self._settings.jwt_secret)
            except TokenError:
                return None
            return payload.get("sub")
        return None

    def _identity_key(self, request: Request, group: str) -> str:
        user_id = self._resolve_user_id(request)
        if user_id is not None:
            return f"{group}:user:{user_id}"
        return f"{group}:ip:{_client_ip(request)}"

    def _group_for(self, path: str) -> str:
        for prefix, _attr in _PATH_GROUP_RULES:
            if path.startswith(prefix):
                return prefix
        return "general"

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.method != "POST":
            return await call_next(request)

        path = request.url.path
        limit = _resolve_limit_per_minute(path, self._settings)
        group = self._group_for(path)
        key = self._identity_key(request, group)

        now = time.monotonic()
        window_start = now - _WINDOW_SECONDS
        bucket = self._buckets[key]
        while bucket and bucket[0] <= window_start:
            bucket.popleft()
        if len(bucket) >= limit:
            retry_after = int(_WINDOW_SECONDS - (now - bucket[0])) + 1
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please retry later."},
                headers={"Retry-After": str(retry_after)},
            )

        bucket.append(now)
        return await call_next(request)