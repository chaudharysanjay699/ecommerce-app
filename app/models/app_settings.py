"""Application-wide settings model for configurable parameters."""
from __future__ import annotations

from sqlalchemy import Boolean, Integer, Numeric, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class AppSettings(Base, UUIDMixin, TimestampMixin):
    """Store application-wide configuration settings.
    
    Only one row should exist in this table (singleton pattern).
    """
    __tablename__ = "app_settings"

    # ── Store Information ─────────────────────────────────────────────────────
    store_name: Mapped[str] = mapped_column(
        String(200), default="Vidharthi Store", nullable=False,
    )
    store_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    store_email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    store_address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── GST / Tax Information ─────────────────────────────────────────────────
    store_gstin: Mapped[str | None] = mapped_column(String(20), nullable=True)
    store_pan: Mapped[str | None] = mapped_column(String(20), nullable=True)
    store_state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    store_state_code: Mapped[str | None] = mapped_column(String(5), nullable=True)
    default_tax_rate: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0, nullable=False,
        comment="Default GST rate (%). Set 0 to disable tax.",
    )
    invoice_prefix: Mapped[str] = mapped_column(
        String(20), default="INV", nullable=False,
    )
    invoice_terms: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Order Management ──────────────────────────────────────────────────────
    daily_order_limit: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
        comment="Maximum number of orders allowed per day. NULL = unlimited",
    )
    order_limit_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
    )
    order_limit_message: Mapped[str] = mapped_column(
        String(500),
        default="We are currently unable to accept new orders. Please try again later.",
        nullable=False,
    )

    # ── Delivery Charges ──────────────────────────────────────────────────────
    delivery_charge_single: Mapped[float] = mapped_column(
        Numeric(10, 2), default=10.0, nullable=False,
    )
    delivery_charge_multiple: Mapped[float] = mapped_column(
        Numeric(10, 2), default=15.0, nullable=False,
    )
    delivery_charge_tiers: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
        default=None,
        comment="List of delivery charge tiers based on order amount",
    )

    # ── Vegetable Order Time Window (hours in UTC) ────────────────────────────
    veg_order_start_hour: Mapped[int] = mapped_column(
        Integer, default=5, nullable=False,
    )
    veg_order_end_hour: Mapped[int] = mapped_column(
        Integer, default=9, nullable=False,
    )
    veg_order_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
    )

    # ── Maintenance Mode ──────────────────────────────────────────────────────
    maintenance_mode: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
    )
    maintenance_message: Mapped[str] = mapped_column(
        String(500),
        default="We are currently under maintenance. Please try again later.",
        nullable=False,
    )
