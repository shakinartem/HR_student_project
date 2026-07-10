# Vercel Deployment Guide

## Настройка деплоя Mini App на Vercel

### 1. Подключение репозитория

1. Зайдите на https://vercel.com и авторизуйтесь
2. Нажмите "New Project" → "Import Git Repository"
3. Выберите репозиторий `shakinartem/HR_student_project`
4. Настройки сборки:

**Framework Preset:** Vite
**Root Directory:** `apps/web`
**Build Command:** `npm run build`
**Output Directory:** `dist`

### 2. Переменные окружения (Environment Variables)

В настройках проекта на Vercel добавьте:

| Name | Value |
|------|-------|
| VITE_API_BASE_URL | URL вашего backend API (например https://your-backend.vercel.app или ваш VPS) |
| VITE_TELEGRAM_WEBAPP_URL | URL вашего Mini App на Vercel (автоматически) |
| VITE_GUEST_FREE_VACANCY_VIEWS | 3 |
| VITE_ENABLE_MOCK_PAYMENT_CONFIRM | true |

⚠️ **Важно:** Backend нужно разместить отдельно (VPS, Railway, Render, Fly.io и т.д.), так как Vercel Serverless Functions не подходят для долгоживущих подключений к PostgreSQL.

### 3. Альтернатива: Монорепозийс на Vercel

Если хотите деплоить frontend и backend вместе:

1. Root Directory оставьте пустым (корень репозитория)
2. Создайте `vercel.json` в корне с конфигурацией для обоих приложений

### 4. Проверка после деплоя

После успешного деплоя:

1. Откройте URL приложения в браузере
2. Проверьте, что лента вакансий загружается (GET /api/vacancies)
3. Откройте 3 вакансии → должен появиться paywall
4. API должен отвечать за API_BASE_URL

### 5. Требования к backend

Backend нужно запустить где-то отдельно с:

- PostgreSQL (можно использовать Supabase, Neon, или VPS)
- Доступность по HTTPS для Telegram Mini App
- CORS настроен на ваш Vercel домен

Примеры бесплатных backend хостингов:
- Railway.app
- Render.com
- Fly.io
- VPS с Docker