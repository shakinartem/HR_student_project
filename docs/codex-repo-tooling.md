# Codex Repo Tooling Guide

Task 1 note:

- no dependencies are installed in this task
- frontend choice for P0 is Vite React
- Next.js remains deferred unless product scope changes

## Purpose

This file tells Codex which external repositories, libraries, templates, MCP tools, UI kits, and agent tooling may be useful for this project.

Do not install everything from this file.

Use this file as a decision matrix. Before adding any dependency, Codex must explain:

1. What task it solves.
2. Why this dependency is needed.
3. Why a simpler built-in solution is not enough.
4. What files will be changed.
5. How the result will be tested.
6. Whether the dependency is runtime, dev-only, or reference-only.

Project context:

We are building a Telegram Mini App + Telegram bot for a student vacancies marketplace.

Core product rules:

1. Guest can view only 3 vacancy cards.
2. Guest cannot apply to vacancies.
3. Student must register and activate monthly access through balance top-up.
4. Student can apply only with active access.
5. Student never sees HR contacts.
6. HR sees student contacts only after accepting the application.
7. HR access is closed and can be granted only by admin or HR referral code.
8. Payments use YooKassa.
9. Backend must enforce all permissions.
10. Frontend must never be trusted as a source of truth.

---

# 1. Hard security rules for using repositories

Before installing, cloning, or running anything from a repository:

1. Inspect README.
2. Inspect package.json / pyproject.toml / setup.py.
3. Inspect install scripts, postinstall scripts, prepare scripts, preinstall scripts.
4. Inspect GitHub Actions if relevant.
5. Inspect example `.env` files.
6. Do not run random install scripts from the internet.
7. Do not paste secrets into generated code.
8. Do not give any tool access to production tokens.
9. Prefer official packages and actively maintained repos.
10. If a repository is only useful as inspiration, do not install it.

Never blindly run:

```bash
curl ... | bash
wget ... | bash
npm install <unknown-package>
pnpm dlx <unknown-package>
npx <unknown-package>
pip install git+https://...
```

without first explaining why it is safe and necessary.

---

# 2. Project stack

Preferred stack:

Frontend:

* Next.js or Vite React
* TypeScript
* React
* Tailwind CSS
* Telegram Mini Apps SDK
* shadcn/ui
* React Hook Form
* Zod
* TanStack Query

Backend:

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy or SQLModel
* Alembic
* aiogram 3

Payments:

* YooKassa
* Webhook confirmation
* Internal balance
* Monthly access subscription

Testing:

* Playwright
* pytest
* API tests for permission rules
* E2E tests for guest limit, paywall, application flow, HR accept flow

---

# 3. Decision matrix

## If building Telegram Mini App frontend

Prefer:

1. Telegram-Mini-Apps/tma.js
2. Telegram-Mini-Apps/reactjs-template
3. shadcn-ui/ui
4. Radix UI primitives
5. Tailwind CSS
6. React Hook Form
7. Zod
8. TanStack Query

Use Magic UI or Motion Primitives only for polish, not for core MVP.

## If building Telegram bot

Prefer:

1. aiogram/aiogram

Do not add multiple Telegram bot frameworks. Use aiogram 3.

## If building backend scaffold

Prefer:

1. FastAPI
2. SQLAlchemy or SQLModel
3. Alembic
4. PostgreSQL
5. fastapi/full-stack-fastapi-template as reference or scaffold

Do not overcomplicate backend architecture.

## If making UI visually better

Prefer:

1. shadcn-ui/ui
2. magicuidesign/magicui
3. ibelick/motion-primitives
4. lucide-icons/lucide
5. Recharts for admin analytics

Do not add Mantine, Chakra, HeroUI, daisyUI, and shadcn all at the same time. Pick one main UI system.

For this project, main UI system must be:

```txt
shadcn/ui + Tailwind + Radix primitives
```

## If Codex needs current documentation

Prefer:

1. upstash/context7

Use Context7 to fetch current docs for:

* Next.js
* React
* Tailwind
* shadcn/ui
* Telegram Mini Apps SDK
* FastAPI
* SQLAlchemy
* aiogram
* YooKassa

## If Codex needs to check UI in browser

Prefer:

1. microsoft/playwright-mcp
2. microsoft/playwright

