from app.models import AuditLog


def _actions(client):
    response = client.get("/api/audit-logs")
    response.raise_for_status()
    return [item["action"] for item in response.json()]


def test_login_success_and_failure_are_audited(unauthenticated_client):
    failed = unauthenticated_client.post(
        "/api/auth/login",
        json={"username": "admin_demo", "password": "wrong-password"},
    )
    succeeded = unauthenticated_client.post(
        "/api/auth/login",
        json={"username": "admin_demo", "password": "admin123456"},
    )
    token = succeeded.json()["access_token"]

    response = unauthenticated_client.get(
        "/api/audit-logs",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert failed.status_code == 401
    assert succeeded.status_code == 200
    actions = [item["action"] for item in response.json()]
    assert "auth.login.failed" in actions
    assert "auth.login.success" in actions
    assert all("wrong-password" not in str(item) for item in response.json())
    assert all(token not in str(item) for item in response.json())


def test_review_approval_is_audited(client):
    run_response = client.post("/api/agent/runs", json={"session_id": 1, "message_id": 1})
    task_id = run_response.json()["review_task"]["id"]

    response = client.post(
        f"/api/review-tasks/{task_id}/approve",
        json={"reviewer_id": 3, "review_comment": "ok", "final_reply": "approved reply"},
    )

    assert response.status_code == 200
    assert "review.approve" in _actions(client)


def test_ticket_claim_and_status_change_are_audited(client):
    run_response = client.post("/api/agent/runs", json={"session_id": 1, "message_id": 1})
    ticket_id = run_response.json()["ticket"]["id"]

    claim_response = client.post(f"/api/tickets/{ticket_id}/claim")
    status_response = client.post(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "resolved", "reason": "handled", "resolution": "done"},
    )

    assert claim_response.status_code == 200
    assert status_response.status_code == 200
    actions = _actions(client)
    assert "ticket.claimed" in actions
    assert "ticket.status_changed" in actions


def test_knowledge_create_and_update_are_audited(client):
    create_response = client.post(
        "/api/knowledge/documents",
        json={
            "title": "Audit policy",
            "document_type": "policy",
            "content": "Audit content",
            "status": "active",
        },
    )
    document_id = create_response.json()["id"]
    update_response = client.put(
        f"/api/knowledge/documents/{document_id}",
        json={"title": "Updated audit policy"},
    )

    assert create_response.status_code == 201
    assert update_response.status_code == 200
    actions = _actions(client)
    assert "knowledge.created" in actions
    assert "knowledge.updated" in actions


def test_agent_run_trigger_is_audited(client):
    response = client.post("/api/agent/runs", json={"session_id": 1, "message_id": 1})

    assert response.status_code == 201
    assert "agent.run_triggered" in _actions(client)


def test_audit_failure_does_not_break_business_flow(client, monkeypatch):
    def broken_record(*args, **kwargs):
        raise RuntimeError("audit storage unavailable")

    monkeypatch.setattr("app.audit.service.record_audit_log", broken_record)

    response = client.post(
        "/api/knowledge/documents",
        json={
            "title": "Audit failure tolerance",
            "document_type": "policy",
            "content": "Audit failure should not block this write.",
            "status": "active",
        },
    )

    assert response.status_code == 201
    assert client.get("/api/audit-logs").status_code == 200
