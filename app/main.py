from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.api.v1 import api_router
from app.core.config import settings
from app.core.middleware import ExceptionHandlerMiddleware

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(parents=True, exist_ok=True)

handlers = [logging.StreamHandler()]
try:
    handlers.append(logging.FileHandler(log_dir / "app.log"))
except (PermissionError, OSError):
    # Fallback to console-only if file creation fails
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=handlers,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: nothing special needed; Alembic handles migrations
    yield
    # Shutdown


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        lifespan=lifespan,
    )

    # ── CORS (outermost layer) ────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception Handler Middleware ──────────────────────────────────────────
    app.add_middleware(ExceptionHandlerMiddleware)

    # ── Static Files ──────────────────────────────────────────────────────────
    # Serve uploaded files (images, etc.)
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

    # ── Routes ────────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "ok", "version": settings.VERSION}

    return app


app = create_application()
