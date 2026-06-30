from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.agent import run_agent
from app.api.deps import get_current_user, require_roles
from app.audit.service import safe_record_audit_log
from app.database import get_db
from app.models import AgentNodeLog, AgentRun, User
from app.schemas import AgentNodeLogRead, AgentRunCreate, AgentRunRead, AgentRunResult

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/runs", response_model=AgentRunResult, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles("admin", "agent"))])
def create_agent_run(
    payload: AgentRunCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    result = run_agent(db, session_id=payload.session_id, message_id=payload.message_id)
    run = result.get("run")
    safe_record_audit_log(
        db=db,
        action="agent.run_triggered",
        resource_type="agent_run",
        resource_id=getattr(run, "id", None),
        current_user=current_user,
        request=request,
        after={"session_id": payload.session_id, "message_id": payload.message_id},
    )
    db.commit()
    return result


@router.get("/runs", response_model=list[AgentRunRead], dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
def list_agent_runs(
    run_status: str | None = Query(default=None, alias="status"),
    intent: str | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
) -> list[AgentRun]:
    query = db.query(AgentRun)
    if run_status:
        query = query.filter(AgentRun.status == run_status)
    if intent:
        query = query.filter(AgentRun.intent == intent)
    return query.order_by(AgentRun.id.desc()).offset(skip).limit(limit).all()


@router.get("/runs/{run_id}", response_model=AgentRunRead, dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
def get_agent_run(run_id: int, db: Session = Depends(get_db)) -> AgentRun:
    run = db.get(AgentRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Agent run not found.")
    return run


@router.get("/runs/{run_id}/node-logs", response_model=list[AgentNodeLogRead], dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
def list_agent_node_logs(run_id: int, db: Session = Depends(get_db)) -> list[AgentNodeLog]:
    if not db.get(AgentRun, run_id):
        raise HTTPException(status_code=404, detail="Agent run not found.")
    return db.query(AgentNodeLog).filter(AgentNodeLog.run_id == run_id).order_by(AgentNodeLog.id).all()
