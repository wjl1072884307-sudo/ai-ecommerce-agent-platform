import json

from sqlalchemy.orm import Session


def test_agent_generate_reply_uses_fallback_when_llm_fails(db_session: Session, monkeypatch):
    from app.agent.pipeline import run_agent
    from app.llm.types import LLMProviderError
    from app.models import AgentNodeLog

    class FailingProvider:
        provider_name = "failing-provider"

        def generate(self, request):
            raise LLMProviderError("provider timeout")

    monkeypatch.setattr("app.agent.nodes.get_llm_provider", lambda: FailingProvider())

    result = run_agent(db_session, session_id=1, message_id=1)

    assert result["run"].status == "success"
    assert result["reply_suggestion"] is not None

    log = (
        db_session.query(AgentNodeLog)
        .filter(AgentNodeLog.run_id == result["run"].id, AgentNodeLog.node_name == "generate_reply")
        .one()
    )
    output = json.loads(log.output_json)

    assert output["llm_used"] is False
    assert output["llm_provider"] == "failing-provider"
    assert output["fallback_used"] is True
    assert "provider timeout" in output["fallback_reason"]


def test_agent_generate_reply_records_mock_provider_usage(db_session: Session):
    import json

    from app.agent.pipeline import run_agent
    from app.core.config import get_settings
    from app.models import AgentNodeLog

    get_settings.cache_clear()
    result = run_agent(db_session, session_id=1, message_id=1)

    log = (
        db_session.query(AgentNodeLog)
        .filter(AgentNodeLog.run_id == result["run"].id, AgentNodeLog.node_name == "generate_reply")
        .one()
    )
    output = json.loads(log.output_json)

    assert output["llm_used"] is True
    assert output["llm_provider"] == "mock"
    assert output["fallback_used"] is False
    assert result["reply_suggestion"].content
