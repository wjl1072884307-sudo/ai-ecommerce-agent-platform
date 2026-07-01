from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.security import hash_password
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
    if db.query(User).filter(User.username == "admin_demo").first():
        return

    now = datetime.now()

    customer = User(
        username="customer_demo",
        display_name="演示买家",
        role="viewer",
        password_hash=hash_password("customer123456"),
        phone="13800000001",
        email="customer@example.com",
    )
    admin = User(
        username="admin_demo",
        display_name="Admin Demo",
        role="admin",
        password_hash=hash_password("admin123456"),
        phone="13800000000",
        email="admin@example.com",
    )
    agent = User(
        username="agent_demo",
        display_name="演示客服",
        role="agent",
        password_hash=hash_password("agent123456"),
        phone="13800000002",
        email="agent@example.com",
    )
    reviewer = User(
        username="reviewer_demo",
        display_name="售后主管",
        role="reviewer",
        password_hash=hash_password("reviewer123456"),
        phone="13800000003",
        email="reviewer@example.com",
    )
    viewer = User(
        username="viewer_demo",
        display_name="Viewer Demo",
        role="viewer",
        password_hash=hash_password("viewer123456"),
        phone="13800000004",
        email="viewer@example.com",
    )
    db.add_all([customer, admin, agent, reviewer, viewer])
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
    monitor = Product(
        name="Aurora 27-inch Monitor",
        sku="MONITOR-AURORA-027",
        category="Computer Display",
        description="27-inch 2K office monitor with adjustable stand.",
        price=1299.0,
        stock=42,
        after_sale_policy="Supports 7-day return and 15-day exchange for quality issues.",
    )
    smartwatch = Product(
        name="Pulse Fit Smartwatch",
        sku="WATCH-PULSE-FIT",
        category="Wearable",
        description="Smartwatch with heart-rate monitoring and long battery mode.",
        price=699.0,
        stock=66,
        after_sale_policy="Battery or sensor issues can enter warranty review within 15 days.",
    )
    charger = Product(
        name="GaN Fast Charger 65W",
        sku="CHARGER-GAN-065",
        category="Phone Accessory",
        description="Dual-port 65W fast charger for phone and laptop charging.",
        price=159.0,
        stock=150,
        after_sale_policy="Accessories support replacement for verified charging failures.",
    )
    speaker = Product(
        name="Mini Bluetooth Speaker",
        sku="SPEAKER-MINI-BT",
        category="Audio",
        description="Portable Bluetooth speaker with waterproof shell.",
        price=199.0,
        stock=95,
        after_sale_policy="Audio distortion or connection failures can request exchange.",
    )
    db.add_all([headphones, phone, keyboard, monitor, smartwatch, charger, speaker])
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
            Order(
                order_no="MOCK202606120004",
                user_id=customer.id,
                product_id=monitor.id,
                quantity=1,
                total_amount=1299.0,
                order_status="shipped",
                payment_status="paid",
                logistics_status="in_transit",
                tracking_no="SF1000000004",
                paid_at=now - timedelta(days=1),
                shipped_at=now - timedelta(hours=12),
                after_sale_status="none",
            ),
            Order(
                order_no="MOCK202606120005",
                user_id=customer.id,
                product_id=smartwatch.id,
                quantity=1,
                total_amount=699.0,
                order_status="delivered",
                payment_status="paid",
                logistics_status="delivered",
                tracking_no="JD1000000005",
                paid_at=now - timedelta(days=9),
                shipped_at=now - timedelta(days=8),
                delivered_at=now - timedelta(days=6),
                after_sale_status="reviewing",
            ),
            Order(
                order_no="MOCK202606120006",
                user_id=customer.id,
                product_id=charger.id,
                quantity=2,
                total_amount=318.0,
                order_status="paid",
                payment_status="paid",
                logistics_status="pending",
                tracking_no=None,
                paid_at=now - timedelta(hours=6),
                after_sale_status="none",
            ),
            Order(
                order_no="MOCK202606120007",
                user_id=customer.id,
                product_id=speaker.id,
                quantity=1,
                total_amount=199.0,
                order_status="delivered",
                payment_status="refunded",
                logistics_status="delivered",
                tracking_no="YT1000000007",
                paid_at=now - timedelta(days=18),
                shipped_at=now - timedelta(days=17),
                delivered_at=now - timedelta(days=15),
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

    extra_session_specs = [
        (
            "Monitor logistics delay",
            "My monitor has shipped but tracking has not updated. Can you check it?",
            "open",
            1,
        ),
        (
            "Smartwatch battery complaint",
            "The smartwatch battery drains too fast and I want after-sales support.",
            "open",
            2,
        ),
        (
            "Charger invoice request",
            "I bought two chargers and need help with invoice and delivery timing.",
            "open",
            3,
        ),
        (
            "Speaker refund follow-up",
            "The speaker refund is marked complete, but I have not received the money.",
            "closed",
            4,
        ),
    ]
    for title, content, session_status, offset in extra_session_specs:
        extra_session = CustomerSession(
            user_id=customer.id,
            title=title,
            status=session_status,
            last_message_at=now - timedelta(minutes=offset * 8),
        )
        db.add(extra_session)
        db.flush()
        db.add(
            Message(
                session_id=extra_session.id,
                sender_id=customer.id,
                sender_type="customer",
                content=content,
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
        KnowledgeDocument(
            title="手机屏幕保护膜售后政策",
            document_type="policy",
            content=(
                "手机屏幕保护膜、钢化膜、手机屏保等配件如出现边缘翘起、气泡、破损、无法贴合等问题，用户可在签收后 7 天内联系客服申请补发或更换。\n\n"
                "如果保护膜已经明显人为损坏或超过售后期限，需要人工审核后判断是否支持补发。\n\n"
                "手机配件补发类问题通常不直接退款，优先创建售后工单并记录用户诉求。"
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
    for keyword in [
        "退货",
        "退款",
        "耳机",
        "杂音",
        "质量问题",
        "物流",
        "投诉",
        "人工审核",
        "工单",
        "手机",
        "屏保",
        "保护膜",
        "钢化膜",
        "补发",
        "更换",
        "翘起",
    ]:
        if keyword in content:
            candidates.append(keyword)
    return ",".join(dict.fromkeys(candidates))
