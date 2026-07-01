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

## V1.1 Conversation Center Draft

V1.1 does not introduce a second physical database for the conversation center.
Conversation data, customer data, orders, Agent runs, review tasks, tickets, and
audit logs should remain in the same business database.

Reasons:

- Conversation handling often needs to write messages, Agent runs, reply
  suggestions, review tasks, tickets, and audit records in one business flow.
- Keeping these records in one database preserves simpler transactional
  consistency for the MVP.
- A second database would add cross-database joins, deployment complexity,
  backups, migrations, and operational risk before the project needs a
  standalone IM storage layer.

### Identity Boundaries

`customer_id` must not be used as the primary key for conversations or messages.

Recommended identity model:

- `customers.id`: identifies an ecommerce customer. This can be added in V1.1
  while keeping backend operators in `users`.
- `sessions.id`: identifies one customer-service conversation. The existing
  table name can be kept for compatibility before any future rename to
  `conversations`.
- `messages.id`: identifies one chat message.
- `sessions.customer_id`: nullable foreign key to `customers.id`.
- `sessions.visitor_id`: nullable anonymous visitor identifier for customers
  who are not logged in or not yet bound to a customer record.

This supports:

- One customer owning many sessions.
- One session containing many messages.
- A session existing without a customer record.
- Anonymous visitors starting pre-sales or suspected after-sales conversations.

### Planned Session Fields

The existing `sessions` table can be expanded in V1.1 instead of creating a new
table immediately.

Planned fields:

- `customer_id`: nullable customer reference.
- `visitor_id`: nullable anonymous visitor identifier.
- `channel`: source channel such as `web`, `admin_demo`, `mock`, or `api`.
- `conversation_type`: `pre_sales`, `after_sales`, `logistics`, `complaint`,
  `invoice`, or `other`.
- `intent`: latest detected intent.
- `status`: `open`, `pending_human`, `resolved`, or `closed`.
- `priority`: `low`, `medium`, or `high`.
- `bound_order_id`: nullable main matched order.
- `bound_product_id`: nullable main matched product.
- `requires_human`: whether the conversation needs human handling.
- `summary`: short conversation summary for queue display.
- `last_message_at`: latest message timestamp.

### Planned Message Fields

The existing `messages` table should keep `messages.id` as the primary key.

Planned additions:

- `language`: `zh`, `en`, or `unknown`; derived from the customer message.
- `message_type`: keep existing text values and extend with values such as
  `agent_reply`, `handoff_notice`, `order_bind_request`, `ticket_created`, and
  `review_required`.
- `metadata_json`: continue using JSON metadata for lightweight links such as
  `run_id`, `reply_suggestion_id`, `risk_level`, and source document ids.

### Anonymous Visitor Flow

Anonymous visitors should not be forced into the backend `users` table.

Recommended behavior:

- Pre-sales questions can be answered without a customer record.
- Suspected after-sales questions should ask for order number, phone number,
  purchase account, product name, purchase time, and issue evidence.
- The Agent must not promise refunds, returns, replacement, or compensation
  without an order or customer binding.

### Right Panel Data Source

The conversation center right panel should read from existing and planned
business records instead of duplicating chat content:

- session/customer/visitor fields for identity context.
- orders/products for purchase context.
- agent_runs and agent_node_logs for execution context.
- knowledge source metadata for RAG evidence.
- review_tasks and tickets for human workflow state.
