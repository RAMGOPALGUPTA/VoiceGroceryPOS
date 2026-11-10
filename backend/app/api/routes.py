import re
import unicodedata
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import Category, Product, ProductAlias, StockMovement, Sale, SaleItem, Payment, Refund
from app.schemas.category import CategoryCreate, CategoryRead
from app.schemas.sale import CheckoutRequest, SaleRead
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


# Inventory spreadsheet import: preview is persisted locally and never changes stock.
import csv as _csv
import io as _io
import json as _json
import uuid as _uuid
from datetime import datetime as _datetime
from decimal import InvalidOperation as _InvalidOperation
from fastapi import File as _File, UploadFile as _UploadFile

def _import_header(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().casefold()).strip("_")

_IMPORT_COLUMNS = {
    "sku": {"sku", "item_code", "product_code", "code"},
    "name": {"name", "product", "product_name", "item", "item_name"},
    "selling_price": {"selling_price", "sale_price", "price", "mrp", "rate"},
    "stock_quantity": {"stock_quantity", "quantity", "stock", "opening_stock", "qty"},
    "brand": {"brand", "manufacturer"}, "barcode": {"barcode", "ean", "upc"},
    "cost_price": {"cost_price", "purchase_price", "buying_price"},
    "stock_unit": {"stock_unit", "unit", "uom"}, "sale_unit": {"sale_unit", "selling_unit"},
    "tax_rate": {"tax_rate", "gst", "gst_rate", "tax"},
    "reorder_level": {"reorder_level", "minimum_stock", "min_stock"},
}

def _import_decimal(value, field):
    if value is None or str(value).strip() == "":
        return None
    try:
        result = Decimal(str(value).replace(",", "").strip())
    except (_InvalidOperation, ValueError):
        raise ValueError(f"{field} must be numeric")
    if not result.is_finite() or result < 0:
        raise ValueError(f"{field} must be zero or greater")
    return result

@router.post("/inventory/import/preview")
async def inventory_import_preview(file: _UploadFile = _File(...), db: Session = Depends(get_db)):
    filename = file.filename or "inventory.csv"
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Import file must be 10 MB or smaller")
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    try:
        if suffix == "csv":
            raw = list(_csv.DictReader(_io.StringIO(content.decode("utf-8-sig"))))
        elif suffix in {"xlsx", "xlsm"}:
            import pandas as pd
            frame = pd.read_excel(_io.BytesIO(content), dtype=object, engine="openpyxl")
            raw = frame.where(frame.notna(), None).to_dict(orient="records")
        else:
            raise HTTPException(status_code=400, detail="Upload a .csv, .xlsx, or .xlsm file")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must use UTF-8 encoding") from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read spreadsheet: {exc}") from exc
    if not raw:
        raise HTTPException(status_code=400, detail="The file contains no data rows")
    mapping = {}
    for header in raw[0].keys():
        key = _import_header(header)
        for field, aliases in _IMPORT_COLUMNS.items():
            if key in aliases:
                mapping[field] = header
    missing = [x for x in ("sku", "name", "selling_price") if x not in mapping]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing required columns: {', '.join(missing)}")
    rows, seen = [], set()
    for number, source in enumerate(raw, 2):
        row = {"row_number": number, "errors": []}
        for field, header in mapping.items():
            value = source.get(header)
            if field in {"selling_price", "stock_quantity", "cost_price", "tax_rate", "reorder_level"}:
                try:
                    parsed = _import_decimal(value, field)
                    row[field] = str(parsed) if parsed is not None else None
                except ValueError as exc:
                    row["errors"].append(str(exc))
            else:
                row[field] = str(value).strip() if value is not None and str(value).strip() else None
        if not row.get("sku"): row["errors"].append("sku is required")
        if not row.get("name"): row["errors"].append("name is required")
        if row.get("selling_price") is None: row["errors"].append("selling_price is required")
        key = (row.get("sku") or "").casefold()
        if key and key in seen: row["errors"].append("duplicate SKU in uploaded file")
        if key: seen.add(key)
        existing = db.scalar(select(Product).where(Product.sku == row.get("sku"))) if key else None
        row["action"] = "update" if existing else "create"
        row["errors"] = list(dict.fromkeys(row["errors"]))
        rows.append(row)
    from app.models.inventory_import import InventoryImport
    token = str(_uuid.uuid4())
    valid = sum(not row["errors"] for row in rows)
    batch = InventoryImport(token=token, filename=filename[:255], status="previewed", row_count=len(rows), valid_count=valid, error_count=len(rows)-valid, rows_json=_json.dumps(rows, ensure_ascii=False))
    db.add(batch); db.commit()
    return {"import_id": token, "filename": filename, "row_count": len(rows), "valid_count": valid, "error_count": len(rows)-valid, "columns": mapping, "rows": rows, "stock_modes": ["replace", "add"]}

