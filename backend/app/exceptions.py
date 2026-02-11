"""
Custom exceptions for the DevSEO application.
"""
from fastapi import HTTPException, status


class DevSEOException(HTTPException):
    """Base exception for all DevSEO errors."""

    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail)


class RateLimitExceededException(DevSEOException):
    """Raised when rate limit is exceeded."""

    def __init__(self, detail: str = "Rate limit exceeded. Please try again later."):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


class QuotaExceededException(DevSEOException):
    """Raised when monthly/plan quota is exceeded."""

    def __init__(self, resource: str = "scans"):
        super().__init__(
            detail=f"Monthly {resource} quota exceeded. Upgrade your plan for higher limits.",
            status_code=status.HTTP_403_FORBIDDEN
        )


class PlanLimitException(DevSEOException):
    """Raised when plan limit is reached."""

    def __init__(self, resource: str, limit: int):
        super().__init__(
            detail=f"Your plan allows {limit} {resource}. Upgrade to add more.",
            status_code=status.HTTP_403_FORBIDDEN
        )


class ResourceNotFoundException(DevSEOException):
    """Raised when a resource is not found."""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            detail=f"{resource} with ID {resource_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class UnauthorizedException(DevSEOException):
    """Raised when user is not authorized."""

    def __init__(self, detail: str = "Not authorized to access this resource"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN
        )


class InvalidInputException(DevSEOException):
    """Raised when input validation fails."""

    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class CrawlException(DevSEOException):
    """Raised when crawl fails."""

    def __init__(self, url: str, reason: str):
        super().__init__(
            detail=f"Failed to crawl {url}: {reason}",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class VerificationException(DevSEOException):
    """Raised when domain verification fails."""

    def __init__(self, method: str, reason: str):
        super().__init__(
            detail=f"Verification failed ({method}): {reason}",
            status_code=status.HTTP_400_BAD_REQUEST
        )
