from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.database import get_db
from app.models import CustomerSession, Message, User
from app.schemas import MessageCreate, MessageRead, SessionCreate, SessionRead

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionRead], dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
def list_sessions(
    session_status: str | None = Query(default=None, alias="status"),
    user_id: int | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
) -> list[CustomerSession]:
    query = db.query(CustomerSession)
    if session_status:
        query = query.filter(CustomerSession.status == session_status)
    if user_id:
        query = query.filter(CustomerSession.user_id == user_id)
    return query.order_by(CustomerSession.id).offset(skip).limit(limit).all()


@router.post("", response_model=SessionRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles("admin", "agent"))])
def create_session(payload: SessionCreate, db: Session = Depends(get_db)) -> CustomerSession:
    if not db.get(User, payload.user_id):
        raise HTTPException(status_code=404, detail="User not found.")

    data = payload.model_dump(exclude={"initial_message"})
    session = CustomerSession(**data)
    db.add(session)
    db.flush()
    if payload.initial_message and payload.initial_message.strip():
        session.last_message_at = datetime.now()
        db.add(
            Message(
                session_id=session.id,
                sender_id=payload.user_id,
                sender_type="customer",
                content=payload.initial_message.strip(),
            )
        )
    db.commit()
    db.refresh(session)
    return session


@router.get("/{session_id}", response_model=SessionRead, dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
def get_session(session_id: int, db: Session = Depends(get_db)) -> CustomerSession:
    session = db.get(CustomerSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return session


@router.get("/{session_id}/messages", response_model=list[MessageRead], dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
def list_messages(session_id: int, db: Session = Depends(get_db)) -> list[Message]:
    if not db.get(CustomerSession, session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    return db.query(Message).filter(Message.session_id == session_id).order_by(Message.id).all()


@router.post("/{session_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles("admin", "agent"))])
def create_message(session_id: int, payload: MessageCreate, db: Session = Depends(get_db)) -> Message:
    session = db.get(CustomerSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    message = Message(session_id=session_id, **payload.model_dump())
    session.last_message_at = datetime.now()
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
