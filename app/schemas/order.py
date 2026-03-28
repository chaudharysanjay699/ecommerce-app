from __future__ import annotations

from uuid import UUID

from pydantic import Field, field_validator

from app.models.order import OrderStatus
from app.schemas.base import BaseSchema, TimestampSchema
from app.schemas.order_tracking import OrderTrackingOut
from app.schemas.product import make_full_url


# ─────────────────────────────────────────────────────────────────────────────
# Create
# ─────────────────────────────────────────────────────────────────────────────

class OrderCreate(BaseSchema):
    """Checkout: convert the current cart into an order."""

    delivery_address: str = Field(..., min_length=5, description="Full delivery address string")
    address_id: UUID | None = Field(
        default=None,
        description="UUID of a saved address; overrides delivery_address when provided",
    )
    notes: str | None = Field(default=None, max_length=500)


# ─────────────────────────────────────────────────────────────────────────────
# Update (admin)
# ─────────────────────────────────────────────────────────────────────────────

class AdminOrderCancel(BaseSchema):
    """Admin: cancel an order and record the reason."""

    reason: str = Field(..., min_length=3, max_length=300)


class OrderStatusUpdate(BaseSchema):
    """Admin: advance an order to the next status."""

    status: OrderStatus
    description: str | None = Field(
        default=None,
        max_length=300,
        description="Optional note appended to the tracking log",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Response
# ─────────────────────────────────────────────────────────────────────────────

class OrderItemProductOut(BaseSchema):
    """Minimal product info for order items."""

    id: UUID
    name: str
    image_url: str | None
    price: float
    is_active: bool
    
    @field_validator('image_url', mode='before')
    @classmethod
    def convert_image_url(cls, v):
        """Convert relative path to full URL."""
        return make_full_url(v)


class OrderItemOut(TimestampSchema):
    """Single line item within an order response."""

    product_id: UUID
    quantity: int
    unit_price: float
    subtotal: float
    product: OrderItemProductOut | None = None


class OrderUserOut(BaseSchema):
    """User information included in order response."""

    full_name: str
    phone: str
    email: str | None
    avatar_url: str | None
    is_active: bool
    is_verified: bool


class OrderOut(TimestampSchema):
    """Full order response — includes items and tracking history."""

    user_id: UUID
    user: OrderUserOut | None = None
    status: OrderStatus
    subtotal: float
    delivery_charge: float
    total: float
    delivery_address: str
    notes: str | None
    cancel_reason: str | None
    items: list[OrderItemOut] = []
    tracking: list[OrderTrackingOut] = []

