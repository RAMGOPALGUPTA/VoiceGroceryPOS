from decimal import Decimal
from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(180), index=True)
    brand: Mapped[str | None] = mapped_column(String(120), nullable=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey('categories.id'), nullable=True)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cost_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    stock_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3), default=Decimal('0'))
    stock_unit: Mapped[str] = mapped_column(String(24), default='piece')
    sale_unit: Mapped[str] = mapped_column(String(24), default='piece')
    conversion_to_stock_unit: Mapped[Decimal] = mapped_column(Numeric(14, 6), default=Decimal('1'))
    barcode: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    tax_rate: Mapped[Decimal | None] = mapped_column(Numeric(6, 3), nullable=True)
    reorder_level: Mapped[Decimal] = mapped_column(Numeric(14, 3), default=Decimal('0'))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    category: Mapped['Category | None'] = relationship(back_populates='products')
    aliases: Mapped[list['ProductAlias']] = relationship(back_populates='product', cascade='all, delete-orphan')
