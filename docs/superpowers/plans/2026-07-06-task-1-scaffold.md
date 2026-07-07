# Task 1 Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the initial repository structure, placeholder source files, environment examples, and concise Task 1 documentation without adding dependencies or product logic.

**Architecture:** Use a monorepo-style layout with separate `apps/backend`, `apps/bot`, and `apps/web` folders plus shared `docs`, `infra`, and `scripts`. All source files created in this task are scaffolding only and must clearly communicate that implementation is deferred.

**Tech Stack:** Python placeholders for backend and bot, Vite React placeholder structure for web, Markdown documentation.

---

### Task 1: Create repository structure

**Files:**
- Create: `apps/backend/`
- Create: `apps/bot/`
- Create: `apps/web/`
- Create: `infra/`
- Create: `scripts/`

- [ ] Create the directory tree required by Task 1.
- [ ] Keep the structure minimal and avoid adding runtime code.

### Task 2: Add placeholder app files

**Files:**
- Create: `apps/backend/README.md`
- Create: `apps/backend/pyproject.toml`
- Create: `apps/backend/app/__init__.py`
- Create: `apps/backend/app/main.py`
- Create: `apps/backend/tests/__init__.py`
- Create: `apps/backend/alembic/README.md`
- Create: `apps/bot/README.md`
- Create: `apps/bot/pyproject.toml`
- Create: `apps/bot/app/__init__.py`
- Create: `apps/bot/app/main.py`
- Create: `apps/bot/tests/__init__.py`
- Create: `apps/web/README.md`
- Create: `apps/web/package.json`
- Create: `apps/web/tsconfig.json`
- Create: `apps/web/src/main.tsx`
- Create: `apps/web/src/App.tsx`

- [ ] Add placeholder files only.
- [ ] Mark all deferred logic as `TODO`.
- [ ] Do not create fake working auth or payment integrations.

### Task 3: Add environment examples

**Files:**
- Create: `apps/backend/.env.example`
- Create: `apps/bot/.env.example`
- Create: `apps/web/.env.example`

- [ ] Add local variable placeholders only.
- [ ] Exclude real tokens and secrets.
- [ ] Keep YooKassa variables documented but not integrated.

### Task 4: Create and update concise docs

**Files:**
- Create: `README.md`
- Create: `docs/spec.md`
- Create: `docs/security-rules.md`
- Create: `docs/ui-rules.md`
- Modify if needed: `docs/p0-scope.md`
- Modify if needed: `docs/statuses.md`
- Modify if needed: `docs/api-contracts.md`
- Modify if needed: `docs/test-scenarios.md`
- Modify if needed: `docs/copy.md`
- Modify if needed: `docs/env.md`
- Modify if needed: `docs/seed-data.md`
- Modify if needed: `docs/codex-repo-tooling.md`

- [ ] Preserve existing useful content.
- [ ] Add the Vite React frontend decision for P0.
- [ ] Keep documentation concise and explicit.

### Task 5: Verify Task 1 boundaries

**Files:**
- Review created files in the repository tree

- [ ] Confirm that no dependencies were installed.
- [ ] Confirm that no real product logic was implemented.
- [ ] Confirm that all placeholders are clearly marked `TODO` where appropriate.
