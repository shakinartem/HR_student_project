# UI Rules

## General direction

- Build mobile-first for Telegram Mini App usage.
- Prefer simple, fast, touch-friendly layouts.
- Use one UI system only: `shadcn/ui + Tailwind CSS + Radix primitives`.
- Keep loading, empty, and error states explicit.
- Keep text concise and action-oriented.

## Navigation

Student primary navigation:

- Feed
- Applications
- Balance
- Profile

HR primary navigation:

- Vacancies
- Applications
- Create
- Company

Admin primary navigation:

- Users
- Vacancies
- Complaints
- Payments
- Stats

## Frontend decision

For P0, `apps/web` uses Vite React.

Next.js is deferred until the project needs public SEO pages, SSR, or a separate public web surface.

## Task 1 boundary

Task 1 does not implement actual UI screens. It only establishes structure and documentation for future UI work.

## Job Hub visual identity

The product name is “Джоб Хаб”.

Use a bold black/orange/white visual identity:
- Roboto font
- black or near-black backgrounds
- orange primary accents and CTAs
- white text and high-contrast cards
- mobile-first Telegram Mini App layout

The style may be inspired by recognizable black/orange hub-style branding, but the app must not copy Pornhub logos, exact layouts, trademarks, or adult visual references.

Forbidden:
- adult imagery
- Pornhub logo/assets
- explicit adult references
- UI text mentioning Pornhub
- designs that make the service look like an adult product

The product must feel like a bold student job marketplace, not an adult website.