from fastapi.testclient import TestClient


def test_create_session_and_messages(client: TestClient) -> None:
    create_session = client.post("/api/sessions", json={"user_id": 1, "title": "新的售后咨询"})

    assert create_session.status_code == 201
    session_id = create_session.json()["id"]

    create_message = client.post(
        f"/api/sessions/{session_id}/messages",
        json={
            "sender_id": 1,
            "sender_type": "customer",
            "content": "我想查询一下订单。",
        },
    )
    messages = client.get(f"/api/sessions/{session_id}/messages")

    assert create_message.status_code == 201
    assert create_message.json()["content"] == "我想查询一下订单。"
    assert messages.status_code == 200
    assert len(messages.json()) == 1


def test_list_and_get_sessions(client: TestClient) -> None:
    sessions = client.get("/api/sessions")
    detail = client.get("/api/sessions/1")

    assert sessions.status_code == 200
    assert len(sessions.json()) == 1
    assert detail.status_code == 200
    assert detail.json()["title"] == "耳机售后咨询"

