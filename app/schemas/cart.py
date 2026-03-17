from __future__ import annotations

from uuid import UUID

from pydantic import Field, computed_field

from app.schemas.base import BaseSchema, TimestampSchema
from app.schemas.product import ProductOut


# ─────────────────────────────────────────────────────────────────────────────
# Cart Item
# ─────────────────────────────────────────────────────────────────────────────

class CartItemAdd(BaseSchema):
    """Add a product to the cart (or increase quantity if already present)."""

    product_id: UUID
    quantity: int = Field(default=1, ge=1)


class CartItemUpdate(BaseSchema):
    """Set an explicit quantity for a cart item."""

    quantity: int = Field(..., ge=1)


class CartItemOut(TimestampSchema):
    """Single line-item in a cart response."""

    product_id: UUID
    quantity: int
    unit_price: float
    product: ProductOut

    @computed_field  # type: ignore[misc]
    @property
    def line_total(self) -> float:
        return round(self.unit_price * self.quantity, 2)


# ─────────────────────────────────────────────────────────────────────────────
# Cart
# ─────────────────────────────────────────────────────────────────────────────

class CartOut(TimestampSchema):
    """Full cart response with embedded line items and computed totals."""

    user_id: UUID
    items: list[CartItemOut] = []

    @computed_field  # type: ignore[misc]
    @property
    def subtotal(self) -> float:
        return round(sum(i.line_total for i in self.items), 2)

    @computed_field  # type: ignore[misc]
    @property
    def item_count(self) -> int:
        return sum(i.quantity for i in self.items)

