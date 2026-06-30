import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import entities  # noqa: F401
from app.services.demo_seed import seed_demo_data


def _build_test_client(authenticate: bool) -> TestClient:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        seed_demo_data(db)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    if authenticate:
        response = test_client.post(
            "/api/auth/login",
            json={"username": "admin_demo", "password": "admin123456"},
        )
        response.raise_for_status()
        test_client.headers.update({"Authorization": f"Bearer {response.json()['access_token']}"})
    return test_client


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        seed_demo_data(db)
        yield db


@pytest.fixture()
def unauthenticated_client() -> TestClient:
    with _build_test_client(authenticate=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def client() -> TestClient:
    with _build_test_client(authenticate=True) as test_client:
        yield test_client
    app.dependency_overrides.clear()
