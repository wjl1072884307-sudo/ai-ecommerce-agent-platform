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

