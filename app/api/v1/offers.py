from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.schemas.offer import OfferCreate, OfferOut, OfferUpdate, OfferWithProductOut, _rebuild_offer_models
from app.schemas.product import ProductOut  # Import ProductOut to resolve forward reference
from app.services.offer_service import OfferService

# Rebuild offer models after ProductOut is imported
_rebuild_offer_models()

router = APIRouter(prefix="/offers", tags=["Offers"])


@router.get("", response_model=list[OfferWithProductOut])
async def list_offers(db: Annotated[AsyncSession, Depends(get_db)]):
    return await OfferService(db).list_active()


@router.get("/admin/all", response_model=list[OfferOut])
async def list_all_offers(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[object, Depends(get_current_admin)],
):
    """Admin: Get all offers (active, inactive, expired)."""
    return await OfferService(db).list_all()


@router.post("", response_model=OfferOut, status_code=201)
async def create_offer(
    payload: OfferCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[object, Depends(get_current_admin)],
):
    return await OfferService(db).create(payload)


@router.patch("/{offer_id}/deactivate", response_model=OfferOut)
async def deactivate_offer(
    offer_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[object, Depends(get_current_admin)],
):
    return await OfferService(db).deactivate(offer_id)


@router.patch("/{offer_id}", response_model=OfferOut)
async def update_offer(
    offer_id: UUID,
    payload: OfferUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[object, Depends(get_current_admin)],
):
    """Admin: Update an existing offer."""
    return await OfferService(db).update(offer_id, payload)


@router.delete("/{offer_id}", status_code=204)
async def delete_offer(
    offer_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[object, Depends(get_current_admin)],
):
    """Admin: Permanently delete an offer."""
    await OfferService(db).delete(offer_id)

