from fastapi.testclient import TestClient


def test_search_knowledge_returns_score_and_metadata(client: TestClient):
    response = client.get("/api/knowledge/search", params={"query": "耳机 杂音 退货"})

    assert response.status_code == 200
    data = response.json()
    assert data
    assert "score" in data[0]
    assert "metadata" in data[0]
    assert data[0]["metadata"]["retriever"] == "keyword"

