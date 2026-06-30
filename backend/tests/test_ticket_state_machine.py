import pytest


def test_ticket_state_machine_allows_only_declared_transitions() -> None:
    from app.tickets.state_machine import (
        TicketStatus,
        is_valid_transition,
        normalize_ticket_status,
        validate_transition,
    )

    assert normalize_ticket_status("open") == TicketStatus.PENDING
    assert is_valid_transition(TicketStatus.PENDING, TicketStatus.PROCESSING) is True
    assert is_valid_transition(TicketStatus.RESOLVED, TicketStatus.PROCESSING) is True
    assert is_valid_transition(TicketStatus.PROCESSING, TicketStatus.CLOSED) is False

    with pytest.raises(ValueError, match="Illegal ticket status transition"):
        validate_transition(TicketStatus.CLOSED, TicketStatus.PROCESSING)


def test_new_agent_ticket_defaults_to_pending(client) -> None:
    response = client.post("/api/agent/runs", json={"session_id": 1, "message_id": 1})

    assert response.status_code == 201
    assert response.json()["ticket"]["status"] == "pending"


def test_illegal_ticket_transition_returns_400(client) -> None:
    run_response = client.post("/api/agent/runs", json={"session_id": 1, "message_id": 1})
    ticket_id = run_response.json()["ticket"]["id"]

    response = client.post(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "closed", "reason": "cannot close before resolution"},
    )

    assert response.status_code == 400
    assert "Illegal ticket status transition" in response.json()["detail"]


def test_legal_ticket_transition_requires_reason(client) -> None:
    run_response = client.post("/api/agent/runs", json={"session_id": 1, "message_id": 1})
    ticket_id = run_response.json()["ticket"]["id"]

    missing_reason = client.post(f"/api/tickets/{ticket_id}/status", json={"status": "processing"})
    valid_update = client.post(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "processing", "reason": "agent started handling this ticket"},
    )

    assert missing_reason.status_code == 422
    assert valid_update.status_code == 200
    assert valid_update.json()["status"] == "processing"
