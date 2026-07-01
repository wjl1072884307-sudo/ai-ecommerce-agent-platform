from fastapi.testclient import TestClient


def test_create_session_and_messages(client: TestClient) -> None:
    create_session = client.post("/api/sessions", json={"user_id": 1, "title": "New after-sales session"})

    assert create_session.status_code == 201
    session_id = create_session.json()["id"]

    create_message = client.post(
        f"/api/sessions/{session_id}/messages",
        json={
            "sender_id": 1,
            "sender_type": "customer",
            "content": "I want to check an order.",
        },
    )
    messages = client.get(f"/api/sessions/{session_id}/messages")

    assert create_message.status_code == 201
    assert create_message.json()["content"] == "I want to check an order."
    assert messages.status_code == 200
    assert len(messages.json()) == 1


def test_create_session_can_seed_first_message(client: TestClient) -> None:
    response = client.post(
        "/api/sessions",
        json={
            "user_id": 1,
            "title": "Warranty follow-up",
            "initial_message": "My smartwatch battery drains too fast.",
        },
    )

    assert response.status_code == 201
    session_id = response.json()["id"]

    messages = client.get(f"/api/sessions/{session_id}/messages")

    assert messages.status_code == 200
    assert messages.json()[0]["content"] == "My smartwatch battery drains too fast."
    assert messages.json()[0]["sender_type"] == "customer"


def test_list_and_get_sessions(client: TestClient) -> None:
    sessions = client.get("/api/sessions")
    detail = client.get("/api/sessions/1")

    assert sessions.status_code == 200
    assert len(sessions.json()) >= 5
    assert detail.status_code == 200
    assert detail.json()["title"]


def test_session_model_supports_customer_and_anonymous_context(client: TestClient) -> None:
    purchased_response = client.post(
        "/api/sessions",
        json={
            "user_id": 1,
            "customer_id": 1,
            "title": "Purchased customer after-sales",
            "conversation_type": "after_sales",
            "channel": "web",
            "requires_human": True,
            "bound_order_id": 1,
            "initial_message": "The headset has noise.",
        },
    )

    anonymous_response = client.post(
        "/api/sessions",
        json={
            "user_id": 1,
            "visitor_id": "visitor-phase2-001",
            "title": "Anonymous pre-sales",
            "conversation_type": "pre_sales",
            "channel": "web",
            "initial_message": "Do you have this headset in stock?",
        },
    )

    assert purchased_response.status_code == 201
    purchased = purchased_response.json()
    assert purchased["customer_id"] == 1
    assert purchased["visitor_id"] is None
    assert purchased["conversation_type"] == "after_sales"
    assert purchased["requires_human"] is True
    assert purchased["bound_order_id"] == 1

    assert anonymous_response.status_code == 201
    anonymous = anonymous_response.json()
    assert anonymous["customer_id"] is None
    assert anonymous["visitor_id"] == "visitor-phase2-001"
    assert anonymous["conversation_type"] == "pre_sales"
    assert anonymous["requires_human"] is False


def test_customer_message_auto_creates_anonymous_session(client: TestClient) -> None:
    response = client.post(
        "/api/sessions/customer-message",
        json={
            "visitor_id": "visitor-phase3-001",
            "content": "Do you have the headset in stock?",
            "channel": "web",
            "run_agent": False,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["session"]["visitor_id"] == "visitor-phase3-001"
    assert data["session"]["customer_id"] is None
    assert data["session"]["title"] == "Do you have the headset in stock?"
    assert data["message"]["sender_type"] == "customer"
    assert data["message"]["content"] == "Do you have the headset in stock?"
    assert data["agent_result"] is None


def test_customer_message_appends_to_existing_session_and_can_run_agent(client: TestClient) -> None:
    created = client.post(
        "/api/sessions/customer-message",
        json={
            "customer_id": 1,
            "content": "The headset has noise. Can I return it?",
            "order_no": "MOCK202606120001",
            "channel": "web",
            "run_agent": False,
        },
    ).json()

    response = client.post(
        "/api/sessions/customer-message",
        json={
            "session_id": created["session"]["id"],
            "customer_id": 1,
            "content": "Please help me check the return policy.",
            "channel": "web",
            "run_agent": True,
        },
    )
    messages = client.get(f"/api/sessions/{created['session']['id']}/messages")

    assert response.status_code == 201
    data = response.json()
    assert data["session"]["id"] == created["session"]["id"]
    assert data["message"]["content"] == "Please help me check the return policy."
    assert data["agent_result"]["run"]["status"] == "success"
    assert len(messages.json()) >= 3
