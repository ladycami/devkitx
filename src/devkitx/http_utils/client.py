"""HTTP client factory functions with safe defaults.

This module provides factory functions for creating HTTP clients with sensible
default configurations including timeouts and connection limits.
"""

from __future__ import annotations

from typing import Optional

try:
    import httpx
    _HTTPX_AVAILABLE = True
except ImportError:
    httpx = None  # type: ignore[assignment]
    _HTTPX_AVAILABLE = False


# Safe default configurations
_DEFAULT_TIMEOUT = httpx.Timeout(10.0, read=15.0, connect=10.0) if _HTTPX_AVAILABLE else None
_DEFAULT_LIMITS = httpx.Limits(max_keepalive_connections=10, max_connections=100) if _HTTPX_AVAILABLE else None


def make_client(
    base_url: Optional[str] = None,
    timeout: Optional["httpx.Timeout"] = None,
    limits: Optional["httpx.Limits"] = None,
    headers: Optional[dict[str, str]] = None,
    **kwargs: object,
) -> "httpx.Client":
    """Create HTTP client with safe defaults.
    
    Creates a synchronous HTTP client with sensible timeout and connection
    limit defaults to prevent hanging requests and resource exhaustion.
    
    Args:
        base_url: Optional base URL for all requests
        timeout: Custom timeout configuration (defaults to 10s connect, 15s read)
        limits: Custom connection limits (defaults to 10 keepalive, 100 total)
        headers: Optional default headers for all requests
        **kwargs: Additional arguments passed to httpx.Client
        
    Returns:
        Configured httpx.Client instance
        
    Raises:
        ImportError: If httpx is not installed
        
    Examples:
        >>> client = make_client()
        >>> response = client.get("https://api.example.com/data")
        
        >>> # With base URL and custom headers
        >>> client = make_client(
        ...     base_url="https://api.example.com",
        ...     headers={"Authorization": "Bearer token"}
        ... )
        >>> response = client.get("/users")
    """
    if not _HTTPX_AVAILABLE:
        raise ImportError(
            "HTTP utilities require the 'http' extra. "
            "Install with: pip install 'devkitx[http]'"
        )
    
    # Use http2=False by default to avoid h2 dependency issues
    use_http2 = kwargs.pop('http2', False)
    
    return httpx.Client(
        base_url=base_url or "",
        timeout=timeout or _DEFAULT_TIMEOUT,
        limits=limits or _DEFAULT_LIMITS,
        headers=headers,
        http2=use_http2,
        follow_redirects=True,
        **kwargs
    )


def make_async_client(
    base_url: Optional[str] = None,
    timeout: Optional["httpx.Timeout"] = None,
    limits: Optional["httpx.Limits"] = None,
    headers: Optional[dict[str, str]] = None,
    **kwargs: object,
) -> "httpx.AsyncClient":
    """Create async HTTP client with safe defaults.
    
    Creates an asynchronous HTTP client with sensible timeout and connection
    limit defaults to prevent hanging requests and resource exhaustion.
    
    Args:
        base_url: Optional base URL for all requests
        timeout: Custom timeout configuration (defaults to 10s connect, 15s read)
        limits: Custom connection limits (defaults to 10 keepalive, 100 total)
        headers: Optional default headers for all requests
        **kwargs: Additional arguments passed to httpx.AsyncClient
        
    Returns:
        Configured httpx.AsyncClient instance
        
    Raises:
        ImportError: If httpx is not installed
        
    Examples:
        >>> async with make_async_client() as client:
        ...     response = await client.get("https://api.example.com/data")
        
        >>> # With base URL and custom headers
        >>> async with make_async_client(
        ...     base_url="https://api.example.com",
        ...     headers={"Authorization": "Bearer token"}
        ... ) as client:
        ...     response = await client.get("/users")
    """
    if not _HTTPX_AVAILABLE:
        raise ImportError(
            "HTTP utilities require the 'http' extra. "
            "Install with: pip install 'devkitx[http]'"
        )
    
    # Use http2=False by default to avoid h2 dependency issues
    use_http2 = kwargs.pop('http2', False)
    
    return httpx.AsyncClient(
        base_url=base_url or "",
        timeout=timeout or _DEFAULT_TIMEOUT,
        limits=limits or _DEFAULT_LIMITS,
        headers=headers,
        http2=use_http2,
        follow_redirects=True,
        **kwargs
    )