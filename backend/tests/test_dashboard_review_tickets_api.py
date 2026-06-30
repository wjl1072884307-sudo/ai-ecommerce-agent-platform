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
    assert ticket_stats.json()[0]["name"] == "pending"
    assert review_tasks.status_code == 200
    assert review_tasks.json()[0]["id"] == review_task_id
    assert tickets.status_code == 200
    assert tickets.json()[0]["id"] == ticket_id

    approve = client.post(
        f"/api/review-tasks/{review_task_id}/approve",
        json={"reviewer_id": 3, "review_comment": "approved"},
    )
    ticket_update = client.post(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "processing", "reason": "start handling", "resolution": "start after-sale handling"},
    )

    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"
    assert ticket_update.status_code == 200
    assert ticket_update.json()["status"] == "processing"


def test_dashboard_summary_excludes_soft_deleted_products_and_orders(client: TestClient) -> None:
    product_response = client.post(
        "/api/products",
        json={
            "name": "Dashboard deleted product",
            "sku": "DASHBOARD-DELETED-PRODUCT",
            "category": "test",
            "price": 1.0,
            "stock": 1,
        },
    )
    order_response = client.post(
        "/api/orders",
        json={
            "order_no": "DASHBOARD-DELETED-ORDER",
            "user_id": 1,
            "product_id": 1,
            "quantity": 1,
            "total_amount": 1.0,
            "order_status": "paid",
            "payment_status": "paid",
            "logistics_status": "pending",
            "after_sale_status": "none",
        },
    )

    client.delete(f"/api/products/{product_response.json()['id']}")
    client.delete(f"/api/orders/{order_response.json()['id']}")
    summary = client.get("/api/dashboard/summary")

    assert summary.status_code == 200
    assert summary.json()["product_count"] == 3
    assert summary.json()["order_count"] == 3
