import json
import logging
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.models import AuditLog, User

logger = logging.getLogger(__name__)


def record_audit_log(
    *,
    db: Session,
    action: str,
    resource_type: str,
    operator_id: int | None = None,
    operator_role: str | None = None,
    resource_id: str | int | None = None,
    request_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        operator_id=operator_id,
        operator_role=operator_role,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        request_id=request_id,
        ip_address=ip_address,
        user_agent=user_agent,
        before_json=_dump_json(before),
        after_json=_dump_json(after),
    )
    db.add(audit_log)
    return audit_log


def safe_record_audit_log(
    *,
    db: Session,
    action: str,
    resource_type: str,
    current_user: User | None = None,
    request: Request | None = None,
    operator_id: int | None = None,
    operator_role: str | None = None,
    resource_id: str | int | None = None,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
) -> AuditLog | None:
    try:
        return record_audit_log(
            db=db,
            operator_id=operator_id if operator_id is not None else getattr(current_user, "id", None),
            operator_role=operator_role if operator_role is not None else getattr(current_user, "role", None),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            request_id=_request_id(request),
            ip_address=_ip_address(request),
            user_agent=_user_agent(request),
            before=before,
            after=after,
        )
    except Exception:
        logger.warning("Failed to record audit log for action=%s", action, exc_info=True)
        return None


def _dump_json(value: dict[str, Any] | None) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)


def _request_id(request: Request | None) -> str | None:
    if request is None:
        return None
    return request.headers.get("X-Request-ID")


def _ip_address(request: Request | None) -> str | None:
    if request is None or request.client is None:
        return None
    return request.client.host


def _user_agent(request: Request | None) -> str | None:
    if request is None:
        return None
    return request.headers.get("User-Agent")
