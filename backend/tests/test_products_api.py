from fastapi.testclient import TestClient


def test_list_products_returns_demo_products(client: TestClient) -> None:
    response = client.get("/api/products")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 6
    assert data[0]["sku"] == "AUDIO-NEBULA-001"


def test_get_product_returns_detail(client: TestClient) -> None:
    response = client.get("/api/products/1")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Nebula Noise-Cancelling Headset"
    assert data["category"] == "Digital Audio"


def test_create_and_update_product(client: TestClient) -> None:
    create_response = client.post(
        "/api/products",
        json={
            "name": "便携充电宝",
            "sku": "POWER-BANK-001",
            "category": "手机配件",
            "description": "10000mAh 便携充电宝。",
            "price": 99.0,
            "stock": 50,
            "after_sale_policy": "支持 7 天无理由退货。",
        },
    )
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]

    update_response = client.put(f"/api/products/{product_id}", json={"stock": 45, "status": "inactive"})

    assert update_response.status_code == 200
    assert update_response.json()["stock"] == 45
    assert update_response.json()["status"] == "inactive"


def test_delete_product_hides_it_from_default_list(client: TestClient) -> None:
    create_response = client.post(
        "/api/products",
        json={
            "name": "可删除测试商品",
            "sku": "DELETE-PRODUCT-001",
            "category": "测试类目",
            "price": 10.0,
            "stock": 1,
        },
    )
    product_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/products/{product_id}")
    list_response = client.get("/api/products")

    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "deleted"
    assert all(item["id"] != product_id for item in list_response.json())
