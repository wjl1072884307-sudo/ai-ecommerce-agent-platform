from datetime import datetime

from app.schemas.common import TimestampedModel
from app.schemas.product import ProductRead


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

