"""Repository for uploaded file metadata operations."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.uploaded_file import UploadedFile
from app.repositories.base_repository import BaseRepository


class UploadedFileRepository(BaseRepository[UploadedFile]):
    """Repository for uploaded file CRUD operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(UploadedFile, db)

    async def get_by_entity(self, entity_type: str, entity_id: UUID) -> list[UploadedFile]:
        """Get all files associated with a specific entity."""
        result = await self.db.execute(
            select(UploadedFile)
            .where(
                UploadedFile.entity_type == entity_type,
                UploadedFile.entity_id == entity_id
            )
            .order_by(UploadedFile.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_path(self, file_path: str) -> UploadedFile | None:
        """Get file metadata by file path."""
        result = await self.db.execute(
            select(UploadedFile).where(UploadedFile.file_path == file_path)
        )
        return result.scalar_one_or_none()

    async def delete_by_entity(self, entity_type: str, entity_id: UUID) -> None:
        """Delete all file records for a specific entity."""
        files = await self.get_by_entity(entity_type, entity_id)
        for file in files:
            await self.delete(file)
