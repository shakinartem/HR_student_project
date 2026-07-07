# HR Student Project

Telegram Mini App MVP for a student vacancies marketplace with three apps:

- `apps/backend` for the FastAPI API, data model, permissions, mock payments, moderation, and event logging
- `apps/bot` for the aiogram bot menus and Mini App shortcuts
- `apps/web` for the Vite React Telegram Mini App

The implemented MVP proves the core guarded flow:

`HR creates vacancy -> student activates access -> student applies -> HR accepts -> HR sees student contacts`

## Repository layout

```txt
apps/
  backend/
  bot/
  web/
docs/
infra/
scripts/
```

## Quickstart

### 1. Create local env files

Copy these example files and fill in local placeholder values:

- `apps/backend/.env.example` -> `apps/backend/.env`
- `apps/bot/.env.example` -> `apps/bot/.env`
- `apps/web/.env.example` -> `apps/web/.env`

Use only local test values. Do not place real production secrets in this repository.

### 2. Backend setup

```powershell
cd apps/backend
py -m venv .venv
. .\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
py -m pip install -e ".[dev]"
```

### 3. Backend migrations

```powershell
cd apps/backend
. .\.venv\Scripts\Activate.ps1
python -m alembic upgrade head
```

### 4. Seed data

```powershell
cd apps/backend
. .\.venv\Scripts\Activate.ps1
python scripts/seed_data.py
```

### 5. Backend run

```powershell
cd apps/backend
. .\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Health check:

```txt
GET http://localhost:8000/health
```

### 6. Backend tests

```powershell
cd apps/backend
. .\.venv\Scripts\Activate.ps1
python -m pytest -q -W default
```

### 7. Bot setup

```powershell
cd apps/bot
py -m venv .venv
. .\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
py -m pip install -e ".[dev]"
```

### 8. Bot run

```powershell
cd apps/bot
. .\.venv\Scripts\Activate.ps1
py -m app.main
```

### 9. Bot tests

```powershell
cd apps/bot
. .\.venv\Scripts\Activate.ps1
py -m pytest -q
```

### 10. Web setup

```powershell
cd apps/web
Copy-Item .env.example .env
npm install
```

### 11. Web run

```powershell
cd apps/web
npm run dev
```

### 12. Web build

```powershell
cd apps/web
npm run build
```

## Docker Compose

For a local production-like launch, use separate exposed ports and keep Postgres internal-only:

- web: `http://localhost:8080`
- backend: `http://localhost:8000`
- postgres: Compose-internal only
- bot: optional background service via Compose profile

If host port `8000` is busy on your machine:

- set `BACKEND_HOST_PORT=8001` in `.env.compose`
- set `BACKEND_BASE_URL=http://localhost:8001`
- set `WEB_VITE_API_BASE_URL=http://localhost:8001`

Compose flow:

```powershell
Copy-Item .env.compose.example .env.compose
docker compose --env-file .env.compose build
docker compose --env-file .env.compose up -d postgres
docker compose --env-file .env.compose run --rm backend alembic upgrade head
docker compose --env-file .env.compose run --rm backend python scripts/seed_data.py
docker compose --env-file .env.compose up -d backend web
```

Health checks:

- backend: `http://localhost:8000/health`
- web: `http://localhost:8080/health`
- app: `http://localhost:8080`

If you changed `BACKEND_HOST_PORT`, use that host port in the backend health URL instead, for example `http://localhost:8001/health`.

Start the bot only after replacing the placeholder token in `.env.compose`:

```powershell
docker compose --env-file .env.compose --profile bot up -d bot
```

Reverse proxy, HTTPS, and domain routing are intentionally deferred.

## What is implemented

### Backend

- Telegram auth with backend-issued bearer token
- guest vacancy feed and guest 3-view limit
- student profile, balance, subscription, payment history, refund-request ticket
- student apply flow with active subscription enforcement
- HR vacancy creation, publication payment, moderation placeholder, application review
- admin users, HR access, moderation, complaints, payments, and stats APIs
- event logging for critical actions
- SQLite/Postgres-compatible dev setup via Alembic

### Bot

- `/start`, `/help`, `/profile`, `/balance`, `/support`
- role-aware main menu
- Mini App deep links for guest, student, HR, and admin entry points
- safe placeholder callbacks for support and not-yet-automated actions

### Web

- student feed, vacancy detail, paywall, profile/registration, balance, applications
- HR dashboard, vacancy create flow, vacancy detail, application detail
- admin dashboard plus users, HR access, moderation, complaints, payments, stats
- Telegram auth bootstrap with guest fallback outside Telegram

## Important local MVP notes

- Payments are mock-confirmed locally; real YooKassa production webhook handling is deferred.
- Student and HR contact visibility is enforced by the backend, not by frontend role state.
- The bot is a safe shell around current web routes and does not bypass backend auth.
- Playwright E2E automation is still deferred.

## Documentation map

- [docs/spec.md](docs/spec.md)
- [docs/screens.md](docs/screens.md)
- [docs/test-scenarios.md](docs/test-scenarios.md)
- [docs/seed-data.md](docs/seed-data.md)
- [docs/env.md](docs/env.md)
- [docs/mvp-manual-checklist.md](docs/mvp-manual-checklist.md)
- [docs/deferred.md](docs/deferred.md)
