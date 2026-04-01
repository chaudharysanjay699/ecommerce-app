"""
Add name_hi (Hindi title) to products and categories

Revision ID: 0006_add_hindi_name
Revises: 0005_add_delivery_charge_tiers
Create Date: 2026-04-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0006_add_hindi_name'
down_revision = '0005_add_delivery_charge_tiers'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('categories', sa.Column('name_hi', sa.String(100), nullable=True))
    op.add_column('products', sa.Column('name_hi', sa.String(200), nullable=True))

def downgrade():
    op.drop_column('products', 'name_hi')
    op.drop_column('categories', 'name_hi')
