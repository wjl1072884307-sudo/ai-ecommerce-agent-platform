from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.audit.service import safe_record_audit_log
from app.database import get_db
from app.models import Ticket, TicketStatusLog, User
from app.schemas import TicketRead, TicketStatusLogRead, TicketStatusUpdate
from app.tickets.state_machine import TicketStatus, normalize_ticket_status, validate_transition

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketRead], dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
def list_tickets(
    ticket_status: str | None = Query(default=None, alias="status"),
    ticket_type: str | None = None,
    priority: str | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
) -> list[Ticket]:
    query = db.query(Ticket)
    if ticket_status:
        query = query.filter(Ticket.status == ticket_status)
    if ticket_type:
        query = query.filter(Ticket.ticket_type == ticket_type)
    if priority:
        query = query.filter(Ticket.priority == priority)
    return query.order_by(Ticket.id.desc()).offset(skip).limit(limit).all()


@router.post("/{ticket_id}/claim", response_model=TicketRead, dependencies=[Depends(require_roles("admin", "reviewer", "agent"))])
def claim_ticket(
    ticket_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Ticket:
    ticket = _get_ticket_for_update(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    current_status = normalize_ticket_status(ticket.status)
    if ticket.assignee_id and ticket.assignee_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=409, detail="Ticket has already been claimed.")

    from_status = current_status.value
    ticket.assignee_id = current_user.id
    if current_status == TicketStatus.PENDING:
        ticket.status = TicketStatus.PROCESSING.value
        _add_status_log(
            db=db,
            ticket=ticket,
            from_status=from_status,
            to_status=ticket.status,
            operator_id=current_user.id,
            reason="claim ticket",
        )

    safe_record_audit_log(
        db=db,
        action="ticket.claimed",
        resource_type="ticket",
        resource_id=ticket.id,
        current_user=current_user,
        request=request,
        before={"status": from_status, "assignee_id": None},
        after={"status": ticket.status, "assignee_id": ticket.assignee_id},
    )
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get(
    "/{ticket_id}/status-logs",
    response_model=list[TicketStatusLogRead],
    dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))],
)
def list_ticket_status_logs(ticket_id: int, db: Session = Depends(get_db)) -> list[TicketStatusLog]:
    ticket = _get_ticket_for_update(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    return (
        db.query(TicketStatusLog)
        .filter(TicketStatusLog.ticket_id == ticket_id)
        .order_by(TicketStatusLog.created_at, TicketStatusLog.id)
        .all()
    )


@router.get("/{ticket_id}", response_model=TicketRead, dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
def get_ticket(ticket_id: int, db: Session = Depends(get_db)) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    return ticket


@router.post("/{ticket_id}/status", response_model=TicketRead, dependencies=[Depends(require_roles("admin", "reviewer", "agent"))])
def update_ticket_status(
    ticket_id: int,
    payload: TicketStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Ticket:
    ticket = _get_ticket_for_update(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    if ticket.assignee_id and ticket.assignee_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only the assignee or admin can update this ticket.")

    try:
        from_status = normalize_ticket_status(ticket.status).value
        to_status = normalize_ticket_status(payload.status).value
        validate_transition(from_status, to_status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    ticket.status = to_status
    ticket.resolution = payload.resolution
    if to_status in {"resolved", "closed", "cancelled"}:
        ticket.closed_at = datetime.now()
    else:
        ticket.closed_at = None
    _add_status_log(
        db=db,
        ticket=ticket,
        from_status=from_status,
        to_status=to_status,
        operator_id=current_user.id,
        reason=payload.reason,
    )

    safe_record_audit_log(
        db=db,
        action="ticket.status_changed",
        resource_type="ticket",
        resource_id=ticket.id,
        current_user=current_user,
        request=request,
        before={"status": from_status},
        after={"status": to_status, "resolution": ticket.resolution},
    )
    db.commit()
    db.refresh(ticket)
    return ticket


def _add_status_log(
    *,
    db: Session,
    ticket: Ticket,
    from_status: str,
    to_status: str,
    operator_id: int,
    reason: str,
) -> None:
    db.add(
        TicketStatusLog(
            ticket=ticket,
            from_status=from_status,
            to_status=to_status,
            operator_id=operator_id,
            reason=reason,
        )
    )


def _get_ticket_for_update(db: Session, ticket_id: int) -> Ticket | None:
    return db.query(Ticket).filter(Ticket.id == ticket_id).with_for_update().one_or_none()
