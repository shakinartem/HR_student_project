# AGENTS.md

## 1. Project goal

Build an MVP Telegram Mini App + Telegram bot for a student vacancies marketplace.

The product connects students and local HR/employers.

Core marketplace flow:

1. HR gets access through admin approval or HR referral code.
2. HR creates and pays for a vacancy.
3. Vacancy passes moderation.
4. Guest opens the Telegram Mini App.
5. Guest can preview only 3 vacancy cards.
6. After 3 previews, guest hits paywall.
7. To continue and apply, student must register and activate monthly access by topping up internal balance.
8. Student applies to a vacancy.
9. Student is returned to the main vacancy feed.
10. Student never sees HR contacts.
11. HR receives the application.
12. HR initially sees the application without student contacts.
13. HR accepts the application.
14. Only after acceptance, HR sees student contacts.
15. Student gets a notification that HR is interested.

The MVP must prove the end-to-end flow:

```txt
HR created vacancy -> student paid access -> student applied -> HR accepted -> HR received student contacts
```

---

## 2. Product rules

These rules are mandatory and override any implementation convenience.

### 2.1 Guest rules

1. Guest can open only 3 vacancy cards.
2. Guest can browse the feed before reaching the 3-card limit.
3. Guest cannot apply to vacancies.
4. Guest cannot save vacancies.
5. Guest cannot use advanced user features.
6. After the 3rd opened vacancy card, show paywall.
7. If guest tries to apply, redirect to registration/paywall.

### 2.2 Student rules

1. Student role is the default role for new users.
2. Student must register before applying.
3. Student registration requires profile completion.
4. Student must top up balance to activate access.
5. First top-up must be at least equal to monthly tariff price.
6. After successful payment, monthly tariff is charged from internal balance.
7. Monthly access is activated for 30 days.
8. Student can top up more than one month.
9. Remaining money stays on internal balance.
10. Refund request is a support ticket in MVP.
11. Automatic refunds are not part of MVP.
12. Do not collect student bank details in MVP.
13. Student can apply only with active access.
14. Student never sees HR contacts.
15. Student does not see HR contacts after application.
16. Student does not see HR contacts after HR accepts application.
17. Student can see application status, but not HR contacts.

### 2.3 HR rules

1. HR cannot self-register freely.
2. HR access is granted only by admin or valid HR referral code.
3. HR can create vacancies only with active HR status.
4. HR must pay for vacancy publication.
5. Vacancy must pass moderation before appearing in feed.
6. HR receives applications from students.
7. HR does not see student contacts before accepting the application.
8. HR sees student contacts only after accepting the application.
9. HR can reject application.
10. HR can complain about student.
11. HR can promote vacancies if promotion feature is enabled.
12. HR contacts are hidden from students forever.

### 2.4 Admin rules

Admin must be able to:

1. Grant HR role.
2. Revoke HR role.
3. Block HR.
4. Block user.
5. Mute student for 24 hours.
6. Review complaints.
7. Review moderation queue.
8. Approve vacancy.
9. Reject vacancy.
10. Inspect users.
11. Inspect vacancies.
12. Inspect applications.
13. Inspect payments.
14. Inspect balance transactions.
15. Inspect support tickets.

---

## 3. Hard security rules

1. Do not expose HR contacts to students anywhere.
2. Do not expose student contacts to HR before HR accepts the application.
3. Backend must enforce all permission checks.
4. Frontend role state must never be trusted.
5. Frontend payment state must never be trusted.
6. Frontend subscription state must never be trusted.
7. Backend must verify Telegram initData.
8. Payment webhooks must be verified.
9. Payment webhooks must be idempotent.
10. Do not activate subscription without confirmed payment.
11. Do not mutate balance without ledger transaction.
12. Do not create invisible side effects without event logging.
13. Do not store secrets in repository.
14. Do not put real tokens into examples.
15. Do not log payment secrets, bot token, YooKassa secret, or personal data.
16. All critical actions must be stored as events.
17. Every role-sensitive endpoint must check role on backend.
18. Every contact-revealing endpoint must check application acceptance status.
19. If contact visibility is uncertain, return no contacts.
20. If payment status is uncertain, do not activate access.

