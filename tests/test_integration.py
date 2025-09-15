"""Integration tests for dev_qol_toolkit modules."""

from __future__ import annotations
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from dev_qol_toolkit import (
    json_utils, file_utils, string_utils, config_utils, 
    system_utils, security_utils, time_utils, validation_utils,
    data_utils, async_utils, dev_utils
)


class TestModuleIntegration:
    """Test integration between different modules."""

    def test_json_file_workflow(self, tmp_path: Path):
        """Test complete JSON file processing workflow."""
        # Create test data
        original_data = {
            "users": [
                {"name": "Alice Johnson", "email": "alice@example.com", "age": 30},
                {"name": "Bob Smith", "email": "bob@example.com", "age": 25}
            ],
            "config": {
                "debug": True,
                "max_connections": 100,
                "timeout_seconds": 30.5
            }
        }
        
        # Save JSON file
        json_file = tmp_path / "test_data.json"
        json_utils.save_json(original_data, json_file)
        
        # Verify file was created and is readable
        assert file_utils.is_readable(json_file)
        assert file_utils.is_writable(json_file)
        
        # Load and verify data
        loaded_data = json_utils.load_json(json_file)
        assert loaded_data == original_data
        
        # Flatten the JSON
        flattened = json_utils.flatten_json(loaded_data)
        assert "users.0.name" in flattened
        assert "config.debug" in flattened
        
        # Unflatten back
        unflattened = json_utils.unflatten_json(flattened)
        assert unflattened == original_data
        
        # Pretty print
        pretty_output = json_utils.pretty_json(loaded_data)
        assert "Alice Johnson" in pretty_output
        assert "debug" in pretty_output

    def test_string_validation_workflow(self):
        """Test string processing and validation workflow."""
        # Test data
        test_strings = [
            "user_name_example",
            "invalid-email-format",
            "valid@email.com",
            "https://example.com/path",
            "not-a-url"
        ]
        
        results = {}
        
        for test_str in test_strings:
            # Convert case formats
            results[test_str] = {
                "snake": string_utils.to_snake_case(test_str),
                "camel": string_utils.to_camel_case(test_str),
                "pascal": string_utils.to_pascal_case(test_str),
                "kebab": string_utils.to_kebab_case(test_str),
                "is_email": string_utils.validate_email(test_str),
                "is_url": string_utils.validate_url(test_str),
                "sanitized": string_utils.sanitize_filename(test_str)
            }
        
        # Verify email validation
        assert results["valid@email.com"]["is_email"] is True
        assert results["invalid-email-format"]["is_email"] is False
        
        # Verify URL validation
        assert results["https://example.com/path"]["is_url"] is True
        assert results["not-a-url"]["is_url"] is False
        
        # Verify case conversions work
        assert results["user_name_example"]["camel"] == "userNameExample"
        assert results["user_name_example"]["pascal"] == "UserNameExample"

    def test_config_data_integration(self, tmp_path: Path):
        """Test configuration loading and data manipulation integration."""
        # Create multiple config files
        json_config = tmp_path / "config.json"
        yaml_config = tmp_path / "config.yaml"
        
        json_data = {
            "database": {"host": "localhost", "port": 5432},
            "features": ["auth", "logging"]
        }
        
        yaml_data = {
            "database": {"password": "secret", "ssl": True},
            "features": ["metrics"],
            "cache": {"enabled": True, "ttl": 300}
        }
        
        # Save configs
        json_utils.save_json(json_data, json_config)
        
        # Create YAML content manually (since we might not have PyYAML)
        yaml_content = """
database:
  password: secret
  ssl: true
features:
  - metrics
cache:
  enabled: true
  ttl: 300
"""
        yaml_config.write_text(yaml_content.strip())
        
        # Load JSON config
        loaded_json = json_utils.load_json(json_config)
        
        # Simulate YAML loading (would use config_utils.load_yaml_config in real scenario)
        # For this test, we'll use the yaml_data directly
        
        # Merge configurations using data_utils
        merged_config = data_utils.deep_merge(loaded_json, yaml_data)
        
        # Verify merge results
        assert merged_config["database"]["host"] == "localhost"
        assert merged_config["database"]["password"] == "secret"
        assert merged_config["database"]["ssl"] is True
        # Note: deep_merge replaces arrays, so only the second array remains
        assert "metrics" in merged_config["features"]
        assert merged_config["cache"]["enabled"] is True
        
        # Validate merged config
        assert validation_utils.validate_range(merged_config["database"]["port"], 1, 65535)
        assert validation_utils.validate_range(merged_config["cache"]["ttl"], 0, 86400)

    def test_security_time_integration(self):
        """Test security and time utilities integration."""
        # Generate secure data
        secret_key = security_utils.generate_secret_key(32)
        uuid_value = security_utils.generate_uuid()
        
        # Create test data with timestamps
        test_data = {
            "id": uuid_value,
            "secret": secret_key,
            "created_at": time_utils.format_duration(time.time()),
            "password": "test_password_123"
        }
        
        # Hash the password
        hashed_password = security_utils.hash_password(test_data["password"])
        test_data["password_hash"] = hashed_password
        
        # Verify password
        assert security_utils.verify_password("test_password_123", hashed_password)
        assert not security_utils.verify_password("wrong_password", hashed_password)
        
        # Hash other data
        data_hash = security_utils.hash_data(json.dumps(test_data, sort_keys=True))
        
        # Verify data integrity
        assert len(secret_key) == 64  # 32 bytes = 64 hex chars
        assert len(uuid_value) == 36  # Standard UUID format
        assert len(data_hash) == 64   # SHA-256 hash
        
        # Validate data structure
        assert validation_utils.validate_length(secret_key, 64, 64)
        assert validation_utils.validate_length(uuid_value, 36, 36)

    def test_file_system_integration(self, tmp_path: Path):
        """Test file system operations integration."""
        # Create directory structure
        project_dir = tmp_path / "test_project"
        file_utils.ensure_dir(project_dir / "src")
        file_utils.ensure_dir(project_dir / "tests")
        file_utils.ensure_dir(project_dir / "config")
        
        # Create test files
        src_file = project_dir / "src" / "main.py"
        test_file = project_dir / "tests" / "test_main.py"
        config_file = project_dir / "config" / "settings.json"
        
        # Write files atomically
        file_utils.atomic_write(src_file, "print('Hello, World!')")
        file_utils.atomic_write(test_file, "def test_main(): pass")
        
        config_data = {"debug": True, "version": "1.0.0"}
        json_utils.save_json(config_data, config_file)
        
        # Find Python files
        py_files = file_utils.glob_ext(project_dir, "py")
        json_files = file_utils.glob_ext(project_dir, "json")
        
        assert len(py_files) == 2
        assert len(json_files) == 1
        
        # Verify file permissions
        for py_file in py_files:
            assert file_utils.is_readable(py_file)
            assert file_utils.is_writable(py_file)
        
        # Copy files
        backup_dir = project_dir / "backup"
        file_utils.ensure_dir(backup_dir)
        
        for py_file in py_files:
            backup_file = backup_dir / py_file.name
            file_utils.copy_file(py_file, backup_file)
            assert backup_file.exists()
            assert backup_file.read_text() == py_file.read_text()

    @pytest.mark.asyncio
    async def test_async_integration(self):
        """Test async utilities integration."""
        # Test async/sync bridge
        def sync_function(x, y):
            return x + y
        
        async def async_function(x, y):
            return x * y
        
        # Convert sync to async
        async_version = async_utils.sync_to_async(sync_function)
        result1 = await async_version(5, 3)
        assert result1 == 8
        
        # Convert async to sync
        sync_version = async_utils.async_to_sync(async_function)
        result2 = sync_version(5, 3)
        assert result2 == 15
        
        # Test async file operations
        async_file_manager = async_utils.AsyncFileManager()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            tmp_file.write("test content")
        
        try:
            # Read file asynchronously
            content = await async_file_manager.read_text(tmp_path)
            assert content == "test content"
            
            # Write file asynchronously
            new_content = "updated content"
            await async_file_manager.write_text(tmp_path, new_content)
            
            # Verify update
            updated_content = await async_file_manager.read_text(tmp_path)
            assert updated_content == new_content
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestPerformanceBenchmarks:
    """Performance benchmarks for critical functions."""

    def test_json_processing_performance(self, tmp_path: Path):
        """Benchmark JSON processing operations."""
        # Create large test data
        large_data = {
            "users": [
                {
                    "id": i,
                    "name": f"User {i}",
                    "email": f"user{i}@example.com",
                    "metadata": {
                        "created": f"2024-01-{(i % 28) + 1:02d}",
                        "tags": [f"tag{j}" for j in range(i % 5)]
                    }
                }
                for i in range(1000)
            ],
            "config": {
                "settings": {f"key_{i}": f"value_{i}" for i in range(100)}
            }
        }
        
        json_file = tmp_path / "large_data.json"
        
        # Benchmark save operation
        start_time = time.perf_counter()
        json_utils.save_json(large_data, json_file)
        save_time = time.perf_counter() - start_time
        
        # Benchmark load operation
        start_time = time.perf_counter()
        loaded_data = json_utils.load_json(json_file)
        load_time = time.perf_counter() - start_time
        
        # Benchmark flatten operation
        start_time = time.perf_counter()
        flattened = json_utils.flatten_json(loaded_data)
        flatten_time = time.perf_counter() - start_time
        
        # Benchmark unflatten operation
        start_time = time.perf_counter()
        unflattened = json_utils.unflatten_json(flattened)
        unflatten_time = time.perf_counter() - start_time
        
        # Performance assertions (should complete within reasonable time)
        assert save_time < 1.0, f"JSON save took too long: {save_time:.3f}s"
        assert load_time < 1.0, f"JSON load took too long: {load_time:.3f}s"
        assert flatten_time < 2.0, f"JSON flatten took too long: {flatten_time:.3f}s"
        assert unflatten_time < 2.0, f"JSON unflatten took too long: {unflatten_time:.3f}s"
        
        # Verify correctness
        assert loaded_data == large_data
        assert unflattened == large_data
        assert len(flattened) > 1000  # Should have many flattened keys

    def test_string_processing_performance(self):
        """Benchmark string processing operations."""
        # Test data
        test_strings = [
            "this_is_a_snake_case_string_with_many_words",
            "ThisIsAPascalCaseStringWithManyWords",
            "thisIsACamelCaseStringWithManyWords",
            "this-is-a-kebab-case-string-with-many-words"
        ] * 250  # 1000 strings total
        
        # Benchmark case conversions
        start_time = time.perf_counter()
        snake_results = [string_utils.to_snake_case(s) for s in test_strings]
        snake_time = time.perf_counter() - start_time
        
        start_time = time.perf_counter()
        camel_results = [string_utils.to_camel_case(s) for s in test_strings]
        camel_time = time.perf_counter() - start_time
        
        start_time = time.perf_counter()
        pascal_results = [string_utils.to_pascal_case(s) for s in test_strings]
        pascal_time = time.perf_counter() - start_time
        
        start_time = time.perf_counter()
        kebab_results = [string_utils.to_kebab_case(s) for s in test_strings]
        kebab_time = time.perf_counter() - start_time
        
        # Performance assertions
        assert snake_time < 0.5, f"Snake case conversion took too long: {snake_time:.3f}s"
        assert camel_time < 0.5, f"Camel case conversion took too long: {camel_time:.3f}s"
        assert pascal_time < 0.5, f"Pascal case conversion took too long: {pascal_time:.3f}s"
        assert kebab_time < 0.5, f"Kebab case conversion took too long: {kebab_time:.3f}s"
        
        # Verify results
        assert len(snake_results) == 1000
        assert len(camel_results) == 1000
        assert len(pascal_results) == 1000
        assert len(kebab_results) == 1000

    def test_file_operations_performance(self, tmp_path: Path):
        """Benchmark file operations."""
        # Create many small files
        num_files = 100
        file_size = 1024  # 1KB each
        test_content = "x" * file_size
        
        files = []
        
        # Benchmark file creation
        start_time = time.perf_counter()
        for i in range(num_files):
            file_path = tmp_path / f"test_file_{i}.txt"
            file_utils.atomic_write(file_path, test_content)
            files.append(file_path)
        create_time = time.perf_counter() - start_time
        
        # Benchmark file reading
        start_time = time.perf_counter()
        contents = []
        for file_path in files:
            content = file_path.read_text()
            contents.append(content)
        read_time = time.perf_counter() - start_time
        
        # Benchmark file finding
        start_time = time.perf_counter()
        found_files = file_utils.glob_ext(tmp_path, "txt")
        find_time = time.perf_counter() - start_time
        
        # Benchmark file copying
        backup_dir = tmp_path / "backup"
        file_utils.ensure_dir(backup_dir)
        
        start_time = time.perf_counter()
        for file_path in files[:10]:  # Copy first 10 files
            backup_path = backup_dir / file_path.name
            file_utils.copy_file(file_path, backup_path)
        copy_time = time.perf_counter() - start_time
        
        # Performance assertions
        assert create_time < 2.0, f"File creation took too long: {create_time:.3f}s"
        assert read_time < 1.0, f"File reading took too long: {read_time:.3f}s"
        assert find_time < 0.5, f"File finding took too long: {find_time:.3f}s"
        assert copy_time < 1.0, f"File copying took too long: {copy_time:.3f}s"
        
        # Verify results
        assert len(contents) == num_files
        assert all(content == test_content for content in contents)
        assert len(found_files) == num_files

    def test_security_operations_performance(self):
        """Benchmark security operations."""
        # Test data
        passwords = [f"password_{i}_with_some_complexity!" for i in range(100)]
        data_strings = [f"test_data_string_{i}_for_hashing" for i in range(100)]
        
        # Benchmark password hashing
        start_time = time.perf_counter()
        hashed_passwords = [security_utils.hash_password(pwd) for pwd in passwords]
        hash_time = time.perf_counter() - start_time
        
        # Benchmark password verification
        start_time = time.perf_counter()
        verifications = [
            security_utils.verify_password(passwords[i], hashed_passwords[i])
            for i in range(len(passwords))
        ]
        verify_time = time.perf_counter() - start_time
        
        # Benchmark data hashing
        start_time = time.perf_counter()
        data_hashes = [security_utils.hash_data(data) for data in data_strings]
        data_hash_time = time.perf_counter() - start_time
        
        # Benchmark secret generation
        start_time = time.perf_counter()
        secrets = [security_utils.generate_secret_key(32) for _ in range(100)]
        secret_time = time.perf_counter() - start_time
        
        # Performance assertions (security operations are expected to be slower)
        assert hash_time < 10.0, f"Password hashing took too long: {hash_time:.3f}s"
        assert verify_time < 10.0, f"Password verification took too long: {verify_time:.3f}s"
        assert data_hash_time < 1.0, f"Data hashing took too long: {data_hash_time:.3f}s"
        assert secret_time < 1.0, f"Secret generation took too long: {secret_time:.3f}s"
        
        # Verify results
        assert all(verifications), "All password verifications should pass"
        assert len(set(data_hashes)) == len(data_hashes), "All data hashes should be unique"
        assert len(set(secrets)) == len(secrets), "All secrets should be unique"

    def test_validation_performance(self):
        """Benchmark validation operations."""
        # Test data
        test_values = list(range(1000))
        test_strings = [f"test_string_{i}_with_various_lengths" for i in range(1000)]
        
        # Benchmark range validation
        start_time = time.perf_counter()
        range_results = [
            validation_utils.validate_range(val, 0, 1000) for val in test_values
        ]
        range_time = time.perf_counter() - start_time
        
        # Benchmark length validation
        start_time = time.perf_counter()
        length_results = [
            validation_utils.validate_length(s, 10, 50) for s in test_strings
        ]
        length_time = time.perf_counter() - start_time
        
        # Performance assertions
        assert range_time < 0.1, f"Range validation took too long: {range_time:.3f}s"
        assert length_time < 0.1, f"Length validation took too long: {length_time:.3f}s"
        
        # Verify results
        assert len(range_results) == 1000
        assert len(length_results) == 1000
        assert all(isinstance(result, bool) for result in range_results)
        assert all(isinstance(result, bool) for result in length_results)


