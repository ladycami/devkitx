"""HTTP utilities for DevKitX.

This package provides HTTP client factories with safe defaults and retry logic
for robust HTTP operations.

Core functions:
    make_client: Create synchronous HTTP client with safe defaults
    make_async_client: Create asynchronous HTTP client with safe defaults
    with_retries: Execute functions with exponential backoff retry logic
"""

from __future__ import annotations

try:
    from .client import make_client, make_async_client
    from .retry import with_retries
    
    __all__ = ["make_client", "make_async_client", "with_retries"]
    
except ImportError:
    # httpx not available - provide helpful error message
    def _missing_httpx_error(*args: object, **kwargs: object) -> None:
        raise ImportError(
            "HTTP utilities require the 'http' extra. "
            "Install with: pip install 'devkitx[http]'"
        )
    
    make_client = _missing_httpx_error
    make_async_client = _missing_httpx_error
    with_retries = _missing_httpx_error
    
    __all__ = ["make_client", "make_async_client", "with_retries"]