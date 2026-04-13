from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import OTP, User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """CRUD + lookup queries for the User model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(User, db)

    # ── Specific queries ──────────────────────────────────────────────────────

    async def get_by_phone(self, phone: str) -> User | None:
        """Return a non-deleted user matching the given phone number."""
        result = await self.db.execute(
            select(User).where(
                User.phone == phone,
                User.is_deleted == False,  # noqa: E712
            )
        )
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        """Return a non-deleted user matching the given email address."""
        result = await self.db.execute(
            select(User).where(
                User.email == email,
                User.is_deleted == False,  # noqa: E712
            )
        )
        return result.scalars().first()

    async def get_with_addresses(self, user_id: UUID) -> User | None:
        """Return a user with all saved addresses eagerly loaded."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.addresses))
            .where(User.id == user_id)
        )
        return result.scalars().first()

    async def list_active(self, skip: int = 0, limit: int = 100):
        """Return only active (non-suspended, non-deleted) users."""
        result = await self.db.execute(
            select(User)
            .where(
                User.is_active == True,  # noqa: E712
                User.is_deleted == False,  # noqa: E712
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def list_for_admin(self, skip: int = 0, limit: int = 100):
        """Return users visible to admin — excludes deleted and super-admin users."""
        result = await self.db.execute(
            select(User)
            .where(
                User.is_deleted == False,  # noqa: E712
                User.is_super_admin == False,  # noqa: E712
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_admin_emails(self) -> list[str]:
        """Return email addresses of all active admin users."""
        result = await self.db.execute(
            select(User.email)
            .where(
                User.is_admin == True,  # noqa: E712
                User.is_active == True,  # noqa: E712
                User.is_deleted == False,  # noqa: E712
                User.email.isnot(None),
            )
        )
        return [row[0] for row in result.all() if row[0]]

    async def soft_delete(self, user: User) -> User:
        """Mark a user as deleted and deactivate them."""
        return await self.update(user, {
            "is_deleted": True,
            "is_active": False,
            "deleted_at": datetime.now(timezone.utc),
        })


class OTPRepository(BaseRepository[OTP]):
    """CRUD + lookup queries for the OTP model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(OTP, db)

    # ── Specific queries ──────────────────────────────────────────────────────

    async def get_latest_for_user(self, user_id: UUID) -> OTP | None:
        """Return the most recent unused OTP for a user."""
        result = await self.db.execute(
            select(OTP)
            .where(OTP.user_id == user_id, OTP.is_used == False)  # noqa: E712
            .order_by(OTP.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def invalidate_all_for_user(self, user_id: UUID) -> None:
        """Mark every unused OTP for a user as used (e.g. after password reset)."""
        from sqlalchemy import update

        await self.db.execute(
            update(OTP)
            .where(OTP.user_id == user_id, OTP.is_used == False)  # noqa: E712
            .values(is_used=True)
        )
        await self.db.flush()
