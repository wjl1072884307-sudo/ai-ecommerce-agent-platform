from fastapi.testclient import TestClient


def _login(client: TestClient, username: str, password: str) -> str:
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_protected_api_requires_login(unauthenticated_client: TestClient):
    response = unauthenticated_client.get("/api/products")

    assert response.status_code == 401


def test_viewer_can_read_but_cannot_write_products(unauthenticated_client: TestClient):
    token = _login(unauthenticated_client, "viewer_demo", "viewer123456")

    read_response = unauthenticated_client.get("/api/products", headers=_auth_header(token))
    write_response = unauthenticated_client.post(
        "/api/products",
        headers=_auth_header(token),
        json={
            "name": "Viewer Blocked Product",
            "sku": "VIEWER-BLOCKED-001",
            "category": "test",
            "description": "viewer cannot create this",
            "price": 1,
            "stock": 1,
            "after_sale_policy": None,
            "status": "active",
        },
    )

    assert read_response.status_code == 200
    assert write_response.status_code == 403


def test_admin_can_write_products(unauthenticated_client: TestClient):
    token = _login(unauthenticated_client, "admin_demo", "admin123456")

    response = unauthenticated_client.post(
        "/api/products",
        headers=_auth_header(token),
        json={
            "name": "Admin Created Product",
            "sku": "ADMIN-CREATED-001",
            "category": "test",
            "description": "created by admin",
            "price": 99,
            "stock": 10,
            "after_sale_policy": None,
            "status": "active",
        },
    )

    assert response.status_code == 201
    assert response.json()["sku"] == "ADMIN-CREATED-001"


def test_viewer_cannot_modify_knowledge_documents(unauthenticated_client: TestClient):
    token = _login(unauthenticated_client, "viewer_demo", "viewer123456")

    response = unauthenticated_client.post(
        "/api/knowledge/documents",
        headers=_auth_header(token),
        json={
            "title": "Viewer Knowledge",
            "document_type": "policy",
            "content": "viewer cannot create knowledge",
            "status": "active",
        },
    )

    assert response.status_code == 403


def test_reviewer_can_approve_review_task_after_agent_run(unauthenticated_client: TestClient):
    agent_token = _login(unauthenticated_client, "agent_demo", "agent123456")
    reviewer_token = _login(unauthenticated_client, "reviewer_demo", "reviewer123456")

    run_response = unauthenticated_client.post(
        "/api/agent/runs",
        headers=_auth_header(agent_token),
        json={"session_id": 1, "message_id": 1},
    )
    assert run_response.status_code == 201
    task_id = run_response.json()["review_task"]["id"]

    approve_response = unauthenticated_client.post(
        f"/api/review-tasks/{task_id}/approve",
        headers=_auth_header(reviewer_token),
        json={"reviewer_id": 3, "review_comment": "approved by reviewer", "final_reply": None},
    )

    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

