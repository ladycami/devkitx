# Dev QoL Toolkit - Usage Examples

This directory contains practical usage examples for all utility modules in the dev-qol-toolkit package. Each example demonstrates real-world scenarios and includes edge cases and limitations.

## Quick Start

```python
# Install the package
pip install dev-qol-toolkit

# Import utilities
from dev_qol_toolkit import json_utils, file_utils, string_utils
```

## Examples by Category

### Core Utilities
- [JSON Utilities](json_examples.py) - JSON manipulation and validation
- [File Utilities](file_examples.py) - File operations and management
- [Data Utilities](data_examples.py) - Data processing and manipulation

### Text and Configuration
- [String Utilities](string_examples.py) - String manipulation and validation
- [Configuration Management](config_examples.py) - Configuration loading and management

### System and CLI
- [System Utilities](system_examples.py) - System information and process management
- [CLI Utilities](cli_examples.py) - Command-line interface helpers

### Advanced Features
- [HTTP Utilities](http_examples.py) - HTTP client operations
- [Async Utilities](async_examples.py) - Asynchronous programming helpers
- [Security Utilities](security_examples.py) - Security and hashing functions
- [Time Utilities](time_examples.py) - Date and time manipulation
- [Validation Utilities](validation_examples.py) - Input validation and schema checking
- [Development Utilities](dev_examples.py) - Debugging and profiling tools
- [Logging Utilities](log_examples.py) - Logging setup and management

## Common Patterns

### Error Handling
All utilities follow consistent error handling patterns:

```python
try:
    result = some_utility_function(data)
except ValidationError as e:
    print(f"Validation failed: {e}")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

### Type Safety
All functions include proper type hints:

```python
from typing import Dict, List, Optional
from dev_qol_toolkit.string_utils import to_pascal_case

# Type-safe usage
result: str = to_pascal_case("hello_world")
```

### Async Support
Many utilities have async variants:

```python
import asyncio
from dev_qol_toolkit.async_utils import AsyncFileManager

async def main():
    async_file = AsyncFileManager()
    content = await async_file.read_text("example.txt")
    
asyncio.run(main())
```

## Edge Cases and Limitations

Each example file documents:
- Common edge cases and how they're handled
- Performance considerations
- Platform-specific limitations
- Dependency requirements

## Contributing Examples

When adding new examples:
1. Include practical, real-world scenarios
2. Document edge cases and limitations
3. Provide both simple and advanced usage
4. Include error handling examples
5. Add performance notes where relevant