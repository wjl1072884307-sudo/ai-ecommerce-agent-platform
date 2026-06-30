from datetime import datetime

from app.schemas.common import ORMModel


class AuditLogRead(ORMModel):
    id: int
    operator_id: int | None
    operator_role: str | None
    action: str
    resource_type: str
    resource_id: str | None
    request_id: str | None
    ip_address: str | None
    user_agent: str | None
    before_json: str | None
    after_json: str | None
    created_at: datetime
