from __future__ import annotations

from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.order import OrderCreate, OrderOut
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Place an order from the current cart."""
    return await OrderService(db).create_order(current_user.id, payload)


@router.get("", response_model=list[OrderOut])
async def list_my_orders(
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    """Return the authenticated user's order history."""
    return await OrderService(db).list_user_orders(current_user.id, skip, limit)


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: UUID,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return a single order (with items and tracking history)."""
    return await OrderService(db).get_order(order_id, current_user.id)


@router.get("/{order_id}/invoice")
async def get_order_invoice(
    order_id: UUID,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return the invoice PDF for a user's order."""
    order = await OrderService(db).get_order(order_id, current_user.id)
    if not order.invoice_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not generated yet")
    filepath = Path(settings.UPLOAD_DIR) / "pdfs" / f"invoice_{order.id}.pdf"
    if not filepath.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice file not found")
    return FileResponse(
        path=str(filepath),
        media_type="application/pdf",
        filename=f"invoice_{str(order.id)[:8]}.pdf",
    )


@router.get("/{order_id}/shipping-label")
async def get_order_shipping_label(
    order_id: UUID,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return the shipping label PDF for a user's order."""
    order = await OrderService(db).get_order(order_id, current_user.id)
    if not order.shipping_label_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipping label not generated yet")
    filepath = Path(settings.UPLOAD_DIR) / "pdfs" / f"shipping_label_{order.id}.pdf"
    if not filepath.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipping label file not found")
    return FileResponse(
        path=str(filepath),
        media_type="application/pdf",
        filename=f"shipping_label_{str(order.id)[:8]}.pdf",
    )