@router.post("/inventory/import/{import_id}/commit")
def inventory_import_commit(import_id: str, stock_mode: str = Query(default="replace", pattern="^(replace|add)$"), db: Session = Depends(get_db)):
    from app.models.inventory_import import InventoryImport
    batch = db.scalar(select(InventoryImport).where(InventoryImport.token == import_id))
    if batch is None: raise HTTPException(status_code=404, detail="Import preview not found")
    if batch.status != "previewed": raise HTTPException(status_code=409, detail="This import has already been committed")
    rows = _json.loads(batch.rows_json)
    if any(row["errors"] for row in rows):
        raise HTTPException(status_code=409, detail="Fix all row errors and upload a corrected file before committing")
    try:
        for row in rows:
            product = db.scalar(select(Product).where(Product.sku == row["sku"]))
            if product is None:
                product = Product(sku=row["sku"], name=row["name"], brand=row.get("brand"),
                    selling_price=Decimal(row["selling_price"]), cost_price=Decimal(row["cost_price"]) if row.get("cost_price") else None,
                    stock_quantity=Decimal("0"), stock_unit=row.get("stock_unit") or "piece",
                    sale_unit=row.get("sale_unit") or row.get("stock_unit") or "piece", barcode=row.get("barcode"),
                    tax_rate=Decimal(row["tax_rate"]) if row.get("tax_rate") else None,
                    reorder_level=Decimal(row["reorder_level"]) if row.get("reorder_level") else Decimal("0"))
                db.add(product); db.flush()
            else:
                product.name = row["name"]; product.brand = row.get("brand")
                product.selling_price = Decimal(row["selling_price"])
                for field in ("cost_price", "tax_rate", "reorder_level"):
                    if row.get(field) is not None: setattr(product, field, Decimal(row[field]))
                for field in ("barcode", "stock_unit", "sale_unit"):
                    if row.get(field): setattr(product, field, row[field])
            if row.get("stock_quantity") is not None:
                imported = Decimal(row["stock_quantity"]); before = Decimal(product.stock_quantity)
                after = imported if stock_mode == "replace" else before + imported
                delta = after - before
                if delta:
                    product.stock_quantity = after
                    db.add(StockMovement(product_id=product.id, quantity_delta=delta, stock_unit=product.stock_unit,
                        movement_type="import_replace" if stock_mode == "replace" else "import_add",
                        reference_type="inventory_import", reference_id=import_id,
                        note=f"Stock {stock_mode} from {batch.filename}"))
        batch.status = "committed"; batch.committed_at = _datetime.utcnow()
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Import conflicts with existing data; no rows were committed") from exc
    return {"import_id": import_id, "status": "committed", "processed_rows": len(rows), "stock_mode": stock_mode}


# Transactional checkout and operational read APIs.
_MONEY = Decimal("0.01")
def _money(value: Decimal) -> Decimal:
    return value.quantize(_MONEY, rounding=ROUND_HALF_UP)

