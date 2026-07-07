# Security Rules

## Core rules

1. Backend must enforce permissions and role checks.
2. Frontend role, payment, and subscription state are never trusted.
3. Telegram `initData` must be verified on backend.
4. Payment webhooks must be verified and idempotent.
5. Subscription access must not activate without confirmed payment.
6. Balance changes must be tied to ledger transactions.
7. Critical actions must be event-logged.
8. Secrets must never be committed to the repository.
9. If payment or contact visibility state is uncertain, return the safer result.

## Contact visibility matrix

### Student

- Student can view public vacancy data.
- Student must never receive HR phone, email, Telegram, or internal notes.
- Student must never receive HR contacts after applying.
- Student must never receive HR contacts after HR accepts.

### HR

- HR can view student profile summary in applications.
- HR must not receive student contacts before application acceptance.
- HR may receive student contacts only after acceptance.

### Admin

- Admin may access operational data needed for moderation and support.

## Task 1 boundary

No real auth or payment security logic is implemented in Task 1.

Any placeholder files created in scaffolding must be treated as non-functional and marked `TODO`.
