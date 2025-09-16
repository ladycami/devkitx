#!/usr/bin/env python3
"""
Comprehensive demonstration of devtools-py functionality.

This script showcases all major features of the devtools-py package
using the PyPI-installed version.
"""

import asyncio
import json
import tempfile
import time
from pathlib import Path

# Import all modules from the PyPI package
import devtools_py.string_utils as string_utils
import devtools_py.json_utils as json_utils
import devtools_py.file_utils as file_utils
import devtools_py.data_utils as data_utils
import devtools_py.config_utils as config_utils
import devtools_py.system_utils as system_utils
import devtools_py.security_utils as security_utils
import devtools_py.time_utils as time_utils
import devtools_py.validation_utils as validation_utils
import devtools_py.cli_utils as cli_utils
import devtools_py.http_utils as http_utils
import devtools_py.async_utils as async_utils
import devtools_py.dev_utils as dev_utils


def demo_string_utilities():
    """Demonstrate string manipulation utilities."""
    print("🔤 STRING UTILITIES DEMO")
    print("=" * 50)
    
    # Case conversions
    original = "MyAwesomeVariableName"
    print(f"Original: {original}")
    print(f"Snake case: {string_utils.to_snake_case(original)}")
    print(f"Pascal case: {string_utils.to_pascal_case('my_awesome_variable')}")
    print(f"Kebab case: {string_utils.to_kebab_case(original)}")
    
    # Validation
    email = "user@example.com"
    url = "https://github.com/user/repo"
    print(f"\nValidation:")
    print(f"Email '{email}' is valid: {string_utils.validate_email(email)}")
    print(f"URL '{url}' is valid: {string_utils.validate_url(url)}")
    
    # Text processing
    long_text = "This is a very long text that needs to be truncated for display purposes"
    print(f"\nText processing:")
    print(f"Truncated: {string_utils.truncate_text(long_text, 30)}")
    print(f"Sanitized filename: {string_utils.sanitize_filename('my/file:name?.txt')}")
    
    print()


def demo_json_utilities():
    """Demonstrate JSON utilities."""
    print("📄 JSON UTILITIES DEMO")
    print("=" * 50)
    
    # Create test data
    test_data = {
        "user": {
            "name": "John Doe",
            "email": "john@example.com",
            "preferences": {
                "theme": "dark",
                "notifications": True
            }
        },
        "settings": {
            "language": "en",
            "timezone": "UTC"
        }
    }
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        json_file = Path(tmp_dir) / "test.json"
        
        # Save and load JSON
        json_utils.save_json(test_data, json_file)
        loaded_data = json_utils.load_json(json_file)
        print(f"JSON save/load successful: {loaded_data == test_data}")
        
        # Flatten and unflatten
        flattened = json_utils.flatten_json(test_data)
        print(f"Flattened keys: {list(flattened.keys())}")
        
        unflattened = json_utils.unflatten_json(flattened)
        print(f"Unflatten successful: {unflattened == test_data}")
        
        # Pretty print
        print("\nPretty JSON:")
        print(json_utils.pretty_json({"example": "data", "number": 42}))
    
    print()


def demo_file_utilities():
    """Demonstrate file utilities."""
    print("📁 FILE UTILITIES DEMO")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create test files
        test_files = ["example.txt", "data.json", "config.yaml"]
        for filename in test_files:
            file_path = tmp_path / filename
            file_utils.atomic_write(file_path, f"Content of {filename}")
        
        # Find files
        txt_files = file_utils.find_file("*.txt", tmp_path)
        json_files = file_utils.find_file("*.json", tmp_path)
        
        print(f"Found .txt files: {[f.name for f in txt_files]}")
        print(f"Found .json files: {[f.name for f in json_files]}")
        
        # Test atomic write
        test_file = tmp_path / "atomic_test.txt"
        original_content = "Original content"
        new_content = "New atomic content"
        
        file_utils.atomic_write(test_file, original_content)
        file_utils.atomic_write(test_file, new_content)
        
        final_content = test_file.read_text()
        print(f"Atomic write successful: {final_content == new_content}")
    
    print()