@router.post("/sales/checkout", response_model=SaleRead, status_code=status.HTTP_201_CREATED)
def checkout(payload: CheckoutRequest, db: Session = Depends(get_db)):
    prior = db.scalar(select(Sale).where(Sale.idempotency_key == payload.idempotency_key))
    if prior is not None:
        return prior
    # Combine repeated product lines before validating stock and calculating totals.
    quantities: dict[int, Decimal] = {}
    for line in payload.items:
        quantities[line.product_id] = quantities.get(line.product_id, Decimal("0")) + line.quantity
    products = {}
    subtotal = Decimal("0")
    calculated = []
    try:
        for product_id, quantity in quantities.items():
            product = db.scalar(select(Product).where(Product.id == product_id).with_for_update())
            if product is None or not product.is_active:
                raise HTTPException(status_code=409, detail=f"Product {product_id} is unavailable")
            stock_delta = quantity * Decimal(product.conversion_to_stock_unit)
            if Decimal(product.stock_quantity) < stock_delta:
                raise HTTPException(status_code=409, detail=f"Insufficient stock for {product.name}")
            line_subtotal = _money(Decimal(product.selling_price) * quantity)
            subtotal += line_subtotal
            products[product_id] = product
            calculated.append((product, quantity, stock_delta, line_subtotal))
        subtotal = _money(subtotal)
        if payload.discount > subtotal:
            raise HTTPException(status_code=422, detail="Discount cannot exceed subtotal")
        # Allocate the discount proportionally to line bases, then calculate tax.
        remaining_discount = payload.discount
        tax_total = Decimal("0")
        sale = Sale(
            receipt_number=f"SV-{_datetime.utcnow():%Y%m%d}-{_uuid.uuid4().hex[:8].upper()}",
            idempotency_key=payload.idempotency_key,
            status="completed", subtotal=subtotal, discount_total=payload.discount,
            grand_total=Decimal("0"), tax_total=Decimal("0"), payment_method=payload.payment_method)
        db.add(sale); db.flush()
        for index, (product, quantity, stock_delta, line_subtotal) in enumerate(calculated):
            if index == len(calculated)-1:
                line_discount = remaining_discount
            elif subtotal:
                line_discount = _money(payload.discount * line_subtotal / subtotal)
                remaining_discount -= line_discount
            else:
                line_discount = Decimal("0")
            taxable = max(Decimal("0"), line_subtotal - line_discount)
            rate = Decimal(product.tax_rate or 0)
            line_tax = _money(taxable * rate / Decimal("100"))
            line_total = taxable + line_tax
            tax_total += line_tax
            db.add(SaleItem(sale_id=sale.id, product_id=product.id, sku_snapshot=product.sku,
                name_snapshot=product.name, unit_snapshot=product.sale_unit, quantity=quantity,
                unit_price=product.selling_price, tax_rate=rate, line_subtotal=taxable,
                line_tax=line_tax, line_total=line_total))
            product.stock_quantity = Decimal(product.stock_quantity) - stock_delta
            db.add(StockMovement(product_id=product.id, quantity_delta=-stock_delta,
                stock_unit=product.stock_unit, movement_type="sale", reference_type="sale",
                reference_id=str(sale.id), note=f"Sold on receipt {sale.receipt_number}"))
        sale.tax_total = _money(tax_total)
        sale.grand_total = _money(subtotal - payload.discount + sale.tax_total)
        db.add(Payment(sale_id=sale.id, method=payload.payment_method, amount=sale.grand_total))
        db.commit()
        return db.scalar(select(Sale).where(Sale.id == sale.id))
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as exc:
        db.rollback()
        prior = db.scalar(select(Sale).where(Sale.idempotency_key == payload.idempotency_key))
        if prior is not None:
            return prior
        raise HTTPException(status_code=409, detail="Checkout conflicted with another transaction; retry safely") from exc
    except Exception:
        db.rollback()
        raise

