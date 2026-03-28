"""
Revision ID: 0004_softdel_prod_cat
Revises: 0003_app_settings
Create Date: 2026-03-22
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0004_softdel_prod_cat'
down_revision = '0003_app_settings'
branch_labels = None
depends_on = None

def upgrade():
    # Add is_deleted to products if it does not exist
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if 'is_deleted' not in [col['name'] for col in insp.get_columns('products')]:
        op.add_column('products', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()))
    if 'is_deleted' not in [col['name'] for col in insp.get_columns('categories')]:
        op.add_column('categories', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()))

def downgrade():
    op.drop_column('products', 'is_deleted')
    op.drop_column('categories', 'is_deleted')
