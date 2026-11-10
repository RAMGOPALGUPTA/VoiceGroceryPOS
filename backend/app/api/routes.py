import re
import unicodedata
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import Category, Product, ProductAlias, StockMovement
from app.schemas.category import CategoryCreate, CategoryRead
from app.schemas.product import (
    ProductAliasCreate, ProductAliasRead, ProductCreate, ProductRead,
    ProductUpdate, StockAdjustment, StockMovementRead,
)

router = APIRouter()


def normalize_alias(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().strip()
    return re.sub(r"\s+", " ", value)


@router.get("/products", response_model=list[ProductRead])
def list_products(
    q: str | None = Query(default=None, max_length=120),
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    statement = select(Product)
    if not include_inactive:
        statement = statement.where(Product.is_active.is_(True))
    if q and q.strip():
        term = f"%{q.strip()}%"
        statement = statement.where(or_(Product.name.ilike(term), Product.sku.ilike(term), Product.brand.ilike(term), Product.barcode.ilike(term)))
    return db.scalars(statement.order_by(Product.name)).all()


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    product = Product(**data)
    db.add(product)
    try:
        db.flush()
        if product.stock_quantity > 0:
            db.add(StockMovement(
                product_id=product.id,
                quantity_delta=product.stock_quantity,
                stock_unit=product.stock_unit,
                movement_type="opening_stock",
                reference_type="product",
                reference_id=str(product.id),
                note="Opening stock recorded when product was created",
            ))
        db.commit()
        db.refresh(product)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="SKU, barcode, or category constraint conflict") from exc
    return product


@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.patch("/products/{product_id}", response_model=ProductRead)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    try:
        db.commit()
        db.refresh(product)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product update conflicts with an existing record") from exc
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False
    db.commit()


@router.post("/products/{product_id}/aliases", response_model=ProductAliasRead, status_code=status.HTTP_201_CREATED)
def add_product_alias(product_id: int, payload: ProductAliasCreate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    normalized = normalize_alias(payload.alias)
    alias = ProductAlias(product_id=product_id, alias=payload.alias.strip(), normalized_alias=normalized, language=payload.language)
    db.add(alias)
    try:
        db.commit()
        db.refresh(alias)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="This alias already exists for the product") from exc
    return alias


@router.get("/products/{product_id}/aliases", response_model=list[ProductAliasRead])
def list_product_aliases(product_id: int, db: Session = Depends(get_db)):
    if db.get(Product, product_id) is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db.scalars(select(ProductAlias).where(ProductAlias.product_id == product_id).order_by(ProductAlias.alias)).all()


@router.get("/categories", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return db.scalars(select(Category).order_by(Category.name)).all()


@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    category = Category(name=payload.name.strip(), parent_id=payload.parent_id)
    if category.parent_id is not None and db.get(Category, category.parent_id) is None:
        raise HTTPException(status_code=404, detail="Parent category not found")
    db.add(category)
    try:
        db.commit()
        db.refresh(category)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Category name already exists or parent is invalid") from exc
    return category


@router.post("/inventory/products/{product_id}/adjustments", response_model=StockMovementRead, status_code=status.HTTP_201_CREATED)
def adjust_stock(product_id: int, payload: StockAdjustment, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    new_quantity = Decimal(product.stock_quantity) + payload.quantity_delta
    if new_quantity < 0:
        raise HTTPException(status_code=409, detail="Adjustment would make stock negative")
    movement = StockMovement(
        product_id=product_id,
        quantity_delta=payload.quantity_delta,
        stock_unit=product.stock_unit,
        movement_type=payload.movement_type,
        reference_type="manual",
        note=payload.note.strip(),
    )
    product.stock_quantity = new_quantity
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


@router.get("/inventory/movements", response_model=list[StockMovementRead])
def list_stock_movements(
    product_id: int | None = Query(default=None, gt=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    statement = select(StockMovement)
    if product_id is not None:
        statement = statement.where(StockMovement.product_id == product_id)
    return db.scalars(statement.order_by(StockMovement.id.desc()).limit(limit)).all()
