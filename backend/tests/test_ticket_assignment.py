from fastapi.testclient import TestClient


def _login(client: TestClient, username: str, password: str) -> str:
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_agent_can_claim_unassigned_ticket_and_moves_to_processing(unauthenticated_client: TestClient) -> None:
    admin_token = _login(unauthenticated_client, "admin_demo", "admin123456")
    agent_token = _login(unauthenticated_client, "agent_demo", "agent123456")

    run_response = unauthenticated_client.post(
        "/api/agent/runs",
        headers=_auth_header(admin_token),
        json={"session_id": 1, "message_id": 1},
    )
    ticket_id = run_response.json()["ticket"]["id"]

    claim = unauthenticated_client.post(f"/api/tickets/{ticket_id}/claim", headers=_auth_header(agent_token))

    assert claim.status_code == 200
    assert claim.json()["assignee_id"] == 3
    assert claim.json()["status"] == "processing"


def test_non_assignee_cannot_update_assigned_ticket(unauthenticated_client: TestClient) -> None:
    admin_token = _login(unauthenticated_client, "admin_demo", "admin123456")
    agent_token = _login(unauthenticated_client, "agent_demo", "agent123456")
    reviewer_token = _login(unauthenticated_client, "reviewer_demo", "reviewer123456")

    run_response = unauthenticated_client.post(
        "/api/agent/runs",
        headers=_auth_header(admin_token),
        json={"session_id": 1, "message_id": 1},
    )
    ticket_id = run_response.json()["ticket"]["id"]
    unauthenticated_client.post(f"/api/tickets/{ticket_id}/claim", headers=_auth_header(agent_token))

    response = unauthenticated_client.post(
        f"/api/tickets/{ticket_id}/status",
        headers=_auth_header(reviewer_token),
        json={"status": "resolved", "reason": "reviewer should not update another assignee ticket"},
    )

    assert response.status_code == 403


def test_second_non_admin_claim_is_rejected(unauthenticated_client: TestClient) -> None:
    admin_token = _login(unauthenticated_client, "admin_demo", "admin123456")
    agent_token = _login(unauthenticated_client, "agent_demo", "agent123456")
    reviewer_token = _login(unauthenticated_client, "reviewer_demo", "reviewer123456")

    run_response = unauthenticated_client.post(
        "/api/agent/runs",
        headers=_auth_header(admin_token),
        json={"session_id": 1, "message_id": 1},
    )
    ticket_id = run_response.json()["ticket"]["id"]
    first_claim = unauthenticated_client.post(f"/api/tickets/{ticket_id}/claim", headers=_auth_header(agent_token))
    second_claim = unauthenticated_client.post(f"/api/tickets/{ticket_id}/claim", headers=_auth_header(reviewer_token))

    assert first_claim.status_code == 200
    assert second_claim.status_code == 409
