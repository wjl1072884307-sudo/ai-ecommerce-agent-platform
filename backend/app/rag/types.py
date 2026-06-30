from dataclasses import dataclass, field
from typing import Any, Protocol


class RetrieverError(Exception):
    pass


class RetrieverNotImplementedError(RetrieverError):
    pass


@dataclass(frozen=True)
class RetrievalQuery:
    query: str
    document_type: str | None = None
    limit: int = 5
    terms: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: int
    document_id: int
    document_title: str
    document_type: str
    content: str
    keywords: str | None
    metadata_json: str | None
    created_at: Any
    chunk_index: int
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_search_result_dict(self) -> dict[str, Any]:
        return {
            "id": self.chunk_id,
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "keywords": self.keywords,
            "metadata_json": self.metadata_json,
            "created_at": self.created_at,
            "document_title": self.document_title,
            "document_type": self.document_type,
            "score": self.score,
            "metadata": self.metadata,
        }

    def to_source_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "document_title": self.document_title,
            "document_type": self.document_type,
            "score": self.score,
            "metadata": self.metadata,
        }


class Retriever(Protocol):
    retriever_name: str

    def retrieve(self, query: RetrievalQuery) -> list[RetrievedChunk]:
        ...