---

## 4. Stack

### 4.1 Backend

Use:

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy or SQLModel
* Alembic
* Pydantic
* pytest

Preferred structure:

```txt
/apps/backend
```

Backend is responsible for:

* Telegram authentication validation;
* users;
* roles;
* student profiles;
* HR profiles;
* companies;
* vacancies;
* vacancy views;
* applications;
* payments;
* internal balance;
* subscriptions;
* referrals;
* complaints;
* support tickets;
* admin actions;
* moderation;
* event logging.

### 4.2 Telegram bot

Use:

* Python
* aiogram 3

Preferred structure:

```txt
/apps/bot
```

Bot is responsible for:

* onboarding;
* opening Mini App;
* student notifications;
* HR notifications;
* admin quick actions;
* support tickets;
* HR application actions;
* vacancy moderation notifications.

Do not add another Telegram bot framework.

### 4.3 Frontend / Mini App

Use:

* Next.js or Vite React
* TypeScript
* React
* Tailwind CSS
* Telegram Mini Apps SDK / tma.js
* shadcn/ui
* Radix UI primitives
* React Hook Form
* Zod
* TanStack Query
* lucide-react

Preferred structure:

```txt
/apps/web
```

Frontend is responsible for:

* mobile-first Telegram Mini App UI;
* vacancy feed;
* vacancy details;
* paywall;
* student registration;
* balance screen;
* applications;
* HR vacancy creation;
* HR applications;
* admin panel.

### 4.4 Payments

Use:

* YooKassa
* webhook-based confirmation
* internal user balance
* subscription activation from balance

Payment rules:

1. Create payment on backend.
2. Confirm payment only from YooKassa webhook.
3. Make webhook idempotent.
4. Create payment record.
5. Create balance transaction.
6. Activate access only after confirmed successful payment.
7. Never trust frontend payment success.

### 4.5 Testing

Use:

* pytest for backend;
* Playwright for frontend E2E;
* optional Playwright MCP for AI/browser checks.

Critical test focus:

* guest 3-vacancy limit;
* paywall;
* student registration;
* payment and subscription activation;
* application creation;
* HR acceptance;
* contact visibility rules;
* role permissions;
* webhook idempotency.

---

## 5. Required documentation files

Before major implementation, create or update:

```txt
docs/spec.md
docs/codex-repo-tooling.md
docs/security-rules.md
docs/test-scenarios.md
docs/ui-rules.md
```

### 5.1 docs/spec.md

Must contain product and technical specification.

### 5.2 docs/codex-repo-tooling.md

Must contain allowed/recommended external repositories and dependency decision rules.

Before adding any dependency, read this file.

### 5.3 docs/security-rules.md

Must contain contact visibility, role, payment, and privacy rules.

### 5.4 docs/test-scenarios.md

Must contain manual and automated test scenarios.

### 5.5 docs/ui-rules.md

Must contain UI principles for Mini App.

---

## 6. External repository and dependency policy

Do not install external repositories blindly.

Before adding any dependency, output this decision block:

```txt
Dependency:
Reason:
Runtime or dev-only:
Alternative considered:
Security notes:
Files affected:
Test plan:
```

Example:

```txt
Dependency: react-hook-form
Reason: Needed for student registration and HR vacancy creation forms.
Runtime or dev-only: Runtime frontend dependency.
Alternative considered: Manual useState forms, but this is more error-prone for large forms.
Security notes: Frontend validation is UX only; backend validation remains mandatory.
Files affected: apps/web/package.json, registration form, vacancy form.
Test plan: Submit valid and invalid forms, verify validation errors and backend rejection.
```

