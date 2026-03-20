"""Schemas for application settings."""
from __future__ import annotations

from pydantic import BaseModel, Field


class AppSettingsOut(BaseModel):
    """Full application settings response."""

    # Store Information
    store_name: str = "Vidharthi Store"
    store_phone: str | None = None
    store_email: str | None = None
    store_address: str | None = None

    # Order Management
    daily_order_limit: int | None = None
    order_limit_enabled: bool = False
    order_limit_message: str = ""

    # Delivery Charges
    delivery_charge_single: float = 10.0
    delivery_charge_multiple: float = 15.0

    # Vegetable Order Time Window
    veg_order_start_hour: int = 5
    veg_order_end_hour: int = 9
    veg_order_enabled: bool = True

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

    # Order Management
    daily_order_limit: int | None = Field(None, ge=0)
    order_limit_enabled: bool | None = None
    order_limit_message: str | None = Field(None, min_length=10, max_length=500)

    # Delivery Charges
    delivery_charge_single: float | None = Field(None, ge=0)
    delivery_charge_multiple: float | None = Field(None, ge=0)

    # Vegetable Order Time Window
    veg_order_start_hour: int | None = Field(None, ge=0, le=23)
    veg_order_end_hour: int | None = Field(None, ge=0, le=23)
    veg_order_enabled: bool | None = None

    # Maintenance Mode
    maintenance_mode: bool | None = None
    maintenance_message: str | None = Field(None, min_length=10, max_length=500)


class AppSettingsPublic(BaseModel):
    """Public subset of settings exposed to unauthenticated users."""

    store_name: str = "Vidharthi Store"
    store_phone: str | None = None
    store_email: str | None = None
    store_address: str | None = None

    delivery_charge_single: float = 10.0
    delivery_charge_multiple: float = 15.0

    veg_order_start_hour: int = 5
    veg_order_end_hour: int = 9
    veg_order_enabled: bool = True

    maintenance_mode: bool = False
    maintenance_message: str = ""

    class Config:
        from_attributes = True
