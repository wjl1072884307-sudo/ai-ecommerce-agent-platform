from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
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
    assert data["reply_suggestion"]["status"] == "pending_review"
    assert data["review_task"]["status"] == "pending"
    assert data["review_task"]["risk_level"] == "medium"
    assert data["ticket"]["ticket_type"] == "return"
    assert data["ticket"]["order_id"] == 1


def test_agent_run_appends_reply_to_session_messages(client: TestClient) -> None:
    response = client.post("/api/agent/runs", json={"session_id": 1, "message_id": 1})
    reply_content = response.json()["reply_suggestion"]["content"]

    messages = client.get("/api/sessions/1/messages")

    assert messages.status_code == 200
    agent_messages = [item for item in messages.json() if item["sender_type"] == "agent"]
    assert len(agent_messages) == 1
    assert agent_messages[0]["content"] == reply_content
    assert agent_messages[0]["message_type"] == "agent_reply"


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


def test_agent_pipeline_uses_existing_user_before_initial_commit() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        seed_demo_data(db)
        result = run_agent(db, session_id=1, message_id=1)

        assert result["run"].user_id != 0


def test_customer_message_reply_follows_chinese_input_language(client: TestClient) -> None:
    response = client.post(
        "/api/sessions/customer-message",
        json={
            "customer_id": 1,
            "order_no": "MOCK202606120001",
            "content": "我的耳机开箱的时候音质就有问题，需要退换",
            "channel": "web",
            "run_agent": True,
        },
    )

    assert response.status_code == 201
    data = response.json()
    content = data["agent_result"]["reply_suggestion"]["content"]
    assert data["agent_result"]["partial_context"]["language"] == "zh"
    assert data["agent_result"]["partial_context"]["conversation_type"] == "after_sales"
    assert "您好" in content
    assert "Dear customer" not in content


def test_customer_message_reply_follows_english_input_language(client: TestClient) -> None:
    response = client.post(
        "/api/sessions/customer-message",
        json={
            "customer_id": 1,
            "order_no": "MOCK202606120001",
            "content": "The headset has noise. Can I return it?",
            "channel": "web",
            "run_agent": True,
        },
    )

    assert response.status_code == 201
    content = response.json()["agent_result"]["reply_suggestion"]["content"]
    assert response.json()["agent_result"]["partial_context"]["language"] == "en"
    assert "Hello" in content
    assert "您好" not in content


def test_pre_sales_question_does_not_create_after_sales_ticket(client: TestClient) -> None:
    response = client.post(
        "/api/sessions/customer-message",
        json={
            "visitor_id": "visitor-presales-001",
            "content": "这款耳机还有库存吗？多少钱？",
            "channel": "web",
            "run_agent": True,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["session"]["conversation_type"] == "pre_sales"
    assert data["agent_result"]["partial_context"]["conversation_type"] == "pre_sales"
    assert data["agent_result"]["ticket"] is None


def test_anonymous_after_sales_guides_for_order_information(client: TestClient) -> None:
    response = client.post(
        "/api/sessions/customer-message",
        json={
            "visitor_id": "visitor-after-sales-001",
            "content": "我的耳机坏了，想退货",
            "channel": "web",
            "run_agent": True,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["session"]["customer_id"] is None
    assert data["agent_result"]["partial_context"]["policy_result"]["requires_order_info"] is True
    assert "订单" in data["agent_result"]["reply_suggestion"]["content"]
