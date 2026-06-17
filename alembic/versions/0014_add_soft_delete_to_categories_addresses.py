"""add_soft_delete_to_categories_and_addresses

Revision ID: 0014
Revises: 0013
Create Date: 2026-05-24 00:00:00.000000

categories already has is_deleted — we only add deleted_at + index.
addresses gets both is_deleted and deleted_at.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0014'
down_revision: Union[str, None] = '0013'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── categories ─────────────────────────────────────────────────────────
    # is_deleted already exists; just add deleted_at and index
    op.add_column('categories', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_categories_is_deleted', 'categories', ['is_deleted'], unique=False)

    # ── addresses ──────────────────────────────────────────────────────────
    op.add_column('addresses', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('addresses', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_addresses_is_deleted', 'addresses', ['is_deleted'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_addresses_is_deleted', table_name='addresses')
    op.drop_column('addresses', 'deleted_at')
    op.drop_column('addresses', 'is_deleted')

    op.drop_index('ix_categories_is_deleted', table_name='categories')
    op.drop_column('categories', 'deleted_at')
