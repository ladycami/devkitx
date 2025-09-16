"""HTTP utilities for DevKitX.

This module provides utilities for making HTTP requests with retry logic,
async support, and convenient API client classes.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Iterable, Mapping, MutableMapping

import httpx


RETRY_STATUSES = {429, 500, 502, 503, 504}


def _sleep_backoff(attempt: int, base: float = 0.25, cap: float = 4.0) -> None:
    delay = min(cap, base * (2 ** (attempt - 1)))
    time.sleep(delay)


def _merge_headers(
    base: Mapping[str, str] | None, extra: Mapping[str, str] | None
) -> MutableMapping[str, str]:
    out: dict[str, str] = {}
    if base:
        out.update(base)
    if extra:
        out.update(extra)
    return out


def api_request(
    method: str,
    url: str,
    *,
    headers: Mapping[str, str] | None = None,
    json_body: Any | None = None,
    params: Mapping[str, Any] | None = None,
    timeout: float = 15.0,
    retries: int = 3,
) -> Any:
    """Make synchronous HTTP request with automatic retries.

    Automatically retries on common transient failures (429, 5xx status codes)
    with exponential backoff. Returns parsed JSON when possible, otherwise text.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: Target URL
        headers: Optional HTTP headers
        json_body: Optional JSON body for request
        params: Optional query parameters
        timeout: Request timeout in seconds
        retries: Number of retry attempts

    Returns:
        Parsed JSON response or text content

    Raises:
        httpx.HTTPStatusError: For HTTP error status codes (after retries)
        httpx.RequestError: For network-related errors (after retries)

    Examples:
        >>> response = api_request("GET", "https://api.example.com/users")
        >>> user_data = api_request("POST", "https://api.example.com/users",
        ...                        json_body={"name": "John", "email": "john@example.com"})
        >>> api_request("GET", "https://api.example.com/data",
        ...              headers={"Authorization": "Bearer token"},
        ...              params={"page": 1, "limit": 10})
    """
    hdrs = _merge_headers({"accept": "application/json"}, headers)
    last_exc: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            with httpx.Client(http2=True, timeout=timeout, follow_redirects=True) as client:
                resp = client.request(
                    method.upper(), url, headers=hdrs, json=json_body, params=params
                )
            if resp.status_code in RETRY_STATUSES and attempt < retries:
                _sleep_backoff(attempt)
                continue
            resp.raise_for_status()
            ctype = resp.headers.get("content-type", "")
            if "application/json" in ctype:
                return resp.json()
            return resp.text
        except Exception as exc:
            last_exc = exc
            if attempt >= retries:
                raise
            _sleep_backoff(attempt)
    if last_exc:
        raise last_exc


class BaseAPIClient:
    """Synchronous API client for making HTTP requests to a base URL.

    Examples:
        >>> client = BaseAPIClient("https://api.example.com")
        >>> users = client.get("/users")
        >>> new_user = client.post("/users", json_body={"name": "John"})

        >>> # With authentication headers
        >>> client = BaseAPIClient("https://api.example.com",
        ...                       headers={"Authorization": "Bearer token"})
        >>> data = client.get("/protected-endpoint")
    """

    def __init__(
        self, base_url: str, headers: Mapping[str, str] | None = None, timeout: float = 15.0
    ):
        """Initialize API client.

        Args:
            base_url: Base URL for all requests
            headers: Default headers to include in all requests
            timeout: Default timeout for requests in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.headers = dict(headers or {})
        self.timeout = timeout

    def _url(self, path: str) -> str:
        """Construct full URL from path."""
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(self, path: str, **kwargs: Any) -> Any:
        """Make GET request to the specified path."""
        return api_request(
            "GET", self._url(path), headers=self.headers, timeout=self.timeout, **kwargs
        )

    def post(self, path: str, **kwargs: Any) -> Any:
        """Make POST request to the specified path."""
        return api_request(
            "POST", self._url(path), headers=self.headers, timeout=self.timeout, **kwargs
        )

    def put(self, path: str, **kwargs: Any) -> Any:
        """Make PUT request to the specified path."""
        return api_request(
            "PUT", self._url(path), headers=self.headers, timeout=self.timeout, **kwargs
        )

    def delete(self, path: str, **kwargs: Any) -> Any:
        """Make DELETE request to the specified path."""
        return api_request(
            "DELETE", self._url(path), headers=self.headers, timeout=self.timeout, **kwargs
        )

    def patch(self, path: str, **kwargs: Any) -> Any:
        """Make PATCH request to the specified path."""
        return api_request(
            "PATCH", self._url(path), headers=self.headers, timeout=self.timeout, **kwargs
        )


# Async helpers
async def _async_sleep_backoff(attempt: int, base: float = 0.25, cap: float = 4.0) -> None:
    """Async version of sleep backoff."""
    delay = min(cap, base * (2 ** (attempt - 1)))
    await asyncio.sleep(delay)


