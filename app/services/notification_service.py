from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.fcm import send_push
from app.models.notification import Banner, Notification
from app.repositories.notification_repository import (
    BannerRepository,
    DeviceTokenRepository,
    NotificationRepository,
)
from app.schemas.notification import BannerCreate, BannerUpdate, DeviceTokenOut, DeviceTokenRegister


class NotificationService:
    """Business logic for in-app notifications and FCM push delivery."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = NotificationRepository(db)
        self.device_repo = DeviceTokenRepository(db)

    # ── In-app notifications ──────────────────────────────────────────

    async def list_for_user(self, user_id: UUID, skip: int = 0, limit: int = 30):
        """Return paginated notifications for the authenticated user."""
        return await self.repo.list_for_user(user_id, skip, limit)

    async def count_unread(self, user_id: UUID) -> int:
        """Return the unread notification count (mobile badge value)."""
        return await self.repo.count_unread(user_id)

    async def mark_read(self, notification_id: UUID, user_id: UUID) -> Notification:
        """Mark a single notification as read. Enforces ownership."""
        notif = await self.repo.get_by_id(notification_id)
        if not notif:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        if notif.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return await self.repo.update(notif, {"is_read": True})

    async def mark_all_read(self, user_id: UUID) -> None:
        """Bulk-mark all unread notifications as read for the authenticated user."""
        await self.repo.mark_all_read(user_id)

    # ── Device token management ─────────────────────────────────────

    async def register_device(self, user_id: UUID, payload: DeviceTokenRegister) -> DeviceTokenOut:
        """Register or refresh an FCM device token for the authenticated user."""
        token = await self.device_repo.upsert(
            user_id=user_id,
            device_token=payload.device_token,
            device_type=payload.device_type,
        )
        await self.db.commit()
        return DeviceTokenOut.model_validate(token)

    # ── FCM push helpers ─────────────────────────────────────────────

    async def send_to_user(self, user_id: UUID, title: str, message: str) -> None:
        """Send an FCM push notification to all devices registered for `user_id`."""
        tokens = await self.device_repo.get_tokens_for_user(user_id)
        await send_push(tokens, title, message)

    async def send_to_admins(self, title: str, message: str) -> None:
        """Send an FCM push notification to all admin users' devices."""
        tokens = await self.device_repo.get_all_admin_tokens()
        await send_push(tokens, title, message)

    async def broadcast(self, title: str, message: str) -> None:
        """Send an FCM push notification to every registered device (all users)."""
        tokens = await self.device_repo.get_all_tokens()
        await send_push(tokens, title, message)


class BannerService:
    """Business logic for home-screen banners."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = BannerRepository(db)

    async def list_active(self):
        """Return all active banners ordered by sort_order."""
        return await self.repo.list_active()

    async def create(self, payload: BannerCreate) -> Banner:
        """Admin: create a new banner."""
        banner = Banner(**payload.model_dump())
        return await self.repo.create(banner)

    async def update(self, banner_id: UUID, payload: BannerUpdate) -> Banner:
        """Admin: partially update a banner."""
        banner = await self.repo.get_by_id(banner_id)
        if not banner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found")
        data = payload.model_dump(exclude_none=True)
        if not data:
            return banner
        return await self.repo.update(banner, data)

    async def toggle(self, banner_id: UUID, is_active: bool) -> Banner:
        """Admin: activate or deactivate a banner."""
        banner = await self.repo.get_by_id(banner_id)
        if not banner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found")
        return await self.repo.update(banner, {"is_active": is_active})
