# Environment Guide

Use the app-local `.env.example` files as the source of truth:

- `apps/backend/.env.example`
- `apps/bot/.env.example`
- `apps/web/.env.example`

All example files are intended to be secret-free and contain only local placeholders.

## Backend

Important variables:

- `APP_ENV`
- `APP_DEBUG`
- `DATABASE_URL`
- `BACKEND_BASE_URL`
- `WEB_APP_URL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_BOT_USERNAME`
- `TELEGRAM_WEBAPP_URL`
- `ADMIN_TELEGRAM_IDS`
- `JWT_SECRET`
- `YOO_KASSA_SHOP_ID`
- `YOO_KASSA_SECRET_KEY`
- `YOO_KASSA_RETURN_URL`
- `YOO_KASSA_WEBHOOK_SECRET`
- `ENABLE_YOOKASSA_TEST_MODE`
- `GUEST_FREE_VACANCY_VIEWS`
- `STUDENT_MONTHLY_TARIFF_RUB`
- `VACANCY_BASIC_PRICE_RUB`
- `TELEGRAM_INIT_DATA_MAX_AGE_SECONDS`
- `ACCESS_TOKEN_TTL_SECONDS`

Local guidance:

- keep `ENABLE_YOOKASSA_TEST_MODE=true` for local MVP checks
- use a local/test `JWT_SECRET`
- use local bot placeholders instead of real production bot credentials

## Bot

Important variables:

- `BOT_TOKEN`
- `TELEGRAM_WEBAPP_URL`
- `BACKEND_BASE_URL`
- `BACKEND_TIMEOUT_SECONDS`

Local guidance:

- `BOT_TOKEN` must be your local test bot token
- `TELEGRAM_WEBAPP_URL` should point to the local web app entry URL
- `BACKEND_BASE_URL` should point to the local backend

## Web

Important variables:

- `VITE_APP_ENV`
- `VITE_API_BASE_URL`
- `VITE_TELEGRAM_WEBAPP_URL`
- `VITE_GUEST_FREE_VACANCY_VIEWS`
- `VITE_ENABLE_MOCK_PAYMENT_CONFIRM`

Local guidance:

- point `VITE_API_BASE_URL` to the local backend
- keep `VITE_ENABLE_MOCK_PAYMENT_CONFIRM=true` in local MVP checks if you want the manual confirm control visible outside dev heuristics

## Secret handling rules

- never commit real production secrets
- never reuse live bot or payment secrets in example files
- keep `.env.example` values as placeholders or local-safe defaults only

## Docker Compose env

Use `.env.compose.example` as the source for the local production-like Docker flow.

Copy:

```powershell
Copy-Item .env.compose.example .env.compose
```

Important Compose variables:

- `BACKEND_HOST_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `BACKEND_BASE_URL`
- `WEB_APP_URL`
- `TELEGRAM_WEBAPP_URL`
- `BOT_TOKEN`
- `BOT_BACKEND_BASE_URL`
- `JWT_SECRET`
- `WEB_VITE_API_BASE_URL`
- `WEB_VITE_TELEGRAM_WEBAPP_URL`

Compose URL guidance:

- `DATABASE_URL` should use the internal hostname `postgres`
- backend is exposed publicly on `http://localhost:8000` by default
- web is exposed publicly on `http://localhost:8080`
- bot should use internal backend access through `BACKEND_BASE_URL=http://backend:8000`
- frontend build should use `WEB_VITE_API_BASE_URL=http://localhost:8000` by default
- `ADMIN_TELEGRAM_IDS` should use JSON list syntax in Compose, for example `[900001]`
- if `8000` is busy, set `BACKEND_HOST_PORT=8001`, then also set `BACKEND_BASE_URL=http://localhost:8001` and `WEB_VITE_API_BASE_URL=http://localhost:8001`

Task 17 intentionally uses separate ports and does not add a reverse proxy.
