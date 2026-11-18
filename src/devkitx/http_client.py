"""Production-ready httpx client with secure defaults.

Folded into devkitx from the standalone `httpx-defaults` 1.0.0 package
(MIT, same author). Public names are unchanged.
"""

from __future__ import annotations

import warnings
from typing import Any

import httpx

__all__ = ["Client", "AsyncClient", "SecurityWarning", "safe_get", "safe_post"]

# Production-ready defaults
DEFAULT_TIMEOUT = httpx.Timeout(
    connect=5.0,  # Connection timeout
    read=30.0,  # Read timeout
    write=30.0,  # Write timeout
    pool=10.0,  # Pool timeout
)

DEFAULT_LIMITS = httpx.Limits(
    max_connections=100,
    max_keepalive_connections=20,
    keepalive_expiry=30.0,
)

SECURE_HEADERS = {
    "User-Agent": "httpx-defaults/1.0",
}

# Hosts where plain HTTP does not leave the machine.
_LOOPBACK_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})


class SecurityWarning(UserWarning):
    """Warning for insecure HTTP usage."""


def _is_loopback(host: str) -> bool:
    host = host.lower().rstrip(".")
    return host in _LOOPBACK_HOSTS or host.endswith(".localhost") or host.startswith("127.")


def _warn_if_plain_http(url: httpx.URL | str, stacklevel: int) -> None:
    """Warn when a request would send data over plain HTTP to a remote host."""
    parsed = httpx.URL(url)
    if parsed.scheme == "http" and not _is_loopback(parsed.host):
        warnings.warn(
            f"Using insecure HTTP for {str(parsed)[:50]}... Consider HTTPS.",
            SecurityWarning,
            stacklevel=stacklevel,
        )


class Client(httpx.Client):
    """httpx.Client with production-ready defaults.

    Differences from vanilla httpx.Client:
    - Timeouts configured (connect=5s, read=30s, write=30s, pool=10s)
    - Connection limits set (max=100, keepalive=20)
    - Redirects followed by default
    - Warns (SecurityWarning) on plain HTTP to non-loopback hosts

    The configured ``limits`` and ``verify`` values are available as
    attributes for inspection.

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
        self.limits = limits or DEFAULT_LIMITS
        self.verify = verify
        super().__init__(
            timeout=timeout or DEFAULT_TIMEOUT,
            limits=self.limits,
            follow_redirects=follow_redirects,
            verify=verify,
            **kwargs,
        )

    def request(self, method: str, url: httpx.URL | str, **kwargs: Any) -> httpx.Response:
        """Make request with URL safety check."""
        _warn_if_plain_http(url, stacklevel=3)
        return super().request(method, url, **kwargs)


class AsyncClient(httpx.AsyncClient):
    """httpx.AsyncClient with production-ready defaults.

    Same defaults and plain-HTTP warning as :class:`Client`.

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
        self.limits = limits or DEFAULT_LIMITS
        self.verify = verify
        super().__init__(
            timeout=timeout or DEFAULT_TIMEOUT,
            limits=self.limits,
            follow_redirects=follow_redirects,
            verify=verify,
            **kwargs,
        )

    async def request(self, method: str, url: httpx.URL | str, **kwargs: Any) -> httpx.Response:
        """Make request with URL safety check."""
        _warn_if_plain_http(url, stacklevel=3)
        return await super().request(method, url, **kwargs)


# Convenience functions
def safe_get(url: str, **kwargs: Any) -> httpx.Response:
    """One-shot GET with secure defaults."""
    with Client() as client:
        return client.get(url, **kwargs)


def safe_post(url: str, **kwargs: Any) -> httpx.Response:
    """One-shot POST with secure defaults."""
    with Client() as client:
        return client.post(url, **kwargs)
