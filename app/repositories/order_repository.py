from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem, OrderStatus
from app.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """CRUD + lookup queries for the Order model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Order, db)

    # ── Specific queries ──────────────────────────────────────────────────────

    async def get_with_items(self, order_id: UUID) -> Order | None:
        """Return an order with its line items eagerly loaded."""
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        return result.scalars().first()

    async def get_full(self, order_id: UUID) -> Order | None:
        """Return an order with items *and* tracking history eagerly loaded."""
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.tracking),
                selectinload(Order.user),
            )
            .where(Order.id == order_id)
        )
        return result.scalars().first()

    async def list_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 20
    ):
        """Return a user's orders (newest first) with items and tracking."""
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.tracking),
            )
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def list_all_orders(self, skip: int = 0, limit: int = 50):
        """Admin: return all orders (newest first) with items and tracking."""
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.tracking),
                selectinload(Order.user),
            )
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def list_by_status(self, status: OrderStatus, skip: int = 0, limit: int = 50):
        """Admin: filter orders by a specific status."""
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.status == status)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


class OrderItemRepository(BaseRepository[OrderItem]):
    """CRUD + lookup queries for the OrderItem model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(OrderItem, db)

    # ── Specific queries ──────────────────────────────────────────────────────

    async def list_by_order(self, order_id: UUID):
        """Return all line items for a given order."""
        result = await self.db.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        return result.scalars().all()
