"""Database backup service.

This service handles creating PostgreSQL database backups using pg_dump.
Optimized for PostgreSQL 16.3+ with modern backup best practices.

Requirements:
- PostgreSQL 16.3+ client tools (pg_dump) must be installed and in PATH
- pg_dump version should match or be newer than the database server version
"""
from __future__ import annotations

import asyncio
import logging
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)


class BackupService:
    """Service for creating and managing database backups.
    
    Features:
    - PostgreSQL 16.3+ optimized backup with modern pg_dump options
    - Verbose logging for better troubleshooting
    - Owner and privilege independence for portable backups
    - Lock wait timeout to prevent indefinite blocking
    - Quoted identifiers for better compatibility
    - Safe restore with --clean and --if-exists (DROP IF EXISTS before CREATE)
    """

    def __init__(self, backup_dir: str = "backups"):
        """Initialize the backup service.
        
        Args:
            backup_dir: Directory to store backup files (relative to project root)
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _parse_database_url(self) -> dict[str, str]:
        """Parse DATABASE_URL into connection parameters.
        
        Returns:
            Dictionary with host, port, database, user, password
            
        Raises:
            HTTPException: If URL parsing fails
        """
        try:
            # Remove asyncpg or psycopg2 specific prefixes
            url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
            url = url.replace("postgresql+psycopg2://", "postgresql://")
            
            parsed = urlparse(url)
            
            if not all([parsed.hostname, parsed.username, parsed.path]):
                raise ValueError("Missing required connection parameters")
            
            return {
                "host": parsed.hostname,
                "port": str(parsed.port or 5432),
                "database": parsed.path.lstrip("/"),
                "user": parsed.username,
                "password": parsed.password or "",
            }
        except Exception as e:
            logger.error(f"Failed to parse DATABASE_URL: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid database configuration"
            )

    def _generate_backup_filename(self) -> str:
        """Generate a timestamped backup filename.
        
        Returns:
            Filename in format: backup_YYYY-MM-DD_HH-MM-SS.sql
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        return f"backup_{timestamp}.sql"

    async def create_backup(self, backup_name: Optional[str] = None) -> dict[str, str]:
        """Create a database backup using pg_dump.
        
        Args:
            backup_name: Optional custom backup filename (auto-generated if not provided)
            
        Returns:
            Dictionary with backup details:
                - filename: Name of the backup file
                - file_path: Full path to the backup file
                - file_size: Size of the backup file in bytes
                - created_at: ISO timestamp of when backup was created
                
        Raises:
            HTTPException: If backup creation fails
        """
        try:
            # Parse database connection details
            db_config = self._parse_database_url()
            
            # Generate backup filename
            if not backup_name:
                backup_name = self._generate_backup_filename()
            elif not backup_name.endswith(".sql"):
                backup_name = f"{backup_name}.sql"
            
            backup_path = self.backup_dir / backup_name
            
            # Build pg_dump command optimized for PostgreSQL 16.3
            # Using plain format (-Fp) for SQL text that can be easily inspected
            # For compressed backups, use "-F c" (custom format) instead
            pg_dump_cmd = [
                "pg_dump",
                "-h", db_config["host"],
                "-p", db_config["port"],
                "-U", db_config["user"],
                "-d", db_config["database"],
                "-F", "p",  # Plain SQL format (use "c" for custom compressed format)
                "-f", str(backup_path),
                "--no-password",  # Use PGPASSWORD environment variable
                "--verbose",  # Show detailed progress (logged to stderr)
                "--no-owner",  # Don't output commands to set ownership
                "--no-privileges",  # Don't output commands to set privileges (ACLs)
                "--clean",  # Add DROP commands before CREATE commands
                "--if-exists",  # Use IF EXISTS with DROP commands (safer restores)
                "--quote-all-identifiers",  # Quote all identifiers for better compatibility
                "--lock-wait-timeout=30000",  # Wait max 30 seconds for locks (milliseconds)
            ]
            
            # Set environment variable for password
            env = {"PGPASSWORD": db_config["password"]}
            
            logger.info(f"Creating database backup using pg_dump 16.3+: {backup_name}")
            
            # Run pg_dump command
            # Using asyncio.to_thread for Windows compatibility (asyncio.create_subprocess_exec doesn't work reliably on Windows)
            def run_pg_dump():
                result = subprocess.run(
                    pg_dump_cmd,
                    env={**os.environ.copy(), **env},
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout to prevent hanging
                )
                return result
            
            process = await asyncio.to_thread(run_pg_dump)
            
            # Log verbose output from pg_dump (goes to stderr even on success)
            if process.stderr:
                logger.debug(f"pg_dump output: {process.stderr}")
            
            if process.returncode != 0:
                error_msg = process.stderr if process.stderr else "Unknown error"
                logger.error(f"pg_dump failed with return code {process.returncode}: {error_msg}")
                
                # Clean up partial backup file if it exists
                if backup_path.exists():
                    backup_path.unlink()
                
                # Check for common errors
                if "pg_dump: command not found" in error_msg or "not recognized" in error_msg:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="pg_dump is not installed or not in PATH. Please install PostgreSQL 16.3+ client tools."
                    )
                elif "aborting because of server version mismatch" in error_msg or "server version mismatch" in error_msg:
                    # Extract versions from error message
                    server_version = "unknown"
                    client_version = "unknown"
                    if "server version:" in error_msg:
                        match = re.search(r"server version:\s*([\d.]+)", error_msg)
                        if match:
                            server_version = match.group(1)
                    if "pg_dump version:" in error_msg or "pg_dump.*version" in error_msg:
                        match = re.search(r"pg_dump.*version[:\s]*([\d.]+)", error_msg, re.IGNORECASE)
                        if match:
                            client_version = match.group(1)
                    
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"pg_dump version mismatch: Client version {client_version} vs Server version {server_version}. "
                               f"For PostgreSQL 16.x servers, use pg_dump 16.3 or higher. "
                               f"pg_dump must be the same or newer version than the database server."
                    )
                elif "password authentication failed" in error_msg:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Database authentication failed. Check DATABASE_URL credentials."
                    )
                elif "could not connect to server" in error_msg or "Connection refused" in error_msg:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Could not connect to database server. Check host, port, and ensure database is running."
                    )
                elif "timeout" in error_msg.lower() or "lock" in error_msg.lower():
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Backup failed due to timeout or lock wait. The database may be under heavy load. Please try again."
                    )
                elif "permission denied" in error_msg.lower():
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Permission denied. Ensure the database user has sufficient privileges to perform backups."
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Backup failed: {error_msg}"
                    )
            
            # Verify backup file was created
            if not backup_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Backup file was not created"
                )
            
            file_size = backup_path.stat().st_size
            created_at = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"Backup created successfully: {backup_name} ({file_size} bytes)")
            
            return {
                "filename": backup_name,
                "file_path": str(backup_path),
                "file_size": file_size,
                "created_at": created_at,
            }
            
        except HTTPException:
            raise
        except subprocess.TimeoutExpired:
            logger.error("pg_dump command timed out after 5 minutes")
            # Clean up partial backup file if it exists
            if backup_path.exists():
                backup_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Backup operation timed out after 5 minutes. The database may be too large or under heavy load."
            )
        except Exception as e:
            logger.error(f"Unexpected error creating backup: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create backup: {str(e)}"
            )

    def list_backups(self) -> list[dict[str, str]]:
        """List all available backup files.
        
        Returns:
            List of dictionaries with backup details:
                - filename: Name of the backup file
                - file_path: Full path to the backup file
                - file_size: Size in bytes
                - created_at: File creation timestamp
        """
        try:
            backups = []
            
            for backup_file in sorted(self.backup_dir.glob("*.sql"), reverse=True):
                stat = backup_file.stat()
                backups.append({
                    "filename": backup_file.name,
                    "file_path": str(backup_file),
                    "file_size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat(),
                })
            
            return backups
            
        except Exception as e:
            logger.error(f"Error listing backups: {e}", exc_info=True)
            return []

    def delete_old_backups(self, keep_count: int = 10) -> int:
        """Delete old backup files, keeping only the most recent ones.
        
        Args:
            keep_count: Number of recent backups to keep
            
        Returns:
            Number of backups deleted
        """
        try:
            backups = sorted(self.backup_dir.glob("*.sql"), key=lambda p: p.stat().st_ctime, reverse=True)
            
            deleted_count = 0
            for backup_file in backups[keep_count:]:
                backup_file.unlink()
                deleted_count += 1
                logger.info(f"Deleted old backup: {backup_file.name}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting old backups: {e}", exc_info=True)
            return 0

    def get_backup_path(self, filename: str) -> Optional[Path]:
        """Get the full path to a backup file.
        
        Args:
            filename: Name of the backup file
            
        Returns:
            Path object if file exists, None otherwise
        """
        backup_path = self.backup_dir / filename
        
        # Validate filename to prevent directory traversal
        if not backup_path.resolve().is_relative_to(self.backup_dir.resolve()):
            logger.warning(f"Invalid backup filename (path traversal attempt): {filename}")
            return None
        
        if not backup_path.exists():
            return None
        
        return backup_path
