from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_roles
from app.database import get_db
from app.models import Order, Product, User
from app.schemas import OrderCreate, OrderDetailRead, OrderRead, OrderUpdate

router = APIRouter(tags=["orders"])


@router.get("/orders", response_model=list[OrderRead], dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
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
    else:
        query = query.filter(Order.order_status != "deleted")
    return query.order_by(Order.id).offset(skip).limit(limit).all()


@router.post("/orders", response_model=OrderDetailRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles("admin"))])
def create_order(payload: OrderCreate, db: Session = Depends(get_db)) -> Order:
    _validate_order_refs(db, payload.user_id, payload.product_id)
    if db.query(Order).filter(Order.order_no == payload.order_no).first():
        raise HTTPException(status_code=400, detail="Order number already exists.")

    order = Order(**payload.model_dump())
    db.add(order)
    db.commit()
    db.refresh(order)
    return db.query(Order).options(joinedload(Order.product)).filter(Order.id == order.id).one()


@router.get("/orders/{order_id}", response_model=OrderDetailRead, dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
def get_order(order_id: int, db: Session = Depends(get_db)) -> Order:
    order = db.query(Order).options(joinedload(Order.product)).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order


@router.put("/orders/{order_id}", response_model=OrderDetailRead, dependencies=[Depends(require_roles("admin"))])
def update_order(order_id: int, payload: OrderUpdate, db: Session = Depends(get_db)) -> Order:
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    update_data = payload.model_dump(exclude_unset=True)
    user_id = update_data.get("user_id", order.user_id)
    product_id = update_data.get("product_id", order.product_id)
    _validate_order_refs(db, user_id, product_id)

    if "order_no" in update_data:
        existing = db.query(Order).filter(Order.order_no == update_data["order_no"], Order.id != order_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Order number already exists.")

    for field, value in update_data.items():
        setattr(order, field, value)

    db.commit()
    db.refresh(order)
    return db.query(Order).options(joinedload(Order.product)).filter(Order.id == order.id).one()


@router.delete("/orders/{order_id}", response_model=OrderDetailRead, dependencies=[Depends(require_roles("admin"))])
def delete_order(order_id: int, db: Session = Depends(get_db)) -> Order:
    order = db.query(Order).options(joinedload(Order.product)).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    order.order_status = "deleted"
    db.commit()
    db.refresh(order)
    return order


@router.get("/orders/by-number/{order_no}", response_model=OrderDetailRead, dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
def get_order_by_number(order_no: str, db: Session = Depends(get_db)) -> Order:
    order = db.query(Order).options(joinedload(Order.product)).filter(Order.order_no == order_no).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order


@router.get("/users/{user_id}/orders", response_model=list[OrderRead], dependencies=[Depends(require_roles("admin", "reviewer", "agent", "viewer"))])
def list_user_orders(user_id: int, db: Session = Depends(get_db)) -> list[Order]:
    return db.query(Order).filter(Order.user_id == user_id, Order.order_status != "deleted").order_by(Order.id).all()


def _validate_order_refs(db: Session, user_id: int, product_id: int) -> None:
    if not db.get(User, user_id):
        raise HTTPException(status_code=404, detail="User not found.")
    product = db.get(Product, product_id)
    if not product or product.status == "deleted":
        raise HTTPException(status_code=404, detail="Product not found.")
