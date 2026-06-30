HIGH_RISK_ACTIONS = {
    "refund",
    "compensation",
    "close_ticket",
    "modify_order_amount",
    "approve_after_sale",
}


def action_requires_human_review(action: str) -> bool:
    return action in HIGH_RISK_ACTIONS


def build_risk_action(action: str, reason: str) -> dict[str, object]:
    return {
        "action": action,
        "reason": reason,
        "requires_human_review": action_requires_human_review(action),
    }

