from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.agent import run_agent
from app.api.deps import require_roles
from app.database import get_db
from app.models import Customer, CustomerSession, Message, Order, Product, User
from app.schemas import AgentRunResult, CustomerMessageCreate, CustomerMessageResponse, MessageCreate, MessageRead, SessionCreate, SessionRead

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionRead], dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
def list_sessions(
    session_status: str | None = Query(default=None, alias="status"),
    user_id: int | None = None,
    customer_id: int | None = None,
    visitor_id: str | None = None,
    conversation_type: str | None = None,
    requires_human: bool | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
) -> list[CustomerSession]:
    query = db.query(CustomerSession)
    if session_status:
        query = query.filter(CustomerSession.status == session_status)
    if user_id:
        query = query.filter(CustomerSession.user_id == user_id)
    if customer_id:
        query = query.filter(CustomerSession.customer_id == customer_id)
    if visitor_id:
        query = query.filter(CustomerSession.visitor_id == visitor_id)
    if conversation_type:
        query = query.filter(CustomerSession.conversation_type == conversation_type)
    if requires_human is not None:
        query = query.filter(CustomerSession.requires_human == requires_human)
    return query.order_by(CustomerSession.id).offset(skip).limit(limit).all()


@router.post("", response_model=SessionRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles("admin", "agent"))])
def create_session(payload: SessionCreate, db: Session = Depends(get_db)) -> CustomerSession:
    if not db.get(User, payload.user_id):
        raise HTTPException(status_code=404, detail="User not found.")
    if payload.customer_id and not db.get(Customer, payload.customer_id):
        raise HTTPException(status_code=404, detail="Customer not found.")
    if payload.bound_order_id and not db.get(Order, payload.bound_order_id):
        raise HTTPException(status_code=404, detail="Order not found.")
    if payload.bound_product_id and not db.get(Product, payload.bound_product_id):
        raise HTTPException(status_code=404, detail="Product not found.")

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
                language="unknown",
            )
        )
    db.commit()
    db.refresh(session)
    return session


@router.post("/customer-message", response_model=CustomerMessageResponse, status_code=status.HTTP_201_CREATED)
def receive_customer_message(payload: CustomerMessageCreate, db: Session = Depends(get_db)) -> dict:
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")

    platform_user = db.get(User, 1)
    if not platform_user:
        raise HTTPException(status_code=500, detail="Default platform user not found.")

    if payload.customer_id and not db.get(Customer, payload.customer_id):
        raise HTTPException(status_code=404, detail="Customer not found.")

    order = None
    if payload.order_no:
        order = db.query(Order).filter(Order.order_no == payload.order_no).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found.")

    if payload.session_id:
        session = db.get(CustomerSession, payload.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found.")
    else:
        title = _build_session_title(content)
        session = CustomerSession(
            user_id=platform_user.id,
            customer_id=payload.customer_id,
            visitor_id=None if payload.customer_id else payload.visitor_id,
            title=title,
            channel=payload.channel,
            conversation_type=payload.conversation_type or "other",
            bound_order_id=order.id if order else None,
            bound_product_id=order.product_id if order else None,
            summary=content[:200],
            last_message_at=datetime.now(),
        )
        db.add(session)
        db.flush()

    if payload.customer_id and session.customer_id is None:
        session.customer_id = payload.customer_id
        session.visitor_id = None
    if payload.visitor_id and session.customer_id is None:
        session.visitor_id = payload.visitor_id
    if order:
        session.bound_order_id = order.id
        session.bound_product_id = order.product_id
    if payload.conversation_type:
        session.conversation_type = payload.conversation_type

    message = Message(
        session_id=session.id,
        sender_id=None,
        sender_type="customer",
        content=content,
        message_type="text",
        language="unknown",
    )
    session.last_message_at = datetime.now()
    session.summary = content[:200]
    db.add(message)
    db.commit()
    db.refresh(session)
    db.refresh(message)

    agent_result = None
    if payload.run_agent:
        agent_result = AgentRunResult.model_validate(run_agent(db, session_id=session.id, message_id=message.id)).model_dump(mode="json")
    db.refresh(session)
    return {"session": session, "message": message, "agent_result": agent_result}


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


def _build_session_title(content: str) -> str:
    title = " ".join(content.split())
    return title[:60] or "Customer conversation"
