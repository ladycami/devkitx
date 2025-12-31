"""Cryptographic utilities with secure defaults."""

from __future__ import annotations

import secrets
import hashlib
from typing import Optional

try:
    import bcrypt
    _BCRYPT_AVAILABLE = True
except ImportError:
    _BCRYPT_AVAILABLE = False


def hash_password(password: str, rounds: int = 12) -> str:
    """Hash password using bcrypt with secure defaults.
    
    Args:
        password: Password to hash
        rounds: Number of bcrypt rounds (default: 12)
        
    Returns:
        Hashed password string
        
    Raises:
        ImportError: If bcrypt is not installed
        
    Example:
        >>> hashed = hash_password("my_password")
        >>> len(hashed) > 50  # bcrypt hashes are long
        True
    """
    if not _BCRYPT_AVAILABLE:
        raise ImportError(
            "Password hashing requires bcrypt. "
            "Install with: pip install bcrypt"
        )
    
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=rounds)
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash.
    
    Args:
        password: Plain text password
        hashed: Bcrypt hash to verify against
        
    Returns:
        True if password matches hash
        
    Raises:
        ImportError: If bcrypt is not installed
        
    Example:
        >>> hashed = hash_password("my_password")
        >>> verify_password("my_password", hashed)
        True
        >>> verify_password("wrong_password", hashed)
        False
    """
    if not _BCRYPT_AVAILABLE:
        raise ImportError(
            "Password verification requires bcrypt. "
            "Install with: pip install bcrypt"
        )
    
    password_bytes = password.encode("utf-8")
    hashed_bytes = hashed.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def generate_token(length: int = 32) -> str:
    """Generate cryptographically secure random token.
    
    Args:
        length: Token length in bytes (default: 32)
        
    Returns:
        Hex-encoded random token
        
    Example:
        >>> token = generate_token()
        >>> len(token) == 64  # 32 bytes = 64 hex chars
        True
        >>> token = generate_token(16)
        >>> len(token) == 32  # 16 bytes = 32 hex chars
        True
    """
    return secrets.token_hex(length)


def generate_secret_key(length: int = 32) -> str:
    """Generate secret key for cryptographic operations.
    
    Args:
        length: Key length in bytes (default: 32 for 256-bit key)
        
    Returns:
        Base64-encoded secret key
        
    Example:
        >>> key = generate_secret_key()
        >>> len(key) > 40  # Base64 encoded 32 bytes
        True
    """
    import base64
    key_bytes = secrets.token_bytes(length)
    return base64.b64encode(key_bytes).decode("utf-8")


def secure_hash(data: str | bytes, algorithm: str = "sha256") -> str:
    """Compute secure hash of data.
    
    Args:
        data: Data to hash
        algorithm: Hash algorithm (default: sha256)
        
    Returns:
        Hex-encoded hash
        
    Example:
        >>> hash_val = secure_hash("hello world")
        >>> len(hash_val) == 64  # SHA256 = 64 hex chars
        True
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    
    hasher = hashlib.new(algorithm)
    hasher.update(data)
    return hasher.hexdigest()