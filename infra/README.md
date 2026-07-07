# Infrastructure Notes

This folder now holds deployment-adjacent files for the local production-like Docker flow.

## Service layout

- `postgres`
  Internal-only PostgreSQL service on the Compose network.
- `backend`
  FastAPI API exposed on `http://localhost:8000`.
- `web`
  Built Vite static app exposed on `http://localhost:8080`.
- `bot`
  Background aiogram service on the Compose network.
  It is placed behind the optional `bot` profile so placeholder bot tokens do not block default local verification.

No reverse proxy is used in Task 17.

If `8000` is already occupied on the host, set `BACKEND_HOST_PORT=8001` in `.env.compose`, then also update:

- `BACKEND_BASE_URL=http://localhost:8001`
- `WEB_VITE_API_BASE_URL=http://localhost:8001`

## Files

- `../docker-compose.yml`
- `../.env.compose.example`
- `web_static_server.py`

## Local compose flow

1. Copy the example env file:

```powershell
Copy-Item .env.compose.example .env.compose
```

2. Build the images:

```powershell
docker compose --env-file .env.compose build
```

3. Start Postgres first:

```powershell
docker compose --env-file .env.compose up -d postgres
```

4. Run migrations:

```powershell
docker compose --env-file .env.compose run --rm backend alembic upgrade head
```

5. Seed the database:

```powershell
docker compose --env-file .env.compose run --rm backend python scripts/seed_data.py
```

6. Start backend and web:

```powershell
docker compose --env-file .env.compose up -d backend web
```

7. Check health:

- Backend: `http://localhost:8000/health`
- Web: `http://localhost:8080/health`
- App: `http://localhost:8080`

If `BACKEND_HOST_PORT` is changed, use that host port for the backend health check instead.

8. Start the bot only after replacing the placeholder bot token:

```powershell
docker compose --env-file .env.compose --profile bot up -d bot
```

## URL rules

- Public web URL: `http://localhost:8080`
- Public backend URL: `http://localhost:8000`
- Public backend host port is configurable with `BACKEND_HOST_PORT`
- Internal Postgres hostname: `postgres`
- Internal backend hostname for the bot: `backend`
- Bot backend base URL env: `BOT_BACKEND_BASE_URL=http://backend:8000`

## Deferred production items

- reverse proxy
- HTTPS
- domain-based routing
- production webhook routing
