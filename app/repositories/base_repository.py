from __future__ import annotations

from typing import Any, Generic, Sequence, Type, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic async repository providing create / read / update / delete for any ORM model.

    Concrete repositories subclass this and add model-specific query methods.
    No business logic lives here — only data-access operations.
    """

    def __init__(self, model: Type[ModelT], db: AsyncSession) -> None:
        self.model = model
        self.db = db

    # ── Read ──────────────────────────────────────────────────────────────────

    async def get_by_id(self, id: UUID) -> ModelT | None:
        """Return a single record by primary key, or None."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalars().first()

    async def list(
        self, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelT]:
        """Return a paginated slice of all records (no filters)."""
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    # Backward-compat alias
    async def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelT]:
        return await self.list(skip, limit)

    async def count(self) -> int:
        """Return the total row count for the model's table."""
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()

    # ── Write ─────────────────────────────────────────────────────────────────

    async def create(self, obj: ModelT) -> ModelT:
        """Persist a new ORM instance, flush, and return the refreshed object."""
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: ModelT, data: dict[str, Any]) -> ModelT:
        """Apply a dict of field→value pairs to *obj*, flush, and return it.

        The caller is responsible for passing only validated, safe data.
        """
        for field, value in data.items():
            setattr(obj, field, value)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: ModelT) -> None:
        """Delete *obj* from the database and flush."""
        await self.db.delete(obj)
        await self.db.flush()
