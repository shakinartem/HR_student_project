# Current Screens

This document reflects the screens and bot entry points that exist in the repository today.

## Student Mini App

### Feed

Route:
- `/feed`

Shows:
- vacancy cards from the public feed
- guest preview counter
- loading, empty, and error states
- success banner after apply

Rules:
- no HR contacts
- guest can open only 3 unique vacancies before paywall

### Vacancy detail

Route:
- `/vacancies/{id}`

Shows:
- public vacancy information only
- apply CTA
- error state for removed/unavailable vacancies

Rules:
- no HR contacts
- guest apply leads to paywall
- inactive student apply leads to paywall

### Paywall

Route:
- `/paywall`

Reasons:
- `guest-limit`
- `guest-apply`
- `inactive-subscription`

Primary actions:
- open profile
- open balance

### Profile / registration

Route:
- `/profile`

Fields:
- first name
- last name
- phone
- email
- university
- course
- speciality
- preferred job types
- preferred schedule
- preferred districts
- experience text

States:
- guest instruction state outside Telegram
- loading
- save success
- save error

### Balance

Route:
- `/balance`

Shows:
- current balance
- subscription status
- quick top-up presets
- payment creation flow
- mock confirm button when enabled
- ledger-derived transaction history
- payment history

### Applications

Route:
- `/applications`

Shows:
- student applications list
- vacancy title
- company
- status
- created date

Rules:
- never show HR contacts

## HR Mini App

### HR dashboard

Route:
- `/hr`

Shows:
- summary cards
- vacancy list
- applications list
- create vacancy CTA

### Create vacancy

Route:
- `/hr/vacancies/new`
- compatibility alias `/hr/create`

Shows:
- vacancy form
- submit CTA
- submit error state

### HR vacancy detail

Route:
- `/hr/vacancies/{id}`

Shows:
- vacancy publication state
- moderation state
- payment-required state
- mock confirm publication payment flow when enabled

### HR application detail

Route:
- `/hr/applications/{id}`

Shows before accept:
- safe student summary fields
- no phone/email/Telegram username

Shows after accept:
- student contacts only if returned by backend

Compatibility dashboard routes:
- `/hr/vacancies`
- `/hr/applications`
- `/hr/company`

## Admin Mini App

### Admin dashboard

Route:
- `/admin`

Shows:
- cards linking to operational sections
- core counters
- access denied state for non-admins

### Users

Route:
- `/admin/users`

Shows:
- users list
- selected user detail

Actions:
- block / unblock
- mute / unmute

### HR access

Routes:
- `/admin/hr`
- compatibility alias `/admin/hr-access`

Shows:
- HR profiles with user and company context

Actions:
- approve HR
- block HR
- return HR to pending

### Moderation

Route:
- `/admin/moderation`

Shows:
- moderation queue
- moderation reason when available

Actions:
- approve vacancy
- reject vacancy

### Complaints

Route:
- `/admin/complaints`

Shows:
- complaint cards
- reporter, target, linked entity context

Actions:
- move complaint through MVP statuses

### Payments

Route:
- `/admin/payments`

Shows:
- read-only payment list
- amount, status, purpose, linked entity

### Stats

Route:
- `/admin/stats`

Shows:
- total users
- students
- HR users
- active vacancies
- applications
- succeeded payments
- open complaints
- manual review vacancies

## Bot surfaces

### Commands

- `/start`
- `/help`
- `/profile`
- `/balance`
- `/support`

### Guest menu

- Open vacancies
- Register / activate access
- Support

### Student menu

- Open vacancies
- My profile
- My balance
- My applications
- Top up balance
- Support

### HR menu

- Create vacancy
- My vacancies
- Applications
- Support

### Admin menu

- Users
- HR access
- Moderation queue
- Complaints
- Payments
- Stats

### Current bot limitation

Support and non-navigation callbacks are placeholders until dedicated backend-safe bot actions are implemented.
