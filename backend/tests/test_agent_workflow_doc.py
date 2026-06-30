from pathlib import Path


def test_agent_workflow_document_describes_nodes_and_high_risk_rules():
    document = Path(__file__).resolve().parents[2] / "AGENT_WORKFLOW.md"

    content = document.read_text(encoding="utf-8")

    for node in [
        "receive_message",
        "classify_intent",
        "query_order",
        "retrieve_knowledge",
        "check_policy",
        "risk_check",
        "generate_reply",
        "create_review_task",
        "create_ticket",
    ]:
        assert node in content
    assert "高风险" in content
    assert "refund" in content
    assert "failed_node" in content

