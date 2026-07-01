from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Customer, KnowledgeChunk, KnowledgeDocument, Order, Product, User, entities
from app.services.demo_seed import seed_demo_data


def _build_test_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, TestingSessionLocal()


def test_core_tables_can_be_created() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    table_names = set(inspect(engine).get_table_names())
    assert {
        "users",
        "products",
        "orders",
        "customers",
        "sessions",
        "messages",
        "knowledge_documents",
        "knowledge_chunks",
        "agent_runs",
        "agent_node_logs",
        "reply_suggestions",
        "review_tasks",
        "tickets",
    }.issubset(table_names)
    assert entities.User.__tablename__ == "users"


def test_seed_demo_data_is_repeatable_and_contains_return_scenario() -> None:
    _, db = _build_test_session()

    seed_demo_data(db)
    seed_demo_data(db)

    assert db.query(User).count() == 5
    assert db.query(Customer).count() == 1
    assert {user.role for user in db.query(User).all()} == {"admin", "reviewer", "agent", "viewer"}
    assert db.query(Product).count() == 7
    assert db.query(Order).count() == 7

    headphones = db.query(Product).filter(Product.sku == "AUDIO-NEBULA-001").one()
    order = db.query(Order).filter(Order.product_id == headphones.id).one()
    policy = db.query(KnowledgeDocument).filter(KnowledgeDocument.title == "退货退款基础政策").one()
    chunk_count = db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == policy.id).count()

    assert order.order_status == "delivered"
    assert order.after_sale_status == "none"
    assert "杂音" in policy.content
    assert chunk_count >= 3
