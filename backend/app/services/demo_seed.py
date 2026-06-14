from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import (
    CustomerSession,
    KnowledgeChunk,
    KnowledgeDocument,
    Message,
    Order,
    Product,
    User,
)


def rebuild_chunks(db: Session, document: KnowledgeDocument) -> None:
    document.chunks.clear()
    paragraphs = [part.strip() for part in document.content.split("\n\n") if part.strip()]
    for index, paragraph in enumerate(paragraphs):
        document.chunks.append(
            KnowledgeChunk(
                chunk_index=index,
                content=paragraph,
                keywords=_extract_keywords(document.document_type, paragraph),
            )
        )


def seed_demo_data(db: Session) -> None:
    if db.query(User).filter(User.username == "customer_demo").first():
        return

    now = datetime.now()

    customer = User(
        username="customer_demo",
        display_name="演示买家",
        role="customer",
        phone="13800000001",
        email="customer@example.com",
    )
    agent = User(
        username="agent_demo",
        display_name="演示客服",
        role="agent",
        phone="13800000002",
        email="agent@example.com",
    )
    reviewer = User(
        username="reviewer_demo",
        display_name="售后主管",
        role="reviewer",
        phone="13800000003",
        email="reviewer@example.com",
    )
    db.add_all([customer, agent, reviewer])
    db.flush()

    headphones = Product(
        name="星云降噪耳机",
        sku="AUDIO-NEBULA-001",
        category="数码音频",
        description="主动降噪蓝牙耳机，支持通透模式和低延迟游戏模式。",
        price=399.0,
        stock=120,
        after_sale_policy="支持 7 天无理由退货；质量问题 15 天内可申请退货或换货。",
    )
    phone = Product(
        name="极光 Pro 手机",
        sku="PHONE-AURORA-PRO",
        category="手机数码",
        description="高性能智能手机，支持快充和高清影像。",
        price=3299.0,
        stock=35,
        after_sale_policy="激活后非质量问题不支持 7 天无理由退货；质量问题按三包政策处理。",
    )
    keyboard = Product(
        name="青轴机械键盘",
        sku="KEYBOARD-BLUE-001",
        category="电脑外设",
        description="有线机械键盘，青轴手感，支持背光。",
        price=259.0,
        stock=80,
        after_sale_policy="支持 7 天无理由退货，影响二次销售除外。",
    )
    db.add_all([headphones, phone, keyboard])
    db.flush()

    db.add_all(
        [
            Order(
                order_no="MOCK202606120001",
                user_id=customer.id,
                product_id=headphones.id,
                quantity=1,
                total_amount=399.0,
                order_status="delivered",
                payment_status="paid",
                logistics_status="delivered",
                tracking_no="SF1000000001",
                paid_at=now - timedelta(days=5),
                shipped_at=now - timedelta(days=4),
                delivered_at=now - timedelta(days=2),
                after_sale_status="none",
            ),
            Order(
                order_no="MOCK202606120002",
                user_id=customer.id,
                product_id=phone.id,
                quantity=1,
                total_amount=3299.0,
                order_status="shipped",
                payment_status="paid",
                logistics_status="shipped",
                tracking_no="JD1000000002",
                paid_at=now - timedelta(days=2),
                shipped_at=now - timedelta(days=1),
                after_sale_status="none",
            ),
            Order(
                order_no="MOCK202606120003",
                user_id=customer.id,
                product_id=keyboard.id,
                quantity=1,
                total_amount=259.0,
                order_status="closed",
                payment_status="refunded",
                logistics_status="delivered",
                tracking_no="YT1000000003",
                paid_at=now - timedelta(days=20),
                shipped_at=now - timedelta(days=19),
                delivered_at=now - timedelta(days=17),
                after_sale_status="done",
            ),
        ]
    )

    session = CustomerSession(
        user_id=customer.id,
        title="耳机售后咨询",
        status="open",
        last_message_at=now,
    )
    db.add(session)
    db.flush()
    db.add(
        Message(
            session_id=session.id,
            sender_id=customer.id,
            sender_type="customer",
            content="我买的耳机有杂音，可以退货吗？",
            message_type="text",
        )
    )

    documents = [
        KnowledgeDocument(
            title="退货退款基础政策",
            document_type="policy",
            content=(
                "消费者签收商品后 7 天内，在商品完好且不影响二次销售的情况下，可以申请 7 天无理由退货。\n\n"
                "如果商品存在质量问题，例如耳机杂音、无法连接、按键失灵等，用户可在签收后 15 天内申请退货或换货，客服需要创建售后工单并进入人工审核。\n\n"
                "超过售后期限或订单金额较高的申请，需要人工审核后再给出最终处理结果。"
            ),
        ),
        KnowledgeDocument(
            title="物流查询处理规范",
            document_type="logistics",
            content=(
                "用户咨询物流时，客服应优先查询订单物流状态和物流单号。\n\n"
                "如果订单已发货但长时间未更新，应创建物流异常工单，并提示用户客服会继续跟进。"
            ),
        ),
        KnowledgeDocument(
            title="投诉问题处理规范",
            document_type="complaint",
            content=(
                "用户表达强烈不满、投诉、差评威胁或监管投诉倾向时，需要提高风险等级。\n\n"
                "投诉类问题应创建人工审核任务，必要时升级给售后主管处理。"
            ),
        ),
    ]
    db.add_all(documents)
    db.flush()
    for document in documents:
        rebuild_chunks(db, document)

    db.commit()


def _extract_keywords(document_type: str, content: str) -> str:
    candidates = [document_type]
    for keyword in ["退货", "退款", "耳机", "杂音", "质量问题", "物流", "投诉", "人工审核", "工单"]:
        if keyword in content:
            candidates.append(keyword)
    return ",".join(dict.fromkeys(candidates))

