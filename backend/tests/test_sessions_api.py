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
