from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wishlist import WishlistItem
from app.repositories.wishlist_repository import WishlistRepository
from app.repositories.product_repository import ProductRepository


class WishlistService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = WishlistRepository(db)
        self.product_repo = ProductRepository(db)

    async def list_items(self, user_id: UUID) -> list[WishlistItem]:
        return await self.repo.get_by_user(user_id)

    async def add(self, user_id: UUID, product_id: UUID) -> WishlistItem:
        product = await self.product_repo.get_by_id(product_id)
        if not product or not product.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        existing = await self.repo.get_item_with_product(user_id, product_id)
        if existing:
            return existing

        item = WishlistItem(user_id=user_id, product_id=product_id)
        await self.repo.create(item)
        # Reload with product relationship so the response schema can serialize it
        return await self.repo.get_item_with_product(user_id, product_id)

    async def remove(self, user_id: UUID, product_id: UUID) -> None:
        await self.repo.remove_item(user_id, product_id)

    async def toggle(self, user_id: UUID, product_id: UUID) -> dict:
        existing = await self.repo.get_item(user_id, product_id)
        if existing:
            await self.repo.remove_item(user_id, product_id)
            return {"wishlisted": False}
        else:
            await self.add(user_id, product_id)
            return {"wishlisted": True}

    async def is_wishlisted(self, user_id: UUID, product_id: UUID) -> bool:
        item = await self.repo.get_item(user_id, product_id)
        return item is not None
