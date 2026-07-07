# Test Scenarios

## Automated verification commands

Current smoke commands:

### Backend

```powershell
cd apps/backend
. .\.venv\Scripts\Activate.ps1
python -m pytest -q -W default
```

### Bot

```powershell
cd apps/bot
py -m pytest -q
```

### Web

```powershell
cd apps/web
npm run build
npm run test:e2e
```

## Automated coverage summary

### Backend

Current backend tests cover:

- Telegram auth validation
- guest vacancy preview limit
- vacancy visibility
- student profile and balance flows
- subscription activation
- payment idempotency
- student apply flow
- HR vacancy creation and publication flow
- HR contact visibility before/after acceptance
- admin users, HR access, moderation, complaints, payments, stats

### Bot

Current bot tests cover:

- role menu builders
- current route links
- query-preserving web app URLs

### Web

Current web automation covers:

- Vite production build
- Playwright guest smoke suite on mobile viewports `390x844`, `393x852`, `414x896`, `430x932`
- guest feed load from seeded backend data
- guest vacancy detail open
- guest 4th unique preview paywall
- guest apply paywall redirect
- guest `/hr` safe fallback
- guest `/admin` access denied
- guest hidden HR contacts not visible in feed/detail

Authenticated Playwright flows remain deferred until a safe local Telegram auth harness exists.

### Web E2E run notes

Expected local targets:

- web: `http://localhost:8080`
- backend: `http://localhost:8001`

Command:

```powershell
cd apps/web
npm run test:e2e
```

Optional headed run:

```powershell
cd apps/web
npm run test:e2e:headed
```

If the web app runs on a different host or port:

```powershell
$env:PLAYWRIGHT_BASE_URL="http://localhost:8080"
npm run test:e2e
```

## Manual smoke scenarios

Use `390x844` for Mini App checks.

### Scenario 1: Guest feed and paywall

1. Open the web app outside Telegram as a new guest.
2. Confirm the feed loads.
3. Open 3 unique vacancies.
4. Try to open the 4th vacancy.

Pass if:

- first 3 vacancies open
- the 4th vacancy is blocked
- paywall appears
- no HR contacts are shown

### Scenario 2: Guest cannot apply

1. Open a vacancy as guest.
2. Tap apply.

Pass if:

- no application is created
- the app routes to paywall/profile activation
- no HR contacts appear

### Scenario 3: Student auth, profile, balance, subscription

1. Open the Mini App inside Telegram or a valid Telegram-compatible test harness.
2. Confirm auth bootstrap succeeds.
3. Save the student profile.
4. Create a top-up for `350`.
5. Mock-confirm the payment.
6. Refresh balance/subscription.

Pass if:

- profile save succeeds
- payment becomes `succeeded` only after backend confirmation
- subscription becomes active
- balance ledger and payment history update

### Scenario 4: Student apply flow

1. Ensure the student has active subscription.
2. Open an active vacancy.
3. Apply.
4. Return to feed.
5. Open applications.

Pass if:

- application is created
- UI returns to feed
- application appears in the list
- student still sees no HR contacts

### Scenario 5: HR vacancy publication flow

1. Open the HR dashboard.
2. Create a vacancy.
3. Open the created vacancy.
4. Create publication payment.
5. Mock-confirm the publication payment.

Pass if:

- draft vacancy is created
- payment can be created
- moderation/publication state updates after confirmation
- approved vacancies appear in the public feed

### Scenario 6: HR application visibility flow

1. Open HR application detail before acceptance.
2. Inspect visible student fields.
3. Accept the application.
4. Re-open or refresh the detail.

Pass if:

- pre-accept view shows no phone/email/Telegram username
- post-accept view shows student contacts only after backend acceptance
- student still never sees HR contacts

### Scenario 7: Admin operational smoke

1. Open `/admin` as non-admin.
2. Confirm access denied.
3. Open `/admin` as admin.
4. Check users, HR access, moderation, complaints, payments, stats.

Pass if:

- non-admin access is blocked
- admin sections load
- user block/mute works
- HR status updates work
- moderation approve/reject works
- complaint status update works
- payments remain read-only

### Scenario 8: Bot smoke

1. Run `/start` as guest.
2. Run `/start` as student.
3. Run `/start` as HR.
4. Run `/start` as admin.
5. Run `/help`, `/profile`, `/balance`, `/support`.

Pass if:

- each role gets the correct menu
- Mini App buttons point to current routes
- placeholder support/action callbacks respond safely

## Known manual-only areas

- full Telegram Mini App auth must be checked inside Telegram or a compatible harness
- production YooKassa webhook behavior is not part of current local MVP verification
- authenticated student/HR/admin Playwright flows are deferred until safe non-bypass local auth is available
