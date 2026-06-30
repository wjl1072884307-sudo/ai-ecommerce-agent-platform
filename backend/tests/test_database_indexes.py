from sqlalchemy import create_engine, inspect
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import entities  # noqa: F401


def _index_names(table_name: str) -> set[str]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return {index["name"] for index in inspect(engine).get_indexes(table_name)}


def test_high_frequency_composite_indexes_exist():
    assert "ix_messages_session_created_at" in _index_names("messages")
    assert "ix_agent_node_logs_run_node" in _index_names("agent_node_logs")
    assert "ix_tickets_status_assignee" in _index_names("tickets")
    assert "ix_tickets_created_at" in _index_names("tickets")

