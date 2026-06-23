from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import TimestampedModel
from app.schemas.product import ProductRead


class OrderBase(BaseModel):
    order_no: str
    user_id: int
    product_id: int
    quantity: int = 1
    total_amount: float
    order_status: str = "paid"
    payment_status: str = "paid"
    logistics_status: str = "pending"
    tracking_no: str | None = None
    paid_at: datetime | None = None
    shipped_at: datetime | None = None
    delivered_at: datetime | None = None
    after_sale_status: str = "none"


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    order_no: str | None = None
    user_id: int | None = None
    product_id: int | None = None
    quantity: int | None = None
    total_amount: float | None = None
    order_status: str | None = None
    payment_status: str | None = None
    logistics_status: str | None = None
    tracking_no: str | None = None
    paid_at: datetime | None = None
    shipped_at: datetime | None = None
    delivered_at: datetime | None = None
    after_sale_status: str | None = None


class OrderRead(TimestampedModel):
    id: int
    order_no: str
    user_id: int
    product_id: int
    quantity: int
    total_amount: float
    order_status: str
    payment_status: str
    logistics_status: str
    tracking_no: str | None
    paid_at: datetime | None
    shipped_at: datetime | None
    delivered_at: datetime | None
    after_sale_status: str


class OrderDetailRead(OrderRead):
    product: ProductRead
