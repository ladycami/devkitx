#!/usr/bin/env python3
"""
Integration test script for devtools-py package.

This script performs a comprehensive integration test of the package
to ensure all components work together correctly.
"""

import sys
import tempfile
from pathlib import Path


def test_json_file_workflow():
    """Test JSON file operations workflow."""
    print("🔍 Testing JSON file workflow...")
    
    import devkitx.json_utils as json_utils
    
    test_data = {
        "users": [
            {"id": 1, "name": "Alice", "active": True},
            {"id": 2, "name": "Bob", "active": False}
        ],
        "config": {
            "version": "1.0.0",
            "debug": True
        }
    }
    
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        temp_file = Path(f.name)
    
    try:
        # Save and load
        json_utils.save_json(test_data, temp_file)
        loaded_data = json_utils.load_json(temp_file)
        assert loaded_data == test_data
        
        # Test flattening
        flattened = json_utils.flatten_json(test_data)
        assert "users.0.name" in flattened
        assert flattened["users.0.name"] == "Alice"
        
        # Test unflattening
        unflattened = json_utils.unflatten_json(flattened)
        assert unflattened["users"][0]["name"] == "Alice"
        
        print("✅ JSON workflow test passed")
        
    finally:
        temp_file.unlink()


def test_string_processing_workflow():
    """Test string processing workflow."""
    print("🔍 Testing string processing workflow...")
    
    import devkitx.string_utils as string_utils
    
    # Test case conversions
    test_string = "MyVariableName"
    snake_case = string_utils.to_snake_case(test_string)
    assert snake_case == "my_variable_name"
    
    pascal_case = string_utils.to_pascal_case(snake_case)
    assert pascal_case == "MyVariableName"
    
    kebab_case = string_utils.to_kebab_case(test_string)
    assert kebab_case == "my-variable-name"
    
    # Test validation
    assert string_utils.validate_email("test@example.com")
    assert not string_utils.validate_email("invalid-email")
    
    assert string_utils.validate_url("https://example.com")
    assert not string_utils.validate_url("not-a-url")
    
    # Test sanitization
    filename = string_utils.sanitize_filename("file<>name?.txt")
    assert "<" not in filename and ">" not in filename
    
    print("✅ String processing workflow test passed")


def test_security_workflow():
    """Test security operations workflow."""
    print("🔍 Testing security workflow...")
    
    import devkitx.security_utils as security_utils
    
    # Test password hashing
    password = "test_password_123"
    hashed = security_utils.hash_password(password)
    assert security_utils.verify_password(password, hashed)
    assert not security_utils.verify_password("wrong_password", hashed)
    
    # Test secret generation
    secret = security_utils.generate_secret_key(32)
    assert len(secret) > 0
    
    uuid_val = security_utils.generate_uuid()
    assert len(uuid_val) > 0
    
    # Test data hashing
    data_hash = security_utils.hash_data("test data")
    assert len(data_hash) == 64  # SHA-256 hex length
    
    print("✅ Security workflow test passed")


def test_system_info_workflow():
    """Test system information workflow."""
    print("🔍 Testing system info workflow...")
    
    import devkitx.system_utils as system_utils
    
    # Test system info
    sys_info = system_utils.get_system_info()
    assert isinstance(sys_info, dict)
    assert "os_name" in sys_info
    assert "hostname" in sys_info
    
    # Test Python info
    py_info = system_utils.get_python_info()
    assert isinstance(py_info, dict)
    assert "version" in py_info
    
    # Test environment variables
    env_vars = system_utils.get_env_vars()
    assert isinstance(env_vars, dict)
    
    print("✅ System info workflow test passed")


def test_data_processing_workflow():
    """Test data processing workflow."""
    print("🔍 Testing data processing workflow...")
    
    import devkitx.data_utils as data_utils
    
    # Test deep operations
    dict1 = {"a": {"b": 1}, "c": 2}
    dict2 = {"a": {"d": 3}, "e": 4}
    
    merged = data_utils.deep_merge(dict1, dict2)
    assert merged["a"]["b"] == 1
    assert merged["a"]["d"] == 3
    assert merged["c"] == 2
    assert merged["e"] == 4
    
    # Test grouping
    items = [
        {"category": "A", "value": 1},
        {"category": "B", "value": 2},
        {"category": "A", "value": 3}
    ]
    
    grouped = data_utils.group_by(items, lambda x: x["category"])
    assert len(grouped["A"]) == 2
    assert len(grouped["B"]) == 1
    
    print("✅ Data processing workflow test passed")


def test_cli_integration():
    """Test CLI integration."""
    print("🔍 Testing CLI integration...")
    
    import subprocess
    
    # Test string conversion command
    result = subprocess.run(
        [sys.executable, "-m", "devkitx", "string", "convert", "--to", "snake", "TestString"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "test_string" in result.stdout
    
    # Test system info command
    result = subprocess.run(
        [sys.executable, "-m", "devkitx", "system", "info"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    
    print("✅ CLI integration test passed")


def test_async_utilities():
    """Test async utilities."""
    print("🔍 Testing async utilities...")
    
    import asyncio
    import devkitx.async_utils as async_utils
    
    # Test sync to async conversion
    def sync_function(x):
        return x * 2
    
    async_func = async_utils.sync_to_async(sync_function)
    
    async def test_async():
        result = await async_func(5)
        assert result == 10
    
    asyncio.run(test_async())
    
    print("✅ Async utilities test passed")


def main():
    """Run all integration tests."""
    print("🚀 Starting devtools-py integration tests")
    print("=" * 50)
    
    tests = [
        test_json_file_workflow,
        test_string_processing_workflow,
        test_security_workflow,
        test_system_info_workflow,
        test_data_processing_workflow,
        test_cli_integration,
        test_async_utilities,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Integration test results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed!")
        return 0
    else:
        print("❌ Some integration tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())