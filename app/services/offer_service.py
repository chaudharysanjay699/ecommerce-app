from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.offer import Offer
from app.repositories.offer_repository import OfferRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.offer import OfferCreate, OfferUpdate


class OfferService:
    """Business logic for managing product discount offers."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = OfferRepository(db)
        self.product_repo = ProductRepository(db)

    # ── Queries ─────────────────────────────────────────────────────────────────────

    async def list_active(self, skip: int = 0, limit: int = 50):
        """Return all currently active, non-expired offers."""
        return await self.repo.list_active(skip, limit)

    async def list_all(self, skip: int = 0, limit: int = 100):
        """Admin: Return all offers (including inactive and expired)."""
        return await self.repo.list_all(skip, limit)

    async def get_offer(self, offer_id: UUID) -> Offer:
        """Return a single offer or raise 404."""
        offer = await self.repo.get_by_id(offer_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found"
            )
        return offer

    # ── Mutations ───────────────────────────────────────────────────────────────────

    async def create(self, payload: OfferCreate) -> Offer:
        """Admin: create a new offer. One active offer per product is enforced."""
        product = await self.product_repo.get_by_id(payload.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        existing = await self.repo.get_active_for_product(payload.product_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An active offer already exists for this product",
            )
        offer = Offer(**payload.model_dump())
        return await self.repo.create(offer)

    async def update(self, offer_id: UUID, payload: OfferUpdate) -> Offer:
        """Admin: partially update an existing offer."""
        offer = await self.repo.get_by_id(offer_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found"
            )
        data = payload.model_dump(exclude_none=True)
        if not data:
            return offer
        return await self.repo.update(offer, data)

    async def deactivate(self, offer_id: UUID) -> Offer:
        """Admin: immediately deactivate an offer."""
        offer = await self.repo.get_by_id(offer_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found"
            )
        return await self.repo.update(offer, {"is_active": False})

    async def delete(self, offer_id: UUID) -> None:
        """Admin: permanently delete an offer."""
        offer = await self.repo.get_by_id(offer_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found"
            )
        await self.repo.delete(offer)

