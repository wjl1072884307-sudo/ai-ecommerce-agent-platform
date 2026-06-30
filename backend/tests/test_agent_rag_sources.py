import json

from sqlalchemy.orm import Session


def test_agent_retrieve_knowledge_logs_structured_sources(db_session: Session):
    from app.agent.pipeline import run_agent
    from app.models import AgentNodeLog

    result = run_agent(db_session, session_id=1, message_id=1)

    log = (
        db_session.query(AgentNodeLog)
        .filter(AgentNodeLog.run_id == result["run"].id, AgentNodeLog.node_name == "retrieve_knowledge")
        .one()
    )
    output = json.loads(log.output_json)

    assert output["knowledge_chunks"]
    assert output["sources"]
    assert output["sources"][0]["document_title"]
    assert output["sources"][0]["chunk_id"]
    assert output["sources"][0]["score"] > 0

