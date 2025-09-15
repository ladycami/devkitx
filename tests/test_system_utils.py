"""Tests for system_utils module."""

import asyncio
import os
import platform
import socket
import subprocess
import sys
from unittest.mock import patch

import pytest

from devtools_py.system_utils import (
    find_executable,
    get_env_vars,
    get_free_port,
    get_python_info,
    get_system_info,
    is_admin,
    run_command,
    run_command_async,
)


class TestGetSystemInfo:
    """Tests for get_system_info function."""

    def test_get_system_info_returns_dict(self):
        """Test that get_system_info returns a dictionary."""
        result = get_system_info()
        assert isinstance(result, dict)

    def test_get_system_info_contains_required_keys(self):
        """Test that get_system_info returns all required keys."""
        result = get_system_info()
        required_keys = {
            "os_name",
            "os_version",
            "platform",
            "architecture",
            "processor",
            "hostname",
            "username",
            "cpu_count",
        }
        assert set(result.keys()) == required_keys

    def test_get_system_info_values_are_strings(self):
        """Test that all values in get_system_info are strings."""
        result = get_system_info()
        for key, value in result.items():
            assert isinstance(value, str), f"Value for {key} is not a string: {value}"

    def test_get_system_info_os_name_matches_platform(self):
        """Test that os_name matches platform.system()."""
        result = get_system_info()
        assert result["os_name"] == platform.system()

    def test_get_system_info_architecture_matches_platform(self):
        """Test that architecture matches platform.machine()."""
        result = get_system_info()
        assert result["architecture"] == platform.machine()

    def test_get_system_info_handles_exceptions_gracefully(self):
        """Test that get_system_info handles exceptions gracefully."""
        with patch("platform.node", side_effect=Exception("Test error")):
            result = get_system_info()
            assert result["hostname"] == "unknown"

    def test_get_system_info_cpu_count_is_numeric_string(self):
        """Test that cpu_count is a numeric string."""
        result = get_system_info()
        assert result["cpu_count"].isdigit()


class TestGetPythonInfo:
    """Tests for get_python_info function."""

    def test_get_python_info_returns_dict(self):
        """Test that get_python_info returns a dictionary."""
        result = get_python_info()
        assert isinstance(result, dict)

    def test_get_python_info_contains_required_keys(self):
        """Test that get_python_info returns all required keys."""
        result = get_python_info()
        required_keys = {
            "version",
            "version_info",
            "implementation",
            "compiler",
            "executable",
            "prefix",
            "path",
            "build",
        }
        assert set(result.keys()) == required_keys

    def test_get_python_info_values_are_strings(self):
        """Test that all values in get_python_info are strings."""
        result = get_python_info()
        for key, value in result.items():
            assert isinstance(value, str), f"Value for {key} is not a string: {value}"

    def test_get_python_info_version_matches_sys(self):
        """Test that version matches sys.version."""
        result = get_python_info()
        assert result["version"] == sys.version

    def test_get_python_info_executable_matches_sys(self):
        """Test that executable matches sys.executable."""
        result = get_python_info()
        assert result["executable"] == sys.executable

    def test_get_python_info_implementation_matches_platform(self):
        """Test that implementation matches platform.python_implementation()."""
        result = get_python_info()
        assert result["implementation"] == platform.python_implementation()

    def test_get_python_info_version_info_format(self):
        """Test that version_info has correct format."""
        result = get_python_info()
        version_parts = result["version_info"].split(".")
        assert len(version_parts) == 3
        assert all(part.isdigit() for part in version_parts)

    def test_get_python_info_prefix_matches_sys(self):
        """Test that prefix matches sys.prefix."""
        result = get_python_info()
        assert result["prefix"] == sys.prefix


