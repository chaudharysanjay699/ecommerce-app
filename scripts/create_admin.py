"""Create admin and super admin users.

Usage:
    python -m scripts.create_admin

This script creates two users:
1. Admin user (is_admin=True)
2. Super admin user (is_super_admin=True)

"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Make sure the project root is on the path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User


async def create_admin_user(
    db: AsyncSession,
    phone: str,
    email: str,
    full_name: str,
    password: str,
    is_super_admin: bool = False
) -> User:
    """Create an admin user."""
    
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.phone == phone, User.is_deleted == False)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        print(f"[WARNING] User with phone {phone} already exists (ID: {existing_user.id})")
        return existing_user
    
    # Create new user
    user = User(
        full_name=full_name,
        email=email,
        phone=phone,
        hashed_password=hash_password(password),
        is_active=True,
        is_verified=True,
        is_admin=True,
        is_super_admin=is_super_admin,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    role = "Super Admin" if is_super_admin else "Admin"
    print(f"[SUCCESS] Created {role} user:")
    print(f"  - ID: {user.id}")
    print(f"  - Name: {user.full_name}")
    print(f"  - Email: {user.email}")
    print(f"  - Phone: {user.phone}")
    print(f"  - Password: {password}")
    print()
    
    return user


async def main() -> None:
    print("=" * 60)
    print("Creating Admin Users")
    print("=" * 60)
    print()
    
    async with AsyncSessionLocal() as db:
        # Create Admin User
        await create_admin_user(
            db=db,
            phone="9999999991",
            email="admin@vidharthi.com",
            full_name="Admin User",
            password="Admin@123",
            is_super_admin=False,
        )
        
        # Create Super Admin User
        await create_admin_user(
            db=db,
            phone="9999999990",
            email="superadmin@vidharthi.com",
            full_name="Super Admin",
            password="SuperAdmin@123",
            is_super_admin=True,
        )
    
    print("=" * 60)
    print("[SUCCESS] Admin users created successfully!")
    print("=" * 60)
    print()
    print("IMPORTANT: Change these passwords after first login!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
