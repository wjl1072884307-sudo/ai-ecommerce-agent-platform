from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.database import get_db
from app.models import AuditLog
from app.schemas import AuditLogRead

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("", response_model=list[AuditLogRead], dependencies=[Depends(require_roles("admin"))])
def list_audit_logs(
    action: str | None = None,
    resource_type: str | None = None,
    operator_id: int | None = None,
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
) -> list[AuditLog]:
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if operator_id:
        query = query.filter(AuditLog.operator_id == operator_id)
    return query.order_by(AuditLog.id.desc()).offset(skip).limit(limit).all()
