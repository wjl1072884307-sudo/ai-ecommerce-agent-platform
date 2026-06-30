from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentContext:
    session_id: int
    message_id: int
    run_id: int
    user_id: int | None = None
    message_content: str | None = None
    recent_messages: list[dict[str, Any]] = field(default_factory=list)
    intent: str | None = None
    confidence: float = 0.0
    extracted_entities: dict[str, Any] = field(default_factory=dict)
    matched_order: dict[str, Any] | None = None
    matched_product: dict[str, Any] | None = None
    knowledge_chunks: list[dict[str, Any]] = field(default_factory=list)
    knowledge_sources: list[dict[str, Any]] = field(default_factory=list)
    policy_result: dict[str, Any] = field(default_factory=dict)
    risk_result: dict[str, Any] = field(default_factory=dict)
    risk_actions: list[dict[str, Any]] = field(default_factory=list)
    llm_result: dict[str, Any] = field(default_factory=dict)
    reply_suggestion_id: int | None = None
    review_task_id: int | None = None
    ticket_id: int | None = None


@dataclass
class NodeResult:
    status: str
    output: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
