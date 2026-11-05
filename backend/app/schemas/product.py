from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=180)
    brand: str | None = None
    selling_price: Decimal = Field(ge=0)
    stock_quantity: Decimal = Field(default=Decimal('0'), ge=0)
    stock_unit: str = 'piece'
    sale_unit: str = 'piece'
    conversion_to_stock_unit: Decimal = Field(default=Decimal('1'), gt=0)
    tax_rate: Decimal | None = Field(default=None, ge=0, le=100)

class ProductRead(ProductCreate):
    id: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
