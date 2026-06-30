from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.rag.keyword_retriever import KeywordRetriever
from app.rag.types import Retriever
from app.rag.vector_retriever import VectorRetriever


class RetrieverConfigError(ValueError):
    pass


def get_retriever(db: Session) -> Retriever:
    retriever = get_settings().rag_retriever.lower()
    if retriever == "keyword":
        return KeywordRetriever(db)
    if retriever == "vector":
        return VectorRetriever(db)
    raise RetrieverConfigError(f"Unsupported RAG retriever: {get_settings().rag_retriever}")

