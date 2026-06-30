from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.agent import run_agent
from app.database import Base
from app.models import AgentNodeLog, AgentRun, entities
from app.services.demo_seed import seed_demo_data

def test_agent_run_completes_return_request_and_creates_business_records(client: TestClient) -> None:
    response = client.post("/api/agent/runs", json={"session_id": 1, "message_id": 1})

    assert response.status_code == 201
    data = response.json()
    assert data["run"]["status"] == "success"
    assert data["run"]["intent"] == "return_request"
    assert "MOCK202606120001" in data["reply_suggestion"]["content"]
    assert data["reply_suggestion"]["status"] == "pending_review"
    assert data["review_task"]["status"] == "pending"
    assert data["review_task"]["risk_level"] == "medium"
    assert data["ticket"]["ticket_type"] == "return"
    assert data["ticket"]["order_id"] == 1


def test_agent_logs_are_queryable(client: TestClient) -> None:
    run_response = client.post("/api/agent/runs", json={"session_id": 1, "message_id": 1})
    run_id = run_response.json()["run"]["id"]

    runs = client.get("/api/agent/runs")
    detail = client.get(f"/api/agent/runs/{run_id}")
    logs = client.get(f"/api/agent/runs/{run_id}/node-logs")

    assert runs.status_code == 200
    assert detail.status_code == 200
    assert logs.status_code == 200
    node_names = [item["node_name"] for item in logs.json()]
    assert node_names == [
        "receive_message",
        "classify_intent",
        "query_order",
        "retrieve_knowledge",
        "check_policy",
        "risk_check",
        "generate_reply",
        "create_review_task",
        "create_ticket",
    ]
    assert all(item["input_json"] for item in logs.json())
    assert all(item["output_json"] for item in logs.json())


def test_agent_endpoint_rejects_invalid_message(client: TestClient) -> None:
    response = client.post("/api/agent/runs", json={"session_id": 1, "message_id": 999})

    assert response.status_code == 201
    data = response.json()
    assert data["run"]["status"] == "failed"
    assert data["failed_node"] == "receive_message"


def test_agent_pipeline_writes_failed_node_log_for_invalid_message() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        seed_demo_data(db)
        result = run_agent(db, session_id=1, message_id=999)

        run = result["run"]
        failed_log = db.query(AgentNodeLog).filter(AgentNodeLog.run_id == run.id).one()

        assert entities.AgentRun.__tablename__ == "agent_runs"
        assert run.status == "failed"
        assert failed_log.node_name == "receive_message"
        assert failed_log.status == "failed"
        assert failed_log.error_message == "Message or session not found."
