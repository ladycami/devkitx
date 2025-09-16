# DevKitX Examples

This directory contains comprehensive examples demonstrating the functionality of the `devkitx` package installed from PyPI.

## 📁 Example Files

### 1. `comprehensive_demo.py`
**Complete functionality showcase**
- Demonstrates all 16 utility modules
- Shows 200+ functions in action
- Tests async operations, CLI utilities, security features, and more
- Perfect for understanding the full scope of the package

**Run it:**
```bash
python examples/comprehensive_demo.py
```

### 2. `cli_demo.py`
**Command-line interface demonstration**
- Tests all CLI commands programmatically
- Shows 50+ CLI commands across 8 categories
- Validates command outputs and help systems
- Great for understanding the CLI capabilities

**Run it:**
```bash
python examples/cli_demo.py
```

### 3. `real_world_example.py`
**Practical development scenarios**
- User management system with authentication
- Configuration management across environments
- Security best practices implementation
- Data validation and processing workflows
- Shows how to combine multiple utilities for real applications

**Run it:**
```bash
python examples/real_world_example.py
```

## 🚀 Quick Start

1. **Install DevKitX from PyPI:**
   ```bash
   pip install devkitx
   ```

2. **Run all examples:**
   ```bash
   # Comprehensive functionality demo
   python examples/comprehensive_demo.py
   
   # CLI commands demo
   python examples/cli_demo.py
   
   # Real-world usage scenarios
   python examples/real_world_example.py
   ```

## 📋 What You'll See

### String Utilities
```python
from devtools_py import string_utils

# Case conversions
string_utils.to_snake_case("MyVariableName")  # "my_variable_name"
string_utils.to_pascal_case("my_variable")    # "MyVariable"

# Validation
string_utils.validate_email("user@example.com")  # True
string_utils.validate_url("https://github.com")  # True
```

### Security Features
```python
from devtools_py import security_utils

# Password hashing
hashed = security_utils.hash_password("MyPassword123!")
verified = security_utils.verify_password("MyPassword123!", hashed)

# JWT tokens
token = security_utils.generate_jwt_token({"user": "alice"}, "secret")
payload = security_utils.verify_jwt_token(token, "secret")
```

### CLI Commands
```bash
# String operations
devkitx string convert --to snake "MyVariableName"

# Security operations
devkitx security hash "my-data"
devkitx security generate-secret --length 32

# System information
devkitx system info

# Time utilities
devkitx time parse "2024-01-15 14:30:00"
```

### Configuration Management
```python
from devtools_py.config_utils import ConfigManager

config = ConfigManager(["config.json", "config.yaml"])
config.load()

# Type-safe getters
port = config.get("server.port", default=8000, type_hint=int)
debug = config.get("debug", default=False, type_hint=bool)
```

## 🎯 Key Features Demonstrated

- **16 Utility Modules**: String, JSON, file, data, config, system, security, time, validation, CLI, HTTP, async, dev utilities
- **200+ Functions**: Comprehensive toolkit for Python development
- **50+ CLI Commands**: Full command-line interface
- **Type Safety**: Complete type annotations throughout
- **Async Support**: Native async/await compatibility
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Security Best Practices**: Secure password hashing, JWT tokens, input sanitization
- **Performance Optimized**: Efficient implementations with benchmarking tools

## 📊 Example Output

When you run the examples, you'll see detailed output showing:
- ✅ Successful operations with results
- 📊 Performance metrics and statistics
- 🔍 Validation results and error handling
- 🎨 Formatted tables and colored output
- 📈 Progress bars and timing information

## 🔧 Requirements

- Python 3.10+
- devkitx (installed from PyPI)
- Internet connection (for HTTP utilities demo)

## 📚 Learn More

- **Package Documentation**: See the main README.md
- **API Reference**: Check function docstrings and type hints
- **PyPI Page**: https://pypi.org/project/devtools-py/
- **Source Code**: Available in the package installation

---

These examples demonstrate how `devkitx` can significantly improve your Python development workflow by providing battle-tested utilities for common tasks. Whether you're building web applications, CLI tools, or data processing pipelines, DevKitX has the utilities you need.