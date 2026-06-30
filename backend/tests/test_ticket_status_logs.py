def test_ticket_status_change_creates_queryable_log(client) -> None:
    run_response = client.post("/api/agent/runs", json={"session_id": 1, "message_id": 1})
    ticket_id = run_response.json()["ticket"]["id"]

    update = client.post(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "processing", "reason": "start after-sale handling"},
    )
    logs = client.get(f"/api/tickets/{ticket_id}/status-logs")

    assert update.status_code == 200
    assert logs.status_code == 200
    assert logs.json()[0]["ticket_id"] == ticket_id
    assert logs.json()[0]["from_status"] == "pending"
    assert logs.json()[0]["to_status"] == "processing"
    assert logs.json()[0]["operator_id"] == 2
    assert logs.json()[0]["reason"] == "start after-sale handling"