async def async_api_request(
    method: str,
    url: str,
    *,
    headers: Mapping[str, str] | None = None,
    json_body: Any | None = None,
    params: Mapping[str, Any] | None = None,
    timeout: float = 15.0,
    retries: int = 3,
) -> Any:
    """
    Async HTTP request with retries/jitter on common transient failures.
    Returns parsed JSON when possible else text.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: Target URL
        headers: Optional HTTP headers
        json_body: Optional JSON body for request
        params: Optional query parameters
        timeout: Request timeout in seconds
        retries: Number of retry attempts

    Returns:
        Parsed JSON response or text content

    Raises:
        httpx.HTTPStatusError: For HTTP error status codes
        httpx.RequestError: For network-related errors
    """
    hdrs = _merge_headers({"accept": "application/json"}, headers)
    last_exc: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(
                http2=True, timeout=timeout, follow_redirects=True
            ) as client:
                resp = await client.request(
                    method.upper(), url, headers=hdrs, json=json_body, params=params
                )
            if resp.status_code in RETRY_STATUSES and attempt < retries:
                await _async_sleep_backoff(attempt)
                continue
            resp.raise_for_status()
            ctype = resp.headers.get("content-type", "")
            if "application/json" in ctype:
                return resp.json()
            return resp.text
        except Exception as exc:
            last_exc = exc
            if attempt >= retries:
                raise
            await _async_sleep_backoff(attempt)
    if last_exc:
        raise last_exc


class AsyncAPIClient:
    """Async version of BaseAPIClient for making HTTP requests."""

    def __init__(
        self, base_url: str, headers: Mapping[str, str] | None = None, timeout: float = 15.0
    ):
        """Initialize async API client.

        Args:
            base_url: Base URL for all requests
            headers: Default headers to include in all requests
            timeout: Default timeout for requests in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.headers = dict(headers or {})
        self.timeout = timeout

    def _url(self, path: str) -> str:
        """Construct full URL from path."""
        return f"{self.base_url}/{path.lstrip('/')}"

    async def get(self, path: str, **kwargs: Any) -> Any:
        """Make async GET request."""
        return await async_api_request(
            "GET", self._url(path), headers=self.headers, timeout=self.timeout, **kwargs
        )

    async def post(self, path: str, **kwargs: Any) -> Any:
        """Make async POST request."""
        return await async_api_request(
            "POST", self._url(path), headers=self.headers, timeout=self.timeout, **kwargs
        )

    async def put(self, path: str, **kwargs: Any) -> Any:
        """Make async PUT request."""
        return await async_api_request(
            "PUT", self._url(path), headers=self.headers, timeout=self.timeout, **kwargs
        )

    async def delete(self, path: str, **kwargs: Any) -> Any:
        """Make async DELETE request."""
        return await async_api_request(
            "DELETE", self._url(path), headers=self.headers, timeout=self.timeout, **kwargs
        )

    async def patch(self, path: str, **kwargs: Any) -> Any:
        """Make async PATCH request."""
        return await async_api_request(
            "PATCH", self._url(path), headers=self.headers, timeout=self.timeout, **kwargs
        )


async def async_batch_requests(
    requests: Iterable[tuple[str, str, dict[str, Any]]],
    concurrency_limit: int = 10,
    **default_kwargs: Any,
) -> list[Any]:
    """Execute multiple HTTP requests concurrently with a concurrency limit.

    Args:
        requests: Iterable of (method, url, kwargs) tuples
        concurrency_limit: Maximum number of concurrent requests
        **default_kwargs: Default arguments for all requests

    Returns:
        List of responses in the same order as input requests

    Example:
        >>> requests = [
        ...     ("GET", "https://api.example.com/users/1", {}),
        ...     ("GET", "https://api.example.com/users/2", {}),
        ...     ("POST", "https://api.example.com/users", {"json_body": {"name": "John"}}),
        ... ]
        >>> responses = await async_batch_requests(requests, concurrency_limit=5)
    """
    # Import here to avoid circular imports
    from .async_utils import gather_with_limit

    async def make_request(method: str, url: str, kwargs: dict[str, Any]) -> Any:
        merged_kwargs = {**default_kwargs, **kwargs}
        return await async_api_request(method, url, **merged_kwargs)

    # Create tasks for all requests
    tasks = [make_request(method, url, kwargs) for method, url, kwargs in requests]

    # Execute with concurrency limit
    return await gather_with_limit(concurrency_limit, *tasks)


async def async_download_file(
    url: str,
    file_path: str,
    *,
    headers: Mapping[str, str] | None = None,
    timeout: float = 30.0,
    chunk_size: int = 8192,
) -> None:
    """Download a file asynchronously.

    Args:
        url: URL to download from
        file_path: Local path to save the file
        headers: Optional HTTP headers
        timeout: Request timeout in seconds
        chunk_size: Size of chunks to read/write

    Raises:
        httpx.HTTPStatusError: For HTTP error status codes
        httpx.RequestError: For network-related errors
        OSError: For file system errors
    """
    hdrs = _merge_headers({}, headers)

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        response = await client.get(url, headers=hdrs)
        response.raise_for_status()

        with open(file_path, "wb") as file:
            file.write(response.content)
