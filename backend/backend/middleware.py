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
    """Logs every request/response pair with method, path, status and duration.

    On 4xx/5xx responses the response body is also captured so the error
    detail is visible in the logs without needing a separate debugging session.
    """

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

        if request.url.query:
            log_data["query"] = request.url.query

        if status_code >= 400:
            # Read the response body to surface the error detail in the log.
            # We must re-stream it afterward, otherwise the client gets an empty body.
            body_bytes = b""
            async for chunk in response.body_iterator:
                body_bytes += chunk

            try:
                log_data["response_body"] = body_bytes.decode("utf-8", errors="replace")
            except Exception:  # pylint: disable=broad-exception-caught
                log_data["response_body"] = "<unreadable>"

            level = logging.ERROR if status_code >= 500 else logging.WARNING
            logger.log(level, "HTTP %s %s → %s", request.method, request.url.path, status_code, extra=log_data)

            # Re-build the response with the already-consumed body
            return Response(
                content=body_bytes,
                status_code=status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        logger.info("HTTP %s %s → %s", request.method, request.url.path, status_code, extra=log_data)
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
