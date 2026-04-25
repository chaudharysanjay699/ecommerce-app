from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.api.v1 import api_router
from app.core.config import settings
from app.core.middleware import ExceptionHandlerMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(),
    ],
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

    # ── Exception Handling (Dual Protection) ──────────────────────────────────
    # This ensures the application NEVER crashes due to API exceptions
    # Layer 1: Global exception handler (catches exceptions at FastAPI level)
    # Layer 2: Middleware (catches exceptions during request processing)
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Catch any unhandled exceptions to prevent app crashes."""
        logger = logging.getLogger(__name__)
        logger.error(
            f"Global exception handler caught: {type(exc).__name__}: {str(exc)}",
            exc_info=True,
            extra={
                "method": request.method,
                "url": str(request.url),
                "client": request.client.host if request.client else None,
            },
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An internal server error occurred. The application is still running.",
                "error_type": type(exc).__name__,
            },
        )

    # Exception Handler Middleware (second layer of protection)
    app.add_middleware(ExceptionHandlerMiddleware)

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
