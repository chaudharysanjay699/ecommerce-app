"""add app_settings table for order limits and store configuration

Revision ID: 0003_app_settings
Revises: 0002_notif_order_id
Create Date: 2025-01-01 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = "0003_app_settings"
down_revision: Union[str, None] = "0002_notif_order_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create app_settings table
    op.create_table(
        "app_settings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        # Store Information
        sa.Column("store_name", sa.String(200), nullable=False, server_default="Vidharthi Store"),
        sa.Column("store_phone", sa.String(20), nullable=True),
        sa.Column("store_email", sa.String(200), nullable=True),
        sa.Column("store_address", sa.Text(), nullable=True),
        # Order Management
        sa.Column("daily_order_limit", sa.Integer(), nullable=True),
        sa.Column("order_limit_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("order_limit_message", sa.String(500), nullable=False,
                   server_default="We are currently unable to accept new orders. Please try again later."),
        # Delivery Charges
        sa.Column("delivery_charge_single", sa.Numeric(10, 2), nullable=False, server_default="10.00"),
        sa.Column("delivery_charge_multiple", sa.Numeric(10, 2), nullable=False, server_default="15.00"),
        # Vegetable Order Time Window
        sa.Column("veg_order_start_hour", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("veg_order_end_hour", sa.Integer(), nullable=False, server_default="9"),
        sa.Column("veg_order_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        # Maintenance Mode
        sa.Column("maintenance_mode", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("maintenance_message", sa.String(500), nullable=False,
                   server_default="We are currently under maintenance. Please try again later."),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    
    # Insert default settings row
    op.execute(
        """
        INSERT INTO app_settings (store_name, daily_order_limit, order_limit_enabled,
            delivery_charge_single, delivery_charge_multiple,
            veg_order_start_hour, veg_order_end_hour, veg_order_enabled,
            maintenance_mode)
        VALUES ('Vidharthi Store', NULL, false, 10.00, 15.00, 5, 9, true, false)
        """
    )


def downgrade() -> None:
    op.drop_table("app_settings")
