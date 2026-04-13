from __future__ import annotations

import random
import string
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import OTP, User
from app.repositories.user_repository import OTPRepository, UserRepository
from app.repositories.app_settings_repository import AppSettingsRepository
from app.schemas.user import (
    AdminLogin,
    ForgotPasswordRequest,
    OTPVerify,
    PasswordChange,
    ResetPasswordRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserUpdate,
)
from app.services.email_service import send_otp_email, send_password_reset_email


def _generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


class AuthService:
    """Handles all authentication and identity business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.user_repo = UserRepository(db)
        self.otp_repo = OTPRepository(db)
        self.settings_repo = AppSettingsRepository(db)

    # ── Registration ────────────────────────────────────────────────────────────────

    async def register(self, payload: UserRegister) -> TokenResponse:
        """Create a new user account. Raises 409 on duplicate phone/email."""
        if await self.user_repo.get_by_phone(payload.phone):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone number already registered",
            )
        if payload.email and await self.user_repo.get_by_email(payload.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        user = User(
            full_name=payload.full_name,
            phone=payload.phone,
            email=payload.email,
            hashed_password=hash_password(payload.password or "Admin@123"),
        )
        user = await self.user_repo.create(user)
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    # ── Login / Token ──────────────────────────────────────────────────────────────

    async def login(self, payload: UserLogin) -> TokenResponse:
        """Authenticate by phone + password and return JWT pair."""
        user = await self.user_repo.get_by_phone(payload.phone)
        if not user or not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        if not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def admin_login(self, payload: AdminLogin) -> TokenResponse:
        """Admin login - authenticate by phone or email and verify admin status."""
        # Try phone first, then email
        user = await self.user_repo.get_by_phone(payload.identifier)
        if not user:
            user = await self.user_repo.get_by_email(payload.identifier)
        if not user or not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        if not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )
        if not user.is_admin and not user.is_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid User",
            )
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def refresh_token(self, payload: TokenRefreshRequest) -> TokenResponse:
        """Issue a new access token from a valid refresh token."""
        credentials_exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
        try:
            data = decode_token(payload.refresh_token)
            if data.get("type") != "refresh":
                raise credentials_exc
            user_id: str | None = data.get("sub")
            if not user_id:
                raise credentials_exc
        except JWTError:
            raise credentials_exc

        user = await self.user_repo.get_by_id(UUID(user_id))
        if not user or not user.is_active or user.is_deleted:
            raise credentials_exc

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    # ── OTP ───────────────────────────────────────────────────────────────────────

    async def _resolve_user_by_identifier(self, identifier: str) -> User:
        """Look up a user by phone number or email address."""
        # Try phone first, then email
        user = await self.user_repo.get_by_phone(identifier)
        if not user:
            user = await self.user_repo.get_by_email(identifier)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No account found for this phone/email",
            )
        return user

    async def send_otp(self, identifier: str) -> None:
        """Generate and persist an OTP for a phone number or email."""
        user = await self._resolve_user_by_identifier(identifier)

        # Invalidate any previously issued unused OTPs first
        await self.otp_repo.invalidate_all_for_user(user.id)

        code = _generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.OTP_EXPIRE_MINUTES
        )
        otp = OTP(user_id=user.id, code=code, expires_at=expires_at.isoformat())
        await self.otp_repo.create(otp)

        if user.email:
            app_settings = await self.settings_repo.get_settings()
            await send_otp_email(user.email, code, store_name=app_settings.store_name)

    async def verify_otp(self, payload: OTPVerify) -> TokenResponse:
        """Verify OTP code, mark it used, mark user as verified, return tokens."""
        user = await self._resolve_user_by_identifier(payload.identifier)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        otp = await self.otp_repo.get_latest_for_user(user.id)
        if not otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No pending OTP found"
            )

        expires_at = datetime.fromisoformat(otp.expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired"
            )

        if otp.code != payload.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect OTP code"
            )

        await self.otp_repo.update(otp, {"is_used": True})
        await self.user_repo.update(user, {"is_verified": True})

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    # ── Profile management ──────────────────────────────────────────────────────────

    async def update_profile(self, user_id: UUID, payload: UserUpdate) -> User:
        """Apply partial profile updates for the authenticated user."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        data = payload.model_dump(exclude_none=True)
        if not data:
            return user
        # Check email uniqueness if being changed
        if "email" in data and data["email"] != user.email:
            if await self.user_repo.get_by_email(data["email"]):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already in use",
                )
        return await self.user_repo.update(user, data)

    async def change_password(self, user_id: UUID, payload: PasswordChange) -> User:
        """Verify current password then replace with a new hashed password."""
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if not verify_password(payload.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )
        return await self.user_repo.update(
            user, {"hashed_password": hash_password(payload.new_password)}
        )

    # ── Forgot / Reset Password ─────────────────────────────────────────────────────

    async def forgot_password(self, payload: ForgotPasswordRequest) -> None:
        """Generate a password-reset token and email it to the admin user."""
        user = await self.user_repo.get_by_email(payload.email)
        if not user or not user.is_admin:
            # Return silently to avoid leaking whether the email exists
            return

        token = create_password_reset_token(str(user.id))
        base = payload.base_url.rstrip("/")
        reset_link = f"{base}/admin/reset-password?token={token}"

        app_settings = await self.settings_repo.get_settings()
        await send_password_reset_email(
            email=user.email,
            reset_link=reset_link,
            store_name=app_settings.store_name,
        )

    async def reset_password(self, payload: ResetPasswordRequest) -> None:
        """Validate the reset token and set the new password."""
        credentials_exc = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset link",
        )
        try:
            data = decode_token(payload.token)
            if data.get("type") != "password_reset":
                raise credentials_exc
            user_id: str | None = data.get("sub")
            if not user_id:
                raise credentials_exc
        except JWTError:
            raise credentials_exc

        user = await self.user_repo.get_by_id(UUID(user_id))
        if not user or not user.is_active or user.is_deleted:
            raise credentials_exc

        await self.user_repo.update(
            user, {"hashed_password": hash_password(payload.new_password)}
        )

    # ── Account deletion ────────────────────────────────────────────────────────────

    async def delete_account(self, user_id: UUID) -> None:
        """Soft-delete the authenticated user's account."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Account already deleted"
            )
        await self.user_repo.soft_delete(user)
