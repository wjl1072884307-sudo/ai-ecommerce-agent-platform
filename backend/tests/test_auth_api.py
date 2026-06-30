from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User


def _login(client: TestClient, username: str, password: str) -> str:
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    return payload["access_token"]


def test_login_returns_jwt_and_me_returns_current_user(unauthenticated_client: TestClient):
    token = _login(unauthenticated_client, "admin_demo", "admin123456")

    response = unauthenticated_client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["username"] == "admin_demo"
    assert response.json()["role"] == "admin"


def test_login_rejects_invalid_password(unauthenticated_client: TestClient):
    response = unauthenticated_client.post(
        "/api/auth/login",
        json={"username": "admin_demo", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_seeded_users_store_password_hashes(db_session: Session):
    admin = db_session.query(User).filter(User.username == "admin_demo").one()

    assert admin.password_hash
    assert admin.password_hash != "admin123456"
    assert admin.password_hash.startswith("pbkdf2_sha256$")


def test_me_rejects_missing_or_invalid_token(unauthenticated_client: TestClient):
    missing = unauthenticated_client.get("/api/auth/me")
    invalid = unauthenticated_client.get("/api/auth/me", headers={"Authorization": "Bearer invalid-token"})

    assert missing.status_code == 401
    assert invalid.status_code == 401


def test_health_remains_public(unauthenticated_client: TestClient):
    response = unauthenticated_client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

