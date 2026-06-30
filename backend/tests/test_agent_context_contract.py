import json

from sqlalchemy.orm import Session


def test_agent_context_snapshot_contains_operational_fields_without_secrets(db_session: Session):
    from app.agent.pipeline import run_agent
    from app.models import AgentNodeLog

    result = run_agent(db_session, session_id=1, message_id=1)

    log = (
        db_session.query(AgentNodeLog)
        .filter(AgentNodeLog.run_id == result["run"].id, AgentNodeLog.node_name == "generate_reply")
        .one()
    )
    snapshot = json.loads(log.input_json)

    assert "knowledge_sources" in snapshot
    assert "llm_result" in snapshot
    assert "risk_actions" in snapshot
    serialized = json.dumps(snapshot)
    assert "JWT_SECRET_KEY" not in serialized
    assert "LLM_API_KEY" not in serialized
    assert "password_hash" not in serialized

