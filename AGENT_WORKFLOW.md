# Agent Workflow

## Pipeline Nodes

The Agent pipeline runs these nodes in order:

1. `receive_message`: loads the session, target message, user id, and recent messages.
2. `classify_intent`: classifies the message intent and confidence.
3. `query_order`: matches the latest or product-related order for the user.
4. `retrieve_knowledge`: calls the configured Retriever and records `knowledge_sources`.
5. `check_policy`: evaluates after-sales policy conditions.
6. `risk_check`: marks review requirements and high-risk actions.
7. `generate_reply`: generates a reply suggestion through the LLM Provider with fallback.
8. `create_review_task`: creates a human review task when risk requires it.
9. `create_ticket`: creates an after-sales ticket when policy requires one.

## Context Contract

`AgentContext` carries state between nodes:

- `session_id`, `message_id`, `run_id`
- `user_id`, `message_content`, `recent_messages`
- `intent`, `confidence`, `extracted_entities`
- `matched_order`, `matched_product`
- `knowledge_chunks`, `knowledge_sources`
- `policy_result`, `risk_result`, `risk_actions`
- `llm_result`
- `reply_suggestion_id`, `review_task_id`, `ticket_id`

Node logs store a sanitized context snapshot before each node runs. The snapshot
must not include JWT secrets, LLM API keys, password hashes, or other sensitive
configuration values.

## Node Logging

Each node writes:

- node name
- status: `success`, `skipped`, or `failed`
- input JSON
- output JSON
- error message
- start time, finish time, and duration

If a node fails, the pipeline stops, sets the run status to `failed`, and returns
`failed_node` plus `partial_context`.

## High-Risk Rules

高风险 actions always require human review. The current high-risk action set is:

- `refund`
- `compensation`
- `close_ticket`
- `modify_order_amount`
- `approve_after_sale`

The Agent is allowed to draft replies, create review tasks, and create tickets.
It is not allowed to directly approve refunds, compensation, order amount
changes, after-sale approval, or ticket closure.

## Failure Response

Agent run responses include:

- `run`
- `reply_suggestion`
- `review_task`
- `ticket`
- `failed_node`
- `partial_context`

Business failures such as a missing session or message are recorded as failed
Agent runs instead of crashing the service.

