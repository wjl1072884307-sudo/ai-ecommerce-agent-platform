from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel, TimestampedModel


class KnowledgeDocumentBase(BaseModel):
    title: str
    document_type: str
    content: str
    status: str = "active"


class KnowledgeDocumentCreate(KnowledgeDocumentBase):
    pass


class KnowledgeDocumentUpdate(BaseModel):
    title: str | None = None
    document_type: str | None = None
    content: str | None = None
    status: str | None = None


class KnowledgeChunkRead(ORMModel):
    id: int
    document_id: int
    chunk_index: int
    content: str
    keywords: str | None
    metadata_json: str | None
    created_at: datetime


class KnowledgeDocumentRead(KnowledgeDocumentBase, TimestampedModel):
    id: int
    created_at: datetime
    updated_at: datetime


class KnowledgeDocumentDetailRead(KnowledgeDocumentRead):
    chunks: list[KnowledgeChunkRead] = []


class KnowledgeSearchResult(KnowledgeChunkRead):
    document_title: str
    document_type: str
    score: float = 0.0
    metadata: dict = {}
