from __future__ import annotations

from uuid import UUID

from app.schemas.base import TimestampSchema
from app.schemas.product import ProductDetailOut, ProductOut


class WishlistItemOut(TimestampSchema):
    """Single wishlist item returned to the client."""

    user_id: UUID
    product_id: UUID
    product: ProductOut


class WishlistStatusOut(TimestampSchema):
    """Is a specific product in the user's wishlist?"""

    product_id: UUID
    wishlisted: bool
