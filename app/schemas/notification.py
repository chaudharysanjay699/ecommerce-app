from __future__ import annotations

from uuid import UUID

from pydantic import Field, field_validator

from app.core.config import settings
from app.schemas.base import BaseSchema, TimestampSchema


# ── Helper function ───────────────────────────────────────────────────────────

def make_full_url(image_url: str | None) -> str | None:
    """Convert relative path to full URL if needed."""
    if not image_url:
        return None
    # If already a full URL, return as-is
    if image_url.startswith('http://') or image_url.startswith('https://'):
        return image_url
    # Convert relative path to full URL
    normalized = image_url.replace('\\', '/')
    if normalized.startswith('/'):
        normalized = normalized[1:]
    return f"{settings.SERVER_URL}/{normalized}"


# ─────────────────────────────────────────────────────────────────────────────
# Notification
# ─────────────────────────────────────────────────────────────────────────────

class NotificationOut(TimestampSchema):
    """Notification item returned to the user."""

    user_id: UUID
    title: str
    body: str
    is_read: bool


# ─────────────────────────────────────────────────────────────────────────────
# Device Token
# ─────────────────────────────────────────────────────────────────────────────

class DeviceTokenRegister(BaseSchema):
    """Mobile app registers or refreshes its FCM token."""

    device_token: str = Field(..., min_length=10, description="FCM registration token from the device")
    device_type: str = Field(
        default="android",
        pattern="^(android|ios|web)$",
        description="Device platform: android | ios | web",
    )


class DeviceTokenOut(TimestampSchema):
    """Registered device token response."""

    user_id: UUID
    device_token: str
    device_type: str


# ─────────────────────────────────────────────────────────────────────────────
# Broadcast
# ─────────────────────────────────────────────────────────────────────────────

class BroadcastPayload(BaseSchema):
    """Admin: send a push notification to all users."""

    title: str = Field(..., min_length=2, max_length=200)
    message: str = Field(..., min_length=2, max_length=500)


# ─────────────────────────────────────────────────────────────────────────────
# Banner
# ─────────────────────────────────────────────────────────────────────────────

class BannerCreate(BaseSchema):
    """Admin: upload a new home-screen banner."""

    title: str = Field(..., min_length=2, max_length=200)
    image_url: str = Field(..., description="Public URL of the banner image")
    link_url: str | None = Field(default=None, description="Optional deep-link or web URL")
    sort_order: int = Field(default=0, ge=0, description="Lower value = displayed first")


class BannerUpdate(BaseSchema):
    """Admin: partial update of an existing banner."""

    title: str | None = Field(default=None, min_length=2, max_length=200)
    image_url: str | None = None
    link_url: str | None = None
    sort_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class BannerOut(TimestampSchema):
    """Banner response."""

    title: str
    image_url: str
    link_url: str | None
    is_active: bool
    sort_order: int
    
    @field_validator('image_url', mode='before')
    @classmethod
    def convert_image_url(cls, v):
        """Convert relative path to full URL."""
        return make_full_url(v) or ""

