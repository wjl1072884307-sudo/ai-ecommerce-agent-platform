from fastapi.testclient import TestClient


def test_dashboard_review_and_ticket_flow(client: TestClient) -> None:
    run_response = client.post("/api/agent/runs", json={"session_id": 1, "message_id": 1})
    assert run_response.status_code == 201
    review_task_id = run_response.json()["review_task"]["id"]
    ticket_id = run_response.json()["ticket"]["id"]

    summary = client.get("/api/dashboard/summary")
    intent_stats = client.get("/api/dashboard/intent-stats")
    ticket_stats = client.get("/api/dashboard/ticket-stats")
    review_tasks = client.get("/api/review-tasks")
    tickets = client.get("/api/tickets")

    assert summary.status_code == 200
    assert summary.json()["pending_review_count"] == 1
    assert intent_stats.status_code == 200
    assert intent_stats.json()[0]["name"] == "return_request"
    assert ticket_stats.status_code == 200
    assert ticket_stats.json()[0]["name"] == "open"
    assert review_tasks.status_code == 200
    assert review_tasks.json()[0]["id"] == review_task_id
    assert tickets.status_code == 200
    assert tickets.json()[0]["id"] == ticket_id

    approve = client.post(
        f"/api/review-tasks/{review_task_id}/approve",
        json={"reviewer_id": 3, "review_comment": "确认可退货。"},
    )
    ticket_update = client.post(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "processing", "resolution": "已进入售后处理。"},
    )

    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"
    assert ticket_update.status_code == 200
    assert ticket_update.json()["status"] == "processing"

