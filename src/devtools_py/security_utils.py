"""Security and hashing utilities for DevKitX.

This module provides utilities for password hashing, secret generation,
data hashing, JWT tokens, and input sanitization.
"""

import bcrypt
import secrets
import uuid
import hashlib
import base64
import jwt
import re
import html
import time
from typing import Any

__all__ = [
    "hash_password",
    "verify_password",
    "generate_secret_key",
    "generate_uuid",
    "hash_data",
    "generate_jwt_token",
    "verify_jwt_token",
    "sanitize_input",
]


def hash_password(password: str) -> str:
    """Hash password using bcrypt algorithm.

    Args:
        password: Plain text password to hash

    Returns:
        Bcrypt hashed password as string

    Example:
        >>> hashed = hash_password("my_secure_password")
        >>> len(hashed) == 60  # bcrypt hashes are always 60 characters
        True
    """
    if not isinstance(password, str):
        raise TypeError("Password must be a string")

    if not password:
        raise ValueError("Password cannot be empty")

    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)

    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash.

    Args:
        password: Plain text password to verify
        hashed: Bcrypt hashed password to verify against

    Returns:
        True if password matches hash, False otherwise

    Example:
        >>> hashed = hash_password("my_password")
        >>> verify_password("my_password", hashed)
        True
        >>> verify_password("wrong_password", hashed)
        False
    """
    if not isinstance(password, str):
        raise TypeError("Password must be a string")

    if not isinstance(hashed, str):
        raise TypeError("Hashed password must be a string")

    if not password:
        raise ValueError("Password cannot be empty")

    if not hashed:
        raise ValueError("Hashed password cannot be empty")

    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        # Invalid hash format
        return False


def generate_secret_key(length: int = 32) -> str:
    """Generate cryptographically secure secret key.

    Args:
        length: Length of secret key in bytes (default: 32)

    Returns:
        Base64-encoded secret key

    Example:
        >>> key = generate_secret_key()
        >>> len(base64.b64decode(key)) == 32
        True
        >>> key1 = generate_secret_key(16)
        >>> key2 = generate_secret_key(16)
        >>> key1 != key2  # Should be different each time
        True
    """
    if not isinstance(length, int):
        raise TypeError("Length must be an integer")

    if length <= 0:
        raise ValueError("Length must be positive")

    if length > 1024:
        raise ValueError("Length cannot exceed 1024 bytes")

    # Generate cryptographically secure random bytes
    random_bytes = secrets.token_bytes(length)

    # Encode as base64 for safe string representation
    return base64.b64encode(random_bytes).decode("utf-8")


def generate_uuid() -> str:
    """Generate UUID4 string.

    Returns:
        UUID4 string in standard format (e.g., '550e8400-e29b-41d4-a716-446655440000')

    Example:
        >>> uuid_str = generate_uuid()
        >>> len(uuid_str) == 36
        True
        >>> uuid_str.count('-') == 4
        True
        >>> uuid1 = generate_uuid()
        >>> uuid2 = generate_uuid()
        >>> uuid1 != uuid2  # Should be different each time
        True
    """
    return str(uuid.uuid4())


def hash_data(data: bytes | str, algorithm: str = "sha256") -> str:
    """Hash data using specified algorithm.

    Args:
        data: Data to hash (string or bytes)
        algorithm: Hashing algorithm to use (sha256, sha1, sha512, md5, etc.)

    Returns:
        Hexadecimal hash string

    Example:
        >>> hash_data("hello world")
        'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'
        >>> hash_data(b"hello world")
        'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'
        >>> hash_data("test", "md5")
        '098f6bcd4621d373cade4e832627b4f6'
    """
    if not isinstance(data, (str, bytes)):
        raise TypeError("Data must be string or bytes")

    if not isinstance(algorithm, str):
        raise TypeError("Algorithm must be a string")

    # Convert string to bytes if necessary
    if isinstance(data, str):
        data_bytes = data.encode("utf-8")
    else:
        data_bytes = data

    # Check if algorithm is supported
    try:
        hasher = hashlib.new(algorithm)
    except ValueError:
        available_algorithms = sorted(hashlib.algorithms_available)
        raise ValueError(f"Unsupported algorithm '{algorithm}'. Available: {available_algorithms}")

    hasher.update(data_bytes)
    return hasher.hexdigest()


def generate_jwt_token(payload: dict[str, Any], secret: str, expires_in: int = 3600) -> str:
    """Generate JWT token with expiration.

    Args:
        payload: Token payload data
        secret: Secret key for signing the token
        expires_in: Token expiration time in seconds (default: 3600 = 1 hour)

    Returns:
        JWT token string

    Example:
        >>> payload = {"user_id": 123, "role": "admin"}
        >>> secret = "my-secret-key"
        >>> token = generate_jwt_token(payload, secret, 3600)
        >>> len(token.split('.')) == 3  # JWT has 3 parts
        True
    """
    if not isinstance(payload, dict):
        raise TypeError("Payload must be a dictionary")

    if not isinstance(secret, str):
        raise TypeError("Secret must be a string")

    if not secret:
        raise ValueError("Secret cannot be empty")

    if not isinstance(expires_in, int):
        raise TypeError("expires_in must be an integer")

    if expires_in <= 0:
        raise ValueError("expires_in must be positive")

    # Create a copy of payload to avoid modifying the original
    token_payload = payload.copy()

    # Add standard JWT claims
    current_time = int(time.time())
    token_payload.update(
        {
            "iat": current_time,  # Issued at
            "exp": current_time + expires_in,  # Expiration time
        }
    )

    # Generate and return JWT token
    return jwt.encode(token_payload, secret, algorithm="HS256")


def verify_jwt_token(token: str, secret: str) -> dict[str, Any] | None:
    """Verify and decode JWT token.

    Args:
        token: JWT token string to verify
        secret: Secret key for verification

    Returns:
        Decoded payload dictionary if valid, None if invalid or expired

    Example:
        >>> payload = {"user_id": 123}
        >>> secret = "my-secret-key"
        >>> token = generate_jwt_token(payload, secret, 3600)
        >>> decoded = verify_jwt_token(token, secret)
        >>> decoded["user_id"] == 123
        True
    """
    if not isinstance(token, str):
        raise TypeError("Token must be a string")

    if not isinstance(secret, str):
        raise TypeError("Secret must be a string")

    if not token:
        raise ValueError("Token cannot be empty")

    if not secret:
        raise ValueError("Secret cannot be empty")

    try:
        # Decode and verify the token
        decoded_payload = jwt.decode(token, secret, algorithms=["HS256"])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Token is invalid (malformed, wrong signature, etc.)
        return None


def sanitize_input(text: str, allowed_chars: str | None = None) -> str:
    """Sanitize user input by removing/escaping dangerous characters.

    This function provides basic input sanitization by:
    1. HTML escaping dangerous characters
    2. Removing or filtering characters based on allowed_chars
    3. Normalizing whitespace

    Args:
        text: Input text to sanitize
        allowed_chars: Optional regex pattern of allowed characters.
                      If provided, only these characters will be kept.

    Returns:
        Sanitized text string

    Example:
        >>> sanitize_input("<script>alert('xss')</script>")
        '&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;'
        >>> sanitize_input("Hello123!", r"[a-zA-Z0-9]")
        'Hello123'
        >>> sanitize_input("  multiple   spaces  ")
        'multiple spaces'
    """
    if not isinstance(text, str):
        raise TypeError("Text must be a string")

    if allowed_chars is not None and not isinstance(allowed_chars, str):
        raise TypeError("allowed_chars must be a string or None")

    # Start with the input text
    sanitized = text

    # HTML escape dangerous characters
    sanitized = html.escape(sanitized, quote=True)

    # If allowed_chars pattern is provided, filter characters
    if allowed_chars is not None:
        try:
            # Keep only characters that match the allowed pattern
            sanitized = re.sub(f"[^{allowed_chars}]", "", sanitized)
        except re.error:
            raise ValueError(f"Invalid regex pattern in allowed_chars: {allowed_chars}")

    # Normalize whitespace (collapse multiple spaces into single spaces)
    sanitized = re.sub(r"\s+", " ", sanitized).strip()

    return sanitized
