from fastapi.testclient import TestClient


def test_list_orders_returns_demo_orders(client: TestClient) -> None:
    response = client.get("/api/orders")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["order_no"] == "MOCK202606120001"


def test_get_order_returns_detail_with_product(client: TestClient) -> None:
    response = client.get("/api/orders/1")

    assert response.status_code == 200
    data = response.json()
    assert data["order_no"] == "MOCK202606120001"
    assert data["product"]["sku"] == "AUDIO-NEBULA-001"


def test_get_order_by_number_and_user_orders(client: TestClient) -> None:
    by_number = client.get("/api/orders/by-number/MOCK202606120001")
    user_orders = client.get("/api/users/1/orders")

    assert by_number.status_code == 200
    assert by_number.json()["id"] == 1
    assert user_orders.status_code == 200
    assert len(user_orders.json()) == 3


def test_create_update_and_delete_order(client: TestClient) -> None:
    create_response = client.post(
        "/api/orders",
        json={
            "order_no": "MOCK202606230001",
            "user_id": 1,
            "product_id": 1,
            "quantity": 2,
            "total_amount": 798.0,
            "order_status": "paid",
            "payment_status": "paid",
            "logistics_status": "pending",
            "after_sale_status": "none",
        },
    )
    assert create_response.status_code == 201
    order_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/orders/{order_id}",
        json={"logistics_status": "shipped", "tracking_no": "SFTEST0001"},
    )
    delete_response = client.delete(f"/api/orders/{order_id}")
    list_response = client.get("/api/orders")

    assert update_response.status_code == 200
    assert update_response.json()["logistics_status"] == "shipped"
    assert update_response.json()["tracking_no"] == "SFTEST0001"
    assert delete_response.status_code == 200
    assert delete_response.json()["order_status"] == "deleted"
    assert all(item["id"] != order_id for item in list_response.json())
