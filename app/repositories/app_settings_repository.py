"""Repository for application settings."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_settings import AppSettings
from app.repositories.base_repository import BaseRepository


class AppSettingsRepository(BaseRepository[AppSettings]):
    """CRUD operations for application settings (singleton pattern)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(AppSettings, db)

    async def get_settings(self) -> AppSettings:
        """Get the application settings (creates default if not exists)."""
        result = await self.db.execute(select(AppSettings).limit(1))
        settings = result.scalars().first()
        
        if not settings:
            # Create default settings if none exist
            settings = AppSettings(
                store_name="Vidharthi Store",
                daily_order_limit=None,
                order_limit_enabled=False,
                order_limit_message="We are currently unable to accept new orders. Please try again later.",
                delivery_charge_single=10.0,
                delivery_charge_multiple=15.0,
                veg_order_start_hour=5,
                veg_order_end_hour=9,
                veg_order_enabled=True,
                maintenance_mode=False,
                maintenance_message="We are currently under maintenance. Please try again later.",
            )
            self.db.add(settings)
            await self.db.flush()
            await self.db.refresh(settings)
        
        return settings

    async def update_settings(self, data: dict) -> AppSettings:
        """Update application settings."""
        settings = await self.get_settings()
        for key, value in data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        await self.db.flush()
        await self.db.refresh(settings)
        return settings