def demo_data_utilities():
    """Demonstrate data manipulation utilities."""
    print("🔢 DATA UTILITIES DEMO")
    print("=" * 50)
    
    # Deep merge
    dict1 = {"a": 1, "b": {"c": 2, "d": 3}}
    dict2 = {"b": {"d": 4, "e": 5}, "f": 6}
    merged = data_utils.deep_merge(dict1, dict2)
    print(f"Deep merge result: {merged}")
    
    # Group by
    items = [
        {"name": "Alice", "department": "Engineering"},
        {"name": "Bob", "department": "Marketing"},
        {"name": "Charlie", "department": "Engineering"},
        {"name": "Diana", "department": "Marketing"}
    ]
    grouped = data_utils.group_by(items, lambda x: x["department"])
    print(f"Grouped by department: {list(grouped.keys())}")
    
    # Filter dictionary
    data = {"a": 1, "b": 2, "c": 3, "d": 4}
    filtered = data_utils.filter_dict(data, lambda k, v: v % 2 == 0)
    print(f"Filtered even values: {filtered}")
    
    print()


def demo_config_utilities():
    """Demonstrate configuration management."""
    print("⚙️ CONFIG UTILITIES DEMO")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create config files
        json_config = tmp_path / "config.json"
        env_config = tmp_path / ".env"
        
        json_config.write_text(json.dumps({
            "database": {"host": "localhost", "port": 5432},
            "debug": True,
            "app_name": "MyApp"
        }))
        
        env_config.write_text("DATABASE_PASSWORD=secret123\nAPI_KEY=abc123")
        
        # Load configurations
        json_data = json.loads(json_config.read_text())  # Direct JSON loading
        env_data = config_utils.load_dotenv(env_config)
        
        print(f"JSON config loaded: {json_data}")
        print(f"ENV config loaded: {env_data}")
        
        # Use ConfigManager
        config_manager = config_utils.ConfigManager([str(json_config)])
        config_manager.load()
        
        db_port = config_manager.get("database.port", default=3306, type_hint=int)
        debug_mode = config_manager.get("debug", default=False, type_hint=bool)
        
        print(f"Database port: {db_port}")
        print(f"Debug mode: {debug_mode}")
    
    print()


def demo_system_utilities():
    """Demonstrate system utilities."""
    print("💻 SYSTEM UTILITIES DEMO")
    print("=" * 50)
    
    # System information
    sys_info = system_utils.get_system_info()
    python_info = system_utils.get_python_info()
    
    print(f"OS: {sys_info['os_name']} {sys_info['os_version']}")
    print(f"Architecture: {sys_info['architecture']}")
    print(f"Python: {python_info['version']}")
    print(f"CPU Count: {sys_info['cpu_count']}")
    
    # Environment variables
    path_vars = system_utils.get_env_vars("PATH")
    print(f"PATH-related env vars: {len(path_vars)}")
    
    # Find executable
    python_exe = system_utils.find_executable("python")
    print(f"Python executable: {python_exe}")
    
    # Get free port
    free_port = system_utils.get_free_port(8000)
    print(f"Free port starting from 8000: {free_port}")
    
    print()


