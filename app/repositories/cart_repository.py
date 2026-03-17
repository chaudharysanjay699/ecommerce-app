from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import Cart, CartItem
from app.repositories.base_repository import BaseRepository


class CartRepository(BaseRepository[Cart]):
    """CRUD + lookup queries for the Cart model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Cart, db)

    # ── Specific queries ──────────────────────────────────────────────────────

    async def get_by_user_id(self, user_id: UUID) -> Cart | None:
        """Return a user's cart with all items eagerly loaded."""
        result = await self.db.execute(
            select(Cart)
            .options(selectinload(Cart.items).selectinload(CartItem.product))
            .where(Cart.user_id == user_id)
        )
        return result.scalars().first()

    async def clear_items(self, cart_id: UUID) -> None:
        """Bulk-delete all items belonging to a cart."""
        await self.db.execute(
            delete(CartItem).where(CartItem.cart_id == cart_id)
        )
        await self.db.flush()


class CartItemRepository(BaseRepository[CartItem]):
    """CRUD + lookup queries for the CartItem model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(CartItem, db)

    # ── Specific queries ──────────────────────────────────────────────────────

    async def get_by_cart_and_product(
        self, cart_id: UUID, product_id: UUID
    ) -> CartItem | None:
        """Return the cart item for a specific product in a specific cart."""
        result = await self.db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart_id,
                CartItem.product_id == product_id,
            )
        )
        return result.scalars().first()

    async def list_by_cart(self, cart_id: UUID):
        """Return all items in a cart with their product eagerly loaded."""
        result = await self.db.execute(
            select(CartItem)
            .options(selectinload(CartItem.product))
            .where(CartItem.cart_id == cart_id)
        )
        return result.scalars().all()
