"""Persist inventory import previews."""
from alembic import op
import sqlalchemy as sa
revision = "0002_inventory_imports"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("inventory_imports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("token", sa.String(36), nullable=False, unique=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="previewed"),
        sa.Column("row_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("valid_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rows_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("committed_at", sa.DateTime()))
    op.create_index("ix_inventory_imports_token", "inventory_imports", ["token"], unique=True)

def downgrade():
    op.drop_table("inventory_imports")