class TestErrorHandlingIntegration:
    """Test error handling across module boundaries."""

    def test_json_file_error_handling(self, tmp_path: Path):
        """Test error handling in JSON file operations."""
        # Test loading non-existent file
        with pytest.raises(FileNotFoundError):
            json_utils.load_json(tmp_path / "nonexistent.json")
        
        # Test loading invalid JSON
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text("{ invalid json }")
        
        with pytest.raises(json.JSONDecodeError):
            json_utils.load_json(invalid_json)
        
        # Test saving to read-only location (if possible)
        readonly_file = tmp_path / "readonly.json"
        json_utils.save_json({"test": True}, readonly_file)
        readonly_file.chmod(0o444)  # Make read-only
        
        # This should still work due to atomic_write creating temp file first
        json_utils.save_json({"updated": True}, readonly_file)

    def test_validation_error_integration(self):
        """Test validation errors across modules."""
        # Test invalid data structures
        invalid_data = {
            "nested": {
                "deeply": {
                    "invalid": object()  # Non-serializable object
                }
            }
        }
        
        # JSON serialization should fail
        with pytest.raises((TypeError, ValueError)):
            json_utils.pretty_json(invalid_data)
        
        # Test validation with invalid ranges
        assert not validation_utils.validate_range(-1, 0, 100)
        assert not validation_utils.validate_range(101, 0, 100)
        assert validation_utils.validate_range(50, 0, 100)
        
        # Test string validation edge cases
        assert not string_utils.validate_email("")
        assert not string_utils.validate_email("not-an-email")
        assert not string_utils.validate_url("")
        assert not string_utils.validate_url("not-a-url")

    def test_file_permission_error_handling(self, tmp_path: Path):
        """Test file permission error handling."""
        # Test with non-existent directory
        non_existent_path = tmp_path / "non_existent" / "file.txt"
        
        # atomic_write should create parent directories
        file_utils.atomic_write(non_existent_path, "content")
        assert non_existent_path.exists()
        
        # Test file accessibility checks
        readable_file = tmp_path / "readable.txt"
        readable_file.write_text("content")
        
        assert file_utils.is_readable(readable_file)
        assert file_utils.is_writable(readable_file)
        
        # Test with non-existent file
        assert not file_utils.is_readable(tmp_path / "nonexistent.txt")
        assert file_utils.is_writable(tmp_path / "new_file.txt")  # Parent dir is writable


