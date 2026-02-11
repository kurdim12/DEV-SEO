"""
Security middleware for adding security headers to responses.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.

    Headers added:
    - X-Frame-Options: Prevent clickjacking
    - X-Content-Type-Options: Prevent MIME sniffing
    - X-XSS-Protection: Enable XSS filter
    - Strict-Transport-Security: Force HTTPS (production only)
    - Content-Security-Policy: Restrict resource loading
    - Referrer-Policy: Control referrer information
    - Permissions-Policy: Control browser features
    """

    def __init__(self, app, production: bool = False):
        super().__init__(app)
        self.production = production

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Force HTTPS (only in production)
        if self.production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content Security Policy - restrictive but allows CDN
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.devseo.io; "
            "frame-ancestors 'none';"
        )

        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Control browser features
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )

        return response
