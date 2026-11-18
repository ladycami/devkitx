"""DevKitX - Security-first Python utilities for regulated environments.

This package provides security and compliance-focused utilities for government,
healthcare, and financial applications. Features include audit logging, PII detection,
secrets scanning, and secure defaults.

Core features:
    - NIST 800-53 compliant audit logging
    - PII detection and scanning
    - Secrets scanning for hardcoded credentials
    - Secure HTTP clients with production defaults
    - Configuration management with secret detection
    - Async/sync conversion utilities

Example:
    >>> from devkitx.compliance import AuditLogger
    >>> from devkitx.security import SecretsScanner
    >>>
    >>> # Audit logging
    >>> logger = AuditLogger(service="my-api")
    >>> logger.log_auth("user_login", user_id="123", outcome="success")
    >>>
    >>> # Security scanning
    >>> scanner = SecretsScanner()
    >>> matches = scanner.scan_directory("./src")
"""

from ._version import __version__

# Async, HTTP and config helpers (formerly the asyncbridge, httpx-defaults
# and configmerge packages; now part of devkitx)
from .async_bridge import async_to_sync, sync_to_async
from .config import load as load_config
from .config import merge as merge_config
from .http_client import AsyncClient as SecureAsyncClient
from .http_client import Client as SecureClient

# Core utilities
from .utils.json_utils import flatten_json
from .utils.string_utils import to_camel_case, to_kebab_case, to_pascal_case, to_snake_case

__all__ = [
    "__version__",
    # Async utilities
    "async_to_sync",
    "sync_to_async",
    # HTTP utilities
    "SecureClient",
    "SecureAsyncClient",
    # Config utilities
    "load_config",
    "merge_config",
    # Core utilities
    "flatten_json",
    "to_snake_case",
    "to_camel_case",
    "to_pascal_case",
    "to_kebab_case",
]
