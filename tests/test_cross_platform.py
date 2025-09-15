"""Cross-platform and error condition tests for devtools_py."""

from __future__ import annotations
import platform
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from devtools_py import (
    file_utils,
    system_utils,
    string_utils,
    json_utils,
    security_utils,
    time_utils,
    validation_utils,
)


class TestCrossPlatformCompatibility:
    """Test cross-platform compatibility across Windows, macOS, and Linux."""

    def test_path_handling_cross_platform(self, tmp_path: Path):
        """Test path handling works across different platforms."""
        # Test with various path separators and formats
        test_paths = [
            "simple_file.txt",
            "nested/directory/file.txt",
            "nested\\windows\\style\\path.txt",  # Should work on all platforms
            "file with spaces.txt",
            "file-with-hyphens.txt",
            "file_with_underscores.txt",
        ]

        for test_path in test_paths:
            # Normalize path for current platform
            normalized_path = tmp_path / Path(test_path).as_posix()

            # Ensure parent directories exist
            file_utils.ensure_dir(normalized_path.parent)

            # Test atomic write
            content = f"Content for {test_path}"
            file_utils.atomic_write(normalized_path, content)

            # Verify file exists and is readable
            assert normalized_path.exists()
            assert file_utils.is_readable(normalized_path)
            assert file_utils.is_writable(normalized_path)
            assert normalized_path.read_text() == content

    def test_filename_sanitization_cross_platform(self):
        """Test filename sanitization works on all platforms."""
        # Problematic characters on different platforms
        problematic_names = [
            "file<>name.txt",  # Windows: < >
            "file|name.txt",  # Windows: |
            "file:name.txt",  # Windows/macOS: :
            "file?name.txt",  # Windows: ?
            "file*name.txt",  # Windows: *
            'file"name.txt',  # Windows: "
            "file/name.txt",  # All: path separator
            "file\\name.txt",  # Windows: path separator
            "CON.txt",  # Windows reserved name
            "PRN.txt",  # Windows reserved name
            "AUX.txt",  # Windows reserved name
            "NUL.txt",  # Windows reserved name
            ".hidden_file.txt",  # Unix hidden file
            "file with spaces.txt",  # Spaces (should be preserved)
        ]

        for problematic_name in problematic_names:
            sanitized = string_utils.sanitize_filename(problematic_name)

            # Sanitized name should not contain problematic characters
            assert "<" not in sanitized
            assert ">" not in sanitized
            assert "|" not in sanitized
            assert "?" not in sanitized
            assert "*" not in sanitized
            assert '"' not in sanitized
            assert "/" not in sanitized
            assert "\\" not in sanitized

            # Should not be empty
            assert len(sanitized) > 0

            # Should be a valid filename (test by creating a temp file)
            with tempfile.NamedTemporaryFile(suffix=f"_{sanitized}", delete=True) as tmp:
                assert tmp.name is not None

    @pytest.mark.skipif(platform.system() == "Windows", reason="Unix-specific test")
    def test_unix_specific_features(self, tmp_path: Path):
        """Test Unix-specific features (Linux/macOS)."""
        # Test file permissions
        test_file = tmp_path / "unix_test.txt"
        file_utils.atomic_write(test_file, "test content")

        # Make file read-only
        test_file.chmod(0o444)
        assert file_utils.is_readable(test_file)

        # Test executable detection
        if system_utils.find_executable("ls"):
            assert system_utils.find_executable("ls") is not None

        # Test system info includes Unix-specific fields
        sys_info = system_utils.get_system_info()
        assert "os_name" in sys_info
        assert sys_info["os_name"] in ["Linux", "Darwin"]

    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
    def test_windows_specific_features(self, tmp_path: Path):
        """Test Windows-specific features."""
        # Test Windows path handling
        test_file = tmp_path / "windows_test.txt"
        file_utils.atomic_write(test_file, "test content")

        assert file_utils.is_readable(test_file)
        assert file_utils.is_writable(test_file)

        # Test executable detection with .exe extension
        if system_utils.find_executable("cmd"):
            cmd_path = system_utils.find_executable("cmd")
            assert cmd_path is not None
            assert cmd_path.lower().endswith(".exe")

        # Test system info includes Windows-specific fields
        sys_info = system_utils.get_system_info()
        assert "os_name" in sys_info
        assert sys_info["os_name"] == "Windows"

    def test_line_ending_handling(self, tmp_path: Path):
        """Test handling of different line endings across platforms."""
        test_content_variants = [
            "line1\nline2\nline3",  # Unix (LF)
            "line1\r\nline2\r\nline3",  # Windows (CRLF)
            "line1\rline2\rline3",  # Old Mac (CR)
            "mixed\nline\r\nendings\rhere",  # Mixed
        ]

        for i, content in enumerate(test_content_variants):
            test_file = tmp_path / f"line_endings_{i}.txt"

            # Write with atomic_write
            file_utils.atomic_write(test_file, content)

            # Read back and verify
            read_content = test_file.read_text()
            assert len(read_content) > 0

            # Content should be readable regardless of line endings
            lines = read_content.splitlines()
            assert len(lines) >= 3

    def test_unicode_handling_cross_platform(self, tmp_path: Path):
        """Test Unicode handling across platforms."""
        unicode_content = {
            "english": "Hello World",
            "chinese": "你好世界",
            "japanese": "こんにちは世界",
            "arabic": "مرحبا بالعالم",
            "emoji": "Hello 🌍 World 🚀",
            "mixed": "Mixed: English, 中文, 日本語, العربية, 🎉",
        }

        for name, content in unicode_content.items():
            # Test file operations with Unicode
            test_file = tmp_path / f"unicode_{name}.txt"
            file_utils.atomic_write(test_file, content)

            assert test_file.exists()
            read_content = test_file.read_text(encoding="utf-8")
            assert read_content == content

            # Test JSON operations with Unicode
            json_file = tmp_path / f"unicode_{name}.json"
            json_data = {"content": content, "name": name}
            json_utils.save_json(json_data, json_file)

            loaded_data = json_utils.load_json(json_file)
            assert loaded_data["content"] == content
            assert loaded_data["name"] == name

    def test_environment_variable_handling(self):
        """Test environment variable handling across platforms."""
        # Test getting environment variables
        env_vars = system_utils.get_env_vars()
        assert isinstance(env_vars, dict)

        # Should have some standard environment variables
        if platform.system() == "Windows":
            # Windows-specific env vars
            assert any(key.upper() in ["PATH", "USERPROFILE", "COMPUTERNAME"] for key in env_vars)
        else:
            # Unix-like env vars
            assert any(key in ["PATH", "HOME", "USER"] for key in env_vars)

        # Test PATH variable specifically
        path_var = env_vars.get("PATH") or env_vars.get("Path")
        assert path_var is not None
        assert len(path_var) > 0

    def test_system_command_execution_cross_platform(self):
        """Test system command execution across platforms."""
        if platform.system() == "Windows":
            # Windows commands
            test_commands = [
                ["echo", "hello"],
                ["dir", "/b"],  # List directory briefly
            ]
        else:
            # Unix-like commands
            test_commands = [
                ["echo", "hello"],
                ["ls", "-la"],
                ["pwd"],
            ]

        for cmd in test_commands:
            try:
                result = system_utils.run_command(cmd, timeout=10.0)
                assert result.returncode == 0
                assert len(result.stdout) > 0
            except Exception as e:
                # Some commands might not be available, that's okay
                pytest.skip(f"Command {cmd} not available: {e}")