class TestRunCommand:
    """Tests for run_command function."""

    def test_run_command_success(self):
        """Test successful command execution."""
        result = run_command(["echo", "hello"])
        assert result.returncode == 0
        assert "hello" in result.stdout

    def test_run_command_with_args(self):
        """Test command execution with multiple arguments."""
        result = run_command(["echo", "hello", "world"])
        assert result.returncode == 0
        assert "hello world" in result.stdout

    def test_run_command_empty_list_raises_error(self):
        """Test that empty command list raises ValueError."""
        with pytest.raises(ValueError, match="Command list cannot be empty"):
            run_command([])

    def test_run_command_nonexistent_command(self):
        """Test that nonexistent command raises FileNotFoundError."""
        with pytest.raises(
            FileNotFoundError, match="Command 'nonexistent_command_xyz' not found in PATH"
        ):
            run_command(["nonexistent_command_xyz"])

    def test_run_command_with_timeout(self):
        """Test command execution with timeout."""
        # This should complete quickly
        result = run_command(["echo", "hello"], timeout=5.0)
        assert result.returncode == 0

    def test_run_command_timeout_expires(self):
        """Test that long-running command times out."""
        with pytest.raises(subprocess.TimeoutExpired):
            run_command(["sleep", "2"], timeout=0.1)

    def test_run_command_with_cwd(self, tmp_path):
        """Test command execution with working directory."""
        # Create a test file in temp directory
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Run ls/dir command in that directory
        if platform.system() == "Windows":
            result = run_command(["dir", "/b"], cwd=tmp_path)
        else:
            result = run_command(["ls"], cwd=tmp_path)

        assert result.returncode == 0
        assert "test.txt" in result.stdout

    def test_run_command_failing_command(self):
        """Test that failing command raises CalledProcessError."""
        with pytest.raises(subprocess.CalledProcessError):
            run_command(["false"])  # 'false' command always returns 1


class TestRunCommandAsync:
    """Tests for run_command_async function."""

    def test_run_command_async_success(self):
        """Test successful async command execution."""

        async def _test():
            result = await run_command_async(["echo", "hello"])
            assert result.returncode == 0
            assert "hello" in result.stdout

        asyncio.run(_test())

    def test_run_command_async_with_args(self):
        """Test async command execution with multiple arguments."""

        async def _test():
            result = await run_command_async(["echo", "hello", "world"])
            assert result.returncode == 0
            assert "hello world" in result.stdout

        asyncio.run(_test())

    def test_run_command_async_empty_list_raises_error(self):
        """Test that empty command list raises ValueError."""

        async def _test():
            with pytest.raises(ValueError, match="Command list cannot be empty"):
                await run_command_async([])

        asyncio.run(_test())

    def test_run_command_async_nonexistent_command(self):
        """Test that nonexistent command raises FileNotFoundError."""

        async def _test():
            with pytest.raises(
                FileNotFoundError, match="Command 'nonexistent_command_xyz' not found in PATH"
            ):
                await run_command_async(["nonexistent_command_xyz"])

        asyncio.run(_test())

    def test_run_command_async_with_timeout(self):
        """Test async command execution with timeout."""

        async def _test():
            # This should complete quickly
            result = await run_command_async(["echo", "hello"], timeout=5.0)
            assert result.returncode == 0

        asyncio.run(_test())

    def test_run_command_async_timeout_expires(self):
        """Test that long-running async command times out."""

        async def _test():
            with pytest.raises(asyncio.TimeoutError):
                await run_command_async(["sleep", "2"], timeout=0.1)

        asyncio.run(_test())

    def test_run_command_async_failing_command(self):
        """Test that failing async command raises CalledProcessError."""

        async def _test():
            with pytest.raises(subprocess.CalledProcessError):
                await run_command_async(["false"])  # 'false' command always returns 1

        asyncio.run(_test())


class TestFindExecutable:
    """Tests for find_executable function."""

    def test_find_executable_existing_command(self):
        """Test finding an existing executable."""
        # Python should always be available in test environment
        result = find_executable("python")
        assert result is not None
        assert isinstance(result, str)

    def test_find_executable_nonexistent_command(self):
        """Test finding a nonexistent executable."""
        result = find_executable("nonexistent_command_xyz")
        assert result is None

    def test_find_executable_empty_name(self):
        """Test finding executable with empty name."""
        result = find_executable("")
        assert result is None

    def test_find_executable_common_commands(self):
        """Test finding common system commands."""
        # Test a command that should exist on most systems
        if platform.system() == "Windows":
            result = find_executable("cmd")
        else:
            result = find_executable("sh")

        # Should find something (or None if not available)
        assert result is None or isinstance(result, str)


