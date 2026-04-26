"""Robust middleware for comprehensive error handling and logging."""
from __future__ import annotations

import logging
import traceback
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import OperationalError, DBAPIError

logger = logging.getLogger(__name__)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Catch and log all unhandled exceptions to prevent app crashes."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except OperationalError as exc:
            # Database connection issues
            logger.error(
                "Database connection error on %s %s: %s",
                request.method,
                request.url.path,
                str(exc),
                exc_info=True,
            )
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "Database temporarily unavailable. Please try again in a moment.",
                    "error_type": "DatabaseError",
                },
            )
        except DBAPIError as exc:
            # Database API issues
            logger.error(
                "Database API error on %s %s: %s",
                request.method,
                request.url.path,
                str(exc),
                exc_info=True,
            )
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "Database error occurred. Please try again.",
                    "error_type": "DatabaseError",
                },
            )
        except Exception as exc:
            # Catch ALL other exceptions to prevent crash
            logger.error(
                "Unhandled exception on %s %s: %s\n%s",
                request.method,
                request.url.path,
                str(exc),
                traceback.format_exc(),
                exc_info=True,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "An unexpected error occurred. The issue has been logged.",
                    "error_type": type(exc).__name__,
                },
            )