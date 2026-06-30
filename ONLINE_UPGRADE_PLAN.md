# Online Upgrade Plan

This document records the V1.0 phase order, rollback strategy, and validation
commands. Do not merge all phases as one unreviewable change; each phase should
be independently verifiable.

## Phase 1: Production Configuration

Scope: central settings module, `.env.example`, CORS, JWT, database, LLM, and
logging configuration.

Rollback: revert config module and restore previous direct environment reads.

Validation:

```bash
python -m pytest backend/tests/test_config.py -v
```

## Phase 2: Database Upgrade

Scope: PostgreSQL URL support, SQLAlchemy engine options, indexes, Alembic
scaffold.

Rollback: restore SQLite-only database configuration and remove new migration
scaffold from deployment paths.

Validation:

```bash
python -m pytest backend/tests/test_database_config.py backend/tests/test_database_engine_config.py backend/tests/test_database_indexes.py backend/tests/test_alembic_setup.py -v
```

## Phase 3: Authentication and RBAC

Scope: password hashing, JWT login, current user dependency, role checks.

Rollback: remove protected dependencies from routes and restore demo-only access.

Validation:

```bash
python -m pytest backend/tests/test_auth_api.py backend/tests/test_rbac.py -v
```

## Phase 4: LLM Provider Abstraction

Scope: mock provider, OpenAI-compatible provider boundary, timeout and fallback.

Rollback: switch `LLM_PROVIDER=mock` and revert provider factory changes.

Validation:

```bash
python -m pytest backend/tests/test_llm_provider.py backend/tests/test_openai_compatible_provider.py backend/tests/test_agent_llm_fallback.py -v
```

## Phase 5: RAG Retrieval Upgrade

Scope: retriever interface, `KeywordRetriever`, `VectorRetriever` placeholder,
structured sources.

Rollback: route knowledge search and Agent retrieval back to keyword logic.

Validation:

```bash
python -m pytest backend/tests/test_rag_retriever.py backend/tests/test_rag_api_integration.py backend/tests/test_agent_rag_sources.py -v
```

## Phase 6: Agent Pipeline Optimization

Scope: node context contract, failure response, high-risk policy boundaries.

Rollback: restore previous Agent pipeline and node behavior.

Validation:

```bash
python -m pytest backend/tests/test_agent_context_contract.py backend/tests/test_agent_failure_response.py backend/tests/test_agent_risk_policy.py -v
```

## Phase 7: Ticket State Machine

Scope: status transition validation, status logs, claim/assignment behavior.

Rollback: restore direct ticket status updates and remove state-machine checks.

Validation:

```bash
python -m pytest backend/tests/test_ticket_state_machine.py backend/tests/test_ticket_status_logs.py backend/tests/test_ticket_assignment.py -v
```

## Phase 8: Logging and Audit

Scope: Python logging config, audit log model/service/API, critical business
audit integration.

Rollback: remove audit writes from routes and hide audit route.

Validation:

```bash
python -m pytest backend/tests/test_logging_config.py backend/tests/test_audit_log.py backend/tests/test_business_audit_integration.py -v
```

## Phase 9: Frontend Adaptation

Scope: login page, token injection, role-aware menus/buttons, ticket timeline,
Agent log readability.

Rollback: restore previous frontend router/layout/views and keep backend RBAC.

Validation:

```bash
cd frontend
npm run build
```

## Phase 10: Docker Deployment

Scope: backend Dockerfile, frontend Dockerfile, Nginx config, docker-compose.

Rollback: remove Docker files and continue local process startup.

Validation:

```bash
python -m pytest backend/tests/test_docker_deployment.py -v
docker compose config
```

## Phase 11: Documentation Upgrade

Scope: README, deployment runbook, upgrade plan, API design, database design,
Agent workflow, and RAG upgrade plan.

Rollback: restore previous docs if inaccurate; no runtime rollback is required.

Validation:

```bash
python -m pytest backend/tests/test_phase11_documents.py -v
```
