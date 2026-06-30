# Deployment Runbook

This runbook describes how to deploy the V1.0 MVP stack with PostgreSQL,
FastAPI, and the Vue/Nginx frontend.

## Environment Variables

Copy `.env.example` to `.env` before running Docker Compose. For any shared or
production-like environment, change these values first:

- `JWT_SECRET_KEY`: must not use `change-me-in-production`.
- `POSTGRES_PASSWORD`: must be unique per environment.
- `APP_ENV`: use `production` for deployed environments.
- `DEBUG`: use `false` outside local development.
- `DATABASE_POOL_SIZE` and `DATABASE_MAX_OVERFLOW`: tune for the database size.
- `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`: configure only when
  using a real OpenAI-compatible provider.
- `BACKEND_CORS_ORIGINS`: include only trusted frontend origins.

## Docker Compose Deployment

Start the full stack from the repository root:

```bash
docker compose up -d --build
```

Services:

- `postgres`: PostgreSQL 16 with persistent `postgres_data` volume.
- `backend`: FastAPI app exposed on `${BACKEND_PORT:-8000}`.
- `frontend`: Nginx static frontend exposed on `${FRONTEND_PORT:-8080}`.

Nginx proxies `/api/` to `backend:8000` and serves Vue Router history fallback
with `try_files $uri $uri/ /index.html`.

## PostgreSQL Initialization

The compose database URL is:

```text
postgresql+psycopg://ai_ecommerce:ai_ecommerce_password@postgres:5432/ai_ecommerce
```

Initialize demo data explicitly:

```bash
docker compose exec backend python scripts/init_db.py --reset
```

Do not automate `--reset` in production. It drops all tables before recreating
demo data.

## Alembic

For production schema changes, prefer Alembic:

```bash
docker compose exec backend alembic upgrade head
```

Current V1.0 still keeps `scripts/init_db.py` for demo and local development.
Future production changes should add migration revisions before deployment.

## Health Checks

Backend health:

```bash
curl http://127.0.0.1:8000/api/health
```

Frontend:

```bash
curl http://127.0.0.1:8080/
```

Compose service status:

```bash
docker compose ps
```

## Logs

Backend logs:

```bash
docker compose logs -f backend
```

Frontend logs:

```bash
docker compose logs -f frontend
```

PostgreSQL logs:

```bash
docker compose logs -f postgres
```

## Production Safety Checklist

- Replace default `JWT_SECRET_KEY`.
- Replace default `POSTGRES_PASSWORD`.
- Keep `.env` out of git.
- Use PostgreSQL for deployed environments.
- Do not run `python scripts/init_db.py --reset` against real data.
- Restrict `BACKEND_CORS_ORIGINS`.
- Configure backup and restore for the Postgres volume.
- Review audit logs after login, review, ticket, knowledge, and Agent actions.

## Troubleshooting

- Backend cannot connect to database: run `docker compose ps` and check the
  `postgres` healthcheck.
- Frontend returns 404 on refresh: verify `frontend/nginx.conf` contains
  `try_files $uri $uri/ /index.html`.
- API calls fail through frontend: verify `/api/` proxy configuration and that
  `backend` is healthy.
- Login fails: initialize demo data or check the seeded demo accounts.
- Schema is missing: run Alembic migrations or the explicit demo init command.
