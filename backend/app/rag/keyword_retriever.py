from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import KnowledgeChunk, KnowledgeDocument
from app.rag.types import RetrievedChunk, RetrievalQuery


class KeywordRetriever:
    retriever_name = "keyword"

    def __init__(self, db: Session) -> None:
        self.db = db

    def retrieve(self, query: RetrievalQuery) -> list[RetrievedChunk]:
        terms = _extract_search_terms(query.query)
        terms.extend(term for term in query.terms if term)
        terms = list(dict.fromkeys(term.strip() for term in terms if term.strip()))

        chunk_query = self.db.query(KnowledgeChunk, KnowledgeDocument).join(KnowledgeDocument)
        if query.document_type:
            chunk_query = chunk_query.filter(KnowledgeDocument.document_type == query.document_type)

        filters = []
        for term in terms:
            filters.append(KnowledgeChunk.content.ilike(f"%{term}%"))
            filters.append(KnowledgeChunk.keywords.ilike(f"%{term}%"))
            filters.append(KnowledgeDocument.title.ilike(f"%{term}%"))

        rows = chunk_query.filter(or_(*filters)).order_by(KnowledgeChunk.id).limit(query.limit).all() if filters else []
        results = [
            RetrievedChunk(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                document_title=document.title,
                document_type=document.document_type,
                content=chunk.content,
                keywords=chunk.keywords,
                metadata_json=chunk.metadata_json,
                created_at=chunk.created_at,
                chunk_index=chunk.chunk_index,
                score=_score_chunk(chunk, document, terms),
                metadata={"retriever": self.retriever_name, "matched_terms": _matched_terms(chunk, document, terms)},
            )
            for chunk, document in rows
        ]
        return sorted(results, key=lambda item: (-item.score, item.chunk_id))


def _score_chunk(chunk: KnowledgeChunk, document: KnowledgeDocument, terms: list[str]) -> float:
    return float(max(1, len(_matched_terms(chunk, document, terms))))


def _matched_terms(chunk: KnowledgeChunk, document: KnowledgeDocument, terms: list[str]) -> list[str]:
    haystack = " ".join([chunk.content or "", chunk.keywords or "", document.title or ""]).lower()
    return [term for term in terms if term.lower() in haystack]


def _extract_search_terms(query: str) -> list[str]:
    known_terms = [
        "退货",
        "退款",
        "耳机",
        "杂音",
        "质量问题",
        "物流",
        "投诉",
        "人工审核",
        "工单",
        "手机",
        "屏保",
        "保护膜",
        "钢化膜",
        "补发",
        "更换",
        "翘起",
    ]
    terms = [term.strip() for term in query.replace("，", " ").replace(",", " ").split() if term.strip()]
    terms.extend(term for term in known_terms if term in query)
    return list(dict.fromkeys(terms)) or [query.strip()]

