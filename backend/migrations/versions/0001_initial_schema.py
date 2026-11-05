"""Initial catalog and stock ledger tables."""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("categories.id")))
    op.create_table("products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sku", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("brand", sa.String(120)),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id")),
        sa.Column("selling_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("cost_price", sa.Numeric(12, 2)),
        sa.Column("stock_quantity", sa.Numeric(14, 3), nullable=False, server_default="0"),
        sa.Column("stock_unit", sa.String(24), nullable=False, server_default="piece"),
        sa.Column("sale_unit", sa.String(24), nullable=False, server_default="piece"),
        sa.Column("conversion_to_stock_unit", sa.Numeric(14, 6), nullable=False, server_default="1"),
        sa.Column("barcode", sa.String(80)),
        sa.Column("tax_rate", sa.Numeric(6, 3)),
        sa.Column("reorder_level", sa.Numeric(14, 3), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_index("ix_products_sku", "products", ["sku"], unique=True)
    op.create_index("ix_products_name", "products", ["name"])
    op.create_index("ix_products_barcode", "products", ["barcode"])
    op.create_table("product_aliases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alias", sa.String(180), nullable=False),
        sa.Column("normalized_alias", sa.String(180), nullable=False),
        sa.Column("language", sa.String(24), nullable=False, server_default="mixed"),
        sa.UniqueConstraint("product_id", "normalized_alias", name="uq_alias_product_normalized"))
    op.create_index("ix_product_aliases_product_id", "product_aliases", ["product_id"])
    op.create_index("ix_product_aliases_normalized_alias", "product_aliases", ["normalized_alias"])
    op.create_table("stock_movements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity_delta", sa.Numeric(14, 3), nullable=False),
        sa.Column("stock_unit", sa.String(24), nullable=False),
        sa.Column("movement_type", sa.String(40), nullable=False),
        sa.Column("reference_type", sa.String(40)),
        sa.Column("reference_id", sa.String(80)),
        sa.Column("note", sa.Text()))
    op.create_index("ix_stock_movements_product_id", "stock_movements", ["product_id"])

def downgrade():
    op.drop_table("stock_movements")
    op.drop_table("product_aliases")
    op.drop_table("products")
    op.drop_table("categories")