Use Playwright for:

* mobile viewport checks;
* paywall after 3 vacancy views;
* student registration;
* mock payment;
* application flow;
* HR application acceptance;
* ensuring student never sees HR contacts.

## If building UI from screenshots

Consider:

1. abi/screenshot-to-code

Use only as inspiration or one-time generation. Clean up generated code before committing.

## If adding AI coding rules

Use as reference:

1. PatrickJS/awesome-cursorrules
2. custom AGENTS.md
3. custom project rules

Do not copy random rules blindly. Adapt them to this product.

---

# 4. Top recommended repositories for this project

## 1. Telegram-Mini-Apps/tma.js

Repository:

```txt
Telegram-Mini-Apps/tma.js
```

Use for:

* Telegram Mini App SDK;
* Telegram initData;
* Telegram theme params;
* viewport;
* back button;
* main button;
* haptics;
* React integration.

When to install:

Install when implementing Mini App frontend.

Expected usage:

* Validate Telegram initData on backend.
* Use SDK only for Telegram WebApp features.
* Do not rely on frontend user data for permissions.

Important:

Backend must verify Telegram initData.

---

## 2. Telegram-Mini-Apps/reactjs-template

Repository:

```txt
Telegram-Mini-Apps/reactjs-template
```

Use for:

* quick Mini App frontend bootstrap;
* example structure;
* Telegram SDK integration reference.

When to install or clone:

Use only if starting the frontend from scratch.

If project already has Next.js frontend, do not replace the whole project. Use as reference.

---

## 3. shadcn-ui/ui

Repository:

```txt
shadcn-ui/ui
```

Use for:

* buttons;
* cards;
* forms;
* dialogs;
* tabs;
* drawers;
* sheets;
* tables;
* badges;
* inputs;
* toast notifications.

When to install:

Install early in frontend work.

Project UI should be based on:

```txt
shadcn/ui + Tailwind CSS
```

Core screens to build with it:

* vacancy feed;
* vacancy card;
* paywall screen;
* registration form;
* balance screen;
* applications screen;
* HR vacancies;
* HR applications;
* admin panel.

---

## 4. Radix UI primitives

Repository:

```txt
radix-ui/primitives
```

Use for:

* accessible primitives;
* dialogs;
* dropdowns;
* tabs;
* popovers;
* forms;
* switches.

When to install:

Usually installed indirectly through shadcn/ui.

Do not use Radix directly unless needed.

---

## 5. magicuidesign/magicui

Repository:

```txt
magicuidesign/magicui
```

Use for:

* animated onboarding;
* beautiful paywall;
* success states;
* empty states;
* premium-looking UI blocks.

When to install:

Only after core flows work.

Do not use Magic UI for core logic.

Best project use cases:

* “Access activated” screen;
* “3 free vacancies used” paywall;
* landing-like “How it works” screen;
* HR value proposition block.

---

## 6. ibelick/motion-primitives

Repository:

```txt
ibelick/motion-primitives
```

Use for:

* small UI animations;
* transitions;
* expandable cards;
* smooth mobile interactions.

When to install:

Only when UI feels too static.

Avoid animation overuse.

---

## 7. microsoft/playwright-mcp

Repository:

```txt
microsoft/playwright-mcp
```

Use for:

* browser control by AI agent;
* UI verification;
* E2E flow checks;
* visual debugging.

When to install:

Install when frontend has first working screens.

Required checks:

1. Open Mini App in mobile viewport.
2. Guest views first vacancy.
3. Guest views second vacancy.
4. Guest views third vacancy.
5. Fourth vacancy triggers paywall.
6. Guest cannot apply.
7. Student registers.
8. Student pays using mock payment.
9. Student applies.
10. Student returns to home.
11. HR sees application without contacts.
12. HR accepts application.
13. HR sees student contacts.
14. Student never sees HR contacts.

---

## 8. microsoft/playwright

Repository:

```txt
microsoft/playwright
```

Use for:

* automated E2E tests;
* CI tests;
* screenshots;
* mobile viewport testing.

When to install:

Install as dev dependency when building frontend flows.

Test viewports:

```txt
390x844
393x852
414x896
430x932
```

---

## 9. upstash/context7

Repository:

```txt
upstash/context7
```

Use for:

