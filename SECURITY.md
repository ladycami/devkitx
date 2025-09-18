# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Features & Best Practices

### Password Hashing (`security_utils`)

**Algorithm**: bcrypt with automatic salt generation
```python
from devkitx import security_utils

# Secure password hashing
hashed = security_utils.hash_password("user_password")
verified = security_utils.verify_password("user_password", hashed)
```

**Security Notes**:
- Uses bcrypt with automatic salt generation
- Cost factor is set to a secure default (12 rounds)
- Passwords are never stored in plain text
- Always use `verify_password()` for authentication

### JWT Tokens (`security_utils`)

**Algorithm**: HS256 (HMAC with SHA-256)
```python
# JWT token generation
token = security_utils.generate_jwt_token(
    payload={"user_id": 123}, 
    secret="your-secret-key",
    expires_in=3600  # 1 hour
)

# JWT token verification
payload = security_utils.verify_jwt_token(token, "your-secret-key")
```

**Security Notes**:
- Uses PyJWT library as a thin wrapper
- Tokens include expiration timestamps
- Secret keys should be cryptographically secure (use `generate_secret_key()`)
- Verify tokens on every request
- Store secrets securely (environment variables, key management systems)

### Secret Generation (`security_utils`)

**Algorithm**: `secrets` module (cryptographically secure)
```python
# Generate secure secrets
secret_key = security_utils.generate_secret_key(32)  # 32 bytes
uuid_val = security_utils.generate_uuid()  # UUID4
```

**Security Notes**:
- Uses Python's `secrets` module for cryptographic randomness
- UUIDs are version 4 (random)
- Suitable for API keys, session tokens, and cryptographic keys

### Data Hashing (`security_utils`)

**Algorithm**: SHA-256 (default), configurable
```python
# Hash data for integrity
data_hash = security_utils.hash_data("sensitive_data", algorithm="sha256")
```

**Security Notes**:
- Default algorithm is SHA-256
- Suitable for data integrity verification
- Not suitable for password hashing (use `hash_password()` instead)

### Input Sanitization (`security_utils`)

```python
# Sanitize user input
clean_input = security_utils.sanitize_input(user_input, allowed_chars="alphanumeric")
```

**Security Notes**:
- Removes potentially dangerous characters
- Configurable character allowlists
- Use for user-generated content that will be stored or displayed

## Key Management Best Practices

### JWT Secrets
- **Generate**: Use `security_utils.generate_secret_key(32)` for JWT secrets
- **Store**: Use environment variables or secure key management systems
- **Rotate**: Implement key rotation for production systems
- **Length**: Minimum 32 bytes (256 bits) for HS256

### Environment Variables
```bash
# Example secure configuration
JWT_SECRET=$(python -c "from devkitx import security_utils; print(security_utils.generate_secret_key(32))")
DATABASE_PASSWORD="your-secure-password"
API_KEY="your-api-key"
```

### Configuration Security
```python
# Load secrets securely
from devkitx.config_utils import ConfigManager

config = ConfigManager([".env"])
config.load()

jwt_secret = config.get("JWT_SECRET", type_hint=str)
if not jwt_secret:
    raise ValueError("JWT_SECRET must be set")
```

## Security Limitations & Caveats

### JWT Tokens
- **Stateless**: Cannot be revoked without additional infrastructure
- **Size**: Larger than session IDs, consider for mobile applications
- **Algorithm**: Currently only supports HS256 (symmetric)
- **Expiration**: Always set reasonable expiration times

### Password Hashing
- **Performance**: bcrypt is intentionally slow, consider async operations
- **Cost Factor**: Fixed at secure default, not configurable in current version
- **Migration**: Changing cost factors requires password reset

### Input Sanitization
- **Context-Dependent**: Sanitization needs vary by use case
- **Not XSS Protection**: Use proper templating engines for HTML output
- **Validation**: Sanitization is not validation, use both

## Reporting Security Vulnerabilities

If you discover a security vulnerability in DevKitX, please report it by emailing the maintainers. Please do not report security vulnerabilities through public GitHub issues.

### What to Include
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline
- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Fix & Release**: Depends on severity, typically within 2-4 weeks

## Security Checklist for Users

### Before Using in Production
- [ ] Review all security-related code and configurations
- [ ] Use environment variables for secrets
- [ ] Implement proper key rotation
- [ ] Set up monitoring for security events
- [ ] Regular security audits of dependencies
- [ ] Keep DevKitX updated to latest version

### JWT Implementation
- [ ] Use strong, unique secrets (32+ bytes)
- [ ] Set appropriate expiration times
- [ ] Implement token refresh mechanisms
- [ ] Validate tokens on every request
- [ ] Consider token revocation strategy

### Password Security
- [ ] Never log or store plain text passwords
- [ ] Use HTTPS for password transmission
- [ ] Implement rate limiting for login attempts
- [ ] Consider additional factors (2FA)
- [ ] Regular password policy reviews

---

**Remember**: Security is a process, not a product. Regularly review and update your security practices.