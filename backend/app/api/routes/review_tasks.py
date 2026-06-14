from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ReplySuggestion, ReviewTask
from app.schemas import ReviewAction, ReviewTaskRead

router = APIRouter(prefix="/review-tasks", tags=["review-tasks"])


@router.get("", response_model=list[ReviewTaskRead])
def list_review_tasks(
    task_status: str | None = Query(default=None, alias="status"),
    risk_level: str | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
) -> list[ReviewTask]:
    query = db.query(ReviewTask)
    if task_status:
        query = query.filter(ReviewTask.status == task_status)
    if risk_level:
        query = query.filter(ReviewTask.risk_level == risk_level)
    return query.order_by(ReviewTask.id.desc()).offset(skip).limit(limit).all()


@router.get("/{task_id}", response_model=ReviewTaskRead)
def get_review_task(task_id: int, db: Session = Depends(get_db)) -> ReviewTask:
    task = db.get(ReviewTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Review task not found.")
    return task


@router.post("/{task_id}/approve", response_model=ReviewTaskRead)
def approve_review_task(task_id: int, payload: ReviewAction, db: Session = Depends(get_db)) -> ReviewTask:
    task = _get_task(db, task_id)
    task.status = "approved"
    task.reviewer_id = payload.reviewer_id
    task.review_comment = payload.review_comment
    task.reviewed_at = datetime.now()

    suggestion = db.get(ReplySuggestion, task.reply_suggestion_id)
    if suggestion:
        suggestion.status = "approved"
        if payload.final_reply:
            suggestion.content = payload.final_reply

    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/reject", response_model=ReviewTaskRead)
def reject_review_task(task_id: int, payload: ReviewAction, db: Session = Depends(get_db)) -> ReviewTask:
    task = _get_task(db, task_id)
    task.status = "rejected"
    task.reviewer_id = payload.reviewer_id
    task.review_comment = payload.review_comment
    task.reviewed_at = datetime.now()

    suggestion = db.get(ReplySuggestion, task.reply_suggestion_id)
    if suggestion:
        suggestion.status = "rejected"

    db.commit()
    db.refresh(task)
    return task


def _get_task(db: Session, task_id: int) -> ReviewTask:
    task = db.get(ReviewTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Review task not found.")
    return task

