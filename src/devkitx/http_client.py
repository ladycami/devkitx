"""Production-ready httpx client with secure defaults.

Folded into devkitx from the standalone `httpx-defaults` 1.0.0 package
(MIT, same author). Public names are unchanged.
"""

from __future__ import annotations

from typing import Any
import httpx

__all__ = ["Client", "AsyncClient", "safe_get", "safe_post"]

# Production-ready defaults
DEFAULT_TIMEOUT = httpx.Timeout(
    connect=5.0,      # Connection timeout
    read=30.0,        # Read timeout  
    write=30.0,       # Write timeout
    pool=10.0,        # Pool timeout
)

DEFAULT_LIMITS = httpx.Limits(
    max_connections=100,
    max_keepalive_connections=20,
    keepalive_expiry=30.0,
)

SECURE_HEADERS = {
    "User-Agent": "httpx-defaults/1.0",
}


class Client(httpx.Client):
    """httpx.Client with production-ready defaults.
    
    Differences from vanilla httpx.Client:
    - Timeouts configured (connect=5s, read=30s, write=30s)
    - Connection limits set (max=100, keepalive=20)
    - Redirects followed by default
    - HTTPS preferred (warns on HTTP in non-localhost)
    
    Example:
        >>> with Client() as client:
        ...     response = client.get("https://api.example.com/users")
        ...     data = response.json()
    """
    
    def __init__(
        self,
        *,
        timeout: httpx.Timeout | None = None,
        limits: httpx.Limits | None = None,
        follow_redirects: bool = True,
        verify: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            timeout=timeout or DEFAULT_TIMEOUT,
            limits=limits or DEFAULT_LIMITS,
            follow_redirects=follow_redirects,
            verify=verify,
            **kwargs,
        )
    
    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Make request with URL safety check."""
        self._warn_http(url)
        return super().request(method, url, **kwargs)
    
    def _warn_http(self, url: str) -> None:
        """Warn if using HTTP for non-localhost URLs."""
        import warnings
        if url.startswith("http://") and "localhost" not in url and "127.0.0.1" not in url:
            warnings.warn(
                f"Using insecure HTTP for {url[:50]}... Consider HTTPS.",
                SecurityWarning,
                stacklevel=3,
            )


class AsyncClient(httpx.AsyncClient):
    """httpx.AsyncClient with production-ready defaults.
    
    Same defaults as Client but for async usage.
    
    Example:
        >>> async with AsyncClient() as client:
        ...     response = await client.get("https://api.example.com/users")
        ...     data = response.json()
    """
    
    def __init__(
        self,
        *,
        timeout: httpx.Timeout | None = None,
        limits: httpx.Limits | None = None,
        follow_redirects: bool = True,
        verify: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            timeout=timeout or DEFAULT_TIMEOUT,
            limits=limits or DEFAULT_LIMITS,
            follow_redirects=follow_redirects,
            verify=verify,
            **kwargs,
        )


class SecurityWarning(UserWarning):
    """Warning for insecure HTTP usage."""
    pass


# Convenience functions
def safe_get(url: str, **kwargs: Any) -> httpx.Response:
    """One-shot GET with secure defaults."""
    with Client() as client:
        return client.get(url, **kwargs)


def safe_post(url: str, **kwargs: Any) -> httpx.Response:
    """One-shot POST with secure defaults."""
    with Client() as client:
        return client.post(url, **kwargs)