"""
Add invoice_url and shipping_label_url to orders

Revision ID: 0008_add_order_pdf_urls
Revises: 0007_add_hindi_description
Create Date: 2026-04-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0008_add_order_pdf_urls'
down_revision = '0007_add_hindi_description'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('orders', sa.Column('invoice_url', sa.String(500), nullable=True))
    op.add_column('orders', sa.Column('shipping_label_url', sa.String(500), nullable=True))

def downgrade():
    op.drop_column('orders', 'shipping_label_url')
    op.drop_column('orders', 'invoice_url')
