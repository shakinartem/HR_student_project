from urllib.parse import urlparse

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import require_admin, require_hr, require_student
from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.hr import router as hr_router
from app.api.routes.hr_vacancies import router as hr_vacancies_router
from app.api.routes.payments import router as payments_router
from app.api.routes.student import router as student_router
from app.api.routes.users import router as users_router
from app.api.routes.vacancies import router as vacancies_router

from app.core.config import get_settings


def _allowed_cors_origins(*origins: str) -> list[str]:
    allowed: list[str] = []

    for origin in origins:
        if not origin:
            continue
        if origin not in allowed:
            allowed.append(origin)

        parsed = urlparse(origin)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            continue

        if parsed.hostname == "localhost":
            alternate_host = "127.0.0.1"
        elif parsed.hostname == "127.0.0.1":
            alternate_host = "localhost"
        else:
            continue

        alternate_netloc = f"{alternate_host}:{parsed.port}" if parsed.port else alternate_host
        alternate_origin = parsed._replace(netloc=alternate_netloc).geturl()
        if alternate_origin not in allowed:
            allowed.append(alternate_origin)

    return allowed


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="HR Student Project Backend",
        debug=settings.app_debug,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_cors_origins(settings.web_app_url, settings.telegram_webapp_url),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    application.include_router(auth_router)
    application.include_router(admin_router)
    application.include_router(hr_router)
    application.include_router(hr_vacancies_router)
    application.include_router(student_router)
    application.include_router(payments_router)
    application.include_router(users_router)
    application.include_router(vacancies_router)

    if settings.app_env in {"local", "test"}:
        @application.get("/api/test/student-only")
        def student_only_route(user=Depends(require_student)) -> dict[str, str]:
            return {"role": user.role.value}

        @application.get("/api/test/hr-only")
        def hr_only_route(user=Depends(require_hr)) -> dict[str, str]:
            return {"role": user.role.value}

        @application.get("/api/test/admin-only")
        def admin_only_route(user=Depends(require_admin)) -> dict[str, str]:
            return {"role": user.role.value}

    return application


app = create_app()
