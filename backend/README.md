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

Health check:

```bash
curl http://127.0.0.1:8000/api/health
```

Expected response:

```json
{"status":"ok"}
```

Run tests:

```bash
cd backend
python -m pytest
```

## Current API Groups

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