* current library docs inside AI coding tools;
* avoiding outdated API usage;
* checking syntax before implementation.

When to use:

Use before implementing:

* Telegram Mini Apps SDK;
* Next.js routing;
* shadcn/ui components;
* aiogram handlers;
* FastAPI dependencies;
* SQLAlchemy models;
* YooKassa integration.

---

## 10. PatrickJS/awesome-cursorrules

Repository:

```txt
PatrickJS/awesome-cursorrules
```

Use for:

* reference AI coding rules;
* Cursor/Codex style rules;
* framework-specific guidance.

When to use:

Use as inspiration for:

* `.cursor/rules`;
* `AGENTS.md`;
* `docs/codex-rules.md`.

Do not copy all rules blindly.

Adapt to this project.

---

## 11. aiogram/aiogram

Repository:

```txt
aiogram/aiogram
```

Use for:

* Telegram bot;
* student notifications;
* HR notifications;
* admin actions;
* support tickets;
* inline buttons.

When to install:

Install when building `/bot`.

Bot must support:

Student:

* start;
* open Mini App;
* balance;
* applications;
* support.

HR:

* create vacancy;
* view applications;
* accept application;
* reject application;
* complain.

Admin:

* grant HR role;
* block HR;
* mute student;
* approve vacancy;
* reject vacancy;
* review complaints.

---

## 12. fastapi/full-stack-fastapi-template

Repository:

```txt
fastapi/full-stack-fastapi-template
```

Use for:

* backend scaffold reference;
* Docker structure;
* SQLModel examples;
* auth patterns;
* frontend/backend separation.

When to use:

Use only as reference or scaffold if starting backend from zero.

Do not copy unrelated features.

Our backend must focus on:

* Telegram auth;
* vacancies;
* applications;
* roles;
* payments;
* balance;
* subscriptions;
* admin;
* webhooks.

---

## 13. abi/screenshot-to-code

Repository:

```txt
abi/screenshot-to-code
```

Use for:

* turning UI screenshots into Tailwind/React drafts;
* quick visual prototyping.

When to use:

Use if we have screenshots or sketches of:

* vacancy feed;
* paywall;
* HR application screen;
* balance screen.

Do not commit raw generated code without cleanup.

Generated code must be refactored into:

* reusable components;
* shadcn/ui components;
* clean Tailwind classes;
* typed props.

---

## 14. tanstack/query

Repository:

```txt
tanstack/query
```

Use for:

* frontend API state;
* caching;
* loading states;
* mutations;
* invalidation after actions.

When to install:

Install for frontend once backend API exists.

Use for:

* vacancy feed;
* vacancy details;
* applications;
* balance;
* HR vacancies;
* admin lists.

---

## 15. tanstack/table

Repository:

```txt
tanstack/table
```

Use for:

* admin tables;
* HR tables;
* users list;
* vacancies list;
* payments list;
* applications list.

When to install:

Only when admin screens become table-heavy.

For MVP, simple lists may be enough.

---

## 16. react-hook-form/react-hook-form

Repository:

```txt
react-hook-form/react-hook-form
```

Use for:

* student registration;
* HR vacancy creation;
* HR profile;
* support tickets;
* admin forms.

When to install:

Install early in frontend work.

Must be combined with Zod.

---

## 17. colinhacks/zod

Repository:

```txt
colinhacks/zod
```

Use for:

* form validation;
* API input validation on frontend;
* shared schemas if practical.

When to install:

Install with React Hook Form.

Important:

Backend must still validate independently.

---

## 18. lucide-icons/lucide

Repository:

```txt
lucide-icons/lucide
```

Use for:

* icons;
* navigation icons;
* vacancy badges;
* HR actions;
* admin actions.

When to install:

Install with UI system.

---

## 19. recharts/recharts

Repository:

```txt
recharts/recharts
```

Use for:

* admin analytics;
* HR analytics later;
* charts for registrations, applications, revenue.

When to install:

Not needed for P0 MVP.

Install at P1/P2 analytics stage.

---

## 20. storybookjs/storybook

Repository:

```txt
storybookjs/storybook
```

Use for:

* component documentation;
* visual testing;
* isolated UI states.

When to install:

Only if UI grows and needs component discipline.

Not needed for first 7-day MVP.

---

# 5. Additional repositories to consider

