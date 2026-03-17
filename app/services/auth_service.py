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
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import OTP, User
from app.repositories.user_repository import OTPRepository, UserRepository
from app.schemas.user import (
    AdminLogin,
    OTPVerify,
    PasswordChange,
    TokenRefreshRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserUpdate,
)


def _generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


async def _send_otp_email(email: str, code: str) -> None:
    """Send OTP to the user's email address via SMTP (fastapi-mail).

    Silently skips if MAIL_USERNAME / MAIL_PASSWORD are not configured.
    """
    import logging
    logger = logging.getLogger(__name__)

    if not all([settings.MAIL_USERNAME, settings.MAIL_PASSWORD, settings.MAIL_FROM]):
        logger.warning("Email not configured — skipping email OTP delivery.")
        return

    try:
        from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

        conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=True,
        )
        message = MessageSchema(
            subject=f"Your {settings.PROJECT_NAME} OTP",
            recipients=[email],
            body=(
                f"<p>Your one-time password is:</p>"
                f"<h2 style='letter-spacing:4px'>{code}</h2>"
                f"<p>Valid for <strong>{settings.OTP_EXPIRE_MINUTES} minutes</strong>. "
                f"Do not share it with anyone.</p>"
            ),
            subtype=MessageType.html,
        )
        await FastMail(conf).send_message(message)
        logger.info("OTP email sent to %s", email)
    except Exception:
        logger.exception("Failed to send OTP email to %s", email)


class AuthService:
    """Handles all authentication and identity business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.user_repo = UserRepository(db)
        self.otp_repo = OTPRepository(db)

    # ── Registration ────────────────────────────────────────────────────────────────

    async def register(self, payload: UserRegister) -> User:
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
            hashed_password=hash_password(payload.password),
        )
        return await self.user_repo.create(user)

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
        if not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required",
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
        if not user or not user.is_active:
            raise credentials_exc

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    # ── OTP ───────────────────────────────────────────────────────────────────────

    async def send_otp(self, phone: str) -> str:
        """Generate and persist an OTP for a phone number.

        Returns the raw code so the caller can forward it to an SMS gateway.
        Remove the return value in production and send silently.
        """
        user = await self.user_repo.get_by_phone(phone)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No account found for this phone number",
            )
        # Invalidate any previously issued unused OTPs first
        await self.otp_repo.invalidate_all_for_user(user.id)

        code = _generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.OTP_EXPIRE_MINUTES
        )
        otp = OTP(user_id=user.id, code=code, expires_at=expires_at.isoformat())
        await self.otp_repo.create(otp)

        if user.email:
            await _send_otp_email(user.email, code)

        return code  # TODO: remove before going to production

    async def verify_otp(self, payload: OTPVerify) -> TokenResponse:
        """Verify OTP code, mark it used, mark user as verified, return tokens."""
        user = await self.user_repo.get_by_phone(payload.phone)
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


    async def register(self, payload: UserRegister) -> User:
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
            hashed_password=hash_password(payload.password),
        )
        return await self.user_repo.create(user)

    async def login(self, payload: UserLogin) -> TokenResponse:
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

    async def send_otp(self, phone: str) -> str:
        """Creates an OTP record and returns the code (send via SMS in production)."""
        user = await self.user_repo.get_by_phone(phone)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No account found for this phone number",
            )
        code = _generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        otp = OTP(user_id=user.id, code=code, expires_at=expires_at.isoformat())
        await self.otp_repo.create(otp)
        # TODO: Integrate SMS gateway here
        return code  # Return for development; remove in production

    async def verify_otp(self, payload: OTPVerify) -> TokenResponse:
        user = await self.user_repo.get_by_phone(payload.phone)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        otp = await self.otp_repo.get_latest_for_user(user.id)
        if not otp:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pending OTP")

        expires_at = datetime.fromisoformat(otp.expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired")

        if otp.code != payload.code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

        otp.is_used = True
        user.is_verified = True

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )
