"""Rename holiday_delivery_dates to unavailable_delivery_dates for clarity."""

from alembic import op
import sqlalchemy as sa


revision = "0016_rename_unavailable_dates"
down_revision = "0015_merge_holiday_soft_delete"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "app_settings",
        "holiday_delivery_dates",
        new_column_name="unavailable_delivery_dates",
    )


def downgrade():
    op.alter_column(
        "app_settings",
        "unavailable_delivery_dates",
        new_column_name="holiday_delivery_dates",
    )
