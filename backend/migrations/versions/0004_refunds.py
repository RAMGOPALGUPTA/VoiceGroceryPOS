"""Add full-sale refund records."""
from alembic import op
import sqlalchemy as sa
revision = "0004_refunds"
down_revision = "0003_sales"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("refunds",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sale_id", sa.Integer(), sa.ForeignKey("sales.id"), nullable=False, unique=True),
        sa.Column("idempotency_key", sa.String(80), nullable=False, unique=True),
        sa.Column("amount", sa.Numeric(12,2), nullable=False),
        sa.Column("reason", sa.String(300), nullable=False),
        sa.Column("method", sa.String(24), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_refunds_sale_id", "refunds", ["sale_id"], unique=True)
    op.create_index("ix_refunds_idempotency_key", "refunds", ["idempotency_key"], unique=True)

def downgrade():
    op.drop_table("refunds")
