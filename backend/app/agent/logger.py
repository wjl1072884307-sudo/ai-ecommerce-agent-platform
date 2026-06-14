import json
from collections.abc import Callable
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.agent.types import AgentContext, NodeResult
from app.models import AgentNodeLog


def run_logged_node(
    db: Session,
    context: AgentContext,
    node_name: str,
    input_data: dict[str, Any],
    node_func: Callable[[Session, AgentContext], NodeResult],
) -> NodeResult:
    started_at = datetime.now()
    log = AgentNodeLog(
        run_id=context.run_id,
        node_name=node_name,
        status="running",
        input_json=_json_dumps(input_data),
        started_at=started_at,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    try:
        result = node_func(db, context)
    except Exception as exc:  # pragma: no cover - defensive safety net
        result = NodeResult(status="failed", error_message=str(exc))

    finished_at = datetime.now()
    log.status = result.status
    log.output_json = _json_dumps(result.output)
    log.error_message = result.error_message
    log.finished_at = finished_at
    log.duration_ms = int((finished_at - started_at).total_seconds() * 1000)
    db.commit()

    return result


def _json_dumps(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)

