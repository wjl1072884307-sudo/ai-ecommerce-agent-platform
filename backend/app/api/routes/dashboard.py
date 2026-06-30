from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.database import get_db
from app.models import AgentRun, CustomerSession, Order, Product, ReviewTask, Ticket
from app.schemas import DashboardSummary, StatItem

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary, dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
def get_dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummary:
    agent_run_count = db.query(AgentRun).count()
    success_count = db.query(AgentRun).filter(AgentRun.status == "success").count()
    success_rate = round(success_count / agent_run_count, 4) if agent_run_count else 0

    return DashboardSummary(
        session_count=db.query(CustomerSession).count(),
        product_count=db.query(Product).filter(Product.status != "deleted").count(),
        order_count=db.query(Order).filter(Order.order_status != "deleted").count(),
        pending_review_count=db.query(ReviewTask).filter(ReviewTask.status == "pending").count(),
        open_ticket_count=db.query(Ticket).filter(Ticket.status.in_(["open", "processing"])).count(),
        agent_run_count=agent_run_count,
        agent_success_rate=success_rate,
    )


@router.get("/intent-stats", response_model=list[StatItem], dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
def get_intent_stats(db: Session = Depends(get_db)) -> list[StatItem]:
    rows = db.query(AgentRun.intent).all()
    stats: dict[str, int] = {}
    for (intent,) in rows:
        key = intent or "unknown"
        stats[key] = stats.get(key, 0) + 1
    return [StatItem(name=name, value=value) for name, value in sorted(stats.items())]


@router.get("/ticket-stats", response_model=list[StatItem], dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
def get_ticket_stats(db: Session = Depends(get_db)) -> list[StatItem]:
    rows = db.query(Ticket.status).all()
    stats: dict[str, int] = {}
    for (ticket_status,) in rows:
        stats[ticket_status] = stats.get(ticket_status, 0) + 1
    return [StatItem(name=name, value=value) for name, value in sorted(stats.items())]
