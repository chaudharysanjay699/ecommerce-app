"""Add holiday delivery date configuration and resolved order delivery date."""

from alembic import op
import sqlalchemy as sa


revision = "0011_add_holiday_delivery_dates"
down_revision = "0010_add_low_stock_alert"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "app_settings",
        sa.Column("holiday_delivery_dates", sa.JSON(), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("delivery_date", sa.Date(), nullable=True),
    )
    op.execute("UPDATE orders SET delivery_date = DATE(created_at) WHERE delivery_date IS NULL")
    op.alter_column("orders", "delivery_date", nullable=False)


def downgrade():
    op.drop_column("orders", "delivery_date")
    op.drop_column("app_settings", "holiday_delivery_dates")