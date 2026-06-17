"""Middleware for comprehensive exception handling and request tracing.

Every request gets a unique X-Request-ID header so CloudWatch log lines
can be correlated end-to-end.

Exception priority (top = most specific):
  1. InsufficientPrivilege / DBAPIError — DB permission / driver error → 503
  2. OperationalError                   — DB connection lost            → 503
  3. Exception                          — everything else               → 500

All exceptions at WARNING level and above are automatically shipped to
CloudWatch by the root logger (configured in logging_setup.py).
Internal details are NEVER sent to the client.
"""
from __future__ import annotations

import logging
import traceback
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import OperationalError, DBAPIError

logger = logging.getLogger(__name__)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Catch every unhandled exception so the application never crashes."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response

        except DBAPIError as exc:
            orig = str(getattr(exc, "orig", exc))
            is_permission = (
                "InsufficientPrivilegeError" in orig
                or "permission denied" in orig.lower()
            )
            logger.error(
                "[%s] DB %s on %s %s — %s",
                request_id,
                "permission denied" if is_permission else "error",
                request.method,
                request.url.path,
                orig,
                exc_info=True,
            )
            return JSONResponse(
                status_code=503,
                headers={"X-Request-ID": request_id},
                content={"detail": "Service temporarily unavailable. Please try again later."},
            )

        except OperationalError as exc:
            logger.error(
                "[%s] DB connection error on %s %s — %s",
                request_id,
                request.method,
                request.url.path,
                exc,
                exc_info=True,
            )
            return JSONResponse(
                status_code=503,
                headers={"X-Request-ID": request_id},
                content={"detail": "Database temporarily unavailable. Please try again in a moment."},
            )

        except Exception as exc:
            logger.error(
                "[%s] Unhandled %s on %s %s\n%s",
                request_id,
                type(exc).__name__,
                request.method,
                request.url.path,
                traceback.format_exc(),
            )
            return JSONResponse(
                status_code=500,
                headers={"X-Request-ID": request_id},
                content={
                    "detail": "An unexpected error occurred. The issue has been logged.",
                    "request_id": request_id,
                },
            )