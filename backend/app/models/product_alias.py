from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class ProductAlias(Base):
    __tablename__ = 'product_aliases'
    __table_args__ = (UniqueConstraint('product_id', 'normalized_alias'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id', ondelete='CASCADE'), index=True)
    alias: Mapped[str] = mapped_column(String(180))
    normalized_alias: Mapped[str] = mapped_column(String(180), index=True)
    language: Mapped[str] = mapped_column(String(24), default='mixed')
    product: Mapped['Product'] = relationship(back_populates='aliases')
