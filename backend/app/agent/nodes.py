from datetime import datetime
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.agent.types import AgentContext, NodeResult
from app.models import (
    CustomerSession,
    KnowledgeChunk,
    KnowledgeDocument,
    Message,
    Order,
    Product,
    ReplySuggestion,
    ReviewTask,
    Ticket,
)

RETURN_INTENTS = {"return_request", "refund_request", "complaint"}


def receive_message(db: Session, context: AgentContext) -> NodeResult:
    message = db.get(Message, context.message_id)
    session = db.get(CustomerSession, context.session_id)
    if not message or not session or message.session_id != session.id:
        return NodeResult(status="failed", error_message="Message or session not found.")

    recent_messages = (
        db.query(Message)
        .filter(Message.session_id == session.id)
        .order_by(Message.id.desc())
        .limit(5)
        .all()
    )
    recent_messages.reverse()

    context.user_id = session.user_id
    context.message_content = message.content
    context.recent_messages = [
        {
            "id": item.id,
            "sender_type": item.sender_type,
            "content": item.content,
            "created_at": item.created_at,
        }
        for item in recent_messages
    ]
    return NodeResult(
        status="success",
        output={
            "user_id": context.user_id,
            "message_content": context.message_content,
            "recent_messages": context.recent_messages,
        },
    )


def classify_intent(db: Session, context: AgentContext) -> NodeResult:
    content = context.message_content or ""
    intent, confidence = classify_intent_text(content)
    context.intent = intent
    context.confidence = confidence
    context.extracted_entities = {"keywords": extract_known_terms(content)}
    return NodeResult(
        status="success",
        output={
            "intent": intent,
            "confidence": confidence,
            "extracted_entities": context.extracted_entities,
        },
    )


def classify_intent_text(content: str) -> tuple[str, float]:
    rules: list[tuple[str, list[str], float]] = [
        ("complaint", ["投诉", "差评", "生气", "监管", "12315", "太差", "不满意"], 0.9),
        ("refund_request", ["退款", "退钱", "返钱"], 0.9),
        ("return_request", ["退货", "退掉", "可以退", "七天无理由", "质量问题", "杂音", "坏了"], 0.88),
        ("logistics_query", ["物流", "快递", "到哪", "运到", "配送", "单号"], 0.86),
        ("order_query", ["订单", "下单", "购买记录", "订单号"], 0.82),
        ("product_inquiry", ["商品", "库存", "价格", "参数", "型号", "保修"], 0.78),
    ]
    for intent, keywords, confidence in rules:
        if any(keyword in content for keyword in keywords):
            return intent, confidence
    return "other", 0.45


def query_order(db: Session, context: AgentContext) -> NodeResult:
    if context.user_id is None:
        return NodeResult(status="failed", error_message="Missing user_id.")

    orders = (
        db.query(Order)
        .options(joinedload(Order.product))
        .filter(Order.user_id == context.user_id)
        .order_by(Order.id.desc())
        .all()
    )
    if not orders:
        context.matched_order = None
        context.matched_product = None
        return NodeResult(status="success", output={"matched_order": None, "match_reason": "no_order"})

    content = context.message_content or ""
    matched_order = None
    match_reason = "latest_order"
    for order in orders:
        product = order.product
        if product and (product.name in content or any(term in product.name for term in extract_known_terms(content))):
            matched_order = order
            match_reason = "product_keyword"
            break

    if matched_order is None:
        matched_order = orders[0]

    context.matched_order = _order_to_dict(matched_order)
    context.matched_product = _product_to_dict(matched_order.product) if matched_order.product else None
    return NodeResult(
        status="success",
        output={
            "matched_order": context.matched_order,
            "matched_product": context.matched_product,
            "match_reason": match_reason,
        },
    )


