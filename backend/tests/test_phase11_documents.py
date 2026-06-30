from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_readme_covers_delivery_basics():
    content = _read("README.md")

    for marker in [
        "Architecture",
        "Tech Stack",
        "Local Startup",
        "Docker Compose MVP Run",
        "Default Accounts",
        "Demo Flow",
        "Core API",
        "Testing",
    ]:
        assert marker in content


def test_deployment_document_covers_operational_runbook():
    content = _read("DEPLOYMENT.md")

    for marker in [
        "Environment Variables",
        "Docker Compose Deployment",
        "PostgreSQL Initialization",
        "Alembic",
        "Health Checks",
        "Logs",
        "Production Safety Checklist",
        "Troubleshooting",
    ]:
        assert marker in content


def test_online_upgrade_plan_documents_phase_delivery_controls():
    content = _read("ONLINE_UPGRADE_PLAN.md")

    for phase in [f"Phase {number}" for number in range(1, 12)]:
        assert phase in content
    assert "Rollback" in content
    assert "Validation" in content


def test_api_design_documents_auth_roles_and_error_codes():
    content = _read("API_DESIGN.md")

    for marker in [
        "Public Endpoints",
        "Protected Endpoints",
        "Role Matrix",
        "400",
        "401",
        "403",
        "404",
        "409",
        "500",
    ]:
        assert marker in content


def test_specialized_design_documents_are_complete_enough():
    database = _read("DATABASE_DESIGN.md")
    agent = _read("AGENT_WORKFLOW.md")
    rag = _read("RAG_UPGRADE_PLAN.md")

    for marker in ["Core Tables", "Index Strategy", "SQLite", "PostgreSQL", "Alembic"]:
        assert marker in database
    for marker in ["Pipeline Nodes", "Context Contract", "Node Logging", "Failure Response"]:
        assert marker in agent
    for marker in ["KeywordRetriever", "embedding", "pgvector", "Evaluation Metrics"]:
        assert marker in rag
