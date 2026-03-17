from __future__ import annotations

from pydantic import Field

from app.schemas.base import BaseSchema, TimestampSchema


# ── Create ────────────────────────────────────────────────────────────────────

class AddressCreate(BaseSchema):
    """User: save a new delivery address."""

    label: str = Field(default="home", max_length=50, examples=["home", "work", "other"])
    street: str = Field(..., min_length=3, max_length=300)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    pincode: str = Field(..., min_length=3, max_length=20)
    country: str = Field(default="India", max_length=100)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    is_default: bool = False


# ── Update ────────────────────────────────────────────────────────────────────

class AddressUpdate(BaseSchema):
    """User: partial update of a saved address (all fields optional)."""

    label: str | None = Field(default=None, max_length=50)
    street: str | None = Field(default=None, min_length=3, max_length=300)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    state: str | None = Field(default=None, min_length=2, max_length=100)
    pincode: str | None = Field(default=None, min_length=3, max_length=20)
    country: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    is_default: bool | None = None


# ── Response ──────────────────────────────────────────────────────────────────

class AddressOut(TimestampSchema):
    """Saved address response."""

    label: str
    street: str
    city: str
    state: str
    pincode: str
    country: str
    latitude: float | None
    longitude: float | None
    is_default: bool
