from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.audit.service import safe_record_audit_log
from app.database import get_db
from app.models import KnowledgeChunk, KnowledgeDocument, User
from app.rag.factory import get_retriever
from app.rag.types import RetrievalQuery
from app.schemas import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentDetailRead,
    KnowledgeDocumentRead,
    KnowledgeDocumentUpdate,
    KnowledgeSearchResult,
)
from app.services.demo_seed import rebuild_chunks

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/documents", response_model=list[KnowledgeDocumentRead], dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
def list_documents(
    keyword: str | None = None,
    document_type: str | None = None,
    document_status: str | None = Query(default=None, alias="status"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
) -> list[KnowledgeDocument]:
    query = db.query(KnowledgeDocument)
    if keyword:
        query = query.filter(KnowledgeDocument.title.ilike(f"%{keyword}%"))
    if document_type:
        query = query.filter(KnowledgeDocument.document_type == document_type)
    if document_status:
        query = query.filter(KnowledgeDocument.status == document_status)
    return query.order_by(KnowledgeDocument.id).offset(skip).limit(limit).all()


@router.post("/documents", response_model=KnowledgeDocumentDetailRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles("admin"))])
def create_document(
    payload: KnowledgeDocumentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> KnowledgeDocument:
    document = KnowledgeDocument(**payload.model_dump())
    db.add(document)
    db.flush()
    rebuild_chunks(db, document)
    safe_record_audit_log(
        db=db,
        action="knowledge.created",
        resource_type="knowledge_document",
        resource_id=document.id,
        current_user=current_user,
        request=request,
        after={"title": document.title, "document_type": document.document_type, "status": document.status},
    )
    db.commit()
    db.refresh(document)
    return document


@router.get("/documents/{document_id}", response_model=KnowledgeDocumentDetailRead, dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
def get_document(document_id: int, db: Session = Depends(get_db)) -> KnowledgeDocument:
    document = db.get(KnowledgeDocument, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Knowledge document not found.")
    return document


@router.put("/documents/{document_id}", response_model=KnowledgeDocumentDetailRead, dependencies=[Depends(require_roles("admin"))])
def update_document(
    document_id: int,
    payload: KnowledgeDocumentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> KnowledgeDocument:
    document = db.get(KnowledgeDocument, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Knowledge document not found.")

    before = {
        "title": document.title,
        "document_type": document.document_type,
        "status": document.status,
    }
    update_data = payload.model_dump(exclude_unset=True)
    content_changed = "content" in update_data
    for field, value in update_data.items():
        setattr(document, field, value)
    if content_changed:
        rebuild_chunks(db, document)

    safe_record_audit_log(
        db=db,
        action="knowledge.updated",
        resource_type="knowledge_document",
        resource_id=document.id,
        current_user=current_user,
        request=request,
        before=before,
        after={
            "title": document.title,
            "document_type": document.document_type,
            "status": document.status,
            "content_changed": content_changed,
        },
    )
    db.commit()
    db.refresh(document)
    return document


@router.post("/documents/{document_id}/rebuild-chunks", response_model=list[KnowledgeSearchResult], dependencies=[Depends(require_roles("admin"))])
def rebuild_document_chunks(document_id: int, db: Session = Depends(get_db)) -> list[KnowledgeSearchResult]:
    document = db.get(KnowledgeDocument, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Knowledge document not found.")

    rebuild_chunks(db, document)
    db.commit()
    db.refresh(document)
    return [_to_search_result(chunk, document) for chunk in document.chunks]


@router.get("/search", response_model=list[KnowledgeSearchResult], dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
def search_knowledge(
    query: str,
    document_type: str | None = None,
    limit: int = 5,
    db: Session = Depends(get_db),
) -> list[KnowledgeSearchResult]:
    retriever = get_retriever(db)
    results = retriever.retrieve(RetrievalQuery(query=query, document_type=document_type, limit=limit))
    return [KnowledgeSearchResult.model_validate(result.to_search_result_dict()) for result in results]


def _to_search_result(chunk: KnowledgeChunk, document: KnowledgeDocument) -> KnowledgeSearchResult:
    return KnowledgeSearchResult.model_validate(
        {
            "id": chunk.id,
            "document_id": chunk.document_id,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "keywords": chunk.keywords,
            "metadata_json": chunk.metadata_json,
            "created_at": chunk.created_at,
            "document_title": document.title,
            "document_type": document.document_type,
        }
    )


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