### 6.1 Preferred repositories by task

For Telegram Mini App:

* Telegram-Mini-Apps/tma.js
* Telegram-Mini-Apps/reactjs-template

For UI:

* shadcn-ui/ui
* radix-ui/primitives
* tailwindcss
* lucide-icons/lucide

For forms:

* react-hook-form/react-hook-form
* colinhacks/zod

For frontend data:

* tanstack/query

For tables, only if needed:

* tanstack/table

For animations, only after core flow works:

* magicuidesign/magicui
* ibelick/motion-primitives

For browser testing:

* microsoft/playwright
* microsoft/playwright-mcp

For current docs in AI tools:

* upstash/context7

For bot:

* aiogram/aiogram

For backend scaffold reference:

* fastapi/full-stack-fastapi-template

For AI coding rules reference:

* PatrickJS/awesome-cursorrules

For screenshot-to-code prototyping, optional:

* abi/screenshot-to-code

### 6.2 Do not mix UI frameworks

Main UI system:

```txt
shadcn/ui + Tailwind CSS + Radix primitives
```

Do not add Mantine, Chakra, HeroUI, daisyUI, and shadcn together.

If shadcn/ui is used, avoid adding other major component frameworks unless explicitly requested.

### 6.3 Repository safety checks

Before installing, cloning, or running anything from the internet:

1. Inspect README.
2. Inspect package.json / pyproject.toml / setup.py.
3. Inspect install scripts.
4. Inspect preinstall/postinstall/prepare scripts.
5. Inspect example environment files.
6. Do not run curl-to-bash installers.
7. Do not run unknown npm/pnpm/npx commands without explanation.
8. Do not install GitHub repos through pip/npm unless needed.
9. Prefer official packages.
10. Keep dependency list minimal.

---

## 7. Data model requirements

Implement models/tables equivalent to:

### users

Fields:

* id
* telegram_id
* vk_id, nullable
* role
* username
* first_name
* last_name
* phone
* email
* is_blocked
* mute_until
* created_at
* updated_at

### student_profiles

Fields:

* id
* user_id
* university
* course
* speciality
* preferred_job_types
* preferred_schedule
* preferred_districts
* experience_text
* profile_completed
* created_at
* updated_at

Do not include bank details in MVP.

### companies

Fields:

* id
* name
* inn
* description
* logo_url
* contact_name
* contact_phone
* contact_email
* contact_telegram
* status
* created_at
* updated_at

### hr_profiles

Fields:

* id
* user_id
* company_id
* position
* verified_status
* created_at
* updated_at

### vacancies

Fields:

* id
* company_id
* hr_user_id
* title
* category
* job_type
* schedule
* salary_text
* salary_min
* salary_max
* district
* address
* format
* description
* responsibilities
* requirements
* conditions
* experience_required
* photo_url
* status
* moderation_status
* is_promoted
* promotion_type
* promotion_expires_at
* published_at
* expires_at
* created_at
* updated_at

### vacancy_views

Fields:

* id
* user_id
* vacancy_id
* created_at

Used to enforce guest preview limit.

### applications

Fields:

* id
* vacancy_id
* student_user_id
* hr_user_id
* status
* student_comment
* accepted_at
* rejected_at
* created_at
* updated_at

Contacts are not stored here. Contacts come from user/profile only after permission check.

### payments

Fields:

* id
* user_id
* amount
* currency
* provider
* provider_payment_id
* status
* purpose
* created_at
* paid_at

### balance_transactions

Fields:

* id
* user_id
* amount
* type
* reason
* payment_id
* created_at

Balance must be calculated from ledger or updated transactionally.

### subscriptions

Fields:

* id
* user_id
* starts_at
* expires_at
* status
* created_at
* updated_at

### referrals

Fields:

* id
* referrer_user_id
* referred_user_id
* code
* type
* status
* created_at

### complaints

Fields:

* id
* reporter_user_id
* target_user_id
* vacancy_id
* application_id
* reason
* status
* admin_comment
* created_at
* updated_at

### support_tickets

Fields:

* id
* user_id
* type
* subject
* message
* status
* created_at
* updated_at

### tariffs

Fields:

* id
* code
* title
* amount
* duration_days
* is_active
* created_at
* updated_at

### moderation_logs

Fields:

* id
* entity_type
* entity_id
* result
* reason
* raw_response
* created_at

### events

Fields:

* id
* user_id
* event_name
* entity_type
* entity_id
* metadata
* created_at

---

## 8. API requirements

Implement API groups.

### Auth

* POST /api/auth/telegram
* GET /api/me
* PATCH /api/me

### Student

* GET /api/student/profile
* PATCH /api/student/profile
* GET /api/student/balance
* GET /api/student/subscription
* GET /api/student/applications

### Vacancies

* GET /api/vacancies
* GET /api/vacancies/{id}
* POST /api/vacancies/{id}/view
* POST /api/vacancies/{id}/apply

Rules:

1. `GET /api/vacancies/{id}` must enforce guest view limit.
2. `POST /api/vacancies/{id}/apply` must require active subscription.
3. Vacancy response for student must never include HR contacts.

### HR

* GET /api/hr/profile
* PATCH /api/hr/profile
* GET /api/hr/vacancies
* POST /api/hr/vacancies
* PATCH /api/hr/vacancies/{id}
* GET /api/hr/applications
* POST /api/hr/applications/{id}/accept
* POST /api/hr/applications/{id}/reject
* POST /api/hr/applications/{id}/complain

Rules:

1. HR endpoints require HR role.
2. HR can access only own company/vacancies unless admin.
3. Application contacts are hidden before acceptance.
4. Contacts are returned only after acceptance.

### Payments

* POST /api/payments/create
* POST /api/payments/yookassa/webhook
* GET /api/payments/history

Rules:

1. Payment creation is backend-only.
2. Webhook must be idempotent.
3. Subscription activation happens after confirmed payment.
4. Balance ledger entry is mandatory.

### Admin

* GET /api/admin/users
* PATCH /api/admin/users/{id}/role
* POST /api/admin/users/{id}/block
* POST /api/admin/users/{id}/mute
* GET /api/admin/vacancies/moderation
* POST /api/admin/vacancies/{id}/approve
* POST /api/admin/vacancies/{id}/reject
* GET /api/admin/complaints
* POST /api/admin/complaints/{id}/resolve
* GET /api/admin/stats

Rules:

1. Admin endpoints require admin role.
2. Admin actions must be event-logged.

---

## 9. Telegram bot requirements

### 9.1 Commands

Implement:

* /start
* /help
* /profile
* /balance
* /support

### 9.2 Student bot menu

Buttons:

* Open vacancies
* My profile
* My balance
* My applications
* Top up balance
* Referral
* Support

### 9.3 HR bot menu

Buttons:

* Create vacancy
* My vacancies
* Applications
* Promotion
* Balance / payments
* Invite HR
* Support

### 9.4 Admin bot menu

Buttons:

* Users
* HR requests
* Moderation queue
* Complaints
* Payments
* Stats
* Broadcast

### 9.5 Bot notifications

Student notifications:

1. Access activated.
2. Access expires soon.
3. Application sent.
4. HR accepted application.
5. Student was muted.
6. Support ticket updated.

HR notifications:

1. Vacancy submitted.
2. Vacancy approved.
3. Vacancy rejected.
4. New application.
5. Application complaint result.
6. Promotion expires soon.

Admin notifications:

1. New HR request.
2. Vacancy needs manual moderation.
3. New complaint.
4. Refund request.
5. Payment issue.

---

## 10. Mini App UI requirements

### 10.1 General UI

Build mobile-first UI for Telegram.

Use:

* bottom navigation;
* large touch targets;
* readable typography;
* fast loading states;
* empty states;
* error states;
* Telegram theme support if practical.

