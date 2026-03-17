"""
Add old_price to products table
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('products', sa.Column('old_price', sa.Numeric(10, 2), nullable=True))

def downgrade():
    op.drop_column('products', 'old_price')
