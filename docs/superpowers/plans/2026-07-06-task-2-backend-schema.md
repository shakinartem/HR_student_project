# Task 2 Backend Schema Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the backend schema foundation with SQLAlchemy models, Alembic migration wiring, seed data, and tested contact visibility helpers.

**Architecture:** Keep the backend split into focused modules for config, database setup, models, and visibility services. Use SQLAlchemy for explicit schema control, Alembic for migration history, and pytest for rule-heavy serializer coverage.

**Tech Stack:** Python, FastAPI, Pydantic, Pydantic Settings, SQLAlchemy, Alembic, psycopg, pytest.

---

### Task 1: Prepare backend environment

**Files:**
- Modify: `apps/backend/pyproject.toml`
- Create: `apps/backend/.venv/`

- [ ] Install the approved backend dependencies only.
- [ ] Keep auth, payments integration, bot, and frontend out of scope.

### Task 2: Write failing tests first

**Files:**
- Create: `apps/backend/tests/test_status_enums.py`
- Create: `apps/backend/tests/test_visibility.py`

- [ ] Add failing tests for documented statuses.
- [ ] Add failing tests for student/HR contact visibility rules.
- [ ] Run pytest and confirm the failures come from missing backend modules.

### Task 3: Implement backend modules

**Files:**
- Create: `apps/backend/app/core/*`
- Create: `apps/backend/app/db/*`
- Create: `apps/backend/app/models/*`
- Create: `apps/backend/app/services/visibility.py`
- Modify: `apps/backend/app/main.py`

- [ ] Add typed settings loading from environment.
- [ ] Add SQLAlchemy models for the MVP schema.
- [ ] Add visibility helper functions that default to the safer result.

### Task 4: Add migration and seed support

**Files:**
- Create: `apps/backend/alembic.ini`
- Create: `apps/backend/alembic/env.py`
- Create: `apps/backend/alembic/script.py.mako`
- Create: `apps/backend/alembic/versions/*`
- Create: `apps/backend/scripts/seed_data.py`
- Modify: `apps/backend/README.md`

- [ ] Wire Alembic to the backend metadata.
- [ ] Generate the initial migration.
- [ ] Add a seed script matching `docs/seed-data.md`.

### Task 5: Verify Task 2

**Files:**
- Verify: `apps/backend/task2.db` local test database

- [ ] Run `alembic upgrade head` on a fresh SQLite database.
- [ ] Run the seed script successfully.
- [ ] Run pytest and confirm all Task 2 tests pass.