Primary student navigation:

* Feed
* Applications
* Balance
* Profile

Primary HR navigation:

* Vacancies
* Applications
* Create
* Company

Primary admin navigation:

* Users
* Vacancies
* Complaints
* Payments
* Stats

### 10.2 Student screens

Required:

1. Vacancy feed.
2. Vacancy detail.
3. Paywall after 3 previews.
4. Registration.
5. Balance and top-up.
6. Applications.
7. Profile.
8. Support.
9. Referral, P1 if needed.

### 10.3 HR screens

Required:

1. HR dashboard.
2. My vacancies.
3. Create vacancy.
4. Edit vacancy.
5. Applications.
6. Application detail.
7. Promotion.
8. Company settings.

### 10.4 Admin screens

Required:

1. Users.
2. Students.
3. HR.
4. Companies.
5. Vacancies.
6. Applications.
7. Complaints.
8. Payments.
9. Tariffs.
10. Basic stats.

For MVP, simple lists are enough. Advanced tables are optional.

---

## 11. Contact visibility matrix

This matrix must be enforced on backend.

### Student viewing vacancy

Allowed:

* vacancy title;
* company name;
* category;
* job type;
* schedule;
* salary;
* district;
* address if public;
* description;
* requirements;
* conditions;
* rating if implemented.

Forbidden:

* HR phone;
* HR email;
* HR Telegram;
* hidden HR contacts;
* internal company notes.

### Student after applying

Allowed:

* application status;
* vacancy data;
* company public name.

Forbidden:

* HR phone;
* HR email;
* HR Telegram;
* hidden HR contacts.

### HR viewing application before acceptance

Allowed:

* student first name;
* university;
* course;
* speciality;
* preferred schedule;
* experience;
* student comment.

Forbidden:

* student phone;
* student email;
* student Telegram username.

### HR viewing application after acceptance

Allowed:

* student phone;
* student email;
* student Telegram username.

### Admin

Allowed:

* all data required for operations.

---

## 12. Moderation rules

Vacancy must be checked before publication.

Reject or manual-review vacancies involving:

1. Scam.
2. Gambling.
3. Casino.
4. Betting.
5. Adult/18+.
6. Escort/intimate services.
7. Financial pyramids.
8. Network marketing.
9. Suspicious high income without clear conditions.
10. Request for prepayment from student.
11. Unknown employer.
12. Illegal work.
13. Dangerous work without clear conditions.
14. Discrimination.
15. Requests to transfer passport/documents to unknown persons.
16. Crypto/trading get-rich schemes.
17. Anything that looks unsafe for students.

Moderation statuses:

* approved
* manual_review
* rejected

For MVP, AI moderation can start as rule-based placeholder, but architecture must allow replacing it with real AI moderation later.

---

## 13. Event logging

Log critical events:

Student:

* mini_app_opened
* vacancy_viewed
* guest_limit_reached
* registration_started
* registration_completed
* payment_started
* payment_succeeded
* subscription_activated
* application_created

HR:

* hr_role_granted
* vacancy_created
* vacancy_payment_started
* vacancy_payment_succeeded
* vacancy_submitted_to_moderation
* vacancy_approved
* vacancy_rejected
* application_viewed
* application_accepted
* application_rejected
* complaint_created

Admin:

* user_blocked
* user_muted
* hr_role_granted
* hr_role_revoked
* complaint_resolved
* tariff_changed

Payments:

* payment_created
* webhook_received
* webhook_duplicate_ignored
* balance_transaction_created
* subscription_extended

---

## 14. Testing requirements

### 14.1 Backend tests

Must test:

1. Guest preview limit.
2. Apply requires active subscription.
3. Student cannot see HR contacts.
4. HR cannot see student contacts before acceptance.
5. HR can see student contacts after acceptance.
6. Non-HR cannot create vacancy.
7. HR cannot access another HR vacancy.
8. Admin can grant HR role.
9. Payment webhook idempotency.
10. Subscription activation from balance.
11. Refund request creates support ticket.
12. Blocked user cannot act.
13. Muted student cannot apply.

