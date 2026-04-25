"""
Global middleware for exception handling and logging.
"""
import logging
import traceback
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to catch all unhandled exceptions, log them, and return a consistent error response.
    This ensures the application never crashes due to an unhandled exception.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Log the exception with full traceback
            try:
                logger.error(
                    f"Unhandled exception in {request.method} {request.url.path}: {str(exc)}",
                    exc_info=True,
                    extra={
                        "method": request.method,
                        "url": str(request.url),
                        "client": request.client.host if request.client else None,
                        "user_agent": request.headers.get("user-agent"),
                        "traceback": traceback.format_exc(),
                    },
                )
            except Exception as log_error:
                # Even if logging fails, print to stderr as last resort
                print(f"CRITICAL: Logging failed: {log_error}, Original error: {exc}", flush=True)

            # Always return a response - never let the exception propagate
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "An internal server error occurred. Please try again later.",
                    "error_type": type(exc).__name__,
                },
            )
