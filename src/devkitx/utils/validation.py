"""Input validation utilities."""

from __future__ import annotations

import re
from urllib.parse import urlparse


def validate_email(email: str) -> bool:
    """Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid
        
    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid-email")
        False
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str, schemes: list[str] | None = None) -> bool:
    """Validate URL format.
    
    Args:
        url: URL to validate
        schemes: Allowed URL schemes (default: http, https)
        
    Returns:
        True if URL format is valid
        
    Example:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("ftp://example.com", schemes=["ftp"])
        True
        >>> validate_url("invalid-url")
        False
    """
    if schemes is None:
        schemes = ["http", "https"]
    
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme in schemes
            and bool(parsed.netloc)
            and "." in parsed.netloc
        )
    except Exception:
        return False


def validate_port(port: int | str) -> bool:
    """Validate port number.
    
    Args:
        port: Port number to validate
        
    Returns:
        True if port is valid (1-65535)
        
    Example:
        >>> validate_port(80)
        True
        >>> validate_port("8080")
        True
        >>> validate_port(70000)
        False
    """
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except (ValueError, TypeError):
        return False