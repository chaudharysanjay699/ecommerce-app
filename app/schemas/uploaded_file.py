"""Schemas for uploaded file metadata."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from app.schemas.base import TimestampSchema


class UploadedFileOut(TimestampSchema):
    """Response schema for uploaded file metadata."""
    
    original_filename: str
    file_path: str
    file_url: str
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str
    entity_type: str = Field(..., description="Type of entity (category, product, banner, etc.)")
    entity_id: UUID | None = Field(None, description="ID of the associated entity")
    uploaded_by: UUID | None = Field(None, description="ID of admin who uploaded")


class UploadedFileCreate(TimestampSchema):
    """Schema for creating uploaded file record."""
    
    original_filename: str
    file_path: str
    file_url: str
    file_size: int
    mime_type: str
    entity_type: str
    entity_id: UUID | None = None
    uploaded_by: UUID | None = None
