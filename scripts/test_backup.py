"""Test script to verify database backup functionality.

Usage:
    python -m scripts.test_backup
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Make sure the project root is on the path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.backup_service import BackupService


async def main() -> None:
    print("=" * 60)
    print("Database Backup Test")
    print("=" * 60)
    print()
    
    service = BackupService()
    
    try:
        print("Creating database backup...")
        backup_info = await service.create_backup()
        
        print()
        print("✓ Backup created successfully!")
        print(f"  - Filename: {backup_info['filename']}")
        print(f"  - File path: {backup_info['file_path']}")
        print(f"  - File size: {backup_info['file_size']:,} bytes")
        print(f"  - Created at: {backup_info['created_at']}")
        print()
        
        # List all backups
        print("Available backups:")
        backups = service.list_backups()
        for backup in backups:
            print(f"  - {backup['filename']} ({backup['file_size']:,} bytes)")
        print()
        
        print("=" * 60)
        print("✓ Backup test completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ Backup test failed: {e}")
        print("=" * 60)
        print()
        print("Common issues:")
        print("  1. pg_dump not installed - Install PostgreSQL client tools")
        print("  2. Database connection error - Check DATABASE_URL in .env")
        print("  3. Authentication error - Verify database credentials")
        print()
        raise


if __name__ == "__main__":
    asyncio.run(main())
