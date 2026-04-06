"""
Add GST invoice fields: invoice_number on orders, tax fields on order_items,
hsn/gst on products, GST settings on app_settings

Revision ID: 0009_add_gst_invoice_fields
Revises: 0008_add_order_pdf_urls
Create Date: 2026-04-07 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0009_add_gst_invoice_fields'
down_revision = '0008_add_order_pdf_urls'
branch_labels = None
depends_on = None


def upgrade():
    # ── Orders: sequential invoice number ────────────────────────────────────
    op.add_column('orders', sa.Column('invoice_number', sa.String(50), nullable=True))
    op.create_index('ix_orders_invoice_number', 'orders', ['invoice_number'], unique=True)

    # ── Order Items: discount, tax, hsn ──────────────────────────────────────
    op.add_column('order_items', sa.Column('discount', sa.Numeric(10, 2), server_default='0', nullable=False))
    op.add_column('order_items', sa.Column('tax_rate', sa.Numeric(5, 2), server_default='0', nullable=False))
    op.add_column('order_items', sa.Column('tax_amount', sa.Numeric(10, 2), server_default='0', nullable=False))
    op.add_column('order_items', sa.Column('hsn_code', sa.String(20), nullable=True))

    # ── Products: HSN code & GST rate ────────────────────────────────────────
    op.add_column('products', sa.Column('hsn_code', sa.String(20), nullable=True))
    op.add_column('products', sa.Column('gst_rate', sa.Numeric(5, 2), nullable=True))

    # ── App Settings: GST & invoice config ───────────────────────────────────
    op.add_column('app_settings', sa.Column('store_gstin', sa.String(20), nullable=True))
    op.add_column('app_settings', sa.Column('store_pan', sa.String(20), nullable=True))
    op.add_column('app_settings', sa.Column('store_state', sa.String(100), nullable=True))
    op.add_column('app_settings', sa.Column('store_state_code', sa.String(5), nullable=True))
    op.add_column('app_settings', sa.Column('default_tax_rate', sa.Numeric(5, 2), server_default='0', nullable=False))
    op.add_column('app_settings', sa.Column('invoice_prefix', sa.String(20), server_default='INV', nullable=False))
    op.add_column('app_settings', sa.Column('invoice_terms', sa.Text(), nullable=True))


def downgrade():
    # App Settings
    op.drop_column('app_settings', 'invoice_terms')
    op.drop_column('app_settings', 'invoice_prefix')
    op.drop_column('app_settings', 'default_tax_rate')
    op.drop_column('app_settings', 'store_state_code')
    op.drop_column('app_settings', 'store_state')
    op.drop_column('app_settings', 'store_pan')
    op.drop_column('app_settings', 'store_gstin')

    # Products
    op.drop_column('products', 'gst_rate')
    op.drop_column('products', 'hsn_code')

    # Order Items
    op.drop_column('order_items', 'hsn_code')
    op.drop_column('order_items', 'tax_amount')
    op.drop_column('order_items', 'tax_rate')
    op.drop_column('order_items', 'discount')

    # Orders
    op.drop_index('ix_orders_invoice_number', 'orders')
    op.drop_column('orders', 'invoice_number')
