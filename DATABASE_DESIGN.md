# Database Design

## Current Scope

The backend uses SQLAlchemy ORM models in `backend/app/models/entities.py`.
Local development keeps SQLite support for fast demo startup, while production
deployments should use PostgreSQL through `DATABASE_URL`.

## Database URLs

- Local SQLite: `sqlite:///./data/app.db`
- PostgreSQL: `postgresql+psycopg://user:password@postgres:5432/ai_ecommerce_agent`

`backend/app/database.py` builds engine options by database type:

- SQLite keeps `check_same_thread=False` for local FastAPI and test usage.
- PostgreSQL enables `pool_pre_ping`, `DATABASE_POOL_SIZE`, and
  `DATABASE_MAX_OVERFLOW`.

## Core Tables

- `users`: demo users and future backend operators.
- `products`: product catalog and after-sale policy text.
- `orders`: order, payment, logistics, and after-sale status.
- `sessions` and `messages`: customer service conversations.
- `knowledge_documents` and `knowledge_chunks`: current keyword RAG storage.
- `agent_runs` and `agent_node_logs`: Agent execution and node-level logs.
- `reply_suggestions`: AI-generated reply drafts.
- `review_tasks`: human review tasks for risky replies or complaints.
- `tickets`: after-sale tickets.

## Index Strategy

Single-column indexes already cover common filters such as order number, user,
status, ticket type, review status, and Agent run status.

Additional V1.0 composite/high-frequency indexes:

- `ix_messages_session_created_at`: message timeline queries.
- `ix_agent_node_logs_run_node`: Agent run node log lookup.
- `ix_tickets_status_assignee`: workbench filters by ticket status and owner.
- `ix_tickets_created_at`: ticket ordering and dashboard queries.

## Alembic Migration Strategy

Alembic scaffold lives under `backend/alembic/`.

Recommended production workflow:

```bash
cd backend
alembic revision --autogenerate -m "describe schema change"
alembic upgrade head
```

`backend/scripts/init_db.py` remains available for local demo initialization and
tests. Do not use `python scripts/init_db.py --reset` against production data.

## Why 生产环境不建议只使用 SQLite

生产环境不建议只使用 SQLite because it has limited concurrent write capacity,
does not provide the same operational tooling as PostgreSQL, is awkward for
multi-instance deployments, and makes backup, restore, permission management,
monitoring, and schema migration risk harder to control.

SQLite is still useful for local demos and quick development. PostgreSQL should
be the default production database for the online MVP.

