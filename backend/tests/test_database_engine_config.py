import warnings


def test_sqlite_engine_options_keep_local_development_behavior():
    from app.database import build_engine_options

    options = build_engine_options("sqlite:///./data/app.db")

    assert options == {"connect_args": {"check_same_thread": False}}


def test_postgresql_engine_options_enable_pooling():
    from app.database import build_engine_options

    options = build_engine_options(
        "postgresql+psycopg://user:pass@db:5432/app",
        pool_size=7,
        max_overflow=13,
    )

    assert options["pool_pre_ping"] is True
    assert options["pool_size"] == 7
    assert options["max_overflow"] == 13
    assert "connect_args" not in options


def test_production_sqlite_database_emits_warning():
    from app.database import warn_if_unsafe_production_database

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        warn_if_unsafe_production_database("production", "sqlite:///./data/app.db")

    assert len(captured) == 1
    assert "SQLite" in str(captured[0].message)
    assert "production" in str(captured[0].message)


def test_development_sqlite_database_does_not_emit_warning():
    from app.database import warn_if_unsafe_production_database

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        warn_if_unsafe_production_database("development", "sqlite:///./data/app.db")

    assert captured == []

