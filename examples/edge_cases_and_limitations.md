# Edge Cases and Limitations Guide

This document comprehensively covers edge cases, limitations, and gotchas for all utilities in the devtools-py.

## Table of Contents

1. [General Limitations](#general-limitations)
2. [Module-Specific Edge Cases](#module-specific-edge-cases)
3. [Platform-Specific Issues](#platform-specific-issues)
4. [Performance Considerations](#performance-considerations)
5. [Security Considerations](#security-considerations)
6. [Workarounds and Solutions](#workarounds-and-solutions)

## General Limitations

### Python Version Compatibility

```python
# Minimum Python 3.10 required
import sys
if sys.version_info < (3, 10):
    raise RuntimeError("Python 3.10+ required")

# Some features may not work on older versions
try:
    from typing import TypeAlias  # Python 3.10+
except ImportError:
    # Fallback for older versions
    pass
```

### Memory Constraints

```python
# Large data processing limitations
def process_large_dataset(data):
    """
    Limitation: Processing very large datasets (>1GB) may cause memory issues.
    Workaround: Use generators and chunked processing.
    """
    if len(data) > 1_000_000:
        print("Warning: Large dataset detected. Consider chunked processing.")
    
    # Process in chunks
    chunk_size = 10_000
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        yield process_chunk(chunk)
```

### Dependency Requirements

```python
# Optional dependencies may not be available
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("YAML support not available. Install with: pip install pyyaml")

def load_yaml_safe(file_path):
    """Safe YAML loading with fallback."""
    if not YAML_AVAILABLE:
        raise ImportError("YAML support not installed")
    
    # Your YAML loading code here
    pass
```

## Module-Specific Edge Cases

### JSON Utilities

#### Circular References

```python
# Problem: Circular references cause infinite recursion
class Node:
    def __init__(self, value):
        self.value = value
        self.parent = None
        self.children = []

# This creates a circular reference
parent = Node("parent")
child = Node("child")
parent.children.append(child)
child.parent = parent  # Circular reference!

# Solution: Custom serializer
import json

def serialize_node(obj):
    """Custom serializer to handle circular references."""
    if isinstance(obj, Node):
        return {
            "value": obj.value,
            "children": [serialize_node(child) for child in obj.children]
            # Exclude parent to break circular reference
        }
    return str(obj)

# Safe serialization
json_str = json.dumps(parent, default=serialize_node)
```

#### Large Numbers and Precision

```python
# Problem: JSON doesn't preserve Python's arbitrary precision integers
large_number = 12345678901234567890123456789
json_str = json.dumps({"number": large_number})
loaded = json.loads(json_str)

print(f"Original: {large_number}")
print(f"After JSON: {loaded['number']}")
print(f"Equal: {large_number == loaded['number']}")  # May be False!

# Solution: Convert to string for preservation
safe_data = {"number": str(large_number)}
json_str = json.dumps(safe_data)
```

#### Date/Time Handling

```python
from datetime import datetime
import json

# Problem: datetime objects aren't JSON serializable
data = {"timestamp": datetime.now()}

try:
    json.dumps(data)  # Raises TypeError
except TypeError as e:
    print(f"Error: {e}")

# Solution: Custom encoder
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Safe serialization
json_str = json.dumps(data, cls=DateTimeEncoder)
```

### String Utilities

#### Unicode and Encoding Issues

```python
# Problem: Unicode normalization edge cases
test_strings = [
    "café",      # NFC normalization
    "cafe\u0301", # NFD normalization (same visual result)
    "🏳️‍🌈",        # Complex emoji with ZWJ sequences
    "\u200b",    # Zero-width space
    "test\x00null"  # Null bytes
]

from devkitx.string_utils import normalize_whitespace

for s in test_strings:
    try:
        normalized = normalize_whitespace(s)
        print(f"'{repr(s)}' → '{repr(normalized)}'")
    except Exception as e:
        print(f"Error processing '{repr(s)}': {e}")
```

#### Case Conversion Edge Cases

```python
# Problem: Acronyms and special cases
edge_cases = [
    "XMLHttpRequest",  # Should preserve XML, HTTP?
    "iPhone",          # Should preserve i?
    "iOS",             # All caps acronym
    "API_KEY_V2",      # Mixed acronyms and versions
    "HTML5Parser",     # Number in middle
    "UTF8Encoding",    # Number at end
    "a",               # Single character
    "",                # Empty string
    "123",             # Numbers only
    "SCREAMING_SNAKE_CASE"  # All caps
]

from devkitx.string_utils import to_camel_case, to_snake_case

for case in edge_cases:
    try:
        camel = to_camel_case(case)
        snake = to_snake_case(case)
        print(f"'{case}' → camel: '{camel}', snake: '{snake}'")
    except Exception as e:
        print(f"Error processing '{case}': {e}")
```

#### Email Validation Limitations

```python
# Problem: Basic email validation has many edge cases
edge_case_emails = [
    "test@localhost",           # Valid format, may not be deliverable
    "user+tag@domain.com",      # Plus addressing (valid)
    "user.name@domain.com",     # Dots in local part (valid)
    "user@domain.co.uk",        # Multiple TLD levels (valid)
    "user@[192.168.1.1]",      # IP address literal (valid but rare)
    "very.long.email.address@very.long.domain.name.com",  # Long but valid
    "user@domain",              # Missing TLD (invalid but common)
    "user@.domain.com",         # Leading dot in domain (invalid)
    "user@domain..com",         # Double dot in domain (invalid)
    "user name@domain.com",     # Space in local part (invalid)
    "user@domain .com",         # Space in domain (invalid)
]

from devkitx.string_utils import validate_email

print("Email validation edge cases:")
for email in edge_case_emails:
    is_valid = validate_email(email)
    print(f"  '{email}' → {is_valid}")

# Note: For production, use specialized libraries like email-validator
```

### File Utilities

#### Path Length Limitations

```python
import os
from pathlib import Path

# Problem: Different platforms have different path length limits
def test_path_limits():
    """Test platform-specific path length limitations."""
    
    # Windows: 260 characters (can be extended with long path support)
    # Linux: 4096 characters for path, 255 for filename
    # macOS: 1024 characters for path, 255 for filename
    
    long_filename = "a" * 300  # Exceeds most filename limits
    long_path = "/".join(["very_long_directory_name"] * 50)  # Very long path
    
    try:
        # This may fail on some platforms
        test_file = Path(long_path) / long_filename
        print(f"Path length: {len(str(test_file))}")
        
        # Test if we can create the path
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.touch()
        print("✓ Long path created successfully")
        
    except OSError as e:
        print(f"✗ Path creation failed: {e}")
        print(f"  Path length was: {len(str(test_file))}")
```

#### File Locking and Concurrent Access

```python
import fcntl  # Unix only
import msvcrt  # Windows only
import platform

def safe_file_write(file_path, content):
    """Write file with platform-specific locking."""
    
    try:
        with open(file_path, 'w') as f:
            # Platform-specific file locking
            if platform.system() == "Windows":
                try:
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                except ImportError:
                    print("Warning: File locking not available on Windows")
            else:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except ImportError:
                    print("Warning: File locking not available on this platform")
            
            f.write(content)
            
    except (IOError, OSError) as e:
        if e.errno == 11:  # Resource temporarily unavailable
            print("File is locked by another process")
        else:
            raise
```

#### Binary vs Text Mode Issues

```python
# Problem: Mixing binary and text modes
def demonstrate_mode_issues():
    """Show common binary/text mode issues."""
    
    # Binary data
    binary_data = b'\x00\x01\x02\x03\xFF\xFE\xFD'
    
    # Problem: Writing binary data in text mode
    try:
        with open("test.bin", "w") as f:  # Text mode!
            f.write(binary_data)  # TypeError!
    except TypeError as e:
        print(f"Error writing binary data in text mode: {e}")
    
    # Solution: Use correct mode
    with open("test.bin", "wb") as f:  # Binary mode
        f.write(binary_data)
    
    # Problem: Reading binary data in text mode
    try:
        with open("test.bin", "r") as f:  # Text mode!
            content = f.read()  # May raise UnicodeDecodeError
    except UnicodeDecodeError as e:
        print(f"Error reading binary data in text mode: {e}")
    
    # Solution: Use correct mode
    with open("test.bin", "rb") as f:  # Binary mode
        content = f.read()
        print(f"Binary content: {content}")
```

### Configuration Utilities

#### Environment Variable Type Conversion

```python
import os

# Problem: Environment variables are always strings
os.environ["DEBUG"] = "true"
os.environ["PORT"] = "8080"
os.environ["TIMEOUT"] = "30.5"
os.environ["FEATURES"] = "auth,api,ui"

def safe_env_conversion():
    """Safely convert environment variables to appropriate types."""
    
    # Boolean conversion edge cases
    bool_values = {
        "true": True, "false": False,
        "1": True, "0": False,
        "yes": True, "no": False,
        "on": True, "off": False,
        "enabled": True, "disabled": False
    }
    
    def str_to_bool(value):
        """Convert string to boolean with edge case handling."""
        if isinstance(value, bool):
            return value
        
        normalized = str(value).lower().strip()
        if normalized in bool_values:
            return bool_values[normalized]
        
        # Edge case: empty string
        if not normalized:
            return False
        
        # Edge case: numeric strings
        try:
            return bool(int(normalized))
        except ValueError:
            # Default to True for non-empty strings
            return True
    
    # Test conversions
    test_cases = ["true", "false", "1", "0", "", "yes", "no", "maybe", "123"]
    for case in test_cases:
        result = str_to_bool(case)
        print(f"'{case}' → {result}")
```

#### Configuration Merging Edge Cases

```python
# Problem: Deep merging with conflicting types
def demonstrate_merge_conflicts():
    """Show configuration merging edge cases."""
    
    base_config = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "options": ["ssl", "timeout=30"]
        },
        "features": {
            "auth": True,
            "api": {"version": "v1", "rate_limit": 100}
        }
    }
    
    override_config = {
        "database": {
            "port": "3306",  # String vs int conflict
            "options": {"ssl": True, "timeout": 60}  # List vs dict conflict
        },
        "features": {
            "api": "disabled"  # Dict vs string conflict
        }
    }
    
    # This requires careful handling of type conflicts
    def safe_deep_merge(base, override):
        """Merge configurations with type conflict handling."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result:
                base_value = result[key]
                
                # Type conflict detection
                if type(base_value) != type(value):
                    print(f"Type conflict for '{key}': {type(base_value)} vs {type(value)}")
                    # Override wins in conflicts
                    result[key] = value
                elif isinstance(value, dict) and isinstance(base_value, dict):
                    # Recursive merge for dicts
                    result[key] = safe_deep_merge(base_value, value)
                else:
                    # Simple override
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    merged = safe_deep_merge(base_config, override_config)
    return merged
```

### HTTP Utilities

#### Timeout and Connection Issues

```python
import asyncio
import aiohttp
from devkitx.http_utils import HTTPClient

async def demonstrate_http_edge_cases():
    """Show HTTP client edge cases and error handling."""
    
    # Timeout scenarios
    timeout_urls = [
        "http://httpbin.org/delay/10",  # Slow response
        "http://10.255.255.1",         # Non-routable IP (timeout)
        "http://nonexistent.domain.invalid",  # DNS resolution failure
    ]
    
    client = HTTPClient(timeout=5.0)
    
    for url in timeout_urls:
        try:
            response = await client.get(url)
            print(f"✓ {url}: {response.status}")
        except asyncio.TimeoutError:
            print(f"✗ {url}: Timeout")
        except aiohttp.ClientConnectorError:
            print(f"✗ {url}: Connection failed")
        except Exception as e:
            print(f"✗ {url}: {type(e).__name__}: {e}")
```

#### Large Response Handling

```python
async def handle_large_responses():
    """Handle large HTTP responses efficiently."""
    
    # Problem: Large responses can consume too much memory
    large_file_url = "http://httpbin.org/bytes/10000000"  # 10MB
    
    client = HTTPClient()
    
    # Bad: Load entire response into memory
    try:
        response = await client.get(large_file_url)
        content = await response.read()  # Loads all 10MB into memory!
        print(f"Loaded {len(content)} bytes into memory")
    except MemoryError:
        print("Out of memory!")
    
    # Good: Stream large responses
    async with client.session.get(large_file_url) as response:
        chunk_size = 8192
        total_size = 0
        
        async for chunk in response.content.iter_chunked(chunk_size):
            total_size += len(chunk)
            # Process chunk without storing entire response
            
        print(f"Streamed {total_size} bytes efficiently")
```

### CLI Utilities

#### Terminal Compatibility Issues

```python
import sys
import os

def check_terminal_capabilities():
    """Check terminal capabilities and provide fallbacks."""
    
    # Check if stdout is a TTY
    is_tty = sys.stdout.isatty()
    print(f"Is TTY: {is_tty}")
    
    # Check color support
    supports_color = (
        is_tty and 
        (os.getenv("TERM", "").lower() != "dumb") and
        (os.getenv("NO_COLOR") is None)
    )
    print(f"Supports color: {supports_color}")
    
    # Check terminal width
    try:
        width = os.get_terminal_size().columns
        print(f"Terminal width: {width}")
    except OSError:
        width = 80  # Fallback
        print(f"Terminal width unknown, using fallback: {width}")
    
    # Check Unicode support
    try:
        print("Unicode test: ✓ ✗ ⚠ ℹ 🔒")
        unicode_support = True
    except UnicodeEncodeError:
        print("Unicode not supported, using ASCII fallbacks")
        unicode_support = False
    
    return {
        "is_tty": is_tty,
        "supports_color": supports_color,
        "width": width,
        "unicode_support": unicode_support
    }

def safe_colored_output(text, color="white"):
    """Output colored text with fallback for unsupported terminals."""
    
    capabilities = check_terminal_capabilities()
    
    if capabilities["supports_color"]:
        # Use colored output
        from devkitx.cli_utils import colored_text
        return colored_text(text, color)
    else:
        # Fallback to plain text
        return text
```

#### Progress Bar Edge Cases

```python
from devkitx.cli_utils import progress_bar
import sys

def demonstrate_progress_bar_issues():
    """Show progress bar edge cases."""
    
    # Problem: Progress bar in non-TTY environment
    if not sys.stdout.isatty():
        print("Warning: Progress bar may not display correctly in non-TTY environment")
    
    # Problem: Very fast iterations
    fast_items = list(range(1000))
    print("Fast iteration test:")
    
    for item in progress_bar(fast_items, desc="Fast"):
        # Very fast processing - progress bar may flicker
        pass
    
    # Problem: Unknown total length
    def unknown_length_generator():
        """Generator with unknown length."""
        for i in range(100):
            yield i
    
    print("Unknown length test:")
    # This may not show percentage completion
    for item in progress_bar(unknown_length_generator(), desc="Unknown"):
        pass
    
    # Problem: Nested progress bars
    print("Nested progress bars (may conflict):")
    
    outer_items = list(range(3))
    for outer in progress_bar(outer_items, desc="Outer"):
        inner_items = list(range(10))
        for inner in progress_bar(inner_items, desc="Inner"):
            pass  # This may interfere with outer progress bar
```

## Platform-Specific Issues

### Windows-Specific Issues

```python
import platform
import os

if platform.system() == "Windows":
    
    # Reserved filenames
    WINDOWS_RESERVED = {
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    }
    
    def is_windows_reserved_name(filename):
        """Check if filename is reserved on Windows."""
        name = os.path.splitext(filename)[0].upper()
        return name in WINDOWS_RESERVED
    
    # Path separator issues
    def normalize_path_separators(path):
        """Normalize path separators for Windows."""
        return path.replace("/", "\\")
    
    # Case insensitivity
    def windows_case_insensitive_exists(path):
        """Check file existence accounting for case insensitivity."""
        if os.path.exists(path):
            return True
        
        # Check all case variations
        parent = os.path.dirname(path)
        filename = os.path.basename(path)
        
        if os.path.exists(parent):
            for item in os.listdir(parent):
                if item.lower() == filename.lower():
                    return True
        
        return False
```

### Unix/Linux-Specific Issues

```python
import os
import stat

if platform.system() in ["Linux", "Darwin"]:
    
    # File permissions
    def check_file_permissions(file_path):
        """Check detailed file permissions on Unix systems."""
        try:
            file_stat = os.stat(file_path)
            mode = file_stat.st_mode
            
            permissions = {
                "owner_read": bool(mode & stat.S_IRUSR),
                "owner_write": bool(mode & stat.S_IWUSR),
                "owner_execute": bool(mode & stat.S_IXUSR),
                "group_read": bool(mode & stat.S_IRGRP),
                "group_write": bool(mode & stat.S_IWGRP),
                "group_execute": bool(mode & stat.S_IXGRP),
                "other_read": bool(mode & stat.S_IROTH),
                "other_write": bool(mode & stat.S_IWOTH),
                "other_execute": bool(mode & stat.S_IXOTH),
            }
            
            return permissions
            
        except OSError as e:
            print(f"Error checking permissions: {e}")
            return None
    
    # Symbolic links
    def handle_symlinks(path):
        """Handle symbolic links safely."""
        if os.path.islink(path):
            target = os.readlink(path)
            print(f"Symlink: {path} → {target}")
            
            # Check if target exists
            if not os.path.exists(target):
                print(f"Warning: Broken symlink - target doesn't exist")
                return None
            
            return target
        
        return path
```

### macOS-Specific Issues

```python
if platform.system() == "Darwin":
    
    # HFS+ filename normalization
    import unicodedata
    
    def normalize_macos_filename(filename):
        """Normalize filename for macOS HFS+ compatibility."""
        # macOS uses NFD normalization
        normalized = unicodedata.normalize('NFD', filename)
        
        # Remove problematic characters
        problematic = [':', '/', '\x00']
        for char in problematic:
            normalized = normalized.replace(char, '_')
        
        return normalized
    
    # Resource forks and extended attributes
    def handle_macos_metadata(file_path):
        """Handle macOS-specific file metadata."""
        try:
            # Check for resource fork
            resource_fork = file_path + "/..namedfork/rsrc"
            if os.path.exists(resource_fork):
                print(f"File has resource fork: {file_path}")
            
            # Check extended attributes
            try:
                import xattr
                attrs = xattr.listxattr(file_path)
                if attrs:
                    print(f"Extended attributes: {list(attrs)}")
            except ImportError:
                print("xattr module not available")
                
        except OSError:
            pass
```

## Performance Considerations

### Memory Usage Patterns

```python
import sys
import gc

def monitor_memory_usage():
    """Monitor memory usage patterns."""
    
    def get_memory_usage():
        """Get current memory usage."""
        # This is a simplified version - use memory_profiler for detailed analysis
        return sys.getsizeof(gc.get_objects())
    
    # Baseline memory
    baseline = get_memory_usage()
    print(f"Baseline memory: {baseline:,} bytes")
    
    # Test large data structure creation
    large_list = list(range(1_000_000))
    after_creation = get_memory_usage()
    print(f"After creating large list: {after_creation:,} bytes (+{after_creation - baseline:,})")
    
    # Test memory cleanup
    del large_list
    gc.collect()
    after_cleanup = get_memory_usage()
    print(f"After cleanup: {after_cleanup:,} bytes")
```

### CPU-Intensive Operations

```python
import time
import multiprocessing

def cpu_intensive_task(data):
    """Simulate CPU-intensive processing."""
    # Simulate heavy computation
    result = sum(x * x for x in data)
    return result

def demonstrate_performance_patterns():
    """Show different performance patterns."""
    
    large_dataset = list(range(1_000_000))
    
    # Sequential processing
    start_time = time.time()
    sequential_result = cpu_intensive_task(large_dataset)
    sequential_time = time.time() - start_time
    print(f"Sequential processing: {sequential_time:.2f}s")
    
    # Parallel processing
    start_time = time.time()
    
    # Split data into chunks
    num_processes = multiprocessing.cpu_count()
    chunk_size = len(large_dataset) // num_processes
    chunks = [
        large_dataset[i:i + chunk_size] 
        for i in range(0, len(large_dataset), chunk_size)
    ]
    
    with multiprocessing.Pool() as pool:
        parallel_results = pool.map(cpu_intensive_task, chunks)
        parallel_result = sum(parallel_results)
    
    parallel_time = time.time() - start_time
    print(f"Parallel processing: {parallel_time:.2f}s")
    print(f"Speedup: {sequential_time / parallel_time:.2f}x")
    
    # Verify results match
    assert sequential_result == parallel_result
```

### I/O Performance Issues

```python
import asyncio
import aiofiles

async def demonstrate_io_patterns():
    """Show different I/O performance patterns."""
    
    files = [f"test_file_{i}.txt" for i in range(100)]
    content = "Test content " * 1000  # ~13KB per file
    
    # Sequential I/O
    start_time = time.time()
    for filename in files:
        with open(filename, 'w') as f:
            f.write(content)
    sequential_io_time = time.time() - start_time
    print(f"Sequential I/O: {sequential_io_time:.2f}s")
    
    # Async I/O
    start_time = time.time()
    
    async def write_file_async(filename, content):
        async with aiofiles.open(filename, 'w') as f:
            await f.write(content)
    
    tasks = [write_file_async(f, content) for f in files]
    await asyncio.gather(*tasks)
    
    async_io_time = time.time() - start_time
    print(f"Async I/O: {async_io_time:.2f}s")
    print(f"I/O Speedup: {sequential_io_time / async_io_time:.2f}x")
    
    # Cleanup
    for filename in files:
        try:
            os.remove(filename)
        except OSError:
            pass
```

## Security Considerations

### Input Validation Edge Cases

```python
def demonstrate_security_edge_cases():
    """Show security-related edge cases."""
    
    # Path traversal attempts
    malicious_paths = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "/etc/shadow",
        "....//....//....//etc/passwd",  # Double encoding
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",  # URL encoded
        "file:///etc/passwd",  # Protocol handler
        "\\\\server\\share\\file.txt",  # UNC path
    ]
    
    def safe_path_validation(user_path):
        """Validate user-provided paths safely."""
        import os.path
        
        # Normalize path
        normalized = os.path.normpath(user_path)
        
        # Check for path traversal
        if ".." in normalized:
            raise ValueError("Path traversal detected")
        
        # Check for absolute paths
        if os.path.isabs(normalized):
            raise ValueError("Absolute paths not allowed")
        
        # Check for protocol handlers
        if ":" in normalized and not (len(normalized) > 1 and normalized[1] == ":"):
            raise ValueError("Protocol handlers not allowed")
        
        return normalized
    
    for path in malicious_paths:
        try:
            safe_path = safe_path_validation(path)
            print(f"✓ Safe: '{path}' → '{safe_path}'")
        except ValueError as e:
            print(f"✗ Blocked: '{path}' - {e}")
```

### Injection Attack Prevention

```python
def demonstrate_injection_prevention():
    """Show injection attack prevention."""
    
    # SQL injection attempts
    sql_attacks = [
        "admin'; DROP TABLE users; --",
        "' OR '1'='1' --",
        "'; SELECT password FROM users WHERE username='admin'; --",
        "admin'/**/OR/**/1=1--",
        "admin' UNION SELECT password FROM users--"
    ]
    
    def safe_sql_parameter(value):
        """Safely handle SQL parameters."""
        # In real applications, use parameterized queries!
        # This is just for demonstration
        
        if not isinstance(value, str):
            return str(value)
        
        # Remove dangerous characters
        dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
        safe_value = value
        
        for char in dangerous_chars:
            safe_value = safe_value.replace(char, "")
        
        return safe_value
    
    for attack in sql_attacks:
        safe_value = safe_sql_parameter(attack)
        print(f"Attack: '{attack}'")
        print(f"Sanitized: '{safe_value}'")
        print()
```

## Workarounds and Solutions

### Graceful Degradation

```python
def implement_graceful_degradation():
    """Implement graceful degradation for missing features."""
    
    # Feature detection and fallbacks
    features = {
        "color_support": False,
        "unicode_support": False,
        "async_support": False,
        "multiprocessing_support": False
    }
    
    # Test color support
    try:
        import colorama
        features["color_support"] = True
    except ImportError:
        print("Color support not available, using plain text")
    
    # Test Unicode support
    try:
        print("🔒")  # Test Unicode output
        features["unicode_support"] = True
    except UnicodeEncodeError:
        print("Unicode not supported, using ASCII alternatives")
    
    # Test async support
    try:
        import asyncio
        features["async_support"] = True
    except ImportError:
        print("Async support not available, using synchronous alternatives")
    
    # Test multiprocessing
    try:
        import multiprocessing
        if multiprocessing.cpu_count() > 1:
            features["multiprocessing_support"] = True
    except (ImportError, OSError):
        print("Multiprocessing not available, using single-threaded processing")
    
    return features

def adaptive_function_behavior(features):
    """Adapt function behavior based on available features."""
    
    def smart_print(message, color=None, use_unicode=True):
        """Print with adaptive formatting."""
        
        # Unicode fallbacks
        if use_unicode and not features["unicode_support"]:
            unicode_map = {
                "✓": "[OK]",
                "✗": "[ERROR]", 
                "⚠": "[WARNING]",
                "ℹ": "[INFO]",
                "🔒": "[SECURE]"
            }
            
            for unicode_char, ascii_fallback in unicode_map.items():
                message = message.replace(unicode_char, ascii_fallback)
        
        # Color fallbacks
        if color and features["color_support"]:
            # Use colored output
            from devkitx.cli_utils import colored_text
            message = colored_text(message, color)
        elif color:
            # Add text indicators for color
            color_indicators = {
                "red": "[ERROR] ",
                "yellow": "[WARNING] ",
                "green": "[SUCCESS] ",
                "blue": "[INFO] "
            }
            prefix = color_indicators.get(color, "")
            message = prefix + message
        
        print(message)
    
    return smart_print
```

### Error Recovery Strategies

```python
import time
import random

def implement_retry_logic():
    """Implement robust retry logic with backoff."""
    
    def retry_with_backoff(func, max_retries=3, base_delay=1.0, max_delay=60.0):
        """Retry function with exponential backoff."""
        
        for attempt in range(max_retries + 1):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries:
                    # Final attempt failed
                    raise e
                
                # Calculate delay with jitter
                delay = min(base_delay * (2 ** attempt), max_delay)
                jitter = random.uniform(0.1, 0.3) * delay
                total_delay = delay + jitter
                
                print(f"Attempt {attempt + 1} failed: {e}")
                print(f"Retrying in {total_delay:.1f} seconds...")
                time.sleep(total_delay)
        
        raise RuntimeError("All retry attempts failed")
    
    # Example usage
    def unreliable_function():
        """Simulate an unreliable function."""
        if random.random() < 0.7:  # 70% failure rate
            raise ConnectionError("Network error")
        return "Success!"
    
    try:
        result = retry_with_backoff(unreliable_function)
        print(f"Function succeeded: {result}")
    except Exception as e:
        print(f"Function failed permanently: {e}")
```

### Resource Management

```python
import contextlib
import weakref

class ResourceManager:
    """Manage resources with automatic cleanup."""
    
    def __init__(self):
        self._resources = weakref.WeakSet()
    
    def register_resource(self, resource):
        """Register a resource for cleanup."""
        self._resources.add(resource)
    
    def cleanup_all(self):
        """Clean up all registered resources."""
        for resource in list(self._resources):
            try:
                if hasattr(resource, 'close'):
                    resource.close()
                elif hasattr(resource, 'cleanup'):
                    resource.cleanup()
            except Exception as e:
                print(f"Error cleaning up resource: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup_all()

# Usage example
def demonstrate_resource_management():
    """Show proper resource management."""
    
    with ResourceManager() as rm:
        # Open files
        file1 = open("temp1.txt", "w")
        file2 = open("temp2.txt", "w")
        
        rm.register_resource(file1)
        rm.register_resource(file2)
        
        # Do work with files
        file1.write("Content 1")
        file2.write("Content 2")
        
        # Resources will be automatically cleaned up
        # even if an exception occurs
```

This comprehensive guide covers the major edge cases, limitations, and workarounds for the devtools-py. Use it as a reference when implementing robust applications that handle edge cases gracefully.