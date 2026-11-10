from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=180)
    brand: str | None = Field(default=None, max_length=120)
    category_id: int | None = Field(default=None, gt=0)
    selling_price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    cost_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    stock_quantity: Decimal = Field(default=Decimal("0"), ge=0, max_digits=14, decimal_places=3)
    stock_unit: str = Field(default="piece", min_length=1, max_length=24)
    sale_unit: str = Field(default="piece", min_length=1, max_length=24)
    conversion_to_stock_unit: Decimal = Field(default=Decimal("1"), gt=0, max_digits=14, decimal_places=6)
    barcode: str | None = Field(default=None, max_length=80)
    tax_rate: Decimal | None = Field(default=None, ge=0, le=100, max_digits=6, decimal_places=3)
    reorder_level: Decimal = Field(default=Decimal("0"), ge=0, max_digits=14, decimal_places=3)

    @field_validator("sku", "name", "stock_unit", "sale_unit")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be blank")
        return value


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    brand: str | None = Field(default=None, max_length=120)
    category_id: int | None = Field(default=None, gt=0)
    selling_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    cost_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    stock_unit: str | None = Field(default=None, min_length=1, max_length=24)
    sale_unit: str | None = Field(default=None, min_length=1, max_length=24)
    conversion_to_stock_unit: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=6)
    barcode: str | None = Field(default=None, max_length=80)
    tax_rate: Decimal | None = Field(default=None, ge=0, le=100, max_digits=6, decimal_places=3)
    reorder_level: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=3)
    is_active: bool | None = None


class ProductRead(ProductCreate):
    id: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class StockAdjustment(BaseModel):
    quantity_delta: Decimal = Field(ne=0, max_digits=14, decimal_places=3)
    note: str = Field(min_length=1, max_length=500)
    movement_type: str = Field(default="manual_adjustment", pattern="^(manual_adjustment|opening_stock|purchase|damage|correction)$")


class StockMovementRead(BaseModel):
    id: int
    product_id: int
    quantity_delta: Decimal
    stock_unit: str
    movement_type: str
    reference_type: str | None
    reference_id: str | None
    note: str | None
    model_config = ConfigDict(from_attributes=True)


class ProductAliasCreate(BaseModel):
    alias: str = Field(min_length=1, max_length=180)
    language: str = Field(default="mixed", min_length=2, max_length=24)


class ProductAliasRead(BaseModel):
    id: int
    product_id: int
    alias: str
    normalized_alias: str
    language: str
    model_config = ConfigDict(from_attributes=True)
