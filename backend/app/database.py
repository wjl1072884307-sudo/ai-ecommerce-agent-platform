from collections.abc import Generator
from pathlib import Path
import warnings

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


def get_database_url() -> str:
    return get_settings().database_url


def ensure_sqlite_parent_dir(database_url: str) -> None:
    if not database_url.startswith("sqlite:///"):
        return

    db_path = database_url.replace("sqlite:///", "", 1)
    if db_path == ":memory:":
        return

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)


def is_sqlite_url(database_url: str) -> bool:
    return database_url.startswith("sqlite")


def build_engine_options(
    database_url: str,
    *,
    pool_size: int | None = None,
    max_overflow: int | None = None,
) -> dict[str, object]:
    if is_sqlite_url(database_url):
        return {"connect_args": {"check_same_thread": False}}

    return {
        "pool_pre_ping": True,
        "pool_size": pool_size if pool_size is not None else get_settings().database_pool_size,
        "max_overflow": max_overflow if max_overflow is not None else get_settings().database_max_overflow,
    }


def warn_if_unsafe_production_database(app_env: str, database_url: str) -> None:
    if app_env.lower() == "production" and is_sqlite_url(database_url):
        warnings.warn(
            "SQLite is not recommended as the only database in production. "
            "Use PostgreSQL for production deployments.",
            RuntimeWarning,
            stacklevel=2,
        )


DATABASE_URL = get_database_url()
ensure_sqlite_parent_dir(DATABASE_URL)
warn_if_unsafe_production_database(get_settings().app_env, DATABASE_URL)

engine = create_engine(
    DATABASE_URL,
    **build_engine_options(DATABASE_URL),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
