from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.cart import CartItemAdd, CartItemUpdate, CartOut
from app.services.cart_service import CartService

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("", response_model=CartOut)
async def get_cart(
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return the authenticated user's cart (created lazily if absent)."""
    return await CartService(db).get_cart(current_user.id)


@router.post("/items", response_model=CartOut, status_code=status.HTTP_201_CREATED)
async def add_item(
    payload: CartItemAdd,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Add a product to the cart or increment its quantity if already present."""
    return await CartService(db).add_item(current_user.id, payload)


@router.put("/items/{product_id}", response_model=CartOut)
async def update_item(
    product_id: UUID,
    payload: CartItemUpdate,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Set the exact quantity for a cart item."""
    return await CartService(db).update_item(current_user.id, product_id, payload)


@router.delete("/items/{product_id}", response_model=CartOut)
async def remove_item(
    product_id: UUID,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Remove a single product from the cart."""
    return await CartService(db).remove_item(current_user.id, product_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Remove all items from the cart at once."""
    await CartService(db).clear_cart(current_user.id)