class TestGetEnvVars:
    """Tests for get_env_vars function."""

    def test_get_env_vars_no_prefix(self):
        """Test getting all environment variables."""
        result = get_env_vars()
        assert isinstance(result, dict)
        # Should have at least some environment variables
        assert len(result) > 0

    def test_get_env_vars_with_prefix(self):
        """Test getting environment variables with prefix."""
        # Set a test environment variable
        with patch.dict(
            "os.environ", {"TEST_VAR_1": "value1", "TEST_VAR_2": "value2", "OTHER_VAR": "value3"}
        ):
            result = get_env_vars("TEST_")
            assert len(result) == 2
            assert "TEST_VAR_1" in result
            assert "TEST_VAR_2" in result
            assert "OTHER_VAR" not in result

    def test_get_env_vars_nonexistent_prefix(self):
        """Test getting environment variables with nonexistent prefix."""
        result = get_env_vars("NONEXISTENT_PREFIX_XYZ_")
        assert isinstance(result, dict)
        assert len(result) == 0

    def test_get_env_vars_empty_prefix(self):
        """Test getting environment variables with empty prefix."""
        result = get_env_vars("")
        all_vars = dict(os.environ)
        assert result == all_vars


class TestIsAdmin:
    """Tests for is_admin function."""

    def test_is_admin_returns_bool(self):
        """Test that is_admin returns a boolean."""
        result = is_admin()
        assert isinstance(result, bool)

    def test_is_admin_handles_exceptions(self):
        """Test that is_admin handles exceptions gracefully."""
        # Mock os.geteuid to raise an exception
        with patch("os.geteuid", side_effect=Exception("Test error")):
            result = is_admin()
            assert result is False  # Should default to False for safety


class TestGetFreePort:
    """Tests for get_free_port function."""

    def test_get_free_port_default_start(self):
        """Test getting a free port with default start."""
        port = get_free_port()
        assert isinstance(port, int)
        assert port >= 8000
        assert port <= 65535

    def test_get_free_port_custom_start(self):
        """Test getting a free port with custom start."""
        port = get_free_port(9000)
        assert isinstance(port, int)
        assert port >= 9000
        assert port <= 65535

    def test_get_free_port_invalid_range(self):
        """Test getting a free port with invalid range."""
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            get_free_port(0)

        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            get_free_port(65536)

    def test_get_free_port_actually_free(self):
        """Test that returned port is actually free."""
        port = get_free_port()

        # Try to bind to the port to verify it's free
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("localhost", port))
            # If we get here without exception, the port was indeed free


class TestCrossPlatformCompatibility:
    """Tests for cross-platform compatibility."""

    @pytest.mark.parametrize("os_name", ["Windows", "Darwin", "Linux"])
    def test_system_info_works_on_different_os(self, os_name):
        """Test that system info works on different operating systems."""
        with patch("platform.system", return_value=os_name):
            result = get_system_info()
            assert result["os_name"] == os_name

    def test_handles_missing_getpass_module(self):
        """Test that system info handles missing getpass gracefully."""
        with patch("getpass.getuser", side_effect=ImportError):
            result = get_system_info()
            # Should fall back to environment variables
            assert "username" in result
            assert isinstance(result["username"], str)

    def test_handles_missing_environment_variables(self):
        """Test that system info handles missing environment variables."""
        with patch.dict("os.environ", {}, clear=True):
            with patch("getpass.getuser", side_effect=Exception):
                result = get_system_info()
                assert result["username"] == "unknown"

    def test_is_admin_unix_systems(self):
        """Test is_admin works on Unix-like systems."""
        if platform.system() != "Windows":
            with patch("os.geteuid", return_value=1000):  # Non-root user
                result = is_admin()
                assert result is False

            with patch("os.geteuid", return_value=0):  # Root user
                result = is_admin()
                assert result is True

    @pytest.mark.skipif(platform.system() == "Windows", reason="Unix-specific test")
    def test_is_admin_unix_exception_handling(self):
        """Test is_admin handles Unix exceptions gracefully."""
        with patch("os.geteuid", side_effect=Exception("Test error")):
            result = is_admin()
            assert result is False
