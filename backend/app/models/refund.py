from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class Refund(Base):
    __tablename__ = "refunds"
    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"), unique=True, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12,2))
    reason: Mapped[str] = mapped_column(String(300))
    method: Mapped[str] = mapped_column(String(24))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
