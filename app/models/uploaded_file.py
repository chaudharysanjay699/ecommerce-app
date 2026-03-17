"""Uploaded file model for tracking image uploads."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class UploadedFile(Base, UUIDMixin, TimestampMixin):
    """Track metadata for all uploaded files (images, documents, etc.)."""
    
    __tablename__ = "uploaded_files"

    # File details
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # bytes
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Entity association (what this file belongs to)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'category', 'product', 'banner', etc.
    entity_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)  # FK to the entity (can be null if uploaded but not yet assigned)
    
    # Upload metadata
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
