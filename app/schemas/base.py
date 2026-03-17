from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Root schema — enables ORM mode for all subclasses."""

    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(BaseSchema):
    """Adds id / created_at / updated_at to any response schema."""

    id: UUID
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseSchema):
    """Generic single-message response (e.g. success confirmations)."""

    message: str


class Page(BaseSchema, Generic[T]):
    """Wrapper for paginated list endpoints."""

    items: list[T]
    total: int
    skip: int
    limit: int
