"""Public application settings endpoint (no auth required)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.app_settings import AppSettingsPublic

router = APIRouter(prefix="/app", tags=["App"])

DB = Annotated[AsyncSession, Depends(get_db)]


@router.get("/settings", response_model=AppSettingsPublic)
async def get_public_settings(db: DB):
    """Return public application settings (store info, delivery charges, maintenance status)."""
    from app.repositories.app_settings_repository import AppSettingsRepository
    return await AppSettingsRepository(db).get_settings()
