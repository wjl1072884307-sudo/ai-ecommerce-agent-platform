from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Order
from app.schemas import OrderDetailRead, OrderRead

router = APIRouter(tags=["orders"])


@router.get("/orders", response_model=list[OrderRead])
def list_orders(
    keyword: str | None = None,
    user_id: int | None = None,
    order_status: str | None = Query(default=None, alias="status"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
) -> list[Order]:
    query = db.query(Order)
    if keyword:
        query = query.filter(Order.order_no.ilike(f"%{keyword}%"))
    if user_id:
        query = query.filter(Order.user_id == user_id)
    if order_status:
        query = query.filter(Order.order_status == order_status)
    return query.order_by(Order.id).offset(skip).limit(limit).all()


@router.get("/orders/{order_id}", response_model=OrderDetailRead)
def get_order(order_id: int, db: Session = Depends(get_db)) -> Order:
    order = db.query(Order).options(joinedload(Order.product)).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order


@router.get("/orders/by-number/{order_no}", response_model=OrderDetailRead)
def get_order_by_number(order_no: str, db: Session = Depends(get_db)) -> Order:
    order = db.query(Order).options(joinedload(Order.product)).filter(Order.order_no == order_no).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order


@router.get("/users/{user_id}/orders", response_model=list[OrderRead])
def list_user_orders(user_id: int, db: Session = Depends(get_db)) -> list[Order]:
    return db.query(Order).filter(Order.user_id == user_id).order_by(Order.id).all()

