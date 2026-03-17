"""File upload utilities for handling image uploads."""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import BinaryIO

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


# ── Configuration ─────────────────────────────────────────────────────────────


UPLOAD_DIR = Path("uploads")
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


# ── Helper Functions ──────────────────────────────────────────────────────────


def get_file_url(file_path: str) -> str:
    """
    Construct full URL for a file path using the configured SERVER_URL.
    
    Args:
        file_path: Relative file path (e.g., 'uploads/products/abc123.jpg')
        
    Returns:
        Full URL (e.g., 'http://localhost:8000/uploads/products/abc123.jpg')
    """
    # Normalize path separators to forward slashes for URLs
    normalized_path = file_path.replace("\\", "/")
    # Ensure path doesn't start with /
    if normalized_path.startswith("/"):
        normalized_path = normalized_path[1:]
    return f"{settings.SERVER_URL}/{normalized_path}"



def ensure_upload_directory(subdir: str = "") -> Path:
    """
    Ensure the upload directory (and optional subdirectory) exists.
    
    Args:
        subdir: Optional subdirectory name (e.g., 'categories', 'products')
        
    Returns:
        Path object for the target directory
    """
    target_dir = UPLOAD_DIR / subdir if subdir else UPLOAD_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def validate_image_file(file: UploadFile) -> None:
    """
    Validate that the uploaded file is an allowed image type.
    
    Args:
        file: The uploaded file from FastAPI
        
    Raises:
        HTTPException: If file validation fails
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    # Check file extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Supported: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    # Check content type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )


async def save_upload_file(
    file: UploadFile,
    subdir: str = "",
    max_size: int = MAX_FILE_SIZE
) -> dict:
    """
    Save an uploaded file to disk with a unique filename.
    
    Args:
        file: The uploaded file from FastAPI
        subdir: Subdirectory within uploads/ to save to
        max_size: Maximum file size in bytes
        
    Returns:
        Dictionary with file metadata:
        {
            "file_path": "uploads/categories/abc123.jpg",
            "file_size": 123456,
            "mime_type": "image/jpeg",
            "original_filename": "my-image.jpg"
        }
        
    Raises:
        HTTPException: If validation or save fails
    """
    # Validate file
    validate_image_file(file)
    
    # Ensure directory exists
    target_dir = ensure_upload_directory(subdir)
    
    # Generate unique filename
    ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = target_dir / unique_filename
    
    # Save file with size check
    try:
        total_size = 0
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(8192):  # Read in 8KB chunks
                total_size += len(chunk)
                if total_size > max_size:
                    # Clean up partial file
                    buffer.close()
                    file_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File too large. Max size: {max_size // (1024 * 1024)}MB"
                    )
                buffer.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Return file metadata
    return {
        "file_path": str(file_path.as_posix()),
        "file_size": total_size,
        "mime_type": file.content_type or "application/octet-stream",
        "original_filename": file.filename,
    }


def delete_file(file_path: str) -> None:
    """
    Delete a file from disk (safe - no exception if file doesn't exist).
    
    Args:
        file_path: Relative or absolute path to the file
    """
    try:
        path = Path(file_path)
        path.unlink(missing_ok=True)
    except Exception:
        pass  # Silently ignore deletion errors


def get_file_url(file_path: str | None, base_url: str = "") -> str | None:
    """
    Convert a file path to a full URL.
    
    Args:
        file_path: Relative file path (e.g., 'uploads/categories/abc.jpg')
        base_url: Base URL of the server (e.g., 'http://localhost:8000')
        
    Returns:
        Full URL to the file, or None if file_path is None
    """
    if not file_path:
        return None
    
    # Ensure forward slashes for URLs
    normalized_path = file_path.replace("\\", "/")
    
    if base_url:
        return f"{base_url.rstrip('/')}/{normalized_path.lstrip('/')}"
    return f"/{normalized_path.lstrip('/')}"
