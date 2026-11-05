from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('categories.id'), nullable=True)
    parent: Mapped['Category | None'] = relationship(remote_side='Category.id', back_populates='children')
    children: Mapped[list['Category']] = relationship(back_populates='parent')
    products: Mapped[list['Product']] = relationship(back_populates='category')
