from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel, TimestampedModel


class SessionCreate(BaseModel):
    user_id: int
    title: str
    status: str = "open"
    initial_message: str | None = None


class SessionRead(TimestampedModel):
    id: int
    user_id: int
    title: str
    status: str
    last_message_at: datetime | None


class MessageCreate(BaseModel):
    sender_id: int | None = None
    sender_type: str
    content: str
    message_type: str = "text"
    metadata_json: str | None = None


class MessageRead(ORMModel):
    id: int
    session_id: int
    sender_id: int | None
    sender_type: str
    content: str
    message_type: str
    metadata_json: str | None
    created_at: datetime
