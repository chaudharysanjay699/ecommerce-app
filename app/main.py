from __future__ import annotations

import logging
from pathlib import Path
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from sqlalchemy import text
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.api.v1 import api_router
from app.core.config import settings
from app.core.logging_setup import configure_logging
from app.core.middleware import ExceptionHandlerMiddleware

# Initialise logging (console + file + CloudWatch) before anything else
configure_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with proper startup/shutdown."""
    logger.info("Starting application: %s v%s", settings.PROJECT_NAME, settings.VERSION)
    
    # Startup
    try:
        # Test database connection
        from app.core.database import engine
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection verified")
    except Exception as e:
        logger.error("Database connection failed during startup: %s", e)
        # Don't crash - let middleware handle DB errors at runtime
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    try:
        # Wait for background tasks to complete
        from app.utils.background_tasks import wait_for_background_tasks
        await wait_for_background_tasks(timeout=10.0)
    except Exception as e:
        logger.warning("Error waiting for background tasks: %s", e)
    
    try:
        # Close database connections
        from app.core.database import engine
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error("Error closing database: %s", e)
    
    logger.info("Application shutdown complete")


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        lifespan=lifespan,
    )

    # ── Global Exception Handlers ────────────────────────────────────────────

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors gracefully."""
        logger.warning(
            "Validation error on %s %s: %s",
            request.method,
            request.url.path,
            exc.errors(),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Catch-all for exceptions that bypass the middleware (e.g. during response streaming)."""
        request_id = getattr(getattr(request, "state", None), "request_id", "unknown")
        logger.error(
            "[%s] Global handler caught %s on %s %s",
            request_id,
            type(exc).__name__,
            request.method,
            request.url.path,
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unexpected error occurred. The issue has been logged.",
                "request_id": request_id,
            },
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
        """Enhanced health check with database connectivity test."""
        health_status = {
            "status": "ok",
            "version": settings.VERSION,
            "app_name": settings.PROJECT_NAME,
        }
        
        # Test database connection
        try:
            from app.core.database import engine
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            health_status["database"] = "connected"
        except Exception as e:
            logger.error("Health check: database connection failed - %s", e)
            health_status["database"] = "disconnected"
            health_status["status"] = "degraded"
        
        return health_status

    return app


app = create_application()
