"""DevKitX - A pragmatic Python toolkit for HTTP, JSON, async bridges, security, and CLI.

This package provides curated utilities for common development tasks with a focus
on safety, simplicity, and reliability. Core functionality is always available,
while specialized features are available through optional dependencies.

Core utilities (always available):
    flatten_json: Flatten nested JSON structures into dot-notation keys
    async_to_sync: Convert async functions to sync with proper event loop handling
    sync_to_async: Convert sync functions to async using thread executors

Optional utilities (require extras):
    HTTP clients with safe defaults (requires 'http' extra)
    JWT utilities with secure defaults (requires 'jwt' extra)
    CLI utilities with rich formatting (requires 'cli' extra)

Example:
    >>> from devkitx import flatten_json, async_to_sync
    >>> flat = flatten_json({"user": {"name": "John", "age": 30}})
    >>> # {'user.name': 'John', 'user.age': 30}
    >>> 
    >>> async def fetch_data(): return "data"
    >>> sync_fetch = async_to_sync(fetch_data)
    >>> result = sync_fetch()  # "data"
"""

from ._version import __version__

# Core utilities (always available)
from .json_utils.flatten import flatten_json
from .async_utils import async_to_sync, sync_to_async

# Optional utilities (gracefully handle missing dependencies)
try:
    from .http_utils import make_client, make_async_client
except (ImportError, AttributeError):
    # HTTP utilities not available without httpx extra
    pass

try:
    from .security_utils import generate_jwt_token, verify_jwt_token
except ImportError:
    # JWT utilities not available without jwt extra
    pass

# Build __all__ dynamically based on available features
__all__ = [
    "__version__",
    "flatten_json",
    "async_to_sync", 
    "sync_to_async",
]

# Add optional utilities to __all__ if they're available
try:
    make_client
    make_async_client
    __all__.extend(["make_client", "make_async_client"])
except NameError:
    pass

try:
    generate_jwt_token
    verify_jwt_token
    __all__.extend(["generate_jwt_token", "verify_jwt_token"])
except NameError:
    pass
