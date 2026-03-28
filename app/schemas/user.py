from __future__ import annotations

from uuid import UUID

from pydantic import EmailStr, Field, field_validator, model_validator

from app.schemas.base import BaseSchema, TimestampSchema


# ─────────────────────────────────────────────────────────────────────────────
# Auth / Registration
# ─────────────────────────────────────────────────────────────────────────────

class UserRegister(BaseSchema):
    """Payload to create a new user account."""

    full_name: str = Field(..., min_length=2, max_length=120, examples=["John Doe"])
    phone: str = Field(..., pattern=r"^\+?[0-9]{7,15}$", examples=["+919876543210"])
    email: EmailStr = Field(..., examples=["john@example.com"])
    password: str | None = Field(default=None, min_length=8, examples=["SecurePass1!"])


class UserLogin(BaseSchema):
    """Credentials for phone-based login."""

    phone: str = Field(..., examples=["+919876543210"])
    password: str = Field(..., examples=["SecurePass1!"])


class AdminLogin(BaseSchema):
    """Admin login – accepts either phone number or email as identifier."""

    identifier: str = Field(..., examples=["admin@example.com", "+919876543210"])
    password: str = Field(..., examples=["SecurePass1!"])


class OTPRequest(BaseSchema):
    """Request an OTP — accepts phone number or email address."""

    identifier: str = Field(
        ...,
        min_length=3,
        examples=["+919876543210", "john@example.com"],
        description="Phone number or email address",
    )


class OTPVerify(BaseSchema):
    """Submit OTP code to verify identity."""

    identifier: str = Field(
        ...,
        min_length=3,
        examples=["+919876543210", "john@example.com"],
        description="Phone number or email address used when requesting the OTP",
    )
    code: str = Field(..., min_length=4, max_length=6, examples=["123456"])


class PasswordChange(BaseSchema):
    """Authenticated user changes their own password."""

    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @model_validator(mode="after")
    def passwords_match(self) -> "PasswordChange":
        if self.new_password != self.confirm_password:
            raise ValueError("new_password and confirm_password do not match")
        return self


# ─────────────────────────────────────────────────────────────────────────────
# Update
# ─────────────────────────────────────────────────────────────────────────────

class UserUpdate(BaseSchema):
    """Fields a user can update on their own profile (all optional)."""

    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    email: EmailStr | None = None
    avatar_url: str | None = None


class AdminUserUpdate(BaseSchema):
    """Admin-only user mutations."""

    is_active: bool | None = None
    is_verified: bool | None = None
    is_admin: bool | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Response
# ─────────────────────────────────────────────────────────────────────────────

class TokenResponse(BaseSchema):
    """JWT tokens returned after successful authentication."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseSchema):
    refresh_token: str


class UserOut(TimestampSchema):
    """Public user representation returned by most endpoints."""

    full_name: str
    phone: str
    email: str | None
    avatar_url: str | None
    is_active: bool
    is_verified: bool
    is_admin: bool


class UserProfile(UserOut):
    """Extended profile — includes saved addresses (used on /auth/me)."""

    addresses: list["AddressOut"] = []


# Resolved after AddressOut is defined in address.py
from app.schemas.address import AddressOut  # noqa: E402  (circular-safe: address has no user import)

UserProfile.model_rebuild()