def retrieve_knowledge(db: Session, context: AgentContext) -> NodeResult:
    terms = extract_known_terms(context.message_content or "")
    if context.intent:
        terms.append(context.intent)
    if context.matched_product:
        terms.extend([context.matched_product["name"], context.matched_product["category"]])

    query = db.query(KnowledgeChunk, KnowledgeDocument).join(KnowledgeDocument)
    filters = []
    for term in dict.fromkeys(terms):
        filters.append(KnowledgeChunk.content.ilike(f"%{term}%"))
        filters.append(KnowledgeChunk.keywords.ilike(f"%{term}%"))
        filters.append(KnowledgeDocument.title.ilike(f"%{term}%"))

    rows = query.filter(or_(*filters)).order_by(KnowledgeChunk.id).limit(5).all() if filters else []
    context.knowledge_chunks = [
        {
            "id": chunk.id,
            "document_id": chunk.document_id,
            "document_title": document.title,
            "document_type": document.document_type,
            "content": chunk.content,
            "keywords": chunk.keywords,
        }
        for chunk, document in rows
    ]
    return NodeResult(status="success", output={"knowledge_chunks": context.knowledge_chunks})


def check_policy(db: Session, context: AgentContext) -> NodeResult:
    order = context.matched_order
    content = context.message_content or ""
    result: dict[str, Any] = {
        "allow_return": False,
        "allow_refund": False,
        "need_ticket": context.intent in RETURN_INTENTS,
        "reason": "未匹配到明确售后规则。",
        "days_since_delivered": None,
        "is_quality_issue": any(term in content for term in ["质量问题", "杂音", "坏了", "无法连接", "失灵"]),
        "is_over_after_sale_period": False,
    }

    if not order:
        result["reason"] = "未找到关联订单，需要人工确认。"
        result["need_ticket"] = context.intent in RETURN_INTENTS
        context.policy_result = result
        return NodeResult(status="success", output=result)

    delivered_at = order.get("delivered_at")
    days_since_delivered = _days_since(delivered_at)
    result["days_since_delivered"] = days_since_delivered

    if context.intent == "return_request":
        if result["is_quality_issue"] and days_since_delivered is not None and days_since_delivered <= 15:
            result.update(allow_return=True, reason="商品疑似质量问题，签收 15 天内可申请退货或换货。")
        elif days_since_delivered is not None and days_since_delivered <= 7:
            result.update(allow_return=True, reason="签收 7 天内，满足基础退货申请条件。")
        else:
            result.update(
                reason="订单可能超过直接退货期限，需要人工审核确认。",
                is_over_after_sale_period=True,
            )
    elif context.intent == "refund_request":
        result.update(allow_refund=True, reason="退款申请需要结合订单和售后状态进入人工审核。")
    elif context.intent == "complaint":
        result.update(reason="投诉类问题需要创建工单并进入人工审核。")
    else:
        result.update(need_ticket=False, reason="非售后申请，暂不需要创建售后工单。")

    context.policy_result = result
    return NodeResult(status="success", output=result)


def risk_check(db: Session, context: AgentContext) -> NodeResult:
    reasons: list[str] = []
    risk_level = "low"
    need_review = False
    content = context.message_content or ""
    amount = context.matched_order["total_amount"] if context.matched_order else 0

    if context.intent in {"return_request", "refund_request"}:
        need_review = True
        reasons.append("退货或退款申请需要人工审核。")
    if context.intent == "complaint" or any(term in content for term in ["投诉", "差评", "监管", "12315", "生气"]):
        need_review = True
        risk_level = "medium"
        reasons.append("投诉或强负面情绪需要升级处理。")
    if amount >= 1000:
        need_review = True
        risk_level = "high"
        reasons.append("订单金额较高，需要人工确认。")
    if context.policy_result.get("is_over_after_sale_period"):
        need_review = True
        risk_level = "medium" if risk_level == "low" else risk_level
        reasons.append("售后期限可能超期。")

    if need_review and risk_level == "low":
        risk_level = "medium"

    context.risk_result = {
        "need_review": need_review,
        "risk_level": risk_level,
        "risk_reasons": reasons,
    }
    return NodeResult(status="success", output=context.risk_result)


