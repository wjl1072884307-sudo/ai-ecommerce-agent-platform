from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_agent_run_returns_failed_result_for_missing_message(client: TestClient):
    response = client.post("/api/agent/runs", json={"session_id": 999, "message_id": 999})

    assert response.status_code == 201
    payload = response.json()
    assert payload["run"]["status"] == "failed"
    assert payload["failed_node"] == "receive_message"
    assert payload["partial_context"]["session_id"] == 999
    assert payload["partial_context"]["message_id"] == 999
    assert payload["reply_suggestion"] is None
    assert payload["review_task"] is None
    assert payload["ticket"] is None


def test_pipeline_failed_result_contains_failed_node_and_partial_context(db_session: Session):
    from app.agent.pipeline import run_agent

    result = run_agent(db_session, session_id=999, message_id=999)

    assert result["run"].status == "failed"
    assert result["failed_node"] == "receive_message"
    assert result["partial_context"]["run_id"] == result["run"].id
    assert result["partial_context"]["session_id"] == 999

