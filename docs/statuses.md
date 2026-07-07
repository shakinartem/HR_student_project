# Statuses

## User roles

- student
- hr
- admin
- moderator
- support

## User status

- active
- blocked

## Student mute

Use `mute_until`.
If `mute_until > now`, student cannot apply.

## HR status

- pending
- active
- blocked

Only `active` HR can create vacancies.

## Vacancy status

- draft
- awaiting_payment
- moderation
- manual_review
- active
- rejected
- archived
- expired

Only `active` vacancies appear in student feed.

## Application status

- sent
- viewed
- accepted
- rejected
- complaint
- closed

Student contacts are visible to HR only if application status is `accepted`.

## Payment status

- pending
- succeeded
- canceled
- failed
- refunded

Only `succeeded` payment can create positive balance transaction.

## Subscription status

- active
- expired
- canceled

Student can apply only if subscription status is `active` and `expires_at > now`.

## Complaint status

- open
- in_review
- resolved
- rejected

## Support ticket status

- open
- in_progress
- resolved
- closed

## Moderation result

- approved
- manual_review
- rejected