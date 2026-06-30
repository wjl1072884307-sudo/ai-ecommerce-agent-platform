from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel, TimestampedModel


class AgentRunCreate(BaseModel):
    session_id: int
    message_id: int


class AgentRunRead(ORMModel):
    id: int
    session_id: int
    message_id: int
    user_id: int
    intent: str | None
    status: str
    summary: str | None
    started_at: datetime | None
    finished_at: datetime | None
    error_message: str | None
    created_at: datetime


class AgentNodeLogRead(ORMModel):
    id: int
    run_id: int
    node_name: str
    status: str
    input_json: str | None
    output_json: str | None
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    duration_ms: int | None
    created_at: datetime


class ReplySuggestionRead(TimestampedModel):
    id: int
    run_id: int
    session_id: int
    message_id: int
    content: str
    intent: str
    confidence: float
    status: str
    source_summary: str | None


class ReviewTaskRead(TimestampedModel):
    id: int
    run_id: int
    reply_suggestion_id: int
    task_type: str
    title: str
    risk_level: str
    risk_reason: str | None
    status: str
    reviewer_id: int | None
    review_comment: str | None
    reviewed_at: datetime | None


class TicketRead(TimestampedModel):
    id: int
    ticket_no: str
    ticket_type: str
    user_id: int
    order_id: int | None
    session_id: int | None
    run_id: int | None
    title: str
    description: str
    priority: str
    status: str
    assignee_id: int | None
    resolution: str | None
    closed_at: datetime | None


class AgentRunResult(BaseModel):
    run: AgentRunRead
    reply_suggestion: ReplySuggestionRead | None
    review_task: ReviewTaskRead | None
    ticket: TicketRead | None
    failed_node: str | None = None
    partial_context: dict | None = None
