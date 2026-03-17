from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.offer import Offer
from app.repositories.base_repository import BaseRepository


class OfferRepository(BaseRepository[Offer]):
    """CRUD + lookup queries for the Offer model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Offer, db)

    # ── Specific queries ──────────────────────────────────────────────────────

    async def get_active_for_product(self, product_id: UUID) -> Offer | None:
        """Return the active, non-expired offer for a product (if any)."""
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(Offer).where(
                Offer.product_id == product_id,
                Offer.is_active == True,  # noqa: E712
                Offer.expires_at > now,
            )
        )
        return result.scalars().first()

    async def list_active(self, skip: int = 0, limit: int = 50):
        """Return all currently active and non-expired offers with product details."""
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(Offer)
            .options(selectinload(Offer.product))
            .where(
                Offer.is_active == True,  # noqa: E712
                Offer.expires_at > now,
            )
            .order_by(Offer.expires_at)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def list_expired(self, skip: int = 0, limit: int = 50):
        """Return offers that have passed their expiry date."""
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(Offer)
            .where(Offer.expires_at <= now)
            .order_by(Offer.expires_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def list_all(self, skip: int = 0, limit: int = 100):
        """Return all offers (active, inactive, expired) - for admin."""
        result = await self.db.execute(
            select(Offer)
            .order_by(Offer.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
