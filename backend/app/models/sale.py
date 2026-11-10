from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class Sale(Base):
    __tablename__ = "sales"
    id: Mapped[int] = mapped_column(primary_key=True)
    receipt_number: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="completed")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12,2))
    tax_total: Mapped[Decimal] = mapped_column(Numeric(12,2), default=Decimal("0"))
    discount_total: Mapped[Decimal] = mapped_column(Numeric(12,2), default=Decimal("0"))
    grand_total: Mapped[Decimal] = mapped_column(Numeric(12,2))
    payment_method: Mapped[str] = mapped_column(String(24))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    items: Mapped[list["SaleItem"]] = relationship(back_populates="sale", cascade="all, delete-orphan")
    payments: Mapped[list["Payment"]] = relationship(back_populates="sale", cascade="all, delete-orphan")

class SaleItem(Base):
    __tablename__ = "sale_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    sku_snapshot: Mapped[str] = mapped_column(String(64))
    name_snapshot: Mapped[str] = mapped_column(String(180))
    unit_snapshot: Mapped[str] = mapped_column(String(24))
    quantity: Mapped[Decimal] = mapped_column(Numeric(14,3))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12,2))
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(6,3), default=Decimal("0"))
    line_subtotal: Mapped[Decimal] = mapped_column(Numeric(12,2))
    line_tax: Mapped[Decimal] = mapped_column(Numeric(12,2))
    line_total: Mapped[Decimal] = mapped_column(Numeric(12,2))
    sale: Mapped[Sale] = relationship(back_populates="items")

class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id", ondelete="CASCADE"), index=True)
    method: Mapped[str] = mapped_column(String(24))
    amount: Mapped[Decimal] = mapped_column(Numeric(12,2))
    reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sale: Mapped[Sale] = relationship(back_populates="payments")
