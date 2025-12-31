# DevKitX

> Security-first Python utilities for government, healthcare, and financial applications.

[![PyPI](https://img.shields.io/pypi/v/devkitx)](https://pypi.org/project/devkitx/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why DevKitX?

Most Python utility libraries optimize for convenience. DevKitX optimizes for **security and compliance**.

| Feature | Generic Libraries | DevKitX |
|---------|-------------------|---------|
| HTTP timeouts | Optional | **Enforced by default** |
| Secret detection | Not included | **Built-in scanner** |
| Audit logging | DIY | **NIST AU-3 compliant** |
| PII detection | Not included | **Automatic scanning** |
| Config secrets | Mixed with config | **Env-only pattern enforced** |

## Quick Start

```bash
pip install devkitx

# Scan for hardcoded secrets
devkitx audit secrets ./src

# Scan for PII
devkitx audit pii ./data

# Check dependencies for CVEs
devkitx audit deps
```

## For Developers

```python
from devkitx.security import SecretsScanner
from devkitx.compliance import AuditLogger, PIIDetector

# Audit logging that meets NIST 800-53 AU controls
logger = AuditLogger(service="my-api")
logger.log_auth("user_login", user_id="123", outcome="success")

# Scan uploads for PII before storage
detector = PIIDetector()
matches = detector.scan_text(user_input)
if matches:
    raise ValueError(f"PII detected: {[m.pii_type for m in matches]}")
```

## Micro-Packages

Need just one feature? Install the standalone packages:

```bash
pip install asyncbridge      # Async/sync conversion
pip install httpx-defaults   # Production-ready HTTP client
pip install confmerge        # Multi-format config loading
```

## Compliance Mapping

DevKitX features map to common compliance frameworks:

| DevKitX Feature | NIST 800-53 | SOC 2 | HIPAA |
|-----------------|-------------|-------|-------|
| AuditLogger | AU-2, AU-3, AU-9 | CC7.2 | 164.312(b) |
| SecretsScanner | SA-3, SC-28 | CC6.1 | 164.312(a)(1) |
| PIIDetector | SI-12, PM-25 | CC6.5 | 164.514 |
| SecureClient | SC-8, SC-13 | CC6.6 | 164.312(e)(1) |

## Installation

### Main Package

```bash
# Basic installation
pip install devkitx

# With CLI support
pip install devkitx[cli]

# With all features
pip install devkitx[all]
```

### Micro-Packages

```bash
# Zero-dependency async/sync conversion
pip install asyncbridge

# Production HTTP client with secure defaults
pip install httpx-defaults

# Multi-format config loading
pip install confmerge
```

## Features

### 🔒 Security & Compliance
- **Secrets Scanner**: Detect hardcoded API keys, passwords, tokens
- **PII Detector**: Find personally identifiable information in text/files
- **Audit Logger**: NIST 800-53 AU-3 compliant structured logging
- **Input Sanitization**: Prevent XSS, SQL injection, path traversal

### 🌐 Secure HTTP
- **Production Defaults**: Timeouts, connection limits, retry logic
- **Security Warnings**: Alert on insecure HTTP usage
- **Certificate Verification**: Enforced by default

### ⚙️ Configuration
- **Multi-format Support**: JSON, YAML, TOML, .env files
- **Secret Detection**: Warn when secrets found in config files
- **Environment Integration**: Secure environment variable handling

### ⚡ Async/Sync Bridges
- **Zero Dependencies**: Pure stdlib implementation
- **Event Loop Safe**: Proper handling of running loops
- **Thread Pool**: Non-blocking sync function execution

### 🛠️ CLI Tools
- **Security Auditing**: `devkitx audit secrets`, `devkitx audit pii`
- **Dependency Scanning**: `devkitx audit deps`
- **Project Scaffolding**: `devkitx init my-project`
- **Utility Commands**: JSON, string, config operations

## CLI Usage

```bash
# Install with CLI support
pip install devkitx[cli]

# Security auditing
devkitx audit secrets ./src          # Scan for hardcoded secrets
devkitx audit pii ./data             # Scan for PII
devkitx audit deps                   # Check for vulnerable dependencies

# Project management
devkitx init my-secure-project       # Create project with secure defaults

# Utilities
devkitx json flatten config.json    # Flatten nested JSON
devkitx string convert "MyClass" --to snake  # Convert case formats
```

## API Examples

### Audit Logging

```python
from devkitx.compliance import AuditLogger

# Initialize logger for your service
logger = AuditLogger(service="user-api")

# Log authentication events
logger.log_auth(
    action="login",
    user_id="user123",
    outcome="success",
    source_ip="192.168.1.100"
)

# Log data access
logger.log_access(
    action="read",
    resource_type="user_profile", 
    resource_id="profile456",
    user_id="user123"
)

# Log data changes with diff
logger.log_change(
    action="update",
    resource_type="user_profile",
    resource_id="profile456", 
    user_id="user123",
    changes={"email": {"old": "old@example.com", "new": "new@example.com"}}
)
```

### Security Scanning

```python
from devkitx.security import SecretsScanner
from devkitx.compliance import PIIDetector

# Scan for hardcoded secrets
scanner = SecretsScanner()
for secret in scanner.scan_directory("./src"):
    print(f"🚨 {secret.secret_type} found in {secret.file_path}:{secret.line_number}")
    print(f"   Severity: {secret.severity}")
    print(f"   Value: {secret.redacted}")

# Scan for PII
detector = PIIDetector()
text = "Contact John Doe at john.doe@company.com or 555-123-4567"
for match in detector.scan_text(text):
    print(f"PII detected: {match.pii_type} = {match.redacted}")
```

### Secure HTTP Client

```python
from devkitx import SecureClient

# HTTP client with production-ready defaults
with SecureClient() as client:
    # Automatic timeouts, connection limits, security warnings
    response = client.get("https://api.example.com/data")
    data = response.json()

# Async version
from devkitx import SecureAsyncClient

async def fetch_data():
    async with SecureAsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()
```

### Configuration Management

```python
from devkitx import load_config, merge_config

# Load and merge multiple config sources
config = load_config(
    "config.yaml",           # Base configuration
    "config.local.yaml",     # Local overrides
    env_prefix="APP_"        # Environment variables (APP_*)
)

# Access nested configuration
db_host = config.get("database.host", "localhost")
```

### Async/Sync Conversion

```python
from devkitx import async_to_sync, sync_to_async

# Convert async function to sync
async def fetch_user(user_id):
    # ... async database call
    return user

get_user = async_to_sync(fetch_user)
user = get_user(123)  # Works in sync context

# Convert sync function to async (runs in thread pool)
def expensive_calculation(data):
    # ... CPU intensive work
    return result

async_calc = sync_to_async(expensive_calculation)
result = await async_calc(data)  # Non-blocking
```

## Compliance Features

### NIST 800-53 Controls

DevKitX helps implement several NIST 800-53 security controls:

- **AU-2 (Audit Events)**: AuditLogger identifies auditable events
- **AU-3 (Content of Audit Records)**: Structured logging with required fields
- **AU-9 (Protection of Audit Information)**: Tamper-evident audit chains
- **SA-3 (System Development Life Cycle)**: Security scanning in development
- **SC-8 (Transmission Confidentiality)**: Secure HTTP defaults
- **SC-28 (Protection of Information at Rest)**: Secret detection
- **SI-12 (Information Handling)**: PII detection and handling
- **PM-25 (PII Minimization)**: Automated PII discovery

### SOC 2 Type II

- **CC6.1 (Logical Access)**: Secret scanning prevents credential exposure
- **CC6.5 (Data Classification)**: PII detection supports data classification
- **CC6.6 (Data Transmission)**: Secure HTTP client protects data in transit
- **CC7.2 (System Monitoring)**: Audit logging provides security monitoring

### HIPAA Compliance

- **164.312(a)(1) (Access Control)**: Secret scanning prevents unauthorized access
- **164.312(b) (Audit Controls)**: Audit logging tracks access to PHI
- **164.312(e)(1) (Transmission Security)**: Secure HTTP protects PHI in transit
- **164.514 (De-identification)**: PII detection helps identify PHI

## Requirements

- Python 3.10+
- Core dependencies: asyncbridge, httpx-defaults, confmerge

## License

MIT License - Free for commercial use

## Security

For security vulnerabilities, please email security@serityops.com instead of creating public issues.

---

**Built for regulated environments. Trusted by government, healthcare, and financial organizations.**