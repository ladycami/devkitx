"""Security utilities for DevKitX.

This module provides security-related utilities including JWT token handling,
password hashing, and input sanitization.
"""

# Import JWT utilities with graceful handling for missing dependencies
try:
    from .jwt_ import generate_jwt_token, verify_jwt_token
    __all__ = ["generate_jwt_token", "verify_jwt_token"]
except ImportError:
    # JWT utilities not available without PyJWT dependency
    __all__ = []