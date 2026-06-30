from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.audit.service import safe_record_audit_log
from app.core.security import create_access_token, verify_password
from app.database import get_db
from app.models import User
from app.schemas import CurrentUserRead, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or user.status != "active" or not verify_password(payload.password, user.password_hash):
        safe_record_audit_log(
            db=db,
            action="auth.login.failed",
            resource_type="auth",
            request=request,
            operator_id=getattr(user, "id", None),
            operator_role=getattr(user, "role", None),
            after={"username": payload.username, "success": False},
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

    token = create_access_token(str(user.id))
    safe_record_audit_log(
        db=db,
        action="auth.login.success",
        resource_type="auth",
        request=request,
        operator_id=user.id,
        operator_role=user.role,
        resource_id=user.id,
        after={"username": user.username, "success": True},
    )
    db.commit()
    return TokenResponse(access_token=token)


@router.get("/me", response_model=CurrentUserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user
