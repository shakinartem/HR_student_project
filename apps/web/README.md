# Mini App Frontend

Vite React Telegram Mini App frontend for the HR Student Project MVP.

## Current scope

Implemented student flow:

- feed
- vacancy detail
- guest preview limit paywall
- profile/registration
- balance, subscription, payment history, mock confirm
- applications list

Implemented HR flow:

- dashboard
- create vacancy
- vacancy detail with publication/payment/moderation state
- application detail before/after accept

Implemented admin flow:

- dashboard
- users
- HR access
- moderation
- complaints
- payments
- stats

Deferred:

- real YooKassa redirect flow
- production Telegram harness

## Environment

Copy `.env.example` to `.env` and set:

- `VITE_API_BASE_URL`
- `VITE_GUEST_FREE_VACANCY_VIEWS`
- optional `VITE_ENABLE_MOCK_PAYMENT_CONFIRM`

## Setup

```powershell
cd apps/web
Copy-Item .env.example .env
npm install
```

## Run

```powershell
cd apps/web
npm run dev
```

## Build

```powershell
cd apps/web
npm run build
```

## E2E smoke tests

The Playwright smoke suite targets a running local web + backend environment without bypassing production auth rules.

Default target:

- web: `http://localhost:8080`
- backend: `http://localhost:8001`

Run:

```powershell
cd apps/web
npm run test:e2e
```

Optional headed run:

```powershell
cd apps/web
npm run test:e2e:headed
```

Optional override if your web app is on a different URL:

```powershell
$env:PLAYWRIGHT_BASE_URL="http://localhost:8080"
npm run test:e2e
```

Current smoke coverage:

- guest feed loads from seeded backend data
- guest opens vacancy detail
- guest hits paywall on the 4th unique preview
- guest apply routes to paywall
- guest cannot access admin routes
- guest hitting `/hr` gets the current safe fallback
- guest flow never shows hidden HR contact values from seed data

Current auth strategy:

- No fake frontend roles or auth bypasses are used.
- Outside Telegram, Playwright stays in guest mode only.
- Authenticated student/HR/admin E2E is deferred until the project has a safe documented local Telegram auth harness or seeded token helper that does not weaken production auth.

## Notes

- Outside Telegram the app stays in guest mode and still supports feed + guest preview flow.
- Authenticated routes rely on backend-issued tokens stored in `sessionStorage`.
- Any `401` clears the frontend token and safely falls back to guest mode.
- Contact visibility is backend-driven; the frontend never invents hidden contact data.