These are optional. Do not install unless there is a specific task.

## UI alternatives

Only use these if we decide not to use shadcn/ui.

```txt
tailwindlabs/headlessui
daisyui/daisyui
heroui-inc/heroui
chakra-ui/chakra-ui
mantinedev/mantine
```

Decision:

For this project, prefer shadcn/ui. Do not mix many UI libraries.

## Design system references

Use as reference only:

```txt
calcom/cal.com
cosscom/coss
origin-space/originui
serafimcloud/21st
```

Do not install full design systems from these repositories.

## AI browser automation

Optional:

```txt
browser-use/browser-use
browserbase/stagehand
browserbase/mcp-server-browserbase
```

Use only if Playwright MCP is not enough.

For this project, Playwright MCP is preferred.

## MCP collections

Reference only:

```txt
modelcontextprotocol/servers
punkpeye/awesome-mcp-servers
github/github-mcp-server
supabase-community/supabase-mcp
mendableai/firecrawl-mcp-server
```

Do not install MCP servers unless the task requires them.

## Figma-related MCP

Use only if we start working from Figma designs:

```txt
GLips/Figma-Context-MCP
sonnylazuardi/cursor-talk-to-figma-mcp
```

Not needed for current MVP unless Figma designs appear.

## Web scraping / reference collection

Optional:

```txt
firecrawl/firecrawl
BuilderIO/gpt-crawler
```

Use only for collecting competitor/reference pages or documentation.

Not needed for core MVP.

## Agent collections

Reference only:

```txt
contains-studio/agents
coleam00/ottomator-agents
hesreallyhim/awesome-claude-code
```

Do not install unknown agent collections into the project.

Use them only as inspiration for custom agents.

## Coding agents

External tools, not project dependencies:

```txt
Aider-AI/aider
continuedev/continue
RooVetGit/Roo-Code
cline/cline
OpenHands-AI/OpenHands
```

Use outside project if needed.

Do not add these as runtime dependencies.

---

# 6. Recommended setup by task

## Task: create Mini App frontend

Allowed tools:

```txt
Telegram-Mini-Apps/tma.js
Telegram-Mini-Apps/reactjs-template
shadcn-ui/ui
tailwindcss
radix-ui/primitives
react-hook-form
zod
tanstack/query
lucide-icons/lucide
```

Do:

1. Build mobile-first layout.
2. Use Telegram theme params.
3. Use shadcn components.
4. Keep screens simple.
5. Add loading and empty states.

Do not:

1. Add multiple UI kits.
2. Add complex animation libraries before core flow works.
3. Trust frontend auth state.
4. Show HR contacts to students.

---

## Task: create vacancy feed

Allowed tools:

```txt
shadcn-ui/ui
tanstack/query
lucide-icons/lucide
```

Must implement:

1. Vacancy list.
2. Vacancy card.
3. Promoted vacancy styling.
4. Free view counter.
5. Paywall after 3 opened vacancies.
6. Filters.

Must test:

1. Guest can open 3 vacancy cards.
2. Guest cannot open 4th without paywall.
3. Guest cannot apply.
4. Active student can apply.

---

## Task: create student registration

Allowed tools:

```txt
react-hook-form
zod
shadcn-ui/ui
```

Must include fields:

1. First name.
2. Last name.
3. Phone.
4. Email.
5. Telegram username.
6. University.
7. Course.
8. Speciality.
9. Preferred job types.
10. Preferred schedule.
11. Preferred districts.
12. Experience text.
13. Consent checkbox.

Must not collect:

```txt
student bank details
```

Bank details are not part of MVP.

---

## Task: create balance and subscription

Allowed tools:

```txt
shadcn-ui/ui
tanstack/query
YooKassa backend integration
```

Must implement:

1. Balance screen.
2. Top-up options.
3. Custom amount.
4. Monthly tariff activation.
5. Payment history.
6. Refund request ticket.

Must enforce on backend:

1. No active access without successful payment.
2. Webhook idempotency.
3. Balance transaction ledger.
4. Subscription expiration.

---

## Task: create HR vacancy creation

Allowed tools:

```txt
react-hook-form
zod
shadcn-ui/ui
```

Must include:

