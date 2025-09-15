"""Security and hashing utilities for the dev-qol-toolkit.

This module provides utilities for password hashing, secret generation,
data hashing, JWT tokens, and input sanitization.
"""

import bcrypt
import secrets
import uuid
import hashlib
import base64
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
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    return hashed.decode('utf-8')


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
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
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
    return base64.b64encode(random_bytes).decode('utf-8')


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
        data_bytes = data.encode('utf-8')
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
    """Generate JWT token.
    
    Args:
        payload: Token payload
        secret: Secret key for signing
        expires_in: Token expiration time in seconds
        
    Returns:
        JWT token string
    """
    # Placeholder implementation
    raise NotImplementedError("Function will be implemented in task 9.3")


def verify_jwt_token(token: str, secret: str) -> dict[str, Any] | None:
    """Verify and decode JWT token.
    
    Args:
        token: JWT token to verify
        secret: Secret key for verification
        
    Returns:
        Decoded payload or None if invalid
    """
    # Placeholder implementation
    raise NotImplementedError("Function will be implemented in task 9.3")


def sanitize_input(text: str, allowed_chars: str | None = None) -> str:
    """Sanitize user input by removing/escaping dangerous characters.
    
    Args:
        text: Input text to sanitize
        allowed_chars: Optional string of allowed characters
        
    Returns:
        Sanitized text
    """
    # Placeholder implementation
    raise NotImplementedError("Function will be implemented in task 9.3")