# API Contracts

Task 1 note:

- this file describes target API behavior
- Task 1 does not implement these contracts yet
- any future stubs must stay clearly marked `TODO`

## Contact visibility rule

All API responses must follow:

- student vacancy responses never include HR contacts
- student application responses never include HR contacts
- HR application responses include student contacts only if application.status == accepted
- admin responses may include contacts

## Frontend decision

For P0, the Mini App frontend uses Vite React. API contracts remain backend-driven regardless of frontend choice.

## Vacancy list item

```json
{
  "id": "uuid",
  "title": "Официант вечерняя смена",
  "company_name": "Verhoff",
  "category": "restaurant",
  "job_type": "shift",
  "salary_text": "2500 ₽/смена",
  "district": "Центр",
  "schedule": "вечер",
  "is_promoted": false,
  "published_at": "2026-07-01T10:00:00Z"
}
Vacancy detail for student

Forbidden fields:

hr_phone
hr_email
hr_telegram
contact_phone
contact_email
contact_telegram
Application for student
{
  "id": "uuid",
  "vacancy_id": "uuid",
  "vacancy_title": "Официант",
  "company_name": "Verhoff",
  "status": "sent",
  "created_at": "2026-07-01T10:00:00Z"
}
Application for HR before accept
{
  "id": "uuid",
  "status": "sent",
  "student": {
    "first_name": "Иван",
    "university": "СГТУ",
    "course": 2,
    "speciality": "Информатика",
    "experience_text": "Работал официантом 2 месяца"
  },
  "contacts": null
}
Application for HR after accept
{
  "id": "uuid",
  "status": "accepted",
  "student": {
    "first_name": "Иван",
    "university": "СГТУ",
    "course": 2,
    "speciality": "Информатика",
    "experience_text": "Работал официантом 2 месяца"
  },
  "contacts": {
    "phone": "+79990000000",
    "email": "student@example.com",
    "telegram_username": "student_username"
  }
}
