from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.user import (
    AdminLogin,
    ForgotPasswordRequest,
    OTPRequest,
    OTPVerify,
    PasswordChange,
    ResetPasswordRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserLogin,
    UserOut,
    UserRegister,
    UserUpdate,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Registration & Login ──────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new user account and return JWT tokens."""
    return await AuthService(db).register(payload)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Authenticate with phone + password and receive a JWT pair."""
    return await AuthService(db).login(payload)


@router.post("/admin/login", response_model=TokenResponse)
async def admin_login(
    payload: AdminLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Admin login with phone or email + password. Returns JWT pair only if user is admin."""
    return await AuthService(db).admin_login(payload)


@router.post("/admin/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Send a password reset link to the admin's email address."""
    await AuthService(db).forgot_password(payload)
    return {"message": "If an admin account exists with this email, a reset link has been sent."}


@router.post("/admin/reset-password")
async def reset_password(
    payload: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Reset admin password using the token from the reset email."""
    await AuthService(db).reset_password(payload)
    return {"message": "Password has been reset successfully."}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: TokenRefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Exchange a valid refresh token for a new access token."""
    return await AuthService(db).refresh_token(payload)


# ── OTP ───────────────────────────────────────────────────────────────────────

@router.post("/otp/send")
async def send_otp(
    payload: OTPRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Send an OTP to the given phone number or email."""
    await AuthService(db).send_otp(payload.identifier)
    return {"message": "OTP sent successfully"}


@router.post("/otp/verify", response_model=TokenResponse)
async def verify_otp(
    payload: OTPVerify,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Verify the OTP code and receive a JWT pair."""
    return await AuthService(db).verify_otp(payload)


# ── Profile ───────────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserOut)
async def me(
    current_user: Annotated[object, Depends(get_current_user)],
):
    """Return the authenticated user's profile."""
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_profile(
    payload: UserUpdate,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Partially update the authenticated user's profile."""
    return await AuthService(db).update_profile(current_user.id, payload)


@router.post("/me/avatar", response_model=UserOut)
async def upload_avatar(
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
):
    """Upload a profile avatar image for the authenticated user."""
    from app.utils.file_upload import save_upload_file, get_file_url

    result = await save_upload_file(file, subdir="avatars")
    avatar_url = get_file_url(result["file_path"])
    return await AuthService(db).update_profile(
        current_user.id, UserUpdate(avatar_url=avatar_url)
    )


@router.post("/me/change-password", response_model=UserOut)
async def change_password(
    payload: PasswordChange,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Change the authenticated user's password."""
    return await AuthService(db).change_password(current_user.id, payload)
