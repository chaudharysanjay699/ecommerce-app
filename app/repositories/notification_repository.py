from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Banner, DeviceToken, Notification
from app.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """CRUD + lookup queries for the Notification model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Notification, db)

    # ── Specific queries ──────────────────────────────────────────────────────

    async def list_for_user(
        self, user_id: UUID, skip: int = 0, limit: int = 30
    ):
        """Return a user's notifications, newest first."""
        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def count_unread(self, user_id: UUID) -> int:
        """Return the number of unread notifications for a user (badge count)."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False,  # noqa: E712
            )
        )
        return result.scalar_one()

    async def mark_all_read(self, user_id: UUID) -> None:
        """Bulk-mark every unread notification for a user as read."""
        await self.db.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False,  # noqa: E712
            )
            .values(is_read=True)
        )
        await self.db.flush()


class BannerRepository(BaseRepository[Banner]):
    """CRUD + lookup queries for the Banner model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Banner, db)

    # ── Specific queries ──────────────────────────────────────────────────────

    async def list_active(self):
        """Return all active banners ordered by sort_order."""
        result = await self.db.execute(
            select(Banner)
            .where(Banner.is_active == True)  # noqa: E712
            .order_by(Banner.sort_order)
        )
        return result.scalars().all()


class DeviceTokenRepository(BaseRepository[DeviceToken]):
    """CRUD + lookup queries for FCM device tokens."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(DeviceToken, db)

    async def get_by_token(self, device_token: str) -> DeviceToken | None:
        """Return a device token record by its token string."""
        result = await self.db.execute(
            select(DeviceToken).where(DeviceToken.device_token == device_token)
        )
        return result.scalars().first()

    async def get_tokens_for_user(self, user_id: UUID) -> list[str]:
        """Return all FCM token strings for a given user."""
        result = await self.db.execute(
            select(DeviceToken.device_token).where(DeviceToken.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_all_admin_tokens(self) -> list[str]:
        """Return FCM tokens belonging to all admin users."""
        from app.models.user import User
        result = await self.db.execute(
            select(DeviceToken.device_token)
            .join(User, User.id == DeviceToken.user_id)
            .where(User.is_admin == True, User.is_active == True)  # noqa: E712
        )
        return list(result.scalars().all())

    async def get_all_tokens(self, skip: int = 0, limit: int = 5000) -> list[str]:
        """Return all registered FCM tokens (for broadcast)."""
        result = await self.db.execute(
            select(DeviceToken.device_token).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def upsert(self, user_id: UUID, device_token: str, device_type: str) -> DeviceToken:
        """Register a new token or update the device_type if the token already exists."""
        existing = await self.get_by_token(device_token)
        if existing:
            return await self.update(existing, {"device_type": device_type, "user_id": user_id})
        token = DeviceToken(user_id=user_id, device_token=device_token, device_type=device_type)
        return await self.create(token)

    async def delete_for_user(self, user_id: UUID, device_token: str) -> None:
        """Remove a specific token for a user (e.g. on logout)."""
        existing = await self.get_by_token(device_token)
        if existing and existing.user_id == user_id:
            await self.delete(existing)
