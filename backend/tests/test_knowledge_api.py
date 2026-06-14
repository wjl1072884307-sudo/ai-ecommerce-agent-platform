from fastapi.testclient import TestClient


def test_create_document_generates_chunks(client: TestClient) -> None:
    response = client.post(
        "/api/knowledge/documents",
        json={
            "title": "发票规则",
            "document_type": "policy",
            "content": "用户可以申请电子发票。\n\n发票信息错误时，可以联系客服修改。",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "发票规则"
    assert len(data["chunks"]) == 2


def test_update_document_and_rebuild_chunks(client: TestClient) -> None:
    update = client.put(
        "/api/knowledge/documents/1",
        json={"content": "退货政策第一段。\n\n退货政策第二段。\n\n退货政策第三段。"},
    )
    rebuild = client.post("/api/knowledge/documents/1/rebuild-chunks")

    assert update.status_code == 200
    assert len(update.json()["chunks"]) == 3
    assert rebuild.status_code == 200
    assert len(rebuild.json()) == 3


def test_search_knowledge_returns_related_chunks(client: TestClient) -> None:
    response = client.get("/api/knowledge/search", params={"query": "耳机有杂音，可以退货吗？"})

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any("退货" in item["content"] or "杂音" in item["content"] for item in data)

