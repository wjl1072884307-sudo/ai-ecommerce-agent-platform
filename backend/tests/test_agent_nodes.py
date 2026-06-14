from app.agent import classify_intent_text


def test_classify_intent_core_cases() -> None:
    assert classify_intent_text("我买的耳机有杂音，可以退货吗？")[0] == "return_request"
    assert classify_intent_text("物流到哪了？")[0] == "logistics_query"
    assert classify_intent_text("我要投诉你们的售后")[0] == "complaint"
    assert classify_intent_text("这个商品还有库存吗？")[0] == "product_inquiry"
    assert classify_intent_text("你好")[0] == "other"

