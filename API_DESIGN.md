# API Design

The backend exposes a single FastAPI application under `/api`. Swagger docs are
available at `/docs` when the backend is running.

## Public Endpoints

- `GET /api/health`: health check.
- `POST /api/auth/login`: returns a bearer token for valid credentials.

## Protected Endpoints

All other application endpoints require:

```text
Authorization: Bearer <token>
```

Current protected groups:

- `/api/auth/me`
- `/api/products`
- `/api/orders`
- `/api/sessions`
- `/api/knowledge`
- `/api/agent`
- `/api/dashboard`
- `/api/review-tasks`
- `/api/tickets`
- `/api/audit-logs`

## Role Matrix

| Role | Read Dashboard/Data | Run Agent | Review Tasks | Handle Tickets | Manage Knowledge | Audit Logs |
| --- | --- | --- | --- | --- | --- | --- |
| `admin` | yes | yes | yes | yes | yes | yes |
| `reviewer` | yes | no | yes | yes | no | no |
| `agent` | yes | yes | no | own/assigned workflow | no | no |
| `viewer` | yes | no | no | read only | no | no |

Backend RBAC is the security boundary. Frontend role filtering is only a user
experience improvement.

## Endpoint Groups

### Auth

- `POST /api/auth/login`
- `GET /api/auth/me`

### Products

- `GET /api/products`
- `GET /api/products/{product_id}`
- `POST /api/products`
- `PUT /api/products/{product_id}`
- `DELETE /api/products/{product_id}`

### Orders

- `GET /api/orders`
- `GET /api/orders/{order_id}`
- `GET /api/orders/by-number/{order_no}`
- `GET /api/users/{user_id}/orders`
- `POST /api/orders`
- `PUT /api/orders/{order_id}`
- `DELETE /api/orders/{order_id}`

### Sessions

- `GET /api/sessions`
- `POST /api/sessions`
- `GET /api/sessions/{session_id}`
- `GET /api/sessions/{session_id}/messages`
- `POST /api/sessions/{session_id}/messages`

### Knowledge

- `GET /api/knowledge/documents`
- `POST /api/knowledge/documents`
- `GET /api/knowledge/documents/{document_id}`
- `PUT /api/knowledge/documents/{document_id}`
- `POST /api/knowledge/documents/{document_id}/rebuild-chunks`
- `GET /api/knowledge/search`

### Agent

- `POST /api/agent/runs`
- `GET /api/agent/runs`
- `GET /api/agent/runs/{run_id}`
- `GET /api/agent/runs/{run_id}/node-logs`

### Review, Tickets, Dashboard, Audit

- `GET /api/review-tasks`
- `GET /api/review-tasks/{task_id}`
- `POST /api/review-tasks/{task_id}/approve`
- `POST /api/review-tasks/{task_id}/reject`
- `GET /api/tickets`
- `GET /api/tickets/{ticket_id}`
- `POST /api/tickets/{ticket_id}/claim`
- `POST /api/tickets/{ticket_id}/status`
- `GET /api/tickets/{ticket_id}/status-logs`
- `GET /api/dashboard/summary`
- `GET /api/dashboard/intent-stats`
- `GET /api/dashboard/ticket-stats`
- `GET /api/audit-logs`

## Error Codes

- `400`: invalid business state or invalid transition.
- `401`: missing, invalid, or expired token.
- `403`: authenticated user does not have the required role.
- `404`: requested resource does not exist.
- `409`: concurrent ticket claim or ownership conflict.
- `422`: request validation error from FastAPI/Pydantic.
- `500`: unexpected server error.

## Compatibility Rules

- Keep existing route paths stable for V1.0.
- Prefer additive fields over breaking response shape changes.
- Do not expose password hashes, JWT secrets, LLM API keys, or raw tokens.
