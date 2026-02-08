"""URL normalization and validation utilities."""
from urllib.parse import urlparse, urljoin, urlunparse
from typing import Optional
import re


def normalize_url(url: str) -> str:
    """
    Normalize a URL by removing fragments, sorting query params, etc.

    Args:
        url: URL to normalize

    Returns:
        Normalized URL
    """
    parsed = urlparse(url)

    # Remove fragment
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc.lower(),
        parsed.path or "/",
        parsed.params,
        parsed.query,
        "",  # Remove fragment
    ))

    # Remove trailing slash from non-root paths
    if normalized.endswith("/") and parsed.path != "/":
        normalized = normalized[:-1]

    return normalized


def is_same_domain(url1: str, url2: str) -> bool:
    """
    Check if two URLs are from the same domain.

    Args:
        url1: First URL
        url2: Second URL

    Returns:
        True if same domain, False otherwise
    """
    domain1 = urlparse(url1).netloc.lower()
    domain2 = urlparse(url2).netloc.lower()
    return domain1 == domain2


def get_base_url(url: str) -> str:
    """
    Get base URL (scheme + netloc) from a URL.

    Args:
        url: Full URL

    Returns:
        Base URL (e.g., https://example.com)
    """
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def ensure_absolute_url(url: str, base_url: str) -> str:
    """
    Convert relative URL to absolute URL.

    Args:
        url: URL (can be relative or absolute)
        base_url: Base URL to use for relative URLs

    Returns:
        Absolute URL
    """
    return urljoin(base_url, url)


def is_valid_url(url: str) -> bool:
    """
    Check if URL is valid.

    Args:
        url: URL to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False


def should_crawl_url(url: str, base_domain: str) -> bool:
    """
    Determine if a URL should be crawled based on various criteria.

    Args:
        url: URL to check
        base_domain: Base domain we're crawling

    Returns:
        True if URL should be crawled, False otherwise
    """
    # Must be valid URL
    if not is_valid_url(url):
        return False

    # Must be same domain
    if not is_same_domain(url, f"https://{base_domain}"):
        return False

    # Must be HTTP or HTTPS
    parsed = urlparse(url)
    if parsed.scheme not in ["http", "https"]:
        return False

    # Skip common non-content URLs
    skip_extensions = [
        ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp",
        ".zip", ".tar", ".gz", ".rar", ".7z",
        ".mp3", ".mp4", ".avi", ".mov", ".wmv",
        ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".css", ".js", ".json", ".xml", ".rss",
    ]

    path_lower = parsed.path.lower()
    if any(path_lower.endswith(ext) for ext in skip_extensions):
        return False

    # Skip common admin/login paths
    skip_patterns = [
        r"/admin",
        r"/login",
        r"/wp-admin",
        r"/user/",
        r"/account",
        r"/cart",
        r"/checkout",
    ]

    for pattern in skip_patterns:
        if re.search(pattern, path_lower):
            return False

    return True
