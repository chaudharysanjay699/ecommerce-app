"""
Revision ID: 0005_add_delivery_charge_tiers
Revises: 0004_softdel_prod_cat
Create Date: 2026-03-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0005_add_delivery_charge_tiers'
down_revision = '0004_softdel_prod_cat'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('app_settings', sa.Column('delivery_charge_tiers', postgresql.JSON(astext_type=sa.Text()), nullable=True))

def downgrade():
    op.drop_column('app_settings', 'delivery_charge_tiers')
