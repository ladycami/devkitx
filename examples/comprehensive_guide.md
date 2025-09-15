# Dev QoL Toolkit - Comprehensive Usage Guide

This guide provides practical examples and patterns for using the devtools-py effectively in real-world projects.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Common Patterns](#common-patterns)
3. [Real-World Examples](#real-world-examples)
4. [Best Practices](#best-practices)
5. [Performance Tips](#performance-tips)
6. [Error Handling](#error-handling)
7. [Testing Strategies](#testing-strategies)
8. [Troubleshooting](#troubleshooting)

## Quick Start

### Installation

```bash
pip install devtools-py
```

### Basic Usage

```python
# Import utilities you need
from devtools_py import (
    json_utils, file_utils, string_utils, 
    config_utils, cli_utils, http_utils
)

# JSON operations
data = json_utils.load_json("config.json")
json_utils.save_json(data, "backup.json", indent=2)

# File operations
content = file_utils.read_file("input.txt")
file_utils.write_file("output.txt", content.upper())

# String manipulation
snake_case = string_utils.to_snake_case("MyVariableName")
clean_filename = string_utils.sanitize_filename("file/with\\bad:chars.txt")

# Configuration management
config = config_utils.ConfigManager(["config.json", "local.json"])
config.load()
db_host = config.get("database.host", default="localhost")
```

## Common Patterns

### 1. Configuration Management Pattern

```python
from devtools_py.config_utils import ConfigManager
import os

class AppConfig:
    def __init__(self, env="development"):
        self.env = env
        self.config = ConfigManager([
            "config/base.json",
            f"config/{env}.json"
        ])
        self.config.load()
        
        # Merge environment variables
        self.config.merge_env_vars(prefix="MYAPP_")
    
    def get_database_url(self):
        return self.config.get("database.url", 
                             default="sqlite:///app.db")
    
    def is_debug_mode(self):
        return self.config.get("debug", default=False, type_hint=bool)

# Usage
config = AppConfig(os.getenv("ENVIRONMENT", "development"))
```

### 2. CLI Application Pattern

```python
from devtools_py.cli_utils import (
    progress_bar, colored_text, confirm_prompt, print_banner
)
from devtools_py.file_utils import find_files
import sys

def process_files_cli(directory, pattern="*.py"):
    """CLI tool for processing files with progress feedback."""
    
    print_banner(f"Processing {pattern} files", style="fancy")
    
    # Find files
    files = find_files(directory, pattern=pattern, recursive=True)
    
    if not files:
        print(colored_text("No files found!", "yellow"))
        return
    
    print(f"Found {len(files)} files")
    
    if not confirm_prompt("Continue processing?"):
        print("Operation cancelled")
        return
    
    # Process with progress bar
    results = {"processed": 0, "errors": 0}
    
    for file_path in progress_bar(files, desc="Processing"):
        try:
            # Your processing logic here
            process_single_file(file_path)
            results["processed"] += 1
        except Exception as e:
            print(f"\n{colored_text('Error', 'red')}: {file_path} - {e}")
            results["errors"] += 1
    
    # Summary
    success_rate = results["processed"] / len(files) * 100
    print(f"\nProcessed: {results['processed']}")
    print(f"Errors: {results['errors']}")
    print(f"Success rate: {success_rate:.1f}%")
```

### 3. Data Processing Pipeline Pattern

```python
from devtools_py.data_utils import deep_merge, group_by
from devtools_py.string_utils import normalize_whitespace, slugify
from devtools_py.validation_utils import Validator

class DataProcessor:
    def __init__(self):
        self.validator = Validator()
        self.setup_validation_rules()
    
    def setup_validation_rules(self):
        """Setup validation rules for data processing."""
        self.validator.add_rule(
            "email", 
            lambda x: "@" in x and "." in x,
            "Invalid email format"
        )
        self.validator.add_rule(
            "age",
            lambda x: 0 <= x <= 150,
            "Age must be between 0 and 150"
        )
    
    def clean_user_data(self, raw_data):
        """Clean and normalize user data."""
        cleaned = {}
        
        # Normalize text fields
        for field in ["name", "company", "title"]:
            if field in raw_data:
                cleaned[field] = normalize_whitespace(raw_data[field])
        
        # Generate slug from name
        if "name" in cleaned:
            cleaned["slug"] = slugify(cleaned["name"])
        
        # Validate data
        errors = self.validator.validate(cleaned)
        if errors:
            raise ValueError(f"Validation errors: {errors}")
        
        return cleaned
    
    def process_batch(self, data_list):
        """Process a batch of data with error handling."""
        results = {"success": [], "errors": []}
        
        for item in data_list:
            try:
                cleaned = self.clean_user_data(item)
                results["success"].append(cleaned)
            except Exception as e:
                results["errors"].append({"item": item, "error": str(e)})
        
        return results
```

### 4. HTTP Client Pattern

```python
from devtools_py.http_utils import HTTPClient
from devtools_py.security_utils import generate_jwt_token
import asyncio

class APIClient:
    def __init__(self, base_url, api_key=None):
        self.client = HTTPClient(base_url)
        self.api_key = api_key
        
        if api_key:
            self.client.set_header("Authorization", f"Bearer {api_key}")
    
    async def get_user(self, user_id):
        """Get user data with error handling."""
        try:
            response = await self.client.get(f"/users/{user_id}")
            return response.json()
        except Exception as e:
            print(f"Failed to get user {user_id}: {e}")
            return None
    
    async def batch_get_users(self, user_ids):
        """Get multiple users concurrently."""
        tasks = [self.get_user(uid) for uid in user_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        return [r for r in results if not isinstance(r, Exception)]

# Usage
async def main():
    client = APIClient("https://api.example.com", api_key="your-key")
    users = await client.batch_get_users([1, 2, 3, 4, 5])
    print(f"Retrieved {len(users)} users")
```

## Real-World Examples

### 1. Log Analysis Tool

```python
#!/usr/bin/env python3
"""
Log Analysis Tool - Real-world example using multiple utilities
"""

from devtools_py import (
    file_utils, string_utils, data_utils, cli_utils, time_utils
)
from pathlib import Path
import re
from collections import defaultdict

class LogAnalyzer:
    def __init__(self):
        self.log_pattern = re.compile(
            r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) '
            r'(?P<level>\w+) '
            r'(?P<message>.*)'
        )
    
    def analyze_log_file(self, log_file):
        """Analyze a single log file."""
        content = file_utils.read_file(log_file)
        lines = content.splitlines()
        
        stats = {
            "total_lines": len(lines),
            "levels": defaultdict(int),
            "errors": [],
            "warnings": [],
            "timespan": {"start": None, "end": None}
        }
        
        for line in cli_utils.progress_bar(lines, desc=f"Analyzing {log_file.name}"):
            match = self.log_pattern.match(line)
            if match:
                data = match.groupdict()
                level = data["level"]
                timestamp = time_utils.parse_date(data["timestamp"])
                
                stats["levels"][level] += 1
                
                if level == "ERROR":
                    stats["errors"].append({
                        "timestamp": timestamp,
                        "message": data["message"]
                    })
                elif level == "WARNING":
                    stats["warnings"].append({
                        "timestamp": timestamp, 
                        "message": data["message"]
                    })
                
                # Track timespan
                if stats["timespan"]["start"] is None:
                    stats["timespan"]["start"] = timestamp
                stats["timespan"]["end"] = timestamp
        
        return stats
    
    def generate_report(self, stats_list, output_file):
        """Generate analysis report."""
        # Merge statistics
        merged_stats = {
            "total_lines": sum(s["total_lines"] for s in stats_list),
            "levels": defaultdict(int),
            "errors": [],
            "warnings": []
        }
        
        for stats in stats_list:
            for level, count in stats["levels"].items():
                merged_stats["levels"][level] += count
            merged_stats["errors"].extend(stats["errors"])
            merged_stats["warnings"].extend(stats["warnings"])
        
        # Generate report
        report_lines = [
            "# Log Analysis Report",
            f"Generated: {time_utils.format_datetime_now()}",
            "",
            "## Summary",
            f"- Total log lines: {merged_stats['total_lines']:,}",
            f"- Error count: {len(merged_stats['errors'])}",
            f"- Warning count: {len(merged_stats['warnings'])}",
            "",
            "## Log Levels"
        ]
        
        for level, count in sorted(merged_stats["levels"].items()):
            percentage = (count / merged_stats["total_lines"]) * 100
            report_lines.append(f"- {level}: {count:,} ({percentage:.1f}%)")
        
        if merged_stats["errors"]:
            report_lines.extend([
                "",
                "## Recent Errors (Last 10)"
            ])
            
            recent_errors = sorted(
                merged_stats["errors"], 
                key=lambda x: x["timestamp"], 
                reverse=True
            )[:10]
            
            for error in recent_errors:
                timestamp = error["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
                message = string_utils.truncate_text(error["message"], 80)
                report_lines.append(f"- {timestamp}: {message}")
        
        # Save report
        report_content = "\n".join(report_lines)
        file_utils.write_file(output_file, report_content)
        
        return report_content

def main():
    """Main CLI function."""
    cli_utils.print_banner("Log Analysis Tool", style="fancy", color="blue")
    
    # Get log directory
    log_dir = Path(input("Enter log directory path: "))
    
    if not log_dir.exists():
        print(cli_utils.colored_text("Directory not found!", "red"))
        return
    
    # Find log files
    log_files = file_utils.find_files(log_dir, pattern="*.log", recursive=True)
    
    if not log_files:
        print(cli_utils.colored_text("No log files found!", "yellow"))
        return
    
    print(f"Found {len(log_files)} log files")
    
    # Analyze files
    analyzer = LogAnalyzer()
    all_stats = []
    
    for log_file in log_files:
        stats = analyzer.analyze_log_file(log_file)
        all_stats.append(stats)
    
    # Generate report
    output_file = log_dir / "analysis_report.md"
    report = analyzer.generate_report(all_stats, output_file)
    
    print(f"\n{cli_utils.colored_text('✓ Analysis complete!', 'green')}")
    print(f"Report saved to: {output_file}")

if __name__ == "__main__":
    main()
```

### 2. Configuration Migration Tool

```python
#!/usr/bin/env python3
"""
Configuration Migration Tool - Convert between config formats
"""

from devtools_py import (
    config_utils, file_utils, string_utils, cli_utils
)
from pathlib import Path

class ConfigMigrator:
    def __init__(self):
        self.supported_formats = {
            ".json": config_utils.load_json_config,
            ".yaml": config_utils.load_yaml_config,
            ".yml": config_utils.load_yaml_config,
            ".toml": config_utils.load_toml_config
        }
    
    def detect_format(self, file_path):
        """Detect configuration file format."""
        suffix = Path(file_path).suffix.lower()
        return suffix if suffix in self.supported_formats else None
    
    def migrate_config(self, source_file, target_file, transform_keys=True):
        """Migrate configuration from one format to another."""
        
        # Load source configuration
        source_format = self.detect_format(source_file)
        if not source_format:
            raise ValueError(f"Unsupported source format: {source_file}")
        
        loader = self.supported_formats[source_format]
        config_data = loader(source_file)
        
        # Transform keys if requested
        if transform_keys:
            config_data = self.transform_keys(config_data)
        
        # Save in target format
        target_format = self.detect_format(target_file)
        if not target_format:
            raise ValueError(f"Unsupported target format: {target_file}")
        
        self.save_config(config_data, target_file, target_format)
        
        return config_data
    
    def transform_keys(self, data, style="snake_case"):
        """Transform configuration keys to specified style."""
        if isinstance(data, dict):
            transformed = {}
            for key, value in data.items():
                if style == "snake_case":
                    new_key = string_utils.to_snake_case(key)
                elif style == "camelCase":
                    new_key = string_utils.to_camel_case(key)
                elif style == "kebab-case":
                    new_key = string_utils.to_kebab_case(key)
                else:
                    new_key = key
                
                transformed[new_key] = self.transform_keys(value, style)
            return transformed
        elif isinstance(data, list):
            return [self.transform_keys(item, style) for item in data]
        else:
            return data
    
    def save_config(self, data, file_path, format_type):
        """Save configuration in specified format."""
        if format_type == ".json":
            import json
            content = json.dumps(data, indent=2)
        elif format_type in [".yaml", ".yml"]:
            import yaml
            content = yaml.dump(data, default_flow_style=False, indent=2)
        elif format_type == ".toml":
            import toml
            content = toml.dumps(data)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        file_utils.write_file(file_path, content)

def main():
    """Main CLI function."""
    cli_utils.print_banner("Configuration Migration Tool", color="green")
    
    # Get source file
    source_file = Path(input("Source config file: "))
    if not source_file.exists():
        print(cli_utils.colored_text("Source file not found!", "red"))
        return
    
    # Get target file
    target_file = Path(input("Target config file: "))
    
    # Options
    transform_keys = cli_utils.confirm_prompt("Transform keys to snake_case?", default=True)
    
    # Migrate
    migrator = ConfigMigrator()
    
    try:
        with cli_utils.spinner("Migrating configuration..."):
            config_data = migrator.migrate_config(
                source_file, target_file, transform_keys
            )
        
        print(f"{cli_utils.colored_text('✓ Migration complete!', 'green')}")
        print(f"Migrated {len(config_data)} top-level keys")
        print(f"Output saved to: {target_file}")
        
    except Exception as e:
        print(f"{cli_utils.colored_text('✗ Migration failed:', 'red')} {e}")

if __name__ == "__main__":
    main()
```

## Best Practices

### 1. Error Handling

```python
from devtools_py.cli_utils import colored_text
import sys

def handle_errors_gracefully(func):
    """Decorator for graceful error handling in CLI tools."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print(f"\n{colored_text('Operation cancelled by user', 'yellow')}")
            sys.exit(1)
        except FileNotFoundError as e:
            print(f"{colored_text('File not found:', 'red')} {e.filename}")
            sys.exit(1)
        except PermissionError as e:
            print(f"{colored_text('Permission denied:', 'red')} {e}")
            print("Try running with elevated privileges")
            sys.exit(1)
        except Exception as e:
            print(f"{colored_text('Unexpected error:', 'red')} {e}")
            print("Please report this issue")
            sys.exit(1)
    return wrapper

@handle_errors_gracefully
def my_cli_function():
    # Your CLI logic here
    pass
```

### 2. Configuration Management

```python
from devtools_py.config_utils import ConfigManager
from pathlib import Path
import os

class ApplicationConfig:
    """Centralized configuration management."""
    
    def __init__(self, app_name="myapp"):
        self.app_name = app_name
        self.config_dir = Path.home() / f".{app_name}"
        self.config_dir.mkdir(exist_ok=True)
        
        # Configuration file hierarchy
        config_files = [
            Path(__file__).parent / "default_config.json",  # Defaults
            self.config_dir / "config.json",                # User config
            Path.cwd() / f".{app_name}.json"               # Project config
        ]
        
        self.config = ConfigManager([f for f in config_files if f.exists()])
        self.config.load()
        
        # Merge environment variables
        self.config.merge_env_vars(prefix=f"{app_name.upper()}_")
    
    def get(self, key, default=None, type_hint=None):
        """Get configuration value with type conversion."""
        return self.config.get(key, default=default, type_hint=type_hint)
    
    def save_user_config(self):
        """Save current configuration to user config file."""
        user_config_file = self.config_dir / "config.json"
        self.config.save(user_config_file)
```

### 3. Logging Integration

```python
from devtools_py.log_utils import setup_logging
from devtools_py.cli_utils import colored_text
import logging

def setup_application_logging(app_name, debug=False):
    """Setup comprehensive application logging."""
    
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Setup file and console logging
    logger = setup_logging(
        name=app_name,
        level=log_level,
        log_file=f"{app_name}.log",
        console=True
    )
    
    # Add colored console handler for CLI
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    class ColoredFormatter(logging.Formatter):
        """Colored log formatter for console output."""
        
        COLORS = {
            'DEBUG': 'cyan',
            'INFO': 'green', 
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red'
        }
        
        def format(self, record):
            log_message = super().format(record)
            color = self.COLORS.get(record.levelname, 'white')
            return colored_text(log_message, color)
    
    console_handler.setFormatter(
        ColoredFormatter('%(levelname)s: %(message)s')
    )
    
    logger.addHandler(console_handler)
    return logger
```

## Performance Tips

### 1. Memory-Efficient File Processing

```python
from devtools_py.file_utils import read_file
from devtools_py.cli_utils import progress_bar

def process_large_files_efficiently(file_paths, chunk_size=8192):
    """Process large files without loading entirely into memory."""
    
    for file_path in progress_bar(file_paths, desc="Processing files"):
        # Process file in chunks
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                # Process chunk
                process_chunk(chunk)

def process_chunk(chunk):
    """Process a single chunk of data."""
    # Your processing logic here
    pass
```

### 2. Async Operations

```python
import asyncio
from devtools_py.async_utils import gather_with_limit
from devtools_py.http_utils import HTTPClient

async def fetch_data_concurrently(urls, max_concurrent=10):
    """Fetch data from multiple URLs with concurrency limit."""
    
    client = HTTPClient()
    
    async def fetch_single(url):
        try:
            response = await client.get(url)
            return response.json()
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            return None
    
    # Limit concurrent requests
    tasks = [fetch_single(url) for url in urls]
    results = await gather_with_limit(max_concurrent, *tasks)
    
    return [r for r in results if r is not None]
```

### 3. Caching Strategies

```python
from functools import lru_cache
from devtools_py.file_utils import get_file_info
import time

class CachedFileProcessor:
    """File processor with intelligent caching."""
    
    def __init__(self):
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    def process_file(self, file_path):
        """Process file with caching based on modification time."""
        
        file_info = get_file_info(file_path)
        cache_key = (file_path, file_info['modified'])
        
        # Check cache
        if cache_key in self._cache:
            cached_result, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return cached_result
        
        # Process file
        result = self._process_file_impl(file_path)
        
        # Cache result
        self._cache[cache_key] = (result, time.time())
        
        return result
    
    def _process_file_impl(self, file_path):
        """Actual file processing implementation."""
        # Your processing logic here
        pass
```

## Error Handling

### Common Error Patterns

```python
from devtools_py.cli_utils import colored_text
import logging

class ApplicationError(Exception):
    """Base application error."""
    pass

class ConfigurationError(ApplicationError):
    """Configuration-related errors."""
    pass

class ValidationError(ApplicationError):
    """Data validation errors."""
    pass

def handle_application_errors(logger):
    """Context manager for application error handling."""
    
    class ErrorHandler:
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                return False
            
            if isinstance(exc_val, ConfigurationError):
                logger.error(f"Configuration error: {exc_val}")
                print(colored_text(f"Configuration error: {exc_val}", "red"))
            elif isinstance(exc_val, ValidationError):
                logger.error(f"Validation error: {exc_val}")
                print(colored_text(f"Validation error: {exc_val}", "yellow"))
            elif isinstance(exc_val, KeyboardInterrupt):
                logger.info("Operation cancelled by user")
                print(colored_text("\nOperation cancelled", "yellow"))
            else:
                logger.exception("Unexpected error occurred")
                print(colored_text(f"Unexpected error: {exc_val}", "red"))
            
            return True  # Suppress exception
    
    return ErrorHandler()

# Usage
logger = logging.getLogger(__name__)

with handle_application_errors(logger):
    # Your application logic here
    pass
```

## Testing Strategies

### Unit Testing with Utilities

```python
import unittest
from unittest.mock import patch, mock_open
from devtools_py import file_utils, string_utils

class TestStringUtils(unittest.TestCase):
    """Test string utilities."""
    
    def test_case_conversions(self):
        """Test case conversion functions."""
        test_cases = [
            ("hello_world", "helloWorld", "HelloWorld", "hello-world"),
            ("XMLHttpRequest", "xmlHttpRequest", "XmlHttpRequest", "xml-http-request")
        ]
        
        for snake, camel, pascal, kebab in test_cases:
            with self.subTest(input=snake):
                self.assertEqual(string_utils.to_camel_case(snake), camel)
                self.assertEqual(string_utils.to_pascal_case(snake), pascal)
                self.assertEqual(string_utils.to_kebab_case(snake), kebab)
    
    def test_validation_functions(self):
        """Test validation functions."""
        # Email validation
        valid_emails = ["test@example.com", "user+tag@domain.co.uk"]
        invalid_emails = ["invalid.email", "@missing.com", ""]
        
        for email in valid_emails:
            self.assertTrue(string_utils.validate_email(email))
        
        for email in invalid_emails:
            self.assertFalse(string_utils.validate_email(email))

class TestFileUtils(unittest.TestCase):
    """Test file utilities."""
    
    @patch("builtins.open", new_callable=mock_open, read_data="test content")
    def test_read_file(self, mock_file):
        """Test file reading."""
        content = file_utils.read_file("test.txt")
        self.assertEqual(content, "test content")
        mock_file.assert_called_once_with("test.txt", "r", encoding="utf-8")
    
    @patch("builtins.open", new_callable=mock_open)
    def test_write_file(self, mock_file):
        """Test file writing."""
        file_utils.write_file("test.txt", "new content")
        mock_file.assert_called_once_with("test.txt", "w", encoding="utf-8")
        mock_file().write.assert_called_once_with("new content")

if __name__ == "__main__":
    unittest.main()
```

### Integration Testing

```python
import tempfile
import unittest
from pathlib import Path
from devtools_py import config_utils, file_utils

class TestConfigIntegration(unittest.TestCase):
    """Integration tests for configuration management."""
    
    def setUp(self):
        """Setup test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Cleanup test environment."""
        self.temp_dir.cleanup()
    
    def test_config_loading_and_merging(self):
        """Test complete configuration workflow."""
        
        # Create base config
        base_config = {"app": {"name": "test"}, "debug": False}
        base_file = self.temp_path / "base.json"
        file_utils.write_file(base_file, json.dumps(base_config))
        
        # Create override config
        override_config = {"debug": True, "new_setting": "value"}
        override_file = self.temp_path / "override.json"
        file_utils.write_file(override_file, json.dumps(override_config))
        
        # Test ConfigManager
        config_manager = config_utils.ConfigManager([base_file, override_file])
        config_manager.load()
        
        # Verify merging
        self.assertEqual(config_manager.get("app.name"), "test")
        self.assertTrue(config_manager.get("debug"))
        self.assertEqual(config_manager.get("new_setting"), "value")
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Import Errors

```python
# Problem: Module not found
try:
    from devtools_py import string_utils
except ImportError as e:
    print("Please install devtools-py: pip install devtools-py")
    sys.exit(1)
```

#### 2. File Permission Issues

```python
from devtools_py.file_utils import write_file
import os

def safe_write_file(file_path, content):
    """Write file with permission handling."""
    try:
        write_file(file_path, content)
    except PermissionError:
        # Try alternative location
        alt_path = Path.home() / "tmp" / Path(file_path).name
        alt_path.parent.mkdir(exist_ok=True)
        write_file(alt_path, content)
        print(f"File written to alternative location: {alt_path}")
```

#### 3. Configuration Loading Issues

```python
from devtools_py.config_utils import ConfigManager

def load_config_safely(config_files):
    """Load configuration with fallback handling."""
    
    # Filter existing files
    existing_files = [f for f in config_files if Path(f).exists()]
    
    if not existing_files:
        print("No configuration files found, using defaults")
        return {"debug": False, "log_level": "INFO"}
    
    try:
        config_manager = ConfigManager(existing_files)
        config_manager.load()
        return config_manager.config
    except Exception as e:
        print(f"Failed to load configuration: {e}")
        print("Using default configuration")
        return {"debug": False, "log_level": "INFO"}
```

#### 4. Memory Issues with Large Files

```python
from devtools_py.file_utils import read_file

def read_large_file_safely(file_path, max_size_mb=100):
    """Read file with size checking."""
    
    file_size = Path(file_path).stat().st_size
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file_size > max_size_bytes:
        print(f"File too large ({file_size / 1024 / 1024:.1f}MB), processing in chunks")
        return read_file_in_chunks(file_path)
    else:
        return read_file(file_path)

def read_file_in_chunks(file_path, chunk_size=8192):
    """Read file in chunks for memory efficiency."""
    chunks = []
    with open(file_path, 'r') as f:
        while chunk := f.read(chunk_size):
            chunks.append(chunk)
    return ''.join(chunks)
```

### Debug Mode

```python
import logging
from devtools_py.log_utils import setup_logging

def enable_debug_mode():
    """Enable comprehensive debug logging."""
    
    # Setup debug logging
    logger = setup_logging(
        name="debug",
        level=logging.DEBUG,
        log_file="debug.log",
        console=True
    )
    
    # Log all function calls
    import functools
    
    def debug_calls(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} returned: {result}")
                return result
            except Exception as e:
                logger.debug(f"{func.__name__} raised: {e}")
                raise
        return wrapper
    
    return debug_calls

# Usage
if os.getenv("DEBUG"):
    debug_decorator = enable_debug_mode()
    
    # Apply to functions you want to debug
    @debug_decorator
    def my_function():
        pass
```

This comprehensive guide provides practical patterns and examples for using the devtools-py effectively in real-world applications. Each section includes working code examples that demonstrate best practices and common use cases.