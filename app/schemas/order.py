from __future__ import annotations

from uuid import UUID

from pydantic import Field

from app.models.order import OrderStatus
from app.schemas.base import BaseSchema, TimestampSchema
from app.schemas.order_tracking import OrderTrackingOut


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

class OrderItemOut(TimestampSchema):
    """Single line item within an order response."""

    product_id: UUID
    quantity: int
    unit_price: float
    subtotal: float


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

