#!/usr/bin/env python3
"""
JSON Utilities Examples

This module demonstrates practical usage of devtools_py.json_utils
including common patterns, edge cases, and limitations.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from devtools_py.json_utils import (
    load_json,
    save_json,
    merge_json,
    validate_json_schema,
    pretty_print_json,
    flatten_json,
    unflatten_json,
    json_to_csv,
    csv_to_json
)


def basic_json_operations():
    """Basic JSON loading and saving operations."""
    print("=== Basic JSON Operations ===")
    
    # Sample data
    data = {
        "name": "John Doe",
        "age": 30,
        "skills": ["Python", "JavaScript", "SQL"],
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "country": "USA"
        }
    }
    
    # Save JSON with pretty formatting
    save_json(data, "example_user.json", indent=2)
    print("✓ Saved JSON file with pretty formatting")
    
    # Load JSON back
    loaded_data = load_json("example_user.json")
    print(f"✓ Loaded data: {loaded_data['name']}")
    
    # Pretty print JSON
    pretty_output = pretty_print_json(data)
    print("✓ Pretty printed JSON:")
    print(pretty_output)


def json_merging_examples():
    """Demonstrate JSON merging capabilities."""
    print("\n=== JSON Merging Examples ===")
    
    base_config = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "myapp"
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(message)s"
        }
    }
    
    override_config = {
        "database": {
            "host": "production.db.com",
            "ssl": True
        },
        "cache": {
            "type": "redis",
            "ttl": 3600
        }
    }
    
    # Merge configurations
    merged = merge_json(base_config, override_config)
    print("✓ Merged configuration:")
    print(pretty_print_json(merged))
    
    # Edge case: merging with None values
    config_with_none = {
        "database": {
            "password": None,  # This will override existing value
            "timeout": 30
        }
    }
    
    merged_with_none = merge_json(base_config, config_with_none)
    print("✓ Merged with None values (None overrides existing):")
    print(pretty_print_json(merged_with_none))


def json_schema_validation():
    """Demonstrate JSON schema validation."""
    print("\n=== JSON Schema Validation ===")
    
    # Define a schema for user data
    user_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "age": {"type": "integer", "minimum": 0, "maximum": 150},
            "email": {"type": "string", "format": "email"},
            "skills": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1
            }
        },
        "required": ["name", "age", "email"]
    }
    
    # Valid data
    valid_user = {
        "name": "Alice Smith",
        "age": 28,
        "email": "alice@example.com",
        "skills": ["Python", "Docker"]
    }
    
    # Invalid data
    invalid_user = {
        "name": "",  # Empty name
        "age": -5,   # Negative age
        "email": "not-an-email",  # Invalid email
        "skills": []  # Empty skills array
    }
    
    # Validate valid data
    is_valid, errors = validate_json_schema(valid_user, user_schema)
    print(f"✓ Valid user validation: {is_valid}")
    
    # Validate invalid data
    is_valid, errors = validate_json_schema(invalid_user, user_schema)
    print(f"✗ Invalid user validation: {is_valid}")
    print(f"  Errors: {errors}")


def json_flattening_examples():
    """Demonstrate JSON flattening and unflattening."""
    print("\n=== JSON Flattening Examples ===")
    
    nested_data = {
        "user": {
            "profile": {
                "name": "John Doe",
                "age": 30
            },
            "preferences": {
                "theme": "dark",
                "notifications": {
                    "email": True,
                    "push": False
                }
            }
        },
        "app": {
            "version": "1.2.3",
            "features": ["auth", "api", "ui"]
        }
    }
    
    # Flatten the nested structure
    flattened = flatten_json(nested_data)
    print("✓ Flattened JSON:")
    for key, value in flattened.items():
        print(f"  {key}: {value}")
    
    # Unflatten back to nested structure
    unflattened = unflatten_json(flattened)
    print("✓ Unflattened back to nested structure:")
    print(pretty_print_json(unflattened))
    
    # Custom separator
    flattened_custom = flatten_json(nested_data, separator="__")
    print("✓ Flattened with custom separator '__':")
    for key, value in list(flattened_custom.items())[:3]:  # Show first 3
        print(f"  {key}: {value}")


def json_csv_conversion():
    """Demonstrate JSON to CSV conversion and vice versa."""
    print("\n=== JSON/CSV Conversion ===")
    
    # Sample data for CSV conversion
    users_data = [
        {"id": 1, "name": "Alice", "department": "Engineering", "salary": 75000},
        {"id": 2, "name": "Bob", "department": "Marketing", "salary": 65000},
        {"id": 3, "name": "Charlie", "department": "Engineering", "salary": 80000}
    ]
    
    # Convert JSON to CSV
    csv_content = json_to_csv(users_data)
    print("✓ Converted JSON to CSV:")
    print(csv_content)
    
    # Save CSV to file
    with open("users.csv", "w") as f:
        f.write(csv_content)
    
    # Convert CSV back to JSON
    json_data = csv_to_json("users.csv")
    print("✓ Converted CSV back to JSON:")
    print(pretty_print_json(json_data))


def error_handling_examples():
    """Demonstrate error handling and edge cases."""
    print("\n=== Error Handling Examples ===")
    
    # Handle missing files gracefully
    try:
        data = load_json("nonexistent.json")
    except FileNotFoundError as e:
        print(f"✓ Handled missing file: {e}")
    
    # Handle invalid JSON
    try:
        with open("invalid.json", "w") as f:
            f.write('{"invalid": json}')  # Invalid JSON syntax
        data = load_json("invalid.json")
    except json.JSONDecodeError as e:
        print(f"✓ Handled invalid JSON: {e}")
    
    # Handle circular references (limitation)
    class CircularRef:
        def __init__(self):
            self.ref = self
    
    circular_data = {"obj": CircularRef()}
    try:
        json_str = json.dumps(circular_data, default=str)
        print("✓ Handled circular reference with custom serializer")
    except (TypeError, ValueError) as e:
        print(f"✗ Circular reference error: {e}")


def performance_considerations():
    """Demonstrate performance considerations and best practices."""
    print("\n=== Performance Considerations ===")
    
    # Large data handling
    large_data = {"items": [{"id": i, "value": f"item_{i}"} for i in range(1000)]}
    
    # Streaming for large files (when available)
    print("✓ For large JSON files:")
    print("  - Use streaming parsers for files > 100MB")
    print("  - Consider ijson library for streaming JSON parsing")
    print("  - Use generators when processing large arrays")
    
    # Memory-efficient processing
    def process_large_json_efficiently(filename: str):
        """Example of memory-efficient JSON processing."""
        # Instead of loading entire file:
        # data = load_json(filename)  # Loads everything into memory
        
        # Use streaming approach:
        with open(filename, 'r') as f:
            for line in f:
                if line.strip():  # Process line by line for JSONL format
                    try:
                        item = json.loads(line)
                        # Process individual item
                        yield item
                    except json.JSONDecodeError:
                        continue
    
    print("✓ Use streaming for large datasets")
    print("✓ Process items individually to reduce memory usage")


def limitations_and_gotchas():
    """Document known limitations and common gotchas."""
    print("\n=== Limitations and Gotchas ===")
    
    print("Known limitations:")
    print("1. JSON doesn't support comments - use YAML/TOML for config files with comments")
    print("2. No native date/datetime support - dates become strings")
    print("3. No distinction between integers and floats in some cases")
    print("4. Keys must be strings (not integers or other types)")
    print("5. No support for functions, classes, or complex objects")
    
    # Demonstrate date handling
    from datetime import datetime
    data_with_date = {
        "created_at": datetime.now().isoformat(),  # Convert to string
        "user_id": 123
    }
    print(f"✓ Date handling: {data_with_date}")
    
    # Key type limitations
    data_with_int_keys = {1: "one", 2: "two", 3: "three"}
    json_str = json.dumps(data_with_int_keys)
    loaded_back = json.loads(json_str)
    print(f"✓ Integer keys become strings: {loaded_back}")
    
    print("\nBest practices:")
    print("- Always validate JSON schema for external data")
    print("- Use proper error handling for file operations")
    print("- Consider using dataclasses or Pydantic for structured data")
    print("- Use streaming for large files")
    print("- Sanitize data before JSON serialization")


if __name__ == "__main__":
    """Run all examples."""
    print("Dev QoL Toolkit - JSON Utilities Examples")
    print("=" * 50)
    
    basic_json_operations()
    json_merging_examples()
    json_schema_validation()
    json_flattening_examples()
    json_csv_conversion()
    error_handling_examples()
    performance_considerations()
    limitations_and_gotchas()
    
    print("\n" + "=" * 50)
    print("All JSON utilities examples completed!")
    print("Check the generated files: example_user.json, users.csv")