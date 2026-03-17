from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import OrderStatus
from app.models.order_tracking import OrderTracking
from app.repositories.base_repository import BaseRepository


class OrderTrackingRepository(BaseRepository[OrderTracking]):
    """CRUD + lookup queries for the OrderTracking model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(OrderTracking, db)

    # ── Specific queries ──────────────────────────────────────────────────────

    async def list_by_order(self, order_id: UUID) -> list[OrderTracking]:
        """Return all tracking events for an order, oldest first."""
        result = await self.db.execute(
            select(OrderTracking)
            .where(OrderTracking.order_id == order_id)
            .order_by(OrderTracking.created_at)
        )
        return list(result.scalars().all())

    async def get_latest(self, order_id: UUID) -> OrderTracking | None:
        """Return the most recent tracking event for an order."""
        result = await self.db.execute(
            select(OrderTracking)
            .where(OrderTracking.order_id == order_id)
            .order_by(OrderTracking.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def has_status(self, order_id: UUID, status: OrderStatus) -> bool:
        """Return True if the order has ever been in the given status."""
        result = await self.db.execute(
            select(OrderTracking).where(
                OrderTracking.order_id == order_id,
                OrderTracking.status == status,
            ).limit(1)
        )
        return result.scalars().first() is not None
