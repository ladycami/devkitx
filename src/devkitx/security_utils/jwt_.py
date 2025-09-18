"""JWT token utilities with safe defaults.

This module provides JWT token generation and verification with secure defaults
and required claims validation.
"""

import datetime as dt
from typing import Any, Mapping

try:
    import jwt
except ImportError:
    raise ImportError(
        "JWT utilities require the 'jwt' extra. "
        "Install with: pip install 'devkitx[jwt]'"
    )

# Safe default algorithm
ALG = "HS256"

__all__ = ["generate_jwt_token", "verify_jwt_token"]


def generate_jwt_token(
    payload: Mapping[str, Any],
    secret: str,
    *,
    expires_in: int = 3600,
    issuer: str | None = None,
    audience: str | None = None,
) -> str:
    """Generate JWT token with safe defaults and required claims.
    
    Args:
        payload: Token payload data
        secret: Secret key for signing the token
        expires_in: Token expiration time in seconds (default: 3600 = 1 hour)
        issuer: Optional issuer claim (iss)
        audience: Optional audience claim (aud)
    
    Returns:
        JWT token string
    
    Raises:
        TypeError: If payload is not a mapping or secret is not a string
        ValueError: If secret is empty or expires_in is not positive
    
    Example:
        >>> payload = {"user_id": 123, "role": "admin"}
        >>> secret = "my-secret-key"
        >>> token = generate_jwt_token(payload, secret, expires_in=3600)
        >>> len(token.split('.')) == 3  # JWT has 3 parts
        True
    """
    if not isinstance(payload, Mapping):
        raise TypeError("Payload must be a mapping")
    
    if not isinstance(secret, str):
        raise TypeError("Secret must be a string")
    
    if not secret:
        raise ValueError("Secret cannot be empty")
    
    if not isinstance(expires_in, int):
        raise TypeError("expires_in must be an integer")
    
    if expires_in <= 0:
        raise ValueError("expires_in must be positive")
    
    # Generate timestamps
    now = dt.datetime.now(dt.timezone.utc)
    
    # Build claims with required iat and exp
    claims = {
        "iat": now,
        "exp": now + dt.timedelta(seconds=expires_in),
        **payload
    }
    
    # Add optional claims
    if issuer:
        claims["iss"] = issuer
    if audience:
        claims["aud"] = audience
    
    return jwt.encode(claims, secret, algorithm=ALG)


def verify_jwt_token(
    token: str,
    secret: str,
    *,
    issuer: str | None = None,
    audience: str | None = None,
    leeway: int = 0,
) -> dict[str, Any]:
    """Verify JWT token with required claims validation.
    
    Args:
        token: JWT token string to verify
        secret: Secret key for verification
        issuer: Optional expected issuer claim (iss)
        audience: Optional expected audience claim (aud)
        leeway: Time leeway in seconds for exp/nbf/iat claims (default: 0)
    
    Returns:
        Decoded payload dictionary if valid
    
    Raises:
        TypeError: If token or secret is not a string
        ValueError: If token or secret is empty
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid or claims don't match
    
    Example:
        >>> payload = {"user_id": 123}
        >>> secret = "my-secret-key"
        >>> token = generate_jwt_token(payload, secret, expires_in=3600)
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
    
    if not isinstance(leeway, int):
        raise TypeError("leeway must be an integer")
    
    if leeway < 0:
        raise ValueError("leeway must be non-negative")
    
    # Decode and verify the token with required claims
    decoded: dict[str, Any] = jwt.decode(
        token,
        secret,
        algorithms=[ALG],
        issuer=issuer,
        audience=audience,
        leeway=leeway,
        options={"require": ["exp", "iat"]},
    )
    return decoded