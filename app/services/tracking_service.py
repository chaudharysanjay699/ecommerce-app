from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import OrderStatus
from app.models.order_tracking import OrderTracking
from app.repositories.order_repository import OrderRepository
from app.repositories.order_tracking_repository import OrderTrackingRepository


class TrackingService:
    """Business logic for order tracking history."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = OrderTrackingRepository(db)
        self.order_repo = OrderRepository(db)

    async def get_timeline(self, order_id: UUID, user_id: UUID) -> list[OrderTracking]:
        """Return the full tracking timeline for an order.

        Validates that the requesting user owns the order.
        Admins should call ``list_for_order`` directly.
        """
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
        return await self.repo.list_by_order(order_id)

    async def list_for_order(self, order_id: UUID) -> list[OrderTracking]:
        """Admin: return all tracking events for any order."""
        return await self.repo.list_by_order(order_id)

    async def add_event(
        self,
        order_id: UUID,
        status: OrderStatus,
        description: str | None = None,
        changed_by: str | None = None,
    ) -> OrderTracking:
        """Append a new tracking event to an order's history."""
        event = OrderTracking(
            order_id=order_id,
            status=status,
            description=description,
            changed_by=changed_by,
        )
        return await self.repo.create(event)

    async def get_latest(self, order_id: UUID) -> OrderTracking | None:
        """Return the most recent tracking event for an order."""
        return await self.repo.get_latest(order_id)
