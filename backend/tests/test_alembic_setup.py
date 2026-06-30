from pathlib import Path


def test_alembic_scaffold_exists_and_targets_app_metadata():
    backend_root = Path(__file__).resolve().parents[1]
    alembic_ini = backend_root / "alembic.ini"
    env_py = backend_root / "alembic" / "env.py"
    versions_dir = backend_root / "alembic" / "versions"

    assert alembic_ini.exists()
    assert env_py.exists()
    assert versions_dir.is_dir()

    env_content = env_py.read_text(encoding="utf-8")
    assert "from app.database import Base" in env_content
    assert "target_metadata = Base.metadata" in env_content
    assert "from app.models import entities" in env_content


def test_phase2_dependencies_are_declared():
    requirements = (Path(__file__).resolve().parents[1] / "requirements.txt").read_text(encoding="utf-8")

    assert "psycopg[binary]" in requirements
    assert "alembic" in requirements


def test_database_design_document_explains_sqlite_and_postgresql_boundary():
    document = Path(__file__).resolve().parents[2] / "DATABASE_DESIGN.md"

    content = document.read_text(encoding="utf-8")

    assert "PostgreSQL" in content
    assert "SQLite" in content
    assert "Alembic" in content
    assert "生产环境不建议只使用 SQLite" in content

