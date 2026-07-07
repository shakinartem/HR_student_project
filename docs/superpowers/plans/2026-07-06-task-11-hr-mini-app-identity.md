# Task 11 HR Mini App Identity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the Job Hub HR visual identity and implement the approved five HR Mini App states in `apps/web`.

**Architecture:** Keep the existing student flow intact while adding an HR-specific route set, data queries, and screen components that consume real backend HR endpoints. Use shared UI primitives where helpful, but introduce dedicated HR layout components so the dark Job Hub brand can evolve without breaking student-specific UX.

**Tech Stack:** Vite React, TypeScript, Tailwind CSS, TanStack Query, existing backend HR endpoints

---

### Scope

- Add Job Hub branding primitives for HR screens.
- Implement five HR states:
  - dashboard
  - vacancy creation form
  - vacancy detail with payment/publication/moderation states
  - application detail before accept
  - application detail after accept
- Keep student contact visibility backend-driven by rendering contacts only when returned by the API.
- Avoid new dependencies.

### Files

- Modify: `apps/web/src/App.tsx`
- Modify: `apps/web/src/lib/api.ts`
- Modify: `apps/web/src/lib/routes.ts`
- Modify: `apps/web/src/types/api.ts`
- Modify: `apps/web/src/styles.css`
- Modify: `apps/web/tailwind.config.ts`
- Modify: `docs/screens.md`
- Create: `apps/web/src/components/job-hub-logo.tsx`
- Create: `apps/web/src/components/hr-shell.tsx`
- Create: `apps/web/src/components/status-badge.tsx`
- Create: `apps/web/src/screens/hr-dashboard-screen.tsx`
- Create: `apps/web/src/screens/hr-vacancy-form-screen.tsx`
- Create: `apps/web/src/screens/hr-vacancy-detail-screen.tsx`
- Create: `apps/web/src/screens/hr-application-detail-screen.tsx`

### Verification

- Run `npm run build` in `apps/web`.
- Manually verify the HR route flow in the browser when backend auth/session is available.
