# Telegram Bot

aiogram 3 bot for the HR Student Project MVP.

## Current scope

Implemented:

- `/start`, `/help`, `/profile`, `/balance`, `/support`
- role-aware main menu
- Mini App route shortcuts for guest, student, HR, and admin users
- backend lookup by Telegram ID for role-aware menu rendering
- safe placeholder callbacks for support and deferred actions

Deferred:

- real bot-driven accept/reject workflows
- production webhook setup
- push notification orchestration with backend event delivery

## Environment

Copy `.env.example` to `.env` and set:

- `BOT_TOKEN`
- `TELEGRAM_WEBAPP_URL`
- optional `BACKEND_BASE_URL`
- optional `BACKEND_TIMEOUT_SECONDS`

## Setup

```powershell
cd apps/bot
py -m venv .venv
. .\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
py -m pip install -e ".[dev]"
```

## Run

```powershell
cd apps/bot
. .\.venv\Scripts\Activate.ps1
py -m app.main
```

## Tests

```powershell
cd apps/bot
. .\.venv\Scripts\Activate.ps1
py -m pytest -q
```

## Notes

- The bot opens current web routes instead of deprecated placeholders.
- The bot does not issue backend JWTs or bypass backend permissions.
- Support and callback actions that still depend on future backend endpoints stay as explicit placeholders.
