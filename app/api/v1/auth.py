from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.user import (
    AdminLogin,
    OTPRequest,
    OTPVerify,
    PasswordChange,
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

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new user account."""
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
    """Send an OTP to the given phone number."""
    code = await AuthService(db).send_otp(payload.phone)
    # TODO: remove debug_code before going to production
    return {"message": "OTP sent", "debug_code": code}


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


@router.post("/me/change-password", response_model=UserOut)
async def change_password(
    payload: PasswordChange,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Change the authenticated user's password."""
    return await AuthService(db).change_password(current_user.id, payload)
