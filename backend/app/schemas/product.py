from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import TimestampedModel


class ProductBase(BaseModel):
    name: str
    sku: str
    category: str
    description: str | None = None
    price: float
    stock: int = 0
    after_sale_policy: str | None = None
    status: str = "active"


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    sku: str | None = None
    category: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None
    after_sale_policy: str | None = None
    status: str | None = None


class ProductRead(ProductBase, TimestampedModel):
    id: int
    created_at: datetime
    updated_at: datetime

