# Task 13 Admin Mini App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add minimal admin backend APIs and Job Hub admin Mini App screens for users, HR access, moderation, complaints, payments, and stats.

**Architecture:** Keep admin scope intentionally small: reuse `require_admin`, existing models, and current Vite route state instead of adding a separate admin app or CRM layer. On the frontend, add simple mobile-first list/detail screens and card actions that call backend-owned admin endpoints, with `401` and `403` handled safely by the existing auth/session flow.

**Tech Stack:** FastAPI, SQLAlchemy, pytest, Vite React, TypeScript, Tailwind CSS, TanStack Query

---

### Scope

- Add missing admin backend APIs only where they do not already exist.
- Add backend tests for admin permissions and state transitions.
- Add `/admin` route state and operational screens in `apps/web`.
- Keep UI simple: cards, counters, filtered lists, and safe one-tap actions.
- Update bot admin deeplinks if route aliases are needed.
- Update `docs/screens.md`, `docs/test-scenarios.md`, and `apps/web/README.md`.

### Files likely touched

- `apps/backend/app/api/routes/admin.py`
- `apps/backend/app/main.py`
- `apps/backend/app/schemas/*.py` for admin response/request models
- `apps/backend/app/services/*.py` for admin list/update helpers if needed
- `apps/backend/tests/test_admin_api.py`
- `apps/web/src/App.tsx`
- `apps/web/src/lib/api.ts`
- `apps/web/src/lib/routes.ts`
- `apps/web/src/types/api.ts`
- `apps/web/src/screens/*admin*.tsx`
- `apps/bot/app/keyboards/main_menu.py` if admin deeplink alias cleanup is needed
- `docs/screens.md`
- `docs/test-scenarios.md`
- `apps/web/README.md`

### Verification

- `pytest` in `apps/backend`
- `pytest` in `apps/bot` if bot routing changes
- `npm run build` in `apps/web`
