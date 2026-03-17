from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin, get_current_user
from app.schemas.notification import (
    BannerOut,
    BroadcastPayload,
    DeviceTokenOut,
    DeviceTokenRegister,
    NotificationOut,
)
from app.services.notification_service import BannerService, NotificationService

router = APIRouter(tags=["Notifications & Banners"])


# ── Device token registration ────────────────────────────────────────────────

@router.post(
    "/notifications/register-device",
    response_model=DeviceTokenOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register FCM device token",
)
async def register_device(
    payload: DeviceTokenRegister,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Register or refresh the FCM push token for the current user's device.
    Call this on app launch and whenever the FCM token rotates.
    """
    return await NotificationService(db).register_device(current_user.id, payload)


# ── In-app notifications ─────────────────────────────────────────────────────

@router.get("/notifications", response_model=list[NotificationOut])
async def list_notifications(
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 30,
):
    """Return paginated in-app notifications for the authenticated user."""
    return await NotificationService(db).list_for_user(current_user.id, skip, limit)


@router.patch("/notifications/{notification_id}/read", response_model=NotificationOut)
async def mark_read(
    notification_id: UUID,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Mark a single notification as read."""
    return await NotificationService(db).mark_read(notification_id, current_user.id)


@router.patch("/notifications/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Mark all notifications as read for the authenticated user."""
    await NotificationService(db).mark_all_read(current_user.id)
    await db.commit()


# ── Broadcast (admin) ────────────────────────────────────────────────────────

@router.post(
    "/notifications/broadcast",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Broadcast push notification to all users (Admin)",
)
async def broadcast_notification(
    payload: BroadcastPayload,
    _: Annotated[object, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Admin: send a push notification to every registered device.
    Returns 202 immediately; FCM delivery happens in the same request.
    """
    await NotificationService(db).broadcast(payload.title, payload.message)
    return {"message": "Broadcast dispatched successfully"}


# ── Banners ──────────────────────────────────────────────────────────────────

@router.get("/banners", response_model=list[BannerOut])
async def list_banners(db: Annotated[AsyncSession, Depends(get_db)]):
    """Return active home-screen banners sorted by sort_order. No auth required."""
    return await BannerService(db).list_active()
