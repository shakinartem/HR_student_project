# MVP Specification

## Current product summary

This repository implements a local MVP of a Telegram Mini App plus Telegram bot for a student vacancies marketplace.

The currently supported end-to-end flow is:

`HR creates vacancy -> HR mock-confirms publication payment -> vacancy is moderated -> student activates access -> student applies -> HR accepts -> HR sees student contacts`

## What is implemented now

### Backend

Implemented API groups:

- auth: `POST /api/auth/telegram`
- current user: `GET /api/me`, `PATCH /api/me`
- student: profile, balance, subscription, applications, refund request
- vacancies: feed, detail, guest view tracking, apply
- HR: vacancy list/create/detail/update, publication payment, HR applications, accept/reject/complain
- admin: users, HR profiles, moderation queue, complaints, payments, stats
- local/test-only mock payment confirmation endpoint

Implemented backend rules:

- guest vacancy preview limit is enforced server-side
- apply requires active student subscription
- students never receive HR contacts
- HR receives student contacts only after acceptance
- role checks are backend-enforced
- payment/subscription activation is backend-controlled
- balance is ledger-driven

### Bot

Implemented bot scope:

- `/start`, `/help`, `/profile`, `/balance`, `/support`
- role-aware menu buttons
- Mini App route shortcuts for guest, student, HR, and admin users
- safe placeholders for support and deferred callback actions

Not implemented in bot:

- production notification delivery
- advanced backend-authorized action callbacks
- broadcast system

### Web Mini App

Implemented student UI:

- feed
- vacancy detail
- paywall
- profile/registration
- balance
- applications

Implemented HR UI:

- dashboard
- create vacancy
- vacancy detail with payment/moderation/publication state
- application detail

Implemented admin UI:

- dashboard
- users
- HR access
- moderation
- complaints
- payments
- stats

## Current auth and payment model

### Auth

- Telegram `initData` is validated by the backend
- backend returns a bearer token
- frontend stores the token in `sessionStorage`
- outside Telegram, the web app falls back to guest mode

### Payments

- local MVP uses backend mock payment confirmation
- payment creation happens on the backend
- subscription activation happens only after confirmed backend payment success
- duplicate confirmations must remain idempotent

## Seeded local actors

The repository includes local seed data for:

- 1 admin
- 3 HR users
- 3 companies
- 3 student users
- 10 active vacancies
- sample applications in `sent`, `accepted`, and `rejected` states
- active student tariff

See `docs/seed-data.md` for the full dataset and manual augmentation steps.

## Current MVP limits

Implemented as local MVP, not production-ready:

- mock payment confirm instead of real YooKassa production webhook flow
- no deployment automation
- no Playwright E2E suite in-repo yet
- bot support and action callbacks are mostly shell behavior
- no production Telegram integration harness

## Deferred from current implementation

See `docs/deferred.md` for the explicit deferred list that is intentionally not part of this MVP readiness pass.