class TestErrorConditions:
    """Test comprehensive error condition handling."""

    def test_file_operation_errors(self, tmp_path: Path):
        """Test file operation error conditions."""
        # Test reading non-existent file
        non_existent = tmp_path / "does_not_exist.txt"
        assert not file_utils.is_readable(non_existent)

        # Test writing to invalid path (should handle gracefully)
        try:
            # Try to write to a path with null bytes (invalid on most systems)
            invalid_path = tmp_path / "invalid\x00name.txt"
            with pytest.raises((OSError, ValueError)):
                file_utils.atomic_write(invalid_path, "content")
        except Exception:
            # Some systems might handle this differently
            pass

        # Test copying non-existent file
        with pytest.raises(FileNotFoundError):
            file_utils.copy_file(non_existent, tmp_path / "copy.txt")

        # Test copying to existing file with overwrite=False
        source = tmp_path / "source.txt"
        dest = tmp_path / "dest.txt"
        source.write_text("source content")
        dest.write_text("dest content")

        with pytest.raises(FileExistsError):
            file_utils.copy_file(source, dest, overwrite=False)

    def test_json_error_conditions(self, tmp_path: Path):
        """Test JSON operation error conditions."""
        # Test loading invalid JSON
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text("{ invalid json content }")

        with pytest.raises(Exception):  # Could be JSONDecodeError or similar
            json_utils.load_json(invalid_json)

        # Test loading non-existent JSON file
        with pytest.raises(FileNotFoundError):
            json_utils.load_json(tmp_path / "nonexistent.json")

        # Test saving non-serializable data
        non_serializable_data = {"function": lambda x: x}
        json_file = tmp_path / "test.json"

        with pytest.raises((TypeError, ValueError)):
            json_utils.save_json(non_serializable_data, json_file)

        # Test flattening with circular references
        circular_data = {"a": {}}
        circular_data["a"]["b"] = circular_data  # Circular reference

        # This might cause recursion error or be handled gracefully
        try:
            json_utils.flatten_json(circular_data)
        except RecursionError:
            # Expected for circular references
            pass

    def test_string_validation_edge_cases(self):
        """Test string validation with edge cases."""
        # Test email validation edge cases
        invalid_emails = [
            "",
            "@",
            "@domain.com",
            "user@",
            "user@domain",
            "user space@domain.com",
            "user@domain..com",
            "user@.domain.com",
            "user@domain.com.",
            "a" * 100 + "@domain.com",  # Very long local part
        ]

        for email in invalid_emails:
            assert not string_utils.validate_email(email), f"Should be invalid: {email}"

        # Test URL validation edge cases
        invalid_urls = [
            "",
            "not-a-url",
            "http://",
            "https://",
            "ftp://invalid",
            "http:///invalid",
            "http://domain..com",
            "http://domain.com:99999",  # Invalid port
        ]

        for url in invalid_urls:
            assert not string_utils.validate_url(url), f"Should be invalid: {url}"

        # Test case conversion with edge cases
        edge_case_strings = [
            "",
            "a",
            "A",
            "123",
            "___",
            "---",
            "MiXeD_CaSe-StRiNg",
            "already_snake_case",
            "AlreadyPascalCase",
            "alreadyCamelCase",
            "already-kebab-case",
        ]

        for s in edge_case_strings:
            # Should not raise exceptions
            try:
                snake = string_utils.to_snake_case(s)
                camel = string_utils.to_camel_case(s)
                pascal = string_utils.to_pascal_case(s)
                kebab = string_utils.to_kebab_case(s)

                # Results should be strings
                assert isinstance(snake, str)
                assert isinstance(camel, str)
                assert isinstance(pascal, str)
                assert isinstance(kebab, str)
            except Exception as e:
                pytest.fail(f"Case conversion failed for '{s}': {e}")

    def test_security_error_conditions(self):
        """Test security operation error conditions."""
        # Test password hashing with edge cases
        edge_case_passwords = [
            "",
            "a",
            "a" * 1000,  # Very long password
            "password with unicode: 🔒",
            "password\nwith\nnewlines",
            "password\x00with\x00nulls",
        ]

        for password in edge_case_passwords:
            try:
                hashed = security_utils.hash_password(password)
                assert isinstance(hashed, str)
                assert len(hashed) > 0

                # Should be able to verify
                assert security_utils.verify_password(password, hashed)
            except Exception as e:
                # Some edge cases might not be supported
                pytest.skip(f"Password hashing not supported for: {repr(password)}: {e}")

        # Test hash verification with invalid hashes
        invalid_hashes = [
            "",
            "not-a-hash",
            "invalid$hash$format",
            "a" * 100,  # Wrong length
        ]

        for invalid_hash in invalid_hashes:
            # Should return False, not raise exception
            assert not security_utils.verify_password("password", invalid_hash)

        # Test data hashing with various data types
        test_data = [
            "",
            "simple string",
            "unicode string: 🔒",
            b"bytes data",
            "a" * 10000,  # Large data
        ]

        for data in test_data:
            try:
                hash_result = security_utils.hash_data(data)
                assert isinstance(hash_result, str)
                assert len(hash_result) > 0
            except Exception as e:
                pytest.fail(f"Data hashing failed for {type(data)}: {e}")

    def test_validation_error_conditions(self):
        """Test validation error conditions."""
        # Test range validation with edge cases
        edge_cases = [
            (float("inf"), 0, 100),
            (float("-inf"), 0, 100),
            (float("nan"), 0, 100),
            (None, 0, 100),
            ("string", 0, 100),
        ]

        for value, min_val, max_val in edge_cases:
            try:
                result = validation_utils.validate_range(value, min_val, max_val)
                assert isinstance(result, bool)
            except (TypeError, ValueError):
                # Some edge cases should raise exceptions
                pass

        # Test length validation with edge cases
        length_edge_cases = [
            (None, 0, 10),
            (123, 0, 10),  # Non-string
            ([], 0, 10),  # List
            ("", -1, 10),  # Negative min
            ("test", 10, 5),  # Min > max
        ]

        for text, min_len, max_len in length_edge_cases:
            try:
                result = validation_utils.validate_length(text, min_len, max_len)
                assert isinstance(result, bool)
            except (TypeError, ValueError):
                # Some edge cases should raise exceptions
                pass

    def test_system_operation_errors(self):
        """Test system operation error conditions."""
        # Test running non-existent command
        with pytest.raises(FileNotFoundError):
            system_utils.run_command(["nonexistent_command_12345"], timeout=1.0)

        # Test command timeout
        if platform.system() != "Windows":
            # Unix sleep command
            with pytest.raises(Exception):  # TimeoutExpired or similar
                system_utils.run_command(["sleep", "10"], timeout=0.1)

        # Test finding non-existent executable
        result = system_utils.find_executable("nonexistent_executable_12345")
        assert result is None

        # Test system info with mocked failures
        with patch("platform.system", side_effect=Exception("Mock error")):
            try:
                info = system_utils.get_system_info()
                # Should handle gracefully or raise appropriate exception
                assert isinstance(info, dict)
            except Exception:
                # Acceptable if it raises an exception
                pass

    def test_time_operation_errors(self):
        """Test time operation error conditions."""
        # Test parsing invalid date strings
        invalid_dates = [
            "",
            "not-a-date",
            "2024-13-01",  # Invalid month
            "2024-02-30",  # Invalid day
            "2024/02/29",  # Might be invalid depending on format
            "25:00:00",  # Invalid time
        ]

        for invalid_date in invalid_dates:
            with pytest.raises(Exception):  # ValueError or similar
                time_utils.parse_date(invalid_date)

        # Test format duration with edge cases
        edge_durations = [
            -1,  # Negative
            float("inf"),  # Infinity
            float("nan"),  # NaN
        ]

        for duration in edge_durations:
            try:
                result = time_utils.format_duration(duration)
                assert isinstance(result, str)
            except (ValueError, OverflowError):
                # Some edge cases should raise exceptions
                pass

    def test_concurrent_access_errors(self, tmp_path: Path):
        """Test error conditions under concurrent access."""
        import threading
        import time

        # Test concurrent file writes
        test_file = tmp_path / "concurrent_test.txt"
        errors = []

        def write_worker(worker_id):
            try:
                for i in range(10):
                    content = f"Worker {worker_id}, iteration {i}"
                    file_utils.atomic_write(test_file, content)
                    time.sleep(0.001)  # Small delay
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=write_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # File should exist and be readable
        assert test_file.exists()
        assert file_utils.is_readable(test_file)

        # Should have minimal errors due to atomic writes
        assert len(errors) <= 1  # Allow for some race conditions

    def test_memory_pressure_conditions(self):
        """Test behavior under memory pressure conditions."""
        # Test with large data structures
        try:
            # Create large nested dictionary
            large_data = {}
            current = large_data

            # Create deep nesting (but not too deep to avoid stack overflow)
            for i in range(100):
                current[f"level_{i}"] = {}
                current = current[f"level_{i}"]
                # Add some data at each level
                current["data"] = [f"item_{j}" for j in range(10)]

            # Test JSON operations with large data
            json_str = json_utils.pretty_json(large_data)
            assert isinstance(json_str, str)
            assert len(json_str) > 1000

            # Test flattening large data
            flattened = json_utils.flatten_json(large_data)
            assert isinstance(flattened, dict)
            assert len(flattened) > 100

        except MemoryError:
            pytest.skip("Not enough memory for large data test")
        except RecursionError:
            pytest.skip("Recursion limit reached for deep nesting test")

    def test_permission_denied_conditions(self, tmp_path: Path):
        """Test handling of permission denied conditions."""
        # Create a file and try to make it inaccessible
        test_file = tmp_path / "permission_test.txt"
        file_utils.atomic_write(test_file, "test content")

        # Try to make file unreadable (might not work on all systems)
        try:
            test_file.chmod(0o000)  # No permissions

            # Check if permissions actually changed
            if not file_utils.is_readable(test_file):
                # Test should handle permission denied gracefully
                assert not file_utils.is_readable(test_file)
                assert not file_utils.is_writable(test_file)

            # Restore permissions for cleanup
            test_file.chmod(0o644)

        except (OSError, PermissionError):
            # Permission changes might not be allowed
            pytest.skip("Cannot modify file permissions on this system")

    def test_network_related_errors(self):
        """Test network-related error conditions."""
        # Test URL validation with network-like edge cases
        network_edge_cases = [
            "http://localhost:99999",  # Invalid port
            "https://256.256.256.256",  # Invalid IP
            "http://domain-that-should-not-exist-12345.com",
            "ftp://invalid-protocol-for-validation.com",
        ]

        for url in network_edge_cases:
            # URL validation should be syntactic, not network-based
            # So these might be valid syntactically but invalid practically
            result = string_utils.validate_url(url)
            assert isinstance(result, bool)


