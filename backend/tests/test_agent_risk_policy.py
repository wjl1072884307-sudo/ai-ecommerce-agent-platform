from sqlalchemy.orm import Session


def test_high_risk_actions_are_declared_and_require_review():
    from app.agent.policies import HIGH_RISK_ACTIONS, action_requires_human_review

    for action in ["refund", "compensation", "close_ticket", "modify_order_amount", "approve_after_sale"]:
        assert action in HIGH_RISK_ACTIONS
        assert action_requires_human_review(action) is True


def test_refund_request_marks_risk_actions_and_creates_review(db_session: Session):
    from app.agent.nodes import risk_check
    from app.agent.types import AgentContext

    context = AgentContext(
        session_id=1,
        message_id=1,
        run_id=1,
        intent="refund_request",
        message_content="我要退款",
        matched_order={"total_amount": 399.0},
        policy_result={},
    )

    result = risk_check(db_session, context)

    assert result.status == "success"
    assert context.risk_result["need_review"] is True
    assert any(action["action"] == "refund" for action in context.risk_actions)
    assert all(action["requires_human_review"] for action in context.risk_actions)
