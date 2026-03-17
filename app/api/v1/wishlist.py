from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.wishlist import WishlistItemOut
from app.services.wishlist_service import WishlistService

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.get("", response_model=list[WishlistItemOut])
async def list_wishlist(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return all wishlist items for the current user."""
    return await WishlistService(db).list_items(current_user.id)


@router.post("/{product_id}", response_model=WishlistItemOut, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    product_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Add a product to the wishlist."""
    return await WishlistService(db).add(current_user.id, product_id)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(
    product_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Remove a product from the wishlist."""
    await WishlistService(db).remove(current_user.id, product_id)


@router.post("/{product_id}/toggle")
async def toggle_wishlist(
    product_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Toggle a product in/out of the wishlist. Returns {wishlisted: bool}."""
    return await WishlistService(db).toggle(current_user.id, product_id)


@router.get("/{product_id}/status")
async def wishlist_status(
    product_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Check if a product is in the user's wishlist."""
    wishlisted = await WishlistService(db).is_wishlisted(current_user.id, product_id)
    return {"product_id": product_id, "wishlisted": wishlisted}