### 14.2 Frontend E2E tests

Use Playwright.

Viewports:

```txt
390x844
393x852
414x896
430x932
```

Must test:

1. Guest opens Mini App.
2. Guest opens 3 vacancy cards.
3. Guest tries to open 4th vacancy.
4. Paywall appears.
5. Guest tries to apply.
6. Registration screen appears.
7. Student completes registration.
8. Student makes mock top-up.
9. Access activates.
10. Student applies.
11. Student returns to feed.
12. Application appears in “My applications”.
13. Student cannot see HR contacts.
14. HR sees application without contacts.
15. HR accepts.
16. HR sees student contacts.
17. Student still cannot see HR contacts.

---

## 15. MVP priority

### P0

Build first:

1. Telegram auth.
2. Backend models and migrations.
3. Bot /start and role menus.
4. Student Mini App vacancy feed.
5. 3-vacancy guest limit.
6. Paywall.
7. Student registration.
8. Balance top-up mock or YooKassa test mode.
9. Subscription activation.
10. Apply to vacancy.
11. HR role grant.
12. HR vacancy creation.
13. Vacancy payment mock or YooKassa test mode.
14. Moderation placeholder.
15. HR applications.
16. HR accept/reject application.
17. Contact visibility rules.
18. Admin basic panel.
19. Event logging.
20. Critical tests.

### P1

Build after P0 works:

1. Real YooKassa flow.
2. Student referral system.
3. HR referral system.
4. Vacancy promotion.
5. Complaints.
6. Student mute.
7. Support tickets.
8. Notifications.
9. Better moderation.
10. Basic admin stats.

### P2

Build later:

1. Map.
2. Employer rating.
3. HR analytics.
4. Competitor analytics.
5. Advanced CRM.
6. Automatic refunds.
7. VK auth.
8. Advanced recommendations.
9. Complex tariff packages.
10. Public landing page.

---

## 16. Forbidden P0 features

Do not build in P0 unless explicitly requested:

1. Map.
2. Complex employer rating.
3. Full CRM.
4. Automatic refunds.
5. Student bank details.
6. VK auth.
7. Advanced analytics.
8. AI competitor analytics.
9. Complex recommendation engine.
10. Multiple UI frameworks.
11. Multiple bot frameworks.
12. Mobile app outside Telegram.
13. Free public HR registration.
14. HR contact visibility for students.
15. Student contact visibility before HR acceptance.

---

## 17. Definition of done

A feature is done only if:

1. Backend logic exists.
2. Frontend or bot UI exists.
3. Backend role checks exist.
4. Contact visibility rules are enforced.
5. Payment/subscription state is backend-controlled.
6. Errors are handled.
7. Empty states are handled.
8. Loading states are handled.
9. Critical events are logged.
10. Tests or documented manual test scenario exist.
11. No forbidden contact exposure exists.
12. No non-MVP feature was added without approval.

---

## 18. MVP final acceptance

MVP is accepted only when this full scenario works:

1. Admin grants HR role to a user.
2. HR creates vacancy.
3. HR pays for vacancy publication.
4. Vacancy passes moderation.
5. Vacancy appears in feed.
6. Guest opens Mini App.
7. Guest views 3 vacancy cards.
8. Guest hits paywall.
9. Guest registers as student.
10. Student tops up balance.
11. Monthly access activates.
12. Student applies to vacancy.
13. Student returns to main feed.
14. HR receives application.
15. HR sees application without contacts.
16. HR accepts application.
17. HR sees student contacts.
18. Student receives notification.
19. Student still does not see HR contacts.
20. Admin can inspect users, vacancies, applications, payments, and complaints.

If any contact visibility rule is broken, MVP is not accepted.
