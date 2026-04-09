"""Schemas for application settings."""
from __future__ import annotations

from pydantic import BaseModel, Field


class DeliveryChargeTier(BaseModel):
    """Delivery charge tier based on order amount."""
    min_price: float = Field(..., ge=0, description="Minimum order amount")
    max_price: float | None = Field(None, ge=0, description="Maximum order amount (None for unlimited)")
    delivery_charge: float = Field(..., ge=0, description="Delivery charge for this tier")


class AppSettingsOut(BaseModel):
    """Full application settings response."""

    # Store Information
    store_name: str = "Vidharthi Store"
    store_phone: str | None = None
    store_email: str | None = None
    store_address: str | None = None

    # GST / Tax Information
    store_gstin: str | None = None
    store_pan: str | None = None
    store_state: str | None = None
    store_state_code: str | None = None
    default_tax_rate: float = 0
    invoice_prefix: str = "INV"
    invoice_terms: str | None = None

    # Order Management
    daily_order_limit: int | None = None
    order_limit_enabled: bool = False
    order_limit_message: str = ""

    # Delivery Charges
    delivery_charge_tiers: list[DeliveryChargeTier] | None = None

    # Vegetable Order Time Window
    veg_order_start_hour: int = 5
    veg_order_end_hour: int = 9
    veg_order_enabled: bool = True

    # Low Stock Alert
    low_stock_threshold: int = 5
    low_stock_alert_enabled: bool = True

    # Maintenance Mode
    maintenance_mode: bool = False
    maintenance_message: str = ""

    class Config:
        from_attributes = True


class AppSettingsUpdate(BaseModel):
    """Update application settings (all fields optional)."""

    # Store Information
    store_name: str | None = Field(None, min_length=1, max_length=200)
    store_phone: str | None = Field(None, max_length=20)
    store_email: str | None = Field(None, max_length=200)
    store_address: str | None = None

    # GST / Tax Information
    store_gstin: str | None = Field(None, max_length=20)
    store_pan: str | None = Field(None, max_length=20)
    store_state: str | None = Field(None, max_length=100)
    store_state_code: str | None = Field(None, max_length=5)
    default_tax_rate: float | None = Field(None, ge=0, le=100)
    invoice_prefix: str | None = Field(None, min_length=1, max_length=20)
    invoice_terms: str | None = None

    # Order Management
    daily_order_limit: int | None = Field(None, ge=0)
    order_limit_enabled: bool | None = None
    order_limit_message: str | None = Field(None, min_length=10, max_length=500)

    # Delivery Charges
    delivery_charge_tiers: list[DeliveryChargeTier] | None = None

    # Vegetable Order Time Window
    veg_order_start_hour: int | None = Field(None, ge=0, le=23)
    veg_order_end_hour: int | None = Field(None, ge=0, le=23)
    veg_order_enabled: bool | None = None

    # Low Stock Alert
    low_stock_threshold: int | None = Field(None, ge=0)
    low_stock_alert_enabled: bool | None = None

    # Maintenance Mode
    maintenance_mode: bool | None = None
    maintenance_message: str | None = Field(None, min_length=10, max_length=500)


class AppSettingsPublic(BaseModel):
    """Public subset of settings exposed to unauthenticated users."""

    store_name: str = "Vidharthi Store"
    store_phone: str | None = None
    store_email: str | None = None
    store_address: str | None = None

    delivery_charge_tiers: list[DeliveryChargeTier] | None = None

    veg_order_start_hour: int = 5
    veg_order_end_hour: int = 9
    veg_order_enabled: bool = True

    maintenance_mode: bool = False
    maintenance_message: str = ""

    class Config:
        from_attributes = True
