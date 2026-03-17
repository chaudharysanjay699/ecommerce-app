from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.models.wishlist import WishlistItem
from app.repositories.base_repository import BaseRepository


class WishlistRepository(BaseRepository[WishlistItem]):
    def __init__(self, db) -> None:
        super().__init__(WishlistItem, db)

    async def get_by_user(self, user_id: UUID) -> list[WishlistItem]:
        result = await self.db.execute(
            select(WishlistItem)
            .where(WishlistItem.user_id == user_id)
            .options(selectinload(WishlistItem.product))
            .order_by(WishlistItem.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_item(self, user_id: UUID, product_id: UUID) -> WishlistItem | None:
        result = await self.db.execute(
            select(WishlistItem).where(
                WishlistItem.user_id == user_id,
                WishlistItem.product_id == product_id,
            )
        )
        return result.scalars().first()

    async def get_item_with_product(self, user_id: UUID, product_id: UUID) -> WishlistItem | None:
        """Same as get_item but eagerly loads the product relationship."""
        result = await self.db.execute(
            select(WishlistItem)
            .where(
                WishlistItem.user_id == user_id,
                WishlistItem.product_id == product_id,
            )
            .options(selectinload(WishlistItem.product))
        )
        return result.scalars().first()

    async def remove_item(self, user_id: UUID, product_id: UUID) -> None:
        await self.db.execute(
            delete(WishlistItem).where(
                WishlistItem.user_id == user_id,
                WishlistItem.product_id == product_id,
            )
        )
        await self.db.flush()
