from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.agent.nodes import check_policy, retrieve_knowledge, risk_check
from app.agent.types import AgentContext


def test_retrieve_knowledge_finds_return_policy(db_session: Session) -> None:
    context = AgentContext(
        session_id=1,
        message_id=1,
        run_id=1,
        user_id=1,
        intent="return_request",
        message_content="我买的耳机有杂音，可以退货吗？",
        matched_product={"name": "星云降噪耳机", "category": "数码音频"},
    )

    result = retrieve_knowledge(db_session, context)

    assert result.status == "success"
    assert context.knowledge_chunks
    assert any("退货" in chunk["content"] for chunk in context.knowledge_chunks)


def test_check_policy_allows_quality_return_within_15_days(db_session: Session) -> None:
    context = AgentContext(
        session_id=1,
        message_id=1,
        run_id=1,
        intent="return_request",
        message_content="耳机有杂音，可以退货吗？",
        matched_order={
            "id": 1,
            "order_no": "MOCK202606120001",
            "total_amount": 399.0,
            "delivered_at": datetime.now() - timedelta(days=2),
        },
    )

    result = check_policy(db_session, context)

    assert result.status == "success"
    assert context.policy_result["allow_return"] is True
    assert context.policy_result["need_ticket"] is True
    assert context.policy_result["is_quality_issue"] is True


def test_check_policy_marks_overdue_return_for_manual_review(db_session: Session) -> None:
    context = AgentContext(
        session_id=1,
        message_id=1,
        run_id=1,
        intent="return_request",
        message_content="这个键盘还能退货吗？",
        matched_order={
            "id": 3,
            "order_no": "MOCK202606120003",
            "total_amount": 259.0,
            "delivered_at": datetime.now() - timedelta(days=20),
        },
    )

    result = check_policy(db_session, context)

    assert result.status == "success"
    assert context.policy_result["allow_return"] is False
    assert context.policy_result["is_over_after_sale_period"] is True


def test_risk_check_flags_return_complaint_and_high_amount(db_session: Session) -> None:
    return_context = AgentContext(
        session_id=1,
        message_id=1,
        run_id=1,
        intent="return_request",
        message_content="我要退货",
        matched_order={"total_amount": 399.0},
        policy_result={"is_over_after_sale_period": False},
    )
    complaint_context = AgentContext(
        session_id=1,
        message_id=1,
        run_id=1,
        intent="complaint",
        message_content="我要投诉你们",
        matched_order={"total_amount": 399.0},
        policy_result={},
    )
    high_amount_context = AgentContext(
        session_id=1,
        message_id=1,
        run_id=1,
        intent="refund_request",
        message_content="我要退款",
        matched_order={"total_amount": 3299.0},
        policy_result={},
    )

    risk_check(db_session, return_context)
    risk_check(db_session, complaint_context)
    risk_check(db_session, high_amount_context)

    assert return_context.risk_result["need_review"] is True
    assert return_context.risk_result["risk_level"] == "medium"
    assert complaint_context.risk_result["risk_level"] == "medium"
    assert high_amount_context.risk_result["risk_level"] == "high"

