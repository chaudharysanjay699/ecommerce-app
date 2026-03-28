"""add order_id to notifications

Revision ID: 0002_notif_order_id
Revises: 0001_consolidated
Create Date: 2025-01-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_notif_order_id"
down_revision: Union[str, None] = "0001_consolidated"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "notifications",
        sa.Column("order_id", sa.Uuid(), nullable=True),
    )
    op.create_index("ix_notifications_order_id", "notifications", ["order_id"])
    op.create_foreign_key(
        "fk_notifications_order_id",
        "notifications",
        "orders",
        ["order_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_notifications_order_id", "notifications", type_="foreignkey")
    op.drop_index("ix_notifications_order_id", table_name="notifications")
    op.drop_column("notifications", "order_id")
