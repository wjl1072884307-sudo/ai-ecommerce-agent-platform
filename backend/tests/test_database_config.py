from pathlib import Path


def test_get_database_url_uses_settings(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./data/custom.db")

    from app.core.config import get_settings
    from app.database import get_database_url

    get_settings.cache_clear()

    assert get_database_url() == "sqlite:///./data/custom.db"


def test_sqlite_parent_directory_is_created(tmp_path):
    from app.database import ensure_sqlite_parent_dir

    db_path = tmp_path / "nested" / "app.db"

    ensure_sqlite_parent_dir(f"sqlite:///{db_path}")

    assert Path(db_path).parent.exists()


def test_non_sqlite_url_does_not_create_directory(tmp_path):
    from app.database import ensure_sqlite_parent_dir

    marker = tmp_path / "postgresql+psycopg:" / "user"

    ensure_sqlite_parent_dir("postgresql+psycopg://user:pass@db:5432/app")

    assert not marker.exists()