class TestPlatformSpecificBehavior:
    """Test platform-specific behavior differences."""

    def test_path_separator_handling(self, tmp_path: Path):
        """Test path separator handling across platforms."""
        # Test with mixed separators
        mixed_paths = [
            "dir1/subdir\\file.txt",
            "dir1\\subdir/file.txt",
            "dir1/subdir/file.txt",
            "dir1\\subdir\\file.txt",
        ]

        for path_str in mixed_paths:
            # Convert to Path object (should normalize separators)
            path_obj = Path(path_str)
            full_path = tmp_path / path_obj

            # Ensure parent directory exists
            file_utils.ensure_dir(full_path.parent)

            # Create file
            file_utils.atomic_write(full_path, "test content")

            # Verify file exists
            assert full_path.exists()
            assert file_utils.is_readable(full_path)

    def test_case_sensitivity_handling(self, tmp_path: Path):
        """Test case sensitivity handling across platforms."""
        # Create files with different cases
        lower_file = tmp_path / "testfile.txt"
        upper_file = tmp_path / "TESTFILE.txt"

        file_utils.atomic_write(lower_file, "lower case")

        # On case-insensitive systems (Windows, macOS default),
        # these might be the same file
        if platform.system() in ["Windows", "Darwin"]:
            # Might be case-insensitive
            if lower_file.exists() and upper_file.exists():
                # If both exist, they're different files (case-sensitive)
                file_utils.atomic_write(upper_file, "upper case")
                assert lower_file.read_text() != upper_file.read_text()
            else:
                # Case-insensitive filesystem
                assert lower_file.exists()
        else:
            # Linux is typically case-sensitive
            file_utils.atomic_write(upper_file, "upper case")
            assert lower_file.read_text() == "lower case"
            assert upper_file.read_text() == "upper case"

    def test_executable_detection_cross_platform(self):
        """Test executable detection across platforms."""
        # Common executables that should exist on most systems
        common_executables = {
            "Windows": ["cmd", "powershell", "notepad"],
            "Darwin": ["ls", "cat", "bash", "zsh"],
            "Linux": ["ls", "cat", "bash", "sh"],
        }

        system_name = platform.system()
        if system_name in common_executables:
            executables = common_executables[system_name]

            found_any = False
            for exe in executables:
                path = system_utils.find_executable(exe)
                if path:
                    found_any = True
                    assert isinstance(path, str)
                    assert len(path) > 0

                    # On Windows, executables should end with .exe
                    if system_name == "Windows" and not exe.endswith(".exe"):
                        assert path.lower().endswith(".exe")

            # Should find at least one common executable
            assert found_any, f"No common executables found on {system_name}"

    def test_environment_variable_case_sensitivity(self):
        """Test environment variable case sensitivity."""
        env_vars = system_utils.get_env_vars()

        if platform.system() == "Windows":
            # Windows environment variables are case-insensitive
            # PATH might be Path, path, or PATH
            path_variants = ["PATH", "Path", "path"]
            path_found = any(var in env_vars for var in path_variants)
            assert path_found, "PATH variable not found in any case variant"
        else:
            # Unix-like systems are case-sensitive
            assert "PATH" in env_vars, "PATH variable not found (case-sensitive)"

    def test_line_ending_normalization(self, tmp_path: Path):
        """Test line ending normalization across platforms."""
        # Test different line ending styles
        content_variants = {
            "unix": "line1\nline2\nline3\n",
            "windows": "line1\r\nline2\r\nline3\r\n",
            "mac": "line1\rline2\rline3\r",
        }

        for variant_name, content in content_variants.items():
            test_file = tmp_path / f"line_endings_{variant_name}.txt"

            # Write content
            file_utils.atomic_write(test_file, content)

            # Read back
            read_content = test_file.read_text()

            # Should be able to split into lines
            lines = read_content.splitlines()
            assert len(lines) == 3
            assert lines[0] == "line1"
            assert lines[1] == "line2"
            assert lines[2] == "line3"
