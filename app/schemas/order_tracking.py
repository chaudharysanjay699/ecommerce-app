from __future__ import annotations

from pydantic import Field

from app.models.order import OrderStatus
from app.schemas.base import BaseSchema, TimestampSchema


# ── Create ────────────────────────────────────────────────────────────────────

class OrderTrackingCreate(BaseSchema):
    """Internal: record a new status event on an order tracking log."""

    status: OrderStatus
    description: str | None = Field(default=None, max_length=300)
    changed_by: str | None = Field(
        default=None,
        max_length=100,
        description="Admin user id (as string) or 'system'",
    )


# ── Response ──────────────────────────────────────────────────────────────────

class OrderTrackingOut(TimestampSchema):
    """Single tracking event returned inside an order response."""

    status: OrderStatus
    description: str | None
    changed_by: str | None
