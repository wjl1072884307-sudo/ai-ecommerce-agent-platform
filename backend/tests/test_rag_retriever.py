import pytest
from sqlalchemy.orm import Session


def test_keyword_retriever_returns_structured_sources(db_session: Session):
    from app.rag.keyword_retriever import KeywordRetriever
    from app.rag.types import RetrievalQuery

    retriever = KeywordRetriever(db_session)
    results = retriever.retrieve(RetrievalQuery(query="耳机 杂音 退货", limit=5))

    assert results
    first = results[0]
    assert first.chunk_id
    assert first.document_id
    assert first.document_title
    assert first.document_type
    assert first.content
    assert first.score > 0
    assert first.metadata["retriever"] == "keyword"


def test_rag_factory_defaults_to_keyword(monkeypatch, db_session: Session):
    monkeypatch.delenv("RAG_RETRIEVER", raising=False)

    from app.core.config import get_settings
    from app.rag.factory import get_retriever
    from app.rag.keyword_retriever import KeywordRetriever

    get_settings.cache_clear()
    retriever = get_retriever(db_session)

    assert isinstance(retriever, KeywordRetriever)


def test_rag_factory_rejects_unknown_retriever(monkeypatch, db_session: Session):
    monkeypatch.setenv("RAG_RETRIEVER", "unknown")

    from app.core.config import get_settings
    from app.rag.factory import RetrieverConfigError, get_retriever

    get_settings.cache_clear()

    with pytest.raises(RetrieverConfigError):
        get_retriever(db_session)
    get_settings.cache_clear()


def test_vector_retriever_is_explicitly_not_implemented(db_session: Session):
    from app.rag.types import RetrievalQuery, RetrieverNotImplementedError
    from app.rag.vector_retriever import VectorRetriever

    retriever = VectorRetriever(db_session)

    with pytest.raises(RetrieverNotImplementedError):
        retriever.retrieve(RetrievalQuery(query="退货"))

