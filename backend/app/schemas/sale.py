from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class CheckoutLine(BaseModel):
    product_id: int = Field(gt=0)
    quantity: Decimal = Field(gt=0, max_digits=14, decimal_places=3)

class CheckoutRequest(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=80)
    payment_method: str = Field(pattern="^(cash|upi|card|other)$")
    discount: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    items: list[CheckoutLine] = Field(min_length=1, max_length=200)

class SaleItemRead(BaseModel):
    product_id: int
    sku_snapshot: str
    name_snapshot: str
    unit_snapshot: str
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal
    line_subtotal: Decimal
    line_tax: Decimal
    line_total: Decimal
    model_config = ConfigDict(from_attributes=True)

class SaleRead(BaseModel):
    id: int
    receipt_number: str
    status: str
    subtotal: Decimal
    tax_total: Decimal
    discount_total: Decimal
    grand_total: Decimal
    payment_method: str
    created_at: datetime
    items: list[SaleItemRead]
    model_config = ConfigDict(from_attributes=True)
