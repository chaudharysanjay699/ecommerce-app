from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.repositories.address_repository import AddressRepository
from app.schemas.address import AddressCreate, AddressOut, AddressUpdate

router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.get("", response_model=list[AddressOut])
async def list_addresses(
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return all saved addresses for the authenticated user."""
    repo = AddressRepository(db)
    return await repo.list_by_user(current_user.id)


@router.post("", response_model=AddressOut, status_code=status.HTTP_201_CREATED)
async def create_address(
    payload: AddressCreate,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Save a new delivery address."""
    repo = AddressRepository(db)

    if payload.is_default:
        await repo.clear_default(current_user.id)

    from app.models.address import Address

    address = Address(user_id=current_user.id, **payload.model_dump())
    return await repo.create(address)


@router.get("/{address_id}", response_model=AddressOut)
async def get_address(
    address_id: UUID,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return a specific saved address."""
    repo = AddressRepository(db)
    address = await repo.get_by_user_and_id(current_user.id, address_id)
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    return address


@router.patch("/{address_id}", response_model=AddressOut)
async def update_address(
    address_id: UUID,
    payload: AddressUpdate,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a saved address."""
    repo = AddressRepository(db)
    address = await repo.get_by_user_and_id(current_user.id, address_id)
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    update_data = payload.model_dump(exclude_unset=True)

    if update_data.get("is_default"):
        await repo.clear_default(current_user.id)

    return await repo.update(address, update_data)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: UUID,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a saved address."""
    repo = AddressRepository(db)
    address = await repo.get_by_user_and_id(current_user.id, address_id)
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    await repo.delete(address)
