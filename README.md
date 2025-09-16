# DevKitX

**Comprehensive quality-of-life utilities for Python developers**

A modern, type-safe toolkit providing essential utilities for common development tasks including JSON manipulation, file operations, logging, CLI utilities, HTTP clients, data processing, string manipulation, configuration management, system operations, async utilities, development tools, security functions, time utilities, and validation.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Typed](https://img.shields.io/badge/typed-yes-brightgreen.svg)](https://mypy-lang.org/)

## Features

- 🚀 **Modern Python**: Built for Python 3.10+ with full type annotations
- 📦 **Comprehensive**: 14+ utility modules covering common development needs
- ⚡ **Async Support**: Async-compatible utilities and bridges between sync/async code
- 🔒 **Security**: Built-in security utilities for hashing, JWT tokens, and input sanitization
- 🛠️ **Developer Tools**: Profiling, debugging, and testing utilities
- 🌐 **HTTP Client**: Robust HTTP utilities with retry logic and async support
- 📝 **Configuration**: Multi-format config management (JSON, YAML, TOML, .env)
- 🎨 **CLI Tools**: Rich terminal output with colors, progress bars, and interactive prompts
- 🔧 **System Utils**: Cross-platform system information and process management
- ✅ **Validation**: Comprehensive input validation and schema checking

## Installation

```bash
pip install devkitx
```

## Quick Start

```python
from devtools_py import json_utils, string_utils, http_utils, config_utils

# JSON operations with enhanced features
data = json_utils.load_json("config.json")
flat_data = json_utils.flatten_json(data)
pretty_output = json_utils.pretty_json(data, color=True)

# String manipulation and validation
snake_case = string_utils.to_snake_case("CamelCaseString")
is_valid_email = string_utils.validate_email("user@example.com")
clean_filename = string_utils.sanitize_filename("file<name>.txt")

# HTTP requests with automatic retries
response = http_utils.api_request("GET", "https://api.example.com/data")
client = http_utils.BaseAPIClient("https://api.example.com")
users = client.get("/users")

# Configuration management
config = config_utils.ConfigManager(["config.json", "config.yaml"])
config.load()
database_url = config.get("database.url", "sqlite:///default.db")
```

## Module Overview

### Core Utilities

#### JSON Utils (`json_utils`)
Enhanced JSON operations with pretty printing and flattening:

```python
from devtools_py import json_utils

# Load and save JSON with automatic formatting
data = json_utils.load_json("config.json")
json_utils.save_json(data, "backup.json", pretty=True)

# Flatten nested JSON for easier processing
nested = {"user": {"profile": {"name": "John", "age": 30}}}
flat = json_utils.flatten_json(nested)
# Result: {"user.profile.name": "John", "user.profile.age": 30}

# Pretty print with optional syntax highlighting
print(json_utils.pretty_json(data, color=True))
```

#### File Utils (`file_utils`)
Cross-platform file operations with safety features:

```python
from devtools_py import file_utils

# Find files with glob patterns or exact names
python_files = file_utils.find_file("*.py", "src")
config_file = file_utils.find_file("config.json", ".")

# Safe file operations
file_utils.ensure_dir("output/data")
file_utils.atomic_write("important.json", '{"key": "value"}')
file_utils.copy_file("source.txt", "backup.txt", overwrite=False)

# Check permissions
if file_utils.is_writable("output.txt"):
    # Safe to write
    pass
```

#### String Utils (`string_utils`)
Comprehensive string manipulation and validation:

```python
from devtools_py import string_utils

# Case conversions
string_utils.to_snake_case("CamelCase")      # "camel_case"
string_utils.to_camel_case("snake_case")     # "snakeCase"
string_utils.to_pascal_case("kebab-case")    # "KebabCase"
string_utils.to_kebab_case("PascalCase")     # "pascal-case"

# Validation
string_utils.validate_email("user@example.com")  # True
string_utils.validate_url("https://example.com") # True

# Text processing
string_utils.sanitize_filename("file<name>.txt")  # "file_name_.txt"
string_utils.truncate_text("Long text here", 10)  # "Long te..."
urls = string_utils.extract_urls("Visit https://example.com for info")
```

### Advanced Utilities

#### HTTP Utils (`http_utils`)
Robust HTTP client with retry logic and async support:

```python
from devtools_py import http_utils
import asyncio

# Synchronous requests with automatic retries
response = http_utils.api_request(
    "POST", 
    "https://api.example.com/users",
    json_body={"name": "John", "email": "john@example.com"},
    headers={"Authorization": "Bearer token"},
    retries=3
)

# API client for consistent base URL and headers
client = http_utils.BaseAPIClient(
    "https://api.example.com",
    headers={"Authorization": "Bearer token"}
)
users = client.get("/users")
new_user = client.post("/users", json_body={"name": "Jane"})

# Async support
async def fetch_data():
    async_client = http_utils.AsyncAPIClient("https://api.example.com")
    return await async_client.get("/data")

# Batch requests with concurrency control
requests = [
    ("GET", "https://api.example.com/users/1", {}),
    ("GET", "https://api.example.com/users/2", {}),
]
responses = await http_utils.async_batch_requests(requests, concurrency_limit=5)
```

#### Config Utils (`config_utils`)
Multi-format configuration management:

```python
from devtools_py import config_utils

# Load from multiple sources with precedence
config = config_utils.ConfigManager([
    "config.json",
    "config.yaml", 
    "local.env"
])
config.load()

# Type-safe configuration access
database_url = config.get("database.url", "sqlite:///default.db", str)
debug_mode = config.get("debug", False, bool)
max_connections = config.get("database.max_connections", 10, int)

# Environment variable integration
config.merge_env_vars("MYAPP_")  # Loads MYAPP_* env vars

# Save configuration
config.set("new.setting", "value")
config.save("updated_config.json")
```

#### Security Utils (`security_utils`)
Security and cryptographic utilities:

```python
from devtools_py import security_utils

# Password hashing with bcrypt
hashed = security_utils.hash_password("my_secure_password")
is_valid = security_utils.verify_password("my_secure_password", hashed)

# Secure key generation
secret_key = security_utils.generate_secret_key(32)
uuid = security_utils.generate_uuid()

# Data hashing
file_hash = security_utils.hash_data(b"file content", "sha256")

# JWT tokens
payload = {"user_id": 123, "role": "admin"}
token = security_utils.generate_jwt_token(payload, secret_key, expires_in=3600)
decoded = security_utils.verify_jwt_token(token, secret_key)

# Input sanitization
clean_input = security_utils.sanitize_input("<script>alert('xss')</script>")
```

#### Async Utils (`async_utils`)
Bridge between sync and async code:

```python
from devtools_py import async_utils
import asyncio

# Convert sync functions to async
def slow_sync_function(x):
    time.sleep(1)
    return x * 2

async_func = async_utils.sync_to_async(slow_sync_function)
result = await async_func(5)  # Non-blocking

# Convert async functions to sync
async def async_function(x):
    await asyncio.sleep(0.1)
    return x * 2

sync_func = async_utils.async_to_sync(async_function)
result = sync_func(5)  # Blocks until complete

# Concurrency control
tasks = [fetch_data(url) for url in urls]
results = await async_utils.gather_with_limit(5, *tasks)  # Max 5 concurrent

# Retry with exponential backoff
result = await async_utils.retry_async(
    unreliable_api_call,
    retries=3,
    delay=1.0,
    exceptions=(ConnectionError,)
)

# Async file operations
async_fm = async_utils.AsyncFileManager()
content = await async_fm.read_text("large_file.txt")
await async_fm.write_text("output.txt", "Hello, World!")
```

#### Development Utils (`dev_utils`)
Debugging and development tools:

```python
from devtools_py import dev_utils

# Function timing and profiling
@dev_utils.time_function
@dev_utils.profile_memory
def expensive_operation():
    return [i**2 for i in range(10000)]

# Pretty printing complex objects
complex_data = {"users": [{"id": 1, "nested": {"deep": "value"}}]}
print(dev_utils.pretty_print_object(complex_data, max_depth=3))

# Test data generation
schema = {"name": str, "age": int, "active": bool}
test_data = dev_utils.generate_test_data(schema, count=10)

# Function benchmarking
def method1(): return sum(range(1000))
def method2(): return sum([i for i in range(1000)])

results = dev_utils.benchmark_functions(method1, method2, iterations=1000)
print(f"method1: {results['method1']:.4f}s avg")

# Mock HTTP server for testing
responses = {
    "/api/users": {"users": [{"id": 1, "name": "John"}]},
    "/api/status": {"status": "ok"}
}
server = dev_utils.MockHTTPServer(responses)
url = server.start()
# Make requests to url + "/api/users"
server.stop()
```

### System and Validation

#### System Utils (`system_utils`)
Cross-platform system operations:

```python
from devtools_py import system_utils

# System information
sys_info = system_utils.get_system_info()
python_info = system_utils.get_python_info()

# Command execution with timeout
result = system_utils.run_command(
    ["python", "--version"], 
    timeout=5.0,
    cwd="/path/to/directory"
)

# Async command execution
result = await system_utils.run_command_async(["ls", "-la"])

# Utility functions
executable_path = system_utils.find_executable("python")
env_vars = system_utils.get_env_vars("PYTHON_")
is_root = system_utils.is_admin()
free_port = system_utils.get_free_port(8000)
```

#### Validation Utils (`validation_utils`)
Comprehensive input validation:

```python
from devtools_py import validation_utils

# Schema validation
schema = {"name": str, "age": int, "active": bool}
data = {"name": "John", "age": 30, "active": True}
errors = validation_utils.validate_schema(data, schema)

# Range and length validation
validation_utils.validate_range(25, 18, 65)        # True
validation_utils.validate_length("hello", 3, 10)   # True
validation_utils.validate_regex("test123", r"^\w+\d+$")  # True

# JSON schema validation
json_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "age": {"type": "integer", "minimum": 0}
    },
    "required": ["name"]
}
errors = validation_utils.validate_json_schema(data, json_schema)

# Rule-based validator
validator = validation_utils.Validator()
validator.add_rule("email", lambda x: "@" in str(x), "Invalid email")
validator.add_rule("age", lambda x: isinstance(x, int) and x >= 0, "Invalid age")
errors = validator.validate({"email": "test@example.com", "age": 25})
```

#### Time Utils (`time_utils`)
Date and time utilities:

```python
from devtools_py import time_utils
from datetime import datetime

# Flexible date parsing
date = time_utils.parse_date("2024-01-15")
date = time_utils.parse_date("15/01/2024", ["%d/%m/%Y"])

# Duration formatting
duration = time_utils.format_duration(3661)  # "1h 1m 1.0s"

# Business day calculations
is_weekday = time_utils.is_business_day(datetime(2024, 1, 15))
next_workday = time_utils.next_business_day(datetime(2024, 1, 12))

# Cron scheduling
next_run = time_utils.cron_next_run("0 9 * * 1-5")  # 9 AM weekdays

# Timer utility
timer = time_utils.Timer()
timer.start()
# ... do work ...
elapsed = timer.stop()

# Or as context manager
with time_utils.Timer() as timer:
    # ... do work ...
    pass
print(f"Elapsed: {timer.elapsed():.2f}s")
```

### CLI and Logging

#### CLI Utils (`cli_utils`)
Rich terminal interfaces:

```python
from devtools_py import cli_utils

# Interactive prompts
password = cli_utils.password_prompt("Enter password:", confirm=True)
selected = cli_utils.multi_select(["option1", "option2", "option3"])

# Progress indicators
for item in cli_utils.progress_bar(range(100), "Processing"):
    # Do work with item
    pass

with cli_utils.spinner("Loading data..."):
    # Long running operation
    time.sleep(2)

# Colored output and tables
print(cli_utils.colored_text("Success!", "green", bold=True))
print(cli_utils.colored_text("Warning", "yellow"))

data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
table = cli_utils.table_format(data, headers=["Name", "Age"])
print(table)
```

#### Log Utils (`log_utils`)
Enhanced logging setup:

```python
from devtools_py import log_utils
import logging

# Quick logger setup
logger = log_utils.setup_logging("INFO", to_file="app.log")
logger = log_utils.setup_logging("DEBUG", json=True, use_loguru=True)

# Time logging context manager
with log_utils.log_time("database_query"):
    # Database operation
    pass
# Logs: "database_query took 123.45 ms"

# Function call logging
@log_utils.log_calls
def process_data(data):
    return {"processed": len(data)}

result = process_data([1, 2, 3])
# Logs function calls and returns at DEBUG level
```

## CLI Interface

The toolkit also provides a command-line interface for common operations:

```bash
# String manipulation
devkitx string convert --to snake "CamelCase"
devkitx string validate --email "user@example.com"

# Configuration management
devkitx config merge config1.json config2.yaml

# Security utilities
devkitx security hash --algorithm sha256 "my-data"
devkitx security generate --type uuid

# System information
devkitx system info
devkitx system find-executable python

# Time utilities
devkitx time parse "2024-01-15 14:30:00"
devkitx time format-duration 3661
```

## Requirements

- Python 3.10 or higher
- Dependencies: `httpx`, `click`, `rich`, `bcrypt`, `PyJWT`

## Development

```bash
# Clone the repository
git clone https://github.com/ladycami/devkitx.git
cd devkitx

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src/
black --check src/
mypy src/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0 (Upcoming)
- Initial release with comprehensive utility modules
- Full type annotations and Python 3.10+ support
- Async utilities and HTTP client with retry logic
- Security utilities with JWT and bcrypt support
- Rich CLI interface with progress bars and colored output
- Multi-format configuration management
- Development and debugging tools
- Comprehensive test suite with 90%+ coverage