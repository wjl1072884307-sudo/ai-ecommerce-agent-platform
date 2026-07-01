from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel, TimestampedModel


class SessionCreate(BaseModel):
    user_id: int
    customer_id: int | None = None
    visitor_id: str | None = None
    title: str
    channel: str = "admin_demo"
    conversation_type: str = "after_sales"
    intent: str | None = None
    status: str = "open"
    priority: str = "medium"
    requires_human: bool = False
    bound_order_id: int | None = None
    bound_product_id: int | None = None
    summary: str | None = None
    initial_message: str | None = None


class SessionRead(TimestampedModel):
    id: int
    user_id: int
    customer_id: int | None
    visitor_id: str | None
    title: str
    channel: str
    conversation_type: str
    intent: str | None
    status: str
    priority: str
    requires_human: bool
    bound_order_id: int | None
    bound_product_id: int | None
    summary: str | None
    last_message_at: datetime | None


class MessageCreate(BaseModel):
    sender_id: int | None = None
    sender_type: str
    content: str
    message_type: str = "text"
    language: str = "unknown"
    metadata_json: str | None = None


class MessageRead(ORMModel):
    id: int
    session_id: int
    sender_id: int | None
    sender_type: str
    content: str
    message_type: str
    language: str
    metadata_json: str | None
    created_at: datetime


class CustomerMessageCreate(BaseModel):
    session_id: int | None = None
    customer_id: int | None = None
    visitor_id: str | None = None
    content: str
    channel: str = "web"
    order_no: str | None = None
    conversation_type: str | None = None
    run_agent: bool = True


class CustomerMessageResponse(BaseModel):
    session: SessionRead
    message: MessageRead
    agent_result: dict | None = None