1. Vacancy title.
2. Company.
3. Category.
4. Job type.
5. Schedule.
6. Salary.
7. District.
8. Address.
9. Work format.
10. Description.
11. Responsibilities.
12. Requirements.
13. Conditions.
14. Experience required.
15. Photo optional.
16. Hidden HR contacts.

Must implement:

1. Payment for publishing.
2. Status moderation.
3. AI moderation placeholder.
4. Active publication after approval.

---

## Task: create applications flow

Allowed tools:

```txt
shadcn-ui/ui
tanstack/query
aiogram notifications
```

Must enforce:

1. Student can apply only with active subscription.
2. Student never sees HR contacts.
3. HR sees application without student contacts before acceptance.
4. HR sees student contacts only after accepting.
5. Student gets notification when HR accepts.

Must test:

1. Student applies.
2. Student returns to home.
3. HR sees application.
4. HR cannot see contacts before accept.
5. HR accepts.
6. HR sees contacts.
7. Student still does not see HR contacts.

---

## Task: create Telegram bot

Allowed tools:

```txt
aiogram/aiogram
```

Must implement:

Student:

1. /start
2. Open Mini App
3. Balance
4. Applications
5. Support

HR:

1. Create vacancy
2. My vacancies
3. Applications
4. Accept application
5. Reject application
6. Complain

Admin:

1. Grant HR access
2. Block HR
3. Mute student
4. Review complaints
5. Review moderation queue

---

## Task: create admin panel

Allowed tools:

```txt
shadcn-ui/ui
tanstack/query
tanstack/table only if needed
```

Must include:

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

MVP can use simple lists instead of advanced tables.

---

## Task: browser testing

Allowed tools:

```txt
microsoft/playwright
microsoft/playwright-mcp
```

Must test mobile viewports:

```txt
390x844
393x852
414x896
430x932
```

Critical E2E scenarios:

1. Guest preview limit.
2. Paywall.
3. Registration.
4. Mock payment.
5. Active subscription.
6. Application creation.
7. HR acceptance.
8. Contacts visibility rules.
9. Vacancy creation.
10. Admin HR role grant.

---

# 7. Dependency policy

Before installing a dependency, Codex must output:

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
Alternative considered: Manual useState forms, but this would be more error-prone.
Security notes: Validation is duplicated on backend; frontend validation is UX only.
Files affected: apps/web/package.json, registration form, vacancy form.
Test plan: Submit valid and invalid forms, verify Zod errors.
```

---

# 8. Forbidden actions

Do not:

1. Install all repositories from this document.
2. Replace project architecture without asking.
3. Add a second UI framework if shadcn/ui is already used.
4. Add a second bot framework if aiogram is already used.
5. Add a second backend framework if FastAPI is already used.
6. Add analytics SaaS before MVP flow works.
7. Add auth providers beyond Telegram unless explicitly requested.
8. Add VK auth in P0.
9. Add student bank details in P0.
10. Show HR contacts to students.
11. Show student contacts to HR before acceptance.
12. Trust frontend role state.
13. Trust frontend payment state.
14. Activate subscription without payment webhook.
15. Make refund automatic in MVP.
16. Build map view in P0.
17. Build complex rating system in P0.
18. Build full CRM in P0.

---

# 9. Suggested project files

Create or update:

```txt
AGENTS.md
docs/spec.md
docs/codex-repo-tooling.md
docs/security-rules.md
docs/test-scenarios.md
docs/ui-rules.md
```

`AGENTS.md` must reference this file:

```md
Before adding dependencies, read docs/codex-repo-tooling.md.
Do not install repositories blindly.
Use the dependency policy described there.
```

---

# 10. MVP definition of done

The MVP is done only when this flow works:

1. HR gets access.
2. HR creates vacancy.
3. HR pays for vacancy.
4. Vacancy passes moderation.
5. Guest opens Mini App.
6. Guest views 3 vacancies.
7. Guest hits paywall.
8. Guest registers as student.
9. Student tops up balance.
10. Student gets monthly access.
11. Student applies to vacancy.
12. Student returns to home.
13. HR receives application.
14. HR sees no contacts before accepting.
15. HR accepts application.
16. HR sees student contacts.
17. Student never sees HR contacts.
18. Admin can inspect users, HR, vacancies, payments, and complaints.

If any contact visibility rule is broken, the task is not done.
