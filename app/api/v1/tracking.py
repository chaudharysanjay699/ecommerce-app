from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.order_tracking import OrderTrackingOut
from app.services.tracking_service import TrackingService

router = APIRouter(prefix="/orders", tags=["Tracking"])


@router.get("/{order_id}/tracking", response_model=list[OrderTrackingOut])
async def get_order_tracking(
    order_id: UUID,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return the full status-change timeline for one of the user's orders."""
    return await TrackingService(db).get_timeline(order_id, current_user.id)
