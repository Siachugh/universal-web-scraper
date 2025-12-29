"""Utility functions for URL validation and URL resolution."""

from urllib.parse import urljoin, urlparse
from typing import Optional


def is_valid_url(url: str) -> bool:
    """Validate that URL is http or https."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https') and parsed.netloc
    except Exception:
        return False


def make_absolute_url(base_url: str, url: str) -> str:
    """Convert relative URL to absolute URL."""
    if not url:
        return ""
    if url.startswith(('http://', 'https://')):
        return url
    return urljoin(base_url, url)


def truncate_html(html: str, max_length: int = 50000) -> str:
    """Truncate HTML if it exceeds max_length."""
    if len(html) <= max_length:
        return html
    return html[:max_length] + "... [truncated]"

