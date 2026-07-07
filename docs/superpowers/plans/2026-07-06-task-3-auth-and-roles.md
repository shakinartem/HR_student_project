# Task 3 Auth And Roles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Telegram authentication, current-user endpoints, and backend role guards on top of the Task 2 schema.

**Architecture:** Keep auth split into small units: Telegram initData verification, signed access-token handling, request dependencies, and API routes. Test through FastAPI request flow against an isolated SQLite database.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, pytest, httpx.

---

### Task 1: Write failing auth tests

**Files:**
- Create: `apps/backend/tests/conftest.py`
- Create: `apps/backend/tests/test_auth_api.py`
- Create: `apps/backend/tests/test_telegram_verifier.py`

- [ ] Cover valid and invalid Telegram initData.
- [ ] Cover default student role and admin bootstrap.
- [ ] Cover `/api/me`, patch safety, and role guards.

### Task 2: Implement auth utilities and dependencies

**Files:**
- Create: `apps/backend/app/core/security.py`
- Create: `apps/backend/app/core/telegram.py`
- Create: `apps/backend/app/api/dependencies.py`

- [ ] Add signed bearer token helpers.
- [ ] Add Telegram initData verification helpers.
- [ ] Add current-user and role guard dependencies.

### Task 3: Implement API routes and app structure

**Files:**
- Create: `apps/backend/app/api/routes/auth.py`
- Create: `apps/backend/app/api/routes/users.py`
- Modify: `apps/backend/app/main.py`
- Create: `apps/backend/app/schemas/*`

- [ ] Add `/health`.
- [ ] Add `POST /api/auth/telegram`.
- [ ] Add `GET /api/me` and `PATCH /api/me`.

### Task 4: Verify and document

**Files:**
- Modify: `apps/backend/README.md`
- Modify: `apps/backend/pytest.ini`

- [ ] Make `python -m pytest -q` work in this environment.
- [ ] Document the auth token approach and endpoint availability.