@router.get("/sales", response_model=list[SaleRead])
def list_sales(limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)):
    return db.scalars(select(Sale).order_by(Sale.created_at.desc()).limit(limit)).unique().all()

@router.get("/sales/{sale_id}", response_model=SaleRead)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = db.scalar(select(Sale).where(Sale.id == sale_id))
    if sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale

@router.get("/inventory/summary")
def inventory_summary(db: Session = Depends(get_db)):
    products = db.scalars(select(Product).where(Product.is_active.is_(True)).order_by(Product.name)).all()
    return {"product_count": len(products), "low_stock_count": sum(1 for p in products if Decimal(p.stock_quantity) <= Decimal(p.reorder_level)), "products": products}

@router.get("/reports/summary")
def reports_summary(db: Session = Depends(get_db)):
    today = _datetime.utcnow().date()
    sales = db.scalars(select(Sale).where(Sale.status == "completed").order_by(Sale.created_at.desc())).all()
    today_sales = [s for s in sales if s.created_at.date() == today]
    products = db.scalars(select(Product).where(Product.is_active.is_(True))).all()
    return {
        "today_sales_count": len(today_sales),
        "today_revenue": str(_money(sum((Decimal(s.grand_total) for s in today_sales), Decimal("0")))),
        "all_time_sales_count": len(sales),
        "all_time_revenue": str(_money(sum((Decimal(s.grand_total) for s in sales), Decimal("0")))),
        "low_stock_count": sum(1 for p in products if Decimal(p.stock_quantity) <= Decimal(p.reorder_level)),
        "inventory_units": str(sum((Decimal(p.stock_quantity) for p in products), Decimal("0"))),
    }


@router.post("/voice/transcribe")
async def voice_transcribe(file: _UploadFile = _File(...)):
    suffix = Path(file.filename or "speech.webm").suffix.lower()
    if suffix not in {".webm", ".wav", ".mp3", ".m4a", ".ogg"}:
        raise HTTPException(status_code=415, detail="Use WebM, WAV, MP3, M4A or OGG audio")
    audio = await file.read()
    if not audio or len(audio) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio must be non-empty and at most 20 MB")
    import tempfile
    from pathlib import Path
    from app.services.voice import transcribe_file
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
            handle.write(audio); temp_path = handle.name
        return transcribe_file(temp_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="Install backend/requirements-voice.txt to enable offline speech recognition") from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Audio transcription failed: {exc}") from exc
    finally:
        if temp_path and Path(temp_path).exists():
            Path(temp_path).unlink(missing_ok=True)

from pydantic import BaseModel, Field
class VoiceInterpretRequest(BaseModel):
    transcript: str = Field(min_length=1, max_length=1000)

