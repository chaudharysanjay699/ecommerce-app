from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema, TimestampSchema


# ─────────────────────────────────────────────────────────────────────────────
# Offer
# ─────────────────────────────────────────────────────────────────────────────

class OfferCreate(BaseSchema):
    """Admin: attach a limited-time discount offer to a product."""

    product_id: UUID
    title: str = Field(..., min_length=3, max_length=200)
    discount_percent: float = Field(..., gt=0, le=100, description="Percentage off the product price")
    max_uses: int | None = Field(default=None, gt=0, description="Leave null for unlimited uses")
    expires_at: datetime = Field(..., description="UTC datetime when the offer expires")


class OfferUpdate(BaseSchema):
    """Admin: partial update of an existing offer."""

    title: str | None = Field(default=None, min_length=3, max_length=200)
    discount_percent: float | None = Field(default=None, gt=0, le=100)
    max_uses: int | None = Field(default=None, gt=0)
    expires_at: datetime | None = None
    is_active: bool | None = None


class OfferOut(TimestampSchema):
    """Offer response."""

    product_id: UUID
    title: str
    discount_percent: float
    max_uses: int | None
    used_count: int
    expires_at: datetime
    is_active: bool


class OfferWithProductOut(OfferOut):
    """Offer response with product details."""

    product: "ProductOut | None" = None


# Resolve forward references after ProductOut is defined
def _rebuild_offer_models():
    from app.schemas.product import ProductOut
    OfferWithProductOut.model_rebuild()

# This will be called when product schema is imported

