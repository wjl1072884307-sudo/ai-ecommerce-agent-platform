from pathlib import Path


def test_rag_upgrade_plan_documents_pgvector_path():
    document = Path(__file__).resolve().parents[2] / "RAG_UPGRADE_PLAN.md"

    content = document.read_text(encoding="utf-8")

    assert "KeywordRetriever" in content
    assert "embedding" in content
    assert "pgvector" in content
    assert "chunk" in content
    assert "引用来源" in content

