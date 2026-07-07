FROM node:20-alpine AS build

WORKDIR /workspace/apps/web

ARG VITE_APP_ENV=production
ARG VITE_API_BASE_URL=http://localhost:8000
ARG VITE_TELEGRAM_WEBAPP_URL=http://localhost:8080
ARG VITE_GUEST_FREE_VACANCY_VIEWS=3
ARG VITE_ENABLE_MOCK_PAYMENT_CONFIRM=true

ENV VITE_APP_ENV=${VITE_APP_ENV} \
    VITE_API_BASE_URL=${VITE_API_BASE_URL} \
    VITE_TELEGRAM_WEBAPP_URL=${VITE_TELEGRAM_WEBAPP_URL} \
    VITE_GUEST_FREE_VACANCY_VIEWS=${VITE_GUEST_FREE_VACANCY_VIEWS} \
    VITE_ENABLE_MOCK_PAYMENT_CONFIRM=${VITE_ENABLE_MOCK_PAYMENT_CONFIRM}

COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci

COPY apps/web/ ./
RUN npm run build

FROM python:3.12-slim AS runtime

WORKDIR /srv/web

COPY infra/web_static_server.py /srv/web/server.py
COPY --from=build /workspace/apps/web/dist /srv/web/dist

EXPOSE 8080

CMD ["python", "server.py"]
