from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class StockMovement(Base):
    __tablename__ = 'stock_movements'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), index=True)
    quantity_delta: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    stock_unit: Mapped[str] = mapped_column(String(24))
    movement_type: Mapped[str] = mapped_column(String(40))
    reference_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    reference_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
