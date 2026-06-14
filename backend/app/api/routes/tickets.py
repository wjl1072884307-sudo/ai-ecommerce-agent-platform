from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Ticket
from app.schemas import TicketRead, TicketStatusUpdate

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketRead])
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


@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    return ticket


@router.post("/{ticket_id}/status", response_model=TicketRead)
def update_ticket_status(ticket_id: int, payload: TicketStatusUpdate, db: Session = Depends(get_db)) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    ticket.status = payload.status
    ticket.resolution = payload.resolution
    if payload.status in {"resolved", "closed"}:
        ticket.closed_at = datetime.now()

    db.commit()
    db.refresh(ticket)
    return ticket

