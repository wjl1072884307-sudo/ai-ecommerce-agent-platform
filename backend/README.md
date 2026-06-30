# Backend

FastAPI backend for the AI ecommerce customer service and after-sales Agent platform.

## Setup

Install dependencies:

```bash
cd backend
python -m pip install -r requirements.txt
```

Run local server:

```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Initialize local database with demo data:

```bash
cd backend
python scripts/init_db.py --reset
```

SQLite remains the default local development database. PostgreSQL is supported
for production-like runs by setting `DATABASE_URL`:

```bash
set DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/ai_ecommerce_agent
set DATABASE_POOL_SIZE=5
set DATABASE_MAX_OVERFLOW=10
```

For production schema changes, use Alembic instead of `Base.metadata.create_all()`:

```bash
cd backend
alembic upgrade head
```

Do not run `python scripts/init_db.py --reset` against production data.

## Docker

Build the backend image from the repository root:

```bash
docker build -t ai-ecommerce-agent-backend ./backend
```

Run the full MVP stack from the repository root:

```bash
docker compose up -d --build
```

Initialize demo data explicitly:

```bash
docker compose exec backend python scripts/init_db.py --reset
```

The backend container reads configuration from environment variables supplied
by `docker-compose.yml`. In compose, `DATABASE_URL` points to PostgreSQL:

```text
postgresql+psycopg://ai_ecommerce:ai_ecommerce_password@postgres:5432/ai_ecommerce
```

Do not automate `--reset` for production deployments.

Health check:

```bash
curl http://127.0.0.1:8000/api/health
```

Expected response:

```json
{"status":"ok"}
```

Default demo backend accounts:

| Username | Password | Role |
| --- | --- | --- |
| admin_demo | admin123456 | admin |
| reviewer_demo | reviewer123456 | reviewer |
| agent_demo | agent123456 | agent |
| viewer_demo | viewer123456 | viewer |

Run tests:

```bash
cd backend
python -m pytest
```

## Current API Groups

- POST /api/auth/login
- GET /api/auth/me
- GET /api/products
- GET /api/products/{product_id}
- POST /api/products
- PUT /api/products/{product_id}
- GET /api/orders
- GET /api/orders/{order_id}
- GET /api/orders/by-number/{order_no}
- GET /api/users/{user_id}/orders
- GET /api/sessions
- POST /api/sessions
- GET /api/sessions/{session_id}
- GET /api/sessions/{session_id}/messages
- POST /api/sessions/{session_id}/messages
- GET /api/knowledge/documents
- POST /api/knowledge/documents
- GET /api/knowledge/documents/{document_id}
- PUT /api/knowledge/documents/{document_id}
- POST /api/knowledge/documents/{document_id}/rebuild-chunks
- GET /api/knowledge/search
- POST /api/agent/runs
- GET /api/agent/runs
- GET /api/agent/runs/{run_id}
- GET /api/agent/runs/{run_id}/node-logs
- GET /api/dashboard/summary
- GET /api/dashboard/intent-stats
- GET /api/dashboard/ticket-stats
- GET /api/review-tasks
- POST /api/review-tasks/{task_id}/approve
- POST /api/review-tasks/{task_id}/reject
- GET /api/tickets
- POST /api/tickets/{ticket_id}/status

## Agent MVP Demo

After database initialization, the demo message is available at session 1 and message 1.

```bash
curl -X POST http://127.0.0.1:8000/api/agent/runs ^
  -H "Content-Type: application/json" ^
  -d "{\"session_id\":1,\"message_id\":1}"
```

The expected result includes:

- intent: return_request
- reply_suggestion
- pending review_task
- return ticket
- queryable node logs