def generate_reply(db: Session, context: AgentContext) -> NodeResult:
    order_no = context.matched_order["order_no"] if context.matched_order else "未匹配到订单"
    product_name = context.matched_product["name"] if context.matched_product else "相关商品"
    policy_reason = context.policy_result.get("reason", "我们会进一步核实售后政策。")
    review_note = "该回复需要人工审核后发送。" if context.risk_result.get("need_review") else "该回复可直接发送。"
    content = (
        f"您好，已为您查询到订单 {order_no}，商品为{product_name}。"
        f"{policy_reason}{review_note}"
    )
    source_summary = "；".join(chunk["document_title"] for chunk in context.knowledge_chunks[:3]) or "基于订单与售后规则判断"
    suggestion = ReplySuggestion(
        run_id=context.run_id,
        session_id=context.session_id,
        message_id=context.message_id,
        content=content,
        intent=context.intent or "other",
        confidence=context.confidence,
        status="pending_review" if context.risk_result.get("need_review") else "draft",
        source_summary=source_summary,
    )
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)
    context.reply_suggestion_id = suggestion.id
    return NodeResult(
        status="success",
        output={
            "reply_suggestion_id": suggestion.id,
            "content": suggestion.content,
            "status": suggestion.status,
            "source_summary": suggestion.source_summary,
        },
    )


def create_review_task(db: Session, context: AgentContext) -> NodeResult:
    if not context.risk_result.get("need_review"):
        return NodeResult(status="skipped", output={"reason": "review_not_required"})
    if context.reply_suggestion_id is None:
        return NodeResult(status="failed", error_message="Missing reply_suggestion_id.")

    task = ReviewTask(
        run_id=context.run_id,
        reply_suggestion_id=context.reply_suggestion_id,
        task_type="reply_review" if context.intent != "complaint" else "complaint_review",
        title=f"审核 {context.intent or 'other'} 回复建议",
        risk_level=context.risk_result.get("risk_level", "medium"),
        risk_reason="；".join(context.risk_result.get("risk_reasons", [])),
        status="pending",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    context.review_task_id = task.id
    return NodeResult(
        status="success",
        output={
            "review_task_id": task.id,
            "status": task.status,
            "risk_level": task.risk_level,
            "risk_reason": task.risk_reason,
        },
    )


def create_ticket(db: Session, context: AgentContext) -> NodeResult:
    if not context.policy_result.get("need_ticket"):
        return NodeResult(status="skipped", output={"reason": "ticket_not_required"})
    if context.user_id is None:
        return NodeResult(status="failed", error_message="Missing user_id.")

    ticket_type = {
        "return_request": "return",
        "refund_request": "refund",
        "complaint": "complaint",
        "logistics_query": "logistics",
    }.get(context.intent or "", "other")
    ticket = Ticket(
        ticket_no=f"TK{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        ticket_type=ticket_type,
        user_id=context.user_id,
        order_id=context.matched_order["id"] if context.matched_order else None,
        session_id=context.session_id,
        run_id=context.run_id,
        title=f"{ticket_type} 售后工单",
        description=context.message_content or "",
        priority=context.risk_result.get("risk_level", "medium"),
        status="open",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    context.ticket_id = ticket.id
    return NodeResult(
        status="success",
        output={
            "ticket_id": ticket.id,
            "ticket_no": ticket.ticket_no,
            "ticket_type": ticket.ticket_type,
            "status": ticket.status,
        },
    )


def extract_known_terms(content: str) -> list[str]:
    terms = ["退货", "退款", "耳机", "杂音", "质量问题", "物流", "投诉", "订单", "手机", "键盘"]
    return [term for term in terms if term in content]


def _days_since(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return (datetime.now() - value).days


def _order_to_dict(order: Order) -> dict[str, Any]:
    return {
        "id": order.id,
        "order_no": order.order_no,
        "user_id": order.user_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "total_amount": order.total_amount,
        "order_status": order.order_status,
        "payment_status": order.payment_status,
        "logistics_status": order.logistics_status,
        "tracking_no": order.tracking_no,
        "paid_at": order.paid_at,
        "shipped_at": order.shipped_at,
        "delivered_at": order.delivered_at,
        "after_sale_status": order.after_sale_status,
    }


def _product_to_dict(product: Product) -> dict[str, Any]:
    return {
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "category": product.category,
        "price": product.price,
        "after_sale_policy": product.after_sale_policy,
    }

