"""
Add description_hi (Hindi description) to products and categories

Revision ID: 0007_add_hindi_description
Revises: 0006_add_hindi_name
Create Date: 2026-04-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0007_add_hindi_description'
down_revision = '0006_add_hindi_name'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('categories', sa.Column('description_hi', sa.Text(), nullable=True))
    op.add_column('products', sa.Column('description_hi', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('products', 'description_hi')
    op.drop_column('categories', 'description_hi')
