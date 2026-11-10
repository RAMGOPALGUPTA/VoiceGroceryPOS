"""Add transactional sales, sale items and payments."""
from alembic import op
import sqlalchemy as sa
revision = "0003_sales"
down_revision = "0002_inventory_imports"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("sales", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("receipt_number", sa.String(40), nullable=False, unique=True), sa.Column("idempotency_key", sa.String(80), nullable=False, unique=True), sa.Column("status", sa.String(20), nullable=False, server_default="completed"), sa.Column("subtotal", sa.Numeric(12,2), nullable=False), sa.Column("tax_total", sa.Numeric(12,2), nullable=False, server_default="0"), sa.Column("discount_total", sa.Numeric(12,2), nullable=False, server_default="0"), sa.Column("grand_total", sa.Numeric(12,2), nullable=False), sa.Column("payment_method", sa.String(24), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_sales_receipt_number", "sales", ["receipt_number"], unique=True)
    op.create_index("ix_sales_idempotency_key", "sales", ["idempotency_key"], unique=True)
    op.create_index("ix_sales_created_at", "sales", ["created_at"])
    op.create_table("sale_items", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("sale_id", sa.Integer(), sa.ForeignKey("sales.id", ondelete="CASCADE"), nullable=False), sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False), sa.Column("sku_snapshot", sa.String(64), nullable=False), sa.Column("name_snapshot", sa.String(180), nullable=False), sa.Column("unit_snapshot", sa.String(24), nullable=False), sa.Column("quantity", sa.Numeric(14,3), nullable=False), sa.Column("unit_price", sa.Numeric(12,2), nullable=False), sa.Column("tax_rate", sa.Numeric(6,3), nullable=False, server_default="0"), sa.Column("line_subtotal", sa.Numeric(12,2), nullable=False), sa.Column("line_tax", sa.Numeric(12,2), nullable=False), sa.Column("line_total", sa.Numeric(12,2), nullable=False))
    op.create_index("ix_sale_items_sale_id", "sale_items", ["sale_id"])
    op.create_table("payments", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("sale_id", sa.Integer(), sa.ForeignKey("sales.id", ondelete="CASCADE"), nullable=False), sa.Column("method", sa.String(24), nullable=False), sa.Column("amount", sa.Numeric(12,2), nullable=False), sa.Column("reference", sa.String(120)), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_payments_sale_id", "payments", ["sale_id"])

def downgrade():
    op.drop_table("payments")
    op.drop_table("sale_items")
    op.drop_table("sales")
