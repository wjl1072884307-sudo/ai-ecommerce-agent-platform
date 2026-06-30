---
name: ai-ecommerce-online-mvp
description: Use when working on the ai-ecommerce-agent-platform online MVP, TASKS_ONLINE_V1 phases, deployment, database, auth/RBAC, Agent, RAG, audit, frontend, Docker, documentation, or project startup tasks in this repository.
---

# AI Ecommerce Online MVP

## Core Rule

Treat this repository as a staged online-MVP project, not a throwaway demo.
Prefer traceable, phase-scoped, verified work over fast unverified changes.

## Context Files

Read only what the task needs:

- `TASKS_ONLINE_V1.md`: source of phase scope and acceptance criteria.
- `README.md`: startup, demo flow, default accounts, and delivery summary.
- `DEPLOYMENT.md`: Docker/PostgreSQL deployment runbook.
- `ONLINE_UPGRADE_PLAN.md`: phase order, rollback, validation commands.
- `API_DESIGN.md`: endpoint groups, role matrix, error codes.
- `DATABASE_DESIGN.md`: SQLite/PostgreSQL boundary and schema notes.
- `AGENT_WORKFLOW.md`: Agent nodes, context contract, failure behavior.
- `RAG_UPGRADE_PLAN.md`: retriever boundary and V1.1 vector plan.

Do not re-read every large document if a smaller design document covers the
current task.

## Phase Workflow

For `TASKS_ONLINE_V1` phase work:

1. Identify the exact phase and do not expand beyond it.
2. List the likely files and validation commands before editing when scope is broad.
3. Add or update focused tests when behavior is testable.
4. Implement the smallest change that satisfies the phase.
5. Run only phase-targeted tests unless the user asks for full tests.
6. Report unverified items explicitly.

Never claim full-project readiness after only targeted verification.

## Token Discipline

Save context without weakening quality:

- Prefer `rg` and targeted file reads.
- Read summaries/design docs before source files when answering architecture questions.
- Avoid repeatedly explaining stable workflow rules.
- Keep intermediate updates short.
- Final answers should include modified areas, verification commands, and remaining risks.

## Anti-Hallucination Checks

Use evidence for environment-sensitive claims:

| Claim | Required evidence |
| --- | --- |
| Backend is running | `GET /api/health` returns `{"status":"ok"}` |
| Frontend is running | HTTP request to frontend URL returns `200` |
| Docker is available | `docker --version` succeeds |
| Compose config is valid | `docker compose config` succeeds |
| Docker deployment is running | `docker compose ps` plus HTTP health checks |
| Active DB is SQLite | Default/local `DATABASE_URL` or `backend/data/app.db` usage |
| Active DB is PostgreSQL | PostgreSQL `DATABASE_URL` and successful connection |
| Tests pass | Exact command output with pass count |

If evidence is missing, state the item as unverified.

## Database Rules

Runtime uses one database at a time:

- Local/default: SQLite at `backend/data/app.db`.
- Deployment: PostgreSQL through `DATABASE_URL`.

`python scripts/init_db.py --reset` drops and recreates the target database.
Before using it on local SQLite with existing data, back up `backend/data/app.db`.
Never run it against production data unless the user explicitly approves.

Old SQLite files may lack newer columns such as `users.password_hash`. The
correct local-demo fix is to back up and rebuild the demo DB, not to weaken the
models.

## Docker Rules

Do not say Docker deployment is complete unless Docker commands actually run.
If `docker` is unavailable, report that Docker config is prepared but deployment
is unverified.

Expected deployment commands:

```bash
docker compose up -d --build
docker compose exec backend python scripts/init_db.py --reset
```

Production safety: change `JWT_SECRET_KEY` and `POSTGRES_PASSWORD`; do not
automate `--reset`.

## Frontend Rules

For frontend phase work:

- Preserve the Vue 3 + Vite + Naive UI structure.
- Keep role filtering as UX only; backend RBAC remains the security boundary.
- Run `npm.cmd run build` on Windows when PowerShell blocks `npm.ps1`.
- If starting dev server from the sandbox fails to persist, use HTTP checks
  before claiming it is running.

## Backend Rules

For backend phase work:

- Preserve existing route paths unless the phase explicitly requires additions.
- Prefer additive response fields over breaking changes.
- Keep auth/RBAC, audit, ticket state machine, Agent fallback, and RAG retriever
  boundaries intact.
- Critical actions should be auditable: login, review, ticket status/claim,
  knowledge changes, and Agent run trigger.

## Final Response Format

Use this compact structure:

```text
Completed:
- ...

Verified:
- `command`: result

Not verified:
- ...

Notes:
- ...
```

Do not end with vague success claims. Tie every status to evidence.
