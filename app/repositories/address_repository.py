from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.address import Address
from app.repositories.base_repository import BaseRepository


class AddressRepository(BaseRepository[Address]):
    """CRUD + lookup queries for the Address model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Address, db)

    # ── Specific queries ──────────────────────────────────────────────────────

    async def list_by_user(self, user_id: UUID) -> list[Address]:
        """Return all saved addresses for a user, default address first."""
        result = await self.db.execute(
            select(Address)
            .where(Address.user_id == user_id)
            .order_by(Address.is_default.desc(), Address.created_at)
        )
        return list(result.scalars().all())

    async def get_default(self, user_id: UUID) -> Address | None:
        """Return the address flagged as default for a user."""
        result = await self.db.execute(
            select(Address).where(
                Address.user_id == user_id,
                Address.is_default == True,  # noqa: E712
            )
        )
        return result.scalars().first()

    async def get_by_user_and_id(self, user_id: UUID, address_id: UUID) -> Address | None:
        """Return a specific address only if it belongs to the given user."""
        result = await self.db.execute(
            select(Address).where(
                Address.id == address_id,
                Address.user_id == user_id,
            )
        )
        return result.scalars().first()

    async def clear_default(self, user_id: UUID) -> None:
        """Remove the default flag from all addresses of a user.

        Call before setting a new default to enforce a single-default invariant.
        """
        await self.db.execute(
            update(Address)
            .where(
                Address.user_id == user_id,
                Address.is_default == True,  # noqa: E712
            )
            .values(is_default=False)
        )
        await self.db.flush()
