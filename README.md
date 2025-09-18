# DevKitX

**A pragmatic Python toolkit: HTTP, JSON, async bridges, security, CLI**

DevKitX is a modern, type-safe toolkit providing essential utilities for common development tasks. This package was previously named `devtools-py` but has been renamed to `devkitx` to avoid confusion with Samuel Colvin's `devtools` package (which focuses on pretty-printing and debugging).

> **Note**: This is **not** the same as Samuel Colvin's `devtools` package. DevKitX provides a broader set of utilities including HTTP clients, async bridges, security functions, and more.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Typed](https://img.shields.io/badge/typed-yes-brightgreen.svg)](https://mypy-lang.org/)
[![Development Status](https://img.shields.io/badge/status-beta-orange.svg)](https://pypi.org/project/devkitx/)

## Features

- 🚀 **Modern Python**: Built for Python 3.10+ with full type annotations
- ⚡ **Async Support**: Bridges between sync/async code with safe event loop handling
- 🌐 **HTTP Client**: HTTP utilities with safe defaults, timeouts, and retry logic
- 📦 **JSON Utils**: Flatten nested JSON structures with configurable separators
- 🔒 **Security**: JWT tokens with safe defaults and proper claim validation
- 🎯 **Minimal Core**: Lightweight base package with optional extras for specific features

## Installation

### Basic Installation

```bash
pip install devkitx
```

### Installation with Optional Features

DevKitX uses optional dependencies to keep the core package lightweight. Install only the features you need:

| Extra | Dependencies | Features |
|-------|-------------|----------|
| `http` | `httpx` | HTTP clients with safe defaults and retry logic |
| `cli` | `click`, `rich` | Command-line interfaces and rich terminal output |
| `jwt` | `PyJWT[crypto]` | JWT token generation and verification |
| `bcrypt` | `bcrypt` | Password hashing utilities |
| `yaml` | `pyyaml` | YAML configuration support |
| `toml` | `tomli`, `tomli-w` | TOML configuration support |

```bash
# Install with HTTP utilities
pip install "devkitx[http]"

# Install with multiple extras
pip install "devkitx[http,jwt,cli]"

# Install all extras
pip install "devkitx[http,cli,jwt,bcrypt,yaml,toml]"

# Development installation
pip install "devkitx[dev]"
```

## Quick Start

```python
# Core utilities (always available)
from devkitx import flatten_json, async_to_sync, sync_to_async

# Flatten nested JSON structures
data = {"user": {"profile": {"name": "John", "age": 30}}}
flat_data = flatten_json(data)
# Result: {"user.profile.name": "John", "user.profile.age": 30}

# Bridge between sync and async code
import asyncio

async def async_function(x):
    await asyncio.sleep(0.1)
    return x * 2

# Convert async function to sync
sync_func = async_to_sync(async_function)
result = sync_func(5)  # Works without event loop

# Convert sync function to async
def slow_function(x):
    import time
    time.sleep(0.1)
    return x * 2

async_func = sync_to_async(slow_function)
result = await async_func(5)  # Non-blocking
```

### HTTP Utilities (requires `http` extra)

```python
# Install with: pip install "devkitx[http]"
from devkitx import make_client, make_async_client

# HTTP client with safe defaults
client = make_client(base_url="https://api.example.com")
response = client.get("/users")

# Async HTTP client
async def fetch_data():
    async_client = make_async_client()
    response = await async_client.get("https://api.example.com/data")
    return response.json()
```

### JWT Utilities (requires `jwt` extra)

```python
# Install with: pip install "devkitx[jwt]"
from devkitx.security_utils.jwt_ import generate_jwt_token, verify_jwt_token

# Generate JWT with safe defaults
payload = {"user_id": 123, "role": "admin"}
token = generate_jwt_token(
    payload, 
    secret="your-secret-key",
    expires_in=3600,  # 1 hour
    issuer="your-app",
    audience="your-users"
)

# Verify JWT token
try:
    decoded = verify_jwt_token(
        token, 
        secret="your-secret-key",
        issuer="your-app",
        audience="your-users"
    )
    print(f"User ID: {decoded['user_id']}")
except Exception as e:
    print(f"Invalid token: {e}")
```

## Core Utilities

### JSON Utilities

Flatten nested JSON structures for easier processing:

```python
from devkitx import flatten_json

# Flatten nested JSON structures
nested = {"user": {"profile": {"name": "John", "age": 30}}}
flat = flatten_json(nested)
# Result: {"user.profile.name": "John", "user.profile.age": 30}

# Custom separator
flat_custom = flatten_json(nested, sep="_")
# Result: {"user_profile_name": "John", "user_profile_age": 30}

# Works with arrays too
data = {"items": [{"id": 1, "name": "first"}, {"id": 2, "name": "second"}]}
flat = flatten_json(data)
# Result: {"items.0.id": 1, "items.0.name": "first", "items.1.id": 2, "items.1.name": "second"}
```

### Async Bridge Utilities

Convert between sync and async functions safely:

```python
from devkitx import async_to_sync, sync_to_async
import asyncio

# Convert async function to sync
async def fetch_data(url):
    # Simulate async HTTP request
    await asyncio.sleep(0.1)
    return f"Data from {url}"

sync_fetch = async_to_sync(fetch_data)
result = sync_fetch("https://api.example.com")  # Works without event loop

# Convert sync function to async
def process_data(data):
    # Simulate CPU-intensive work
    import time
    time.sleep(0.1)
    return data.upper()

async_process = sync_to_async(process_data)
result = await async_process("hello")  # Non-blocking

# Concurrency control (requires async_utils module)
from devkitx.async_utils.concurrency import gather_with_limit

async def fetch_multiple():
    urls = ["https://api.example.com/1", "https://api.example.com/2"]
    tasks = [fetch_data(url) for url in urls]
    # Limit to 5 concurrent operations
    results = await gather_with_limit(5, *tasks)
    return results
```

## Optional Utilities

### HTTP Utilities (requires `http` extra)

HTTP clients with safe defaults and retry logic:

```python
# Install with: pip install "devkitx[http]"
from devkitx import make_client, make_async_client
from devkitx.http_utils.retry import with_retries

# Create HTTP client with safe defaults
# - 10s connect timeout, 15s read timeout
# - Connection pooling with limits
# - HTTP/2 support
client = make_client(
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer token"}
)

response = client.get("/users")
print(response.json())

# Async HTTP client
async def fetch_data():
    async_client = make_async_client(base_url="https://api.example.com")
    response = await async_client.get("/data")
    return response.json()

# Retry logic with exponential backoff
def unreliable_request():
    response = client.get("/flaky-endpoint")
    if response.status_code >= 500:
        raise Exception("Server error")
    return response

# Retry up to 3 times with exponential backoff and jitter
result = with_retries(
    unreliable_request,
    retries=3,
    base_delay=0.2,
    jitter=0.2
)
```

### Security Utilities (requires `jwt` extra)

JWT token utilities with safe defaults:

```python
# Install with: pip install "devkitx[jwt]"
from devkitx.security_utils.jwt_ import generate_jwt_token, verify_jwt_token

# Generate JWT token with safe defaults
# - Uses HS256 algorithm
# - Requires exp and iat claims
# - Supports issuer and audience validation
payload = {"user_id": 123, "role": "admin"}
token = generate_jwt_token(
    payload,
    secret="your-secret-key",
    expires_in=3600,  # 1 hour
    issuer="your-app",
    audience="your-users"
)

# Verify JWT token with proper validation
try:
    decoded = verify_jwt_token(
        token,
        secret="your-secret-key",
        issuer="your-app",
        audience="your-users",
        leeway=10  # Allow 10 seconds clock skew
    )
    print(f"User: {decoded['user_id']}, Role: {decoded['role']}")
except Exception as e:
    print(f"Token validation failed: {e}")
```

> **Security Note**: JWT utilities use HS256 algorithm by default and require proper secret key management. Always validate issuer, audience, and implement key rotation in production.

## API Reference

For detailed API documentation, see the individual module files:

- **Core utilities**: Always available after `pip install devkitx`
  - `flatten_json()` - Flatten nested JSON structures
  - `async_to_sync()` - Convert async functions to sync
  - `sync_to_async()` - Convert sync functions to async

- **HTTP utilities**: Available with `pip install "devkitx[http]"`
  - `make_client()` - Create HTTP client with safe defaults
  - `make_async_client()` - Create async HTTP client
  - `with_retries()` - Retry logic with exponential backoff

- **Security utilities**: Available with `pip install "devkitx[jwt]"`
  - `generate_jwt_token()` - Generate JWT tokens with safe defaults
  - `verify_jwt_token()` - Verify JWT tokens with proper validation

- **Async utilities**: Advanced async patterns
  - `gather_with_limit()` - Execute awaitables with concurrency limits

## Requirements

- Python 3.10 or higher
- Core package has minimal dependencies (only `typing-extensions` for Python < 3.11)
- Optional features require additional packages (see Installation section)

## Development

```bash
# Clone the repository
git clone https://github.com/ladycami/devkitx.git
cd devkitx

# Install in development mode with all extras
pip install -e ".[http,cli,jwt,bcrypt,yaml,toml,dev]"

# Run tests
pytest

# Run linting and type checking
ruff check .
mypy devkitx
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security Considerations

DevKitX includes security utilities with safe defaults, but proper security requires understanding their scope and limitations.

### JWT Security

The JWT utilities in DevKitX provide secure defaults but require proper implementation:

**Safe Defaults:**
- Uses HS256 algorithm (HMAC with SHA-256)
- Requires `exp` (expiration) and `iat` (issued at) claims
- Supports `iss` (issuer) and `aud` (audience) validation
- Configurable clock skew tolerance (`leeway`)

**Best Practices:**
```python
from devkitx.security_utils.jwt_ import generate_jwt_token, verify_jwt_token

# ✅ Good: Include issuer and audience
token = generate_jwt_token(
    {"user_id": 123},
    secret="your-256-bit-secret",
    expires_in=900,  # 15 minutes, not hours
    issuer="your-app-name",
    audience="your-app-users"
)

# ✅ Good: Validate issuer and audience
decoded = verify_jwt_token(
    token,
    secret="your-256-bit-secret",
    issuer="your-app-name",
    audience="your-app-users"
)
```

**Security Requirements:**
- **Secret Management**: Use strong, randomly generated secrets (≥256 bits)
- **Key Rotation**: Implement regular secret key rotation
- **Short Expiration**: Use short-lived tokens (15-60 minutes)
- **HTTPS Only**: Always transmit tokens over HTTPS
- **Secure Storage**: Store tokens securely (httpOnly cookies, not localStorage)

### HTTP Security

HTTP utilities include safe defaults but don't handle all security concerns:

**Included Protections:**
- Connection timeouts prevent hanging requests
- Connection pooling limits prevent resource exhaustion
- HTTP/2 support for better performance

**Not Included (implement separately):**
- Request/response validation
- Authentication headers management
- Rate limiting
- SSL certificate verification (relies on httpx defaults)

### Input Sanitization Scope

DevKitX does **not** currently include comprehensive input sanitization. The security utilities focus on:

**Covered:**
- JWT token generation and validation
- Safe HTTP client defaults

**Not Covered (use dedicated libraries):**
- SQL injection prevention → Use parameterized queries
- XSS prevention → Use template engines with auto-escaping
- Command injection prevention → Avoid shell=True, validate inputs
- Path traversal prevention → Use pathlib, validate file paths

### Recommended Security Libraries

For comprehensive security, combine DevKitX with specialized libraries:

```python
# SQL injection prevention
import sqlalchemy  # Use parameterized queries

# XSS prevention  
import markupsafe  # Safe HTML handling
import bleach      # HTML sanitization

# Input validation
import pydantic    # Data validation with types
import cerberus    # Schema validation

# Cryptography
import cryptography  # Advanced crypto operations
import bcrypt       # Password hashing (available as devkitx[bcrypt])
```

### Security Reporting

If you discover security vulnerabilities in DevKitX, please report them responsibly:

1. **Do not** create public GitHub issues for security vulnerabilities
2. Email security concerns to the maintainers
3. Include detailed reproduction steps
4. Allow reasonable time for fixes before public disclosure

## Package History

### Package Rename Notice

This package was previously named `devtools-py` but has been renamed to `devkitx` to avoid confusion with Samuel Colvin's `devtools` package. If you were using the old package name, please update your dependencies:

```bash
# Old (deprecated)
pip uninstall devtools-py
# New
pip install devkitx
```

Update your imports:
```python
# Old
from devtools_py import some_function
# New  
from devkitx import some_function
```

## Changelog

### v1.0.1 (2025-09-16)

#### Changed
- **BREAKING**: Renamed package from `devtools-py` to `devkitx`
- Updated development status to Beta (was incorrectly marked as Production/Stable)
- Restructured as lightweight core package with optional extras
- Updated all project URLs to point to correct repository

#### Added
- HTTP clients with safe defaults (10s connect, 15s read timeout)
- Async bridge utilities with proper event loop handling
- JWT utilities with secure defaults and proper validation
- JSON flattening utility with configurable separators
- Retry logic with exponential backoff and jitter
- Type annotations with `py.typed` marker
- Minimal test suite with CI/CD pipeline

#### Fixed
- Import statements now use correct `devkitx` namespace
- Package metadata points to correct repository
- Optional dependencies properly isolated with extras