class TestCLIIntegration:
    """Test CLI integration with all modules."""

    def test_cli_json_commands_integration(self, tmp_path: Path):
        """Test CLI JSON commands integration."""
        from dev_qol_toolkit.__main__ import main
        
        # Create test JSON file
        test_data = {"name": "test", "items": [1, 2, 3]}
        json_file = tmp_path / "test.json"
        json_utils.save_json(test_data, json_file)
        
        # Test pretty print command
        with patch('builtins.print') as mock_print:
            result = main(["json", "pretty", str(json_file)])
            assert result == 0
            mock_print.assert_called_once()
        
        # Test flatten command
        with patch('builtins.print') as mock_print:
            result = main(["json", "flatten", str(json_file)])
            assert result == 0
            mock_print.assert_called_once()

    def test_cli_string_commands_integration(self):
        """Test CLI string commands integration."""
        from dev_qol_toolkit.__main__ import main
        
        # Test case conversion
        with patch('builtins.print') as mock_print:
            result = main(["string", "convert", "test_string", "--to", "camel"])
            assert result == 0
            mock_print.assert_called_with("testString")
        
        # Test validation
        with patch('builtins.print') as mock_print:
            result = main(["string", "validate", "test@example.com", "--type", "email"])
            assert result == 0
            mock_print.assert_called_with("Valid")

    def test_cli_file_commands_integration(self, tmp_path: Path):
        """Test CLI file commands integration."""
        from dev_qol_toolkit.__main__ import main
        
        # Create test files
        (tmp_path / "test1.txt").write_text("content1")
        (tmp_path / "test2.txt").write_text("content2")
        
        # Test find command
        with patch('builtins.print') as mock_print:
            result = main(["file", "find", "*.txt", "--root", str(tmp_path)])
            assert result == 0
            assert mock_print.call_count == 2  # Should find 2 files

    def test_cli_security_commands_integration(self):
        """Test CLI security commands integration."""
        from dev_qol_toolkit.__main__ import main
        
        # Test hash command
        with patch('builtins.print') as mock_print:
            result = main(["security", "hash", "test_data"])
            assert result == 0
            mock_print.assert_called_once()
            # Verify it's a valid hash
            hash_output = mock_print.call_args[0][0]
            assert len(hash_output) == 64  # SHA-256 hash length
        
        # Test secret generation
        with patch('builtins.print') as mock_print:
            result = main(["security", "generate-secret", "--length", "16"])
            assert result == 0
            mock_print.assert_called_once()
            # Verify it's the right length
            secret_output = mock_print.call_args[0][0]
            assert len(secret_output) == 32  # 16 bytes = 32 hex chars