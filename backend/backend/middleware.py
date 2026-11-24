import logging
import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.config import get_settings

logger = logging.getLogger(__name__)

_SWAGGER_PATHS = {"/docs", "/docs/oauth2-redirect", "/redoc", "/openapi.json"}


class RequestLoggingMiddleware(BaseHTTPMiddleware):  # pylint: disable=too-few-public-methods
    """Log failed requests with enough context to diagnose server-side errors."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start) * 1000)
        status_code = response.status_code
        log_data: dict = {
            "method": request.method,
            "path": request.url.path,
            "status_code": status_code,
            "duration_ms": duration_ms,
        }

        if status_code >= 400:
            level = logging.ERROR if status_code >= 500 else logging.WARNING
            logger.log(level, "HTTP request failed", extra=log_data)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):  # pylint: disable=too-few-public-methods
    """Middleware to add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        is_docs = request.url.path in _SWAGGER_PATHS
        cdn = " https://cdn.jsdelivr.net" if is_docs else ""
        favicon = " https://fastapi.tiangolo.com" if is_docs else ""
        keycloak = f" {get_settings().keycloak_host}" if is_docs else ""

        # Content Security Policy - prevents XSS attacks
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            f"script-src 'self' 'unsafe-inline'{cdn}; "
            f"style-src 'self' 'unsafe-inline'{cdn}; "
            f"img-src 'self' data:{favicon}; "
            f"connect-src 'self'{keycloak}"
        )

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response
