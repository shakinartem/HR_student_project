# P0 Scope

## Goal

Build only the minimum working end-to-end marketplace flow:

HR creates paid vacancy -> vacancy appears in feed -> guest sees 3 vacancies -> student registers and pays -> student applies -> HR accepts -> HR sees student contacts.

## P0 features

- Telegram auth
- Student role by default
- HR role granted by admin
- Vacancy feed
- Guest limit: 3 vacancy cards
- Paywall after 3 vacancy cards
- Student registration
- Balance top-up
- Monthly access activation
- Student application
- Student never sees HR contacts
- HR application list
- HR accepts application
- HR sees student contacts only after accept
- HR creates vacancy
- HR pays for vacancy
- Vacancy moderation placeholder
- Admin can grant HR role
- Admin can inspect users, vacancies, applications, payments
- Basic event logging
- Critical tests

## Not P0

- Map
- Complex employer rating
- VK auth
- Student bank details
- Automatic refunds
- Full CRM
- Advanced HR analytics
- AI competitor analytics
- Public landing
- Complex referral competitions
- Multiple UI frameworks
- Multiple bot frameworks
- Mobile app outside Telegram