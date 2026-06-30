from app.audit.service import record_audit_log
from app.models import AuditLog


def test_record_audit_log_persists_structured_entry(db_session):
    audit_log = record_audit_log(
        db=db_session,
        operator_id=1,
        operator_role="admin",
        action="knowledge.created",
        resource_type="knowledge_document",
        resource_id="42",
        request_id="req-1",
        ip_address="127.0.0.1",
        user_agent="pytest",
        before={"status": "draft"},
        after={"status": "active"},
    )
    db_session.commit()

    saved = db_session.get(AuditLog, audit_log.id)
    assert saved is not None
    assert saved.action == "knowledge.created"
    assert saved.operator_id == 1
    assert saved.operator_role == "admin"
    assert saved.before_json == '{"status":"draft"}'
    assert saved.after_json == '{"status":"active"}'


def test_admin_can_list_audit_logs(client):
    response = client.get("/api/audit-logs")

    assert response.status_code == 200


def test_viewer_cannot_list_audit_logs(unauthenticated_client):
    login_response = unauthenticated_client.post(
        "/api/auth/login",
        json={"username": "viewer_demo", "password": "viewer123456"},
    )
    token = login_response.json()["access_token"]

    response = unauthenticated_client.get(
        "/api/audit-logs",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
