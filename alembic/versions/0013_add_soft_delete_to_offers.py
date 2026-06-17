"""add_soft_delete_to_offers

Revision ID: 0013
Revises: 0012_drop_old_idx
Create Date: 2026-05-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0013'
down_revision: Union[str, None] = '0012_drop_old_idx'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add soft delete columns to offers table."""
    # Add is_deleted column with default False
    op.add_column('offers', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'))
    
    # Add deleted_at column (nullable for non-deleted records)
    op.add_column('offers', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    
    # Create index on is_deleted for query performance
    op.create_index('ix_offers_is_deleted', 'offers', ['is_deleted'], unique=False)


def downgrade() -> None:
    """Remove soft delete columns from offers table."""
    op.drop_index('ix_offers_is_deleted', table_name='offers')
    op.drop_column('offers', 'deleted_at')
    op.drop_column('offers', 'is_deleted')
