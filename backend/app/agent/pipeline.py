from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.agent.logger import run_logged_node
from app.agent.nodes import (
    check_policy,
    classify_intent,
    create_review_task,
    create_ticket,
    generate_reply_llm,
    query_order,
    receive_message,
    retrieve_knowledge,
    risk_check,
)
from app.agent.types import AgentContext, NodeResult
from app.models import AgentRun, CustomerSession, ReplySuggestion, ReviewTask, Ticket

NODE_SEQUENCE = [
    ("receive_message", receive_message),
    ("classify_intent", classify_intent),
    ("query_order", query_order),
    ("retrieve_knowledge", retrieve_knowledge),
    ("check_policy", check_policy),
    ("risk_check", risk_check),
    ("generate_reply", generate_reply_llm),
    ("create_review_task", create_review_task),
    ("create_ticket", create_ticket),
]


def run_agent(db: Session, session_id: int, message_id: int) -> dict[str, Any]:
    session = db.get(CustomerSession, session_id)
    run = AgentRun(
        session_id=session_id,
        message_id=message_id,
        user_id=session.user_id if session else 0,
        status="running",
        started_at=datetime.now(),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    context = AgentContext(session_id=session_id, message_id=message_id, run_id=run.id)
    failed_result: NodeResult | None = None
    failed_node: str | None = None

    for node_name, node_func in NODE_SEQUENCE:
        result = run_logged_node(db, context, node_name, _context_snapshot(context), node_func)
        if result.status == "failed":
            failed_result = result
            failed_node = node_name
            break

    run.user_id = context.user_id or 0
    run.intent = context.intent
    run.finished_at = datetime.now()
    if failed_result:
        run.status = "failed"
        run.error_message = failed_result.error_message
        run.summary = f"Agent failed: {failed_result.error_message}"
    else:
        run.status = "success"
        run.summary = _build_summary(context)
    db.commit()
    db.refresh(run)

    partial_context = _context_snapshot(context)
    return {
        "run": run,
        "reply_suggestion": db.get(ReplySuggestion, context.reply_suggestion_id)
        if context.reply_suggestion_id
        else None,
        "review_task": db.get(ReviewTask, context.review_task_id) if context.review_task_id else None,
        "ticket": db.get(Ticket, context.ticket_id) if context.ticket_id else None,
        "failed_node": failed_node,
        "partial_context": partial_context,
    }


def _context_snapshot(context: AgentContext) -> dict[str, Any]:
    return {
        "session_id": context.session_id,
        "message_id": context.message_id,
        "run_id": context.run_id,
        "user_id": context.user_id,
        "intent": context.intent,
        "message_content": context.message_content,
        "matched_order": context.matched_order,
        "matched_product": context.matched_product,
        "knowledge_sources": context.knowledge_sources,
        "policy_result": context.policy_result,
        "risk_result": context.risk_result,
        "risk_actions": context.risk_actions,
        "llm_result": context.llm_result,
    }


def _build_summary(context: AgentContext) -> str:
    order_no = context.matched_order["order_no"] if context.matched_order else "未匹配订单"
    return f"intent={context.intent or 'other'}, order={order_no}, review_task={context.review_task_id}, ticket={context.ticket_id}"
