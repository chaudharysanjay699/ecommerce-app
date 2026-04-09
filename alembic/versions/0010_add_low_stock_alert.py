"""
Add low stock alert settings: low_stock_threshold and low_stock_alert_enabled
on app_settings

Revision ID: 0010_add_low_stock_alert
Revises: 0009_add_gst_invoice_fields
Create Date: 2026-04-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0010_add_low_stock_alert'
down_revision = '0009_add_gst_invoice_fields'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('app_settings', sa.Column('low_stock_threshold', sa.Integer(), server_default='5', nullable=False))
    op.add_column('app_settings', sa.Column('low_stock_alert_enabled', sa.Boolean(), server_default=sa.text('true'), nullable=False))


def downgrade():
    op.drop_column('app_settings', 'low_stock_alert_enabled')
    op.drop_column('app_settings', 'low_stock_threshold')