@router.post("/voice/interpret")
def voice_interpret(payload: VoiceInterpretRequest, db: Session = Depends(get_db)):
    from rapidfuzz import fuzz, process
    import re as _re
    text = unicodedata.normalize("NFKC", payload.transcript).casefold()
    products = db.scalars(select(Product).where(Product.is_active.is_(True))).all()
    aliases = db.scalars(select(ProductAlias)).all()
    alias_map = {}
    for product in products:
        alias_map[normalize_alias(product.name)] = product
        alias_map[normalize_alias(product.sku)] = product
        if product.brand:
            alias_map.setdefault(normalize_alias(product.brand + " " + product.name), product)
            alias_map.setdefault(normalize_alias(product.brand), product)
    for alias in aliases:
        alias_map[normalize_alias(alias.alias)] = next((p for p in products if p.id == alias.product_id), None)
    alias_map = {k:v for k,v in alias_map.items() if v is not None}
    number_words = {"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10,
                    "ek":1,"do":2,"teen":3,"char":4,"paanch":5,"che":6,"chhe":6,"saat":7,"aath":8,"nau":9,"das":10,
                    "एक":1,"दो":2,"तीन":3,"चार":4,"पांच":5,"पाँच":5,"छह":6,"सात":7,"आठ":8,"नौ":9,"दस":10}
    tokens = list(alias_map.keys())
    found = []
    # Longest known alias first; each matched phrase is consumed once.
    for alias in sorted(tokens, key=len, reverse=True):
        if alias and alias in text:
            before = text[:text.index(alias)]
            qty_match = _re.search(r"([0-9]+(?:\.[0-9]+)?|एक|दो|तीन|चार|पांच|पाँच|छह|सात|आठ|नौ|दस|one|two|three|four|five|six|seven|eight|nine|ten|ek|do|teen|char|paanch|che|chhe|saat|aath|nau|das)(?:\s*(?:kg|kilo|kilos|gram|grams|g|litre|liter|ltr|packet|packets|pcs|piece|pieces))?\s*$", before)
            qty = Decimal(qty_match.group(1)) if qty_match and re.match(r"^[0-9]",qty_match.group(1)) else Decimal(number_words.get(qty_match.group(1),1)) if qty_match else Decimal("1")
            product = alias_map[alias]
            if not any(x["product_id"] == product.id for x in found):
                found.append({"product_id":product.id,"name":product.name,"quantity":str(qty),"unit":product.sale_unit,"selling_price":str(product.selling_price),"confidence":0.98,"requires_confirmation":True})
            text = text.replace(alias, " ", 1)
    if not found and tokens:
        candidate = process.extractOne(text.strip(), tokens, scorer=fuzz.WRatio, score_cutoff=72)
        if candidate:
            product = alias_map[candidate[0]]
            found.append({"product_id":product.id,"name":product.name,"quantity":"1","unit":product.sale_unit,"selling_price":str(product.selling_price),"confidence":round(candidate[1]/100,2),"requires_confirmation":True})
    return {"transcript":payload.transcript,"items":found,"unmatched_text":text.strip(),"confirmation_required":True}

from pydantic import BaseModel, Field
class RefundRequest(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=80)
    reason: str = Field(min_length=3, max_length=300)
    method: str = Field(default="cash", pattern="^(cash|upi|card|other)$")

@router.post("/sales/{sale_id}/refund")
def refund_sale(sale_id: int, payload: RefundRequest, db: Session = Depends(get_db)):
    existing = db.scalar(select(Refund).where(Refund.idempotency_key == payload.idempotency_key))
    if existing is not None:
        return {"refund_id":existing.id,"sale_id":existing.sale_id,"amount":str(existing.amount),"status":"refunded"}
    sale = db.scalar(select(Sale).where(Sale.id == sale_id).with_for_update())
    if sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    if sale.status != "completed":
        raise HTTPException(status_code=409, detail="Only completed sales can be refunded")
    try:
        for item in sale.items:
            product = db.scalar(select(Product).where(Product.id == item.product_id).with_for_update())
            if product is None:
                raise HTTPException(status_code=409, detail=f"Product {item.name_snapshot} no longer exists")
            restored = Decimal(item.quantity) * Decimal(product.conversion_to_stock_unit)
            product.stock_quantity = Decimal(product.stock_quantity) + restored
            db.add(StockMovement(product_id=product.id,quantity_delta=restored,stock_unit=product.stock_unit,
                movement_type="refund",reference_type="sale",reference_id=str(sale.id),
                note=f"Stock restored for refund {sale.receipt_number}"))
        refund = Refund(sale_id=sale.id,idempotency_key=payload.idempotency_key,
            amount=sale.grand_total,reason=payload.reason.strip(),method=payload.method)
        db.add(refund)
        sale.status = "refunded"
        db.commit()
        return {"refund_id":refund.id,"sale_id":sale.id,"amount":str(refund.amount),"status":"refunded"}
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Refund was already processed or conflicted") from exc