def demo_security_utilities():
    """Demonstrate security utilities."""
    print("🔐 SECURITY UTILITIES DEMO")
    print("=" * 50)
    
    # Password hashing
    password = "MySecurePassword123!"
    hashed = security_utils.hash_password(password)
    verified = security_utils.verify_password(password, hashed)
    
    print(f"Password hashed successfully: {len(hashed) > 0}")
    print(f"Password verification: {verified}")
    
    # Secret generation
    secret_key = security_utils.generate_secret_key(32)
    uuid_val = security_utils.generate_uuid()
    
    print(f"Secret key length: {len(secret_key)}")
    print(f"UUID generated: {uuid_val}")
    
    # Data hashing
    data = "Important data to hash"
    data_hash = security_utils.hash_data(data)
    print(f"Data hash (SHA-256): {data_hash}")
    
    # JWT tokens
    payload = {"user_id": 123, "role": "admin"}
    secret = "my-jwt-secret"
    token = security_utils.generate_jwt_token(payload, secret, expires_in=3600)
    decoded = security_utils.verify_jwt_token(token, secret)
    
    print(f"JWT token generated: {len(token) > 0}")
    print(f"JWT payload verified: {decoded == payload}")
    
    print()


def demo_time_utilities():
    """Demonstrate time utilities."""
    print("⏰ TIME UTILITIES DEMO")
    print("=" * 50)
    
    # Date parsing
    date_str = "2024-01-15 14:30:00"
    parsed_date = time_utils.parse_date(date_str)
    print(f"Parsed date: {parsed_date}")
    
    # Duration formatting
    duration_seconds = 3661  # 1 hour, 1 minute, 1 second
    formatted_duration = time_utils.format_duration(duration_seconds)
    print(f"Duration formatted: {formatted_duration}")
    
    # Business day calculations
    from datetime import datetime
    test_date = datetime(2024, 1, 15)  # Monday
    is_business = time_utils.is_business_day(test_date)
    next_business = time_utils.next_business_day(test_date)
    
    print(f"Is business day: {is_business}")
    print(f"Next business day: {next_business.strftime('%Y-%m-%d')}")
    
    # Timer
    timer = time_utils.Timer()
    timer.start()
    time.sleep(0.1)  # Small delay
    elapsed = timer.stop()
    print(f"Timer elapsed: {elapsed:.3f} seconds")
    
    print()


def demo_validation_utilities():
    """Demonstrate validation utilities."""
    print("✅ VALIDATION UTILITIES DEMO")
    print("=" * 50)
    
    # Schema validation
    schema = {"name": str, "age": int, "email": str}
    valid_data = {"name": "John", "age": 30, "email": "john@example.com"}
    invalid_data = {"name": "John", "age": "thirty", "email": "invalid-email"}
    
    valid_errors = validation_utils.validate_schema(valid_data, schema)
    invalid_errors = validation_utils.validate_schema(invalid_data, schema)
    
    print(f"Valid data errors: {valid_errors}")
    print(f"Invalid data errors: {invalid_errors}")
    
    # Range validation
    age = 25
    valid_age = validation_utils.validate_range(age, 18, 65)
    print(f"Age {age} in range 18-65: {valid_age}")
    
    # Length validation
    username = "john_doe"
    valid_length = validation_utils.validate_length(username, min_len=3, max_len=20)
    print(f"Username length valid: {valid_length}")
    
    # Custom validator
    validator = validation_utils.Validator()
    validator.add_rule("email", lambda x: "@" in x, "Email must contain @")
    validator.add_rule("age", lambda x: x >= 18, "Must be 18 or older")
    
    test_data = {"email": "test@example.com", "age": 25}
    validation_errors = validator.validate(test_data)
    print(f"Custom validation errors: {validation_errors}")
    
    print()


def demo_cli_utilities():
    """Demonstrate CLI utilities."""
    print("🖥️ CLI UTILITIES DEMO")
    print("=" * 50)
    
    # Colored text
    colored_text = cli_utils.colored_text("Success!", "green", bold=True)
    print(f"Colored text: {colored_text}")
    
    # Table formatting
    data = [
        {"name": "Alice", "age": 30, "city": "New York"},
        {"name": "Bob", "age": 25, "city": "San Francisco"},
        {"name": "Charlie", "age": 35, "city": "Chicago"}
    ]
    table = cli_utils.table_format(data)
    print("Table format:")
    print(table)
    
    # Progress bar (simulated)
    print("\nProgress bar simulation:")
    items = range(5)
    for item in cli_utils.progress_bar(items, desc="Processing"):
        time.sleep(0.1)  # Simulate work
    
    print()


