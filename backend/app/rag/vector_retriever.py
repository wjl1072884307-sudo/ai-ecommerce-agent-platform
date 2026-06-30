from sqlalchemy.orm import Session

from app.rag.types import RetrievedChunk, RetrievalQuery, RetrieverNotImplementedError


class VectorRetriever:
    retriever_name = "vector"

    def __init__(self, db: Session) -> None:
        self.db = db

    def retrieve(self, query: RetrievalQuery) -> list[RetrievedChunk]:
        raise RetrieverNotImplementedError(
            "VectorRetriever is reserved for V1.1. Configure RAG_RETRIEVER=keyword for V1.0."
        )

