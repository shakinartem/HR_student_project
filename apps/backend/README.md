# Backend

FastAPI backend for the HR Student Project MVP.

## Current scope

Implemented:

- `/health`
- `POST /api/auth/telegram`
- `GET /api/me`
- `PATCH /api/me`
- student profile, balance, subscription, applications, refund request
- public vacancies feed, vacancy detail, guest view tracking, student apply
- HR vacancies, HR publication payment, HR applications, accept/reject/complain
- admin users, HR access, moderation, complaints, payments, stats
- mock payment confirmation for local/test mode

Deferred here:

- real YooKassa production webhook flow
- production deployment concerns
- browser E2E automation

## Environment

Copy `.env.example` to `.env` and set local values.

Key variables:

- `DATABASE_URL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_WEBAPP_URL`
- `ADMIN_TELEGRAM_IDS`
- `JWT_SECRET`
- `ENABLE_YOOKASSA_TEST_MODE`

## Local setup

```powershell
cd apps/backend
py -m venv .venv
. .\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
py -m pip install -e ".[dev]"
```

## Run migrations

```powershell
cd apps/backend
. .\.venv\Scripts\Activate.ps1
python -m alembic upgrade head
```

## Seed local data

```powershell
cd apps/backend
. .\.venv\Scripts\Activate.ps1
python scripts/seed_data.py
```

## Run the API

```powershell
cd apps/backend
. .\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

## Canonical test command

```powershell
cd apps/backend
. .\.venv\Scripts\Activate.ps1
python -m pytest -q
```

Warning-clean verification:

```powershell
cd apps/backend
. .\.venv\Scripts\Activate.ps1
python -m pytest -q -W default
```

## Local MVP behavior

- Mock payment confirmation is available only in local/test flows.
- Student access is activated only after backend payment confirmation.
- Guest vacancy preview limit is enforced on the backend.
- Vacancy detail and student application responses never include HR contacts.
- HR sees student contacts only after acceptance.