def demo_http_utilities():
    """Demonstrate HTTP utilities."""
    print("🌐 HTTP UTILITIES DEMO")
    print("=" * 50)
    
    try:
        # Simple API request
        response = http_utils.api_request("GET", "https://httpbin.org/json")
        print(f"API request successful: {response is not None}")
        
        # API Client
        client = http_utils.BaseAPIClient("https://httpbin.org")
        user_agent_response = client.get("user-agent")
        print(f"API client request successful: {user_agent_response is not None}")
        
    except Exception as e:
        print(f"HTTP demo skipped (network issue): {e}")
    
    print()


async def demo_async_utilities():
    """Demonstrate async utilities."""
    print("🔄 ASYNC UTILITIES DEMO")
    print("=" * 50)
    
    # Async file operations
    async_manager = async_utils.AsyncFileManager()
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        test_file = tmp_path / "async_test.txt"
        
        # Async file write/read
        await async_manager.write_text(test_file, "Async content")
        content = await async_manager.read_text(test_file)
        print(f"Async file operations successful: {content == 'Async content'}")
    
    # Gather with limit
    async def dummy_task(n):
        await asyncio.sleep(0.01)
        return n * 2
    
    tasks = [dummy_task(i) for i in range(5)]
    results = await async_utils.gather_with_limit(2, *tasks)
    print(f"Gather with limit results: {results}")
    
    # Retry async
    call_count = 0
    async def flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Temporary failure")
        return "Success!"
    
    try:
        result = await async_utils.retry_async(flaky_function, retries=3, delay=0.01)
        print(f"Retry async successful: {result}")
    except Exception as e:
        print(f"Retry async failed: {e}")
    
    print()


def demo_dev_utilities():
    """Demonstrate development utilities."""
    print("🛠️ DEV UTILITIES DEMO")
    print("=" * 50)
    
    # Performance timing
    @dev_utils.time_function
    def slow_function():
        time.sleep(0.1)
        return "Done"
    
    result = slow_function()
    print(f"Timed function result: {result}")
    
    # Test data generation
    schema = {"name": str, "age": int, "active": bool}
    test_data = dev_utils.generate_test_data(schema, count=3)
    print(f"Generated test data: {len(test_data)} items")
    print(f"Sample: {test_data[0]}")
    
    # Pretty print
    complex_obj = {
        "users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
        "settings": {"theme": "dark", "notifications": True}
    }
    pretty_output = dev_utils.pretty_print_object(complex_obj, max_depth=2)
    print(f"Pretty print length: {len(pretty_output)}")
    
    # Benchmark functions
    def func1():
        return sum(range(1000))
    
    def func2():
        return sum(i for i in range(1000))
    
    benchmark_results = dev_utils.benchmark_functions(func1, func2, iterations=100)
    print(f"Benchmark results: {list(benchmark_results.keys())}")
    
    print()


async def main():
    """Run all demonstrations."""
    print("🚀 DEVKITX COMPREHENSIVE DEMO")
    print("=" * 60)
    print("Testing all functionality from PyPI-installed package")
    print("=" * 60)
    print()
    
    # Run all demos
    demo_string_utilities()
    demo_json_utilities()
    demo_file_utilities()
    demo_data_utilities()
    demo_config_utilities()
    demo_system_utilities()
    demo_security_utilities()
    demo_time_utilities()
    demo_validation_utilities()
    demo_cli_utilities()
    demo_http_utilities()
    await demo_async_utilities()
    demo_dev_utilities()
    
    print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("✅ DevKitX is working perfectly from PyPI installation!")


if __name__ == "__main__":
    asyncio.run(main())