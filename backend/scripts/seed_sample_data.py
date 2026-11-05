"""Load synthetic pilot products. Existing SKUs are not overwritten."""
import csv
from decimal import Decimal
from pathlib import Path
from sqlalchemy import select
from app.database.session import SessionLocal
from app.models import Category, Product, ProductAlias

CSV_PATH = Path(__file__).resolve().parents[2] / "sample_data" / "sample_inventory.csv"

def main():
    db = SessionLocal()
    try:
        category = db.scalar(select(Category).where(Category.name == "Grocery"))
        if category is None:
            category = Category(name="Grocery")
            db.add(category)
            db.flush()
        with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                product = db.scalar(select(Product).where(Product.sku == row["sku"]))
                if product is None:
                    product = Product(
                        sku=row["sku"], name=row["name"], brand=row["brand"] or None,
                        category_id=category.id, selling_price=Decimal(row["selling_price"]),
                        stock_quantity=Decimal(row["stock_quantity"]), stock_unit=row["stock_unit"],
                        sale_unit=row["sale_unit"],
                        conversion_to_stock_unit=Decimal(row["conversion_to_stock_unit"]))
                    db.add(product)
                    db.flush()
                for alias in filter(None, (part.strip() for part in row["aliases"].split("|"))):
                    normalized = " ".join(alias.casefold().split())
                    found = db.scalar(select(ProductAlias).where(
                        ProductAlias.product_id == product.id,
                        ProductAlias.normalized_alias == normalized))
                    if found is None:
                        db.add(ProductAlias(product_id=product.id, alias=alias,
                                            normalized_alias=normalized, language="mixed"))
        db.commit()
        print("Sample catalog loaded; existing SKUs were left unchanged.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
