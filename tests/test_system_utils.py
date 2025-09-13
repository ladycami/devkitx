"""Tests for system_utils module."""

import asyncio
import platform
import subprocess
import sys
from unittest.mock import patch

import pytest

from dev_qol_toolkit.system_utils import (
    get_python_info,
    get_system_info,
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
            'os_name', 'os_version', 'platform', 'architecture', 
            'processor', 'hostname', 'username', 'cpu_count'
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
        assert result['os_name'] == platform.system()

    def test_get_system_info_architecture_matches_platform(self):
        """Test that architecture matches platform.machine()."""
        result = get_system_info()
        assert result['architecture'] == platform.machine()

    def test_get_system_info_handles_exceptions_gracefully(self):
        """Test that get_system_info handles exceptions gracefully."""
        with patch('platform.node', side_effect=Exception("Test error")):
            result = get_system_info()
            assert result['hostname'] == 'unknown'

    def test_get_system_info_cpu_count_is_numeric_string(self):
        """Test that cpu_count is a numeric string."""
        result = get_system_info()
        assert result['cpu_count'].isdigit()


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
            'version', 'version_info', 'implementation', 'compiler',
            'executable', 'prefix', 'path', 'build'
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
        assert result['version'] == sys.version

    def test_get_python_info_executable_matches_sys(self):
        """Test that executable matches sys.executable."""
        result = get_python_info()
        assert result['executable'] == sys.executable

    def test_get_python_info_implementation_matches_platform(self):
        """Test that implementation matches platform.python_implementation()."""
        result = get_python_info()
        assert result['implementation'] == platform.python_implementation()

    def test_get_python_info_version_info_format(self):
        """Test that version_info has correct format."""
        result = get_python_info()
        version_parts = result['version_info'].split('.')
        assert len(version_parts) == 3
        assert all(part.isdigit() for part in version_parts)

    def test_get_python_info_prefix_matches_sys(self):
        """Test that prefix matches sys.prefix."""
        result = get_python_info()
        assert result['prefix'] == sys.prefix


class TestRunCommand:
    """Tests for run_command function."""

    def test_run_command_success(self):
        """Test successful command execution."""
        result = run_command(['echo', 'hello'])
        assert result.returncode == 0
        assert 'hello' in result.stdout

    def test_run_command_with_args(self):
        """Test command execution with multiple arguments."""
        result = run_command(['echo', 'hello', 'world'])
        assert result.returncode == 0
        assert 'hello world' in result.stdout

    def test_run_command_empty_list_raises_error(self):
        """Test that empty command list raises ValueError."""
        with pytest.raises(ValueError, match="Command list cannot be empty"):
            run_command([])

    def test_run_command_nonexistent_command(self):
        """Test that nonexistent command raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Command 'nonexistent_command_xyz' not found in PATH"):
            run_command(['nonexistent_command_xyz'])

    def test_run_command_with_timeout(self):
        """Test command execution with timeout."""
        # This should complete quickly
        result = run_command(['echo', 'hello'], timeout=5.0)
        assert result.returncode == 0

    def test_run_command_timeout_expires(self):
        """Test that long-running command times out."""
        with pytest.raises(subprocess.TimeoutExpired):
            run_command(['sleep', '2'], timeout=0.1)

    def test_run_command_with_cwd(self, tmp_path):
        """Test command execution with working directory."""
        # Create a test file in temp directory
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        # Run ls/dir command in that directory
        if platform.system() == "Windows":
            result = run_command(['dir', '/b'], cwd=tmp_path)
        else:
            result = run_command(['ls'], cwd=tmp_path)
        
        assert result.returncode == 0
        assert 'test.txt' in result.stdout

    def test_run_command_failing_command(self):
        """Test that failing command raises CalledProcessError."""
        with pytest.raises(subprocess.CalledProcessError):
            run_command(['false'])  # 'false' command always returns 1


class TestRunCommandAsync:
    """Tests for run_command_async function."""

    def test_run_command_async_success(self):
        """Test successful async command execution."""
        async def _test():
            result = await run_command_async(['echo', 'hello'])
            assert result.returncode == 0
            assert 'hello' in result.stdout
        
        asyncio.run(_test())

    def test_run_command_async_with_args(self):
        """Test async command execution with multiple arguments."""
        async def _test():
            result = await run_command_async(['echo', 'hello', 'world'])
            assert result.returncode == 0
            assert 'hello world' in result.stdout
        
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
            with pytest.raises(FileNotFoundError, match="Command 'nonexistent_command_xyz' not found in PATH"):
                await run_command_async(['nonexistent_command_xyz'])
        
        asyncio.run(_test())

    def test_run_command_async_with_timeout(self):
        """Test async command execution with timeout."""
        async def _test():
            # This should complete quickly
            result = await run_command_async(['echo', 'hello'], timeout=5.0)
            assert result.returncode == 0
        
        asyncio.run(_test())

    def test_run_command_async_timeout_expires(self):
        """Test that long-running async command times out."""
        async def _test():
            with pytest.raises(asyncio.TimeoutError):
                await run_command_async(['sleep', '2'], timeout=0.1)
        
        asyncio.run(_test())

    def test_run_command_async_failing_command(self):
        """Test that failing async command raises CalledProcessError."""
        async def _test():
            with pytest.raises(subprocess.CalledProcessError):
                await run_command_async(['false'])  # 'false' command always returns 1
        
        asyncio.run(_test())


class TestCrossPlatformCompatibility:
    """Tests for cross-platform compatibility."""

    @pytest.mark.parametrize("os_name", ["Windows", "Darwin", "Linux"])
    def test_system_info_works_on_different_os(self, os_name):
        """Test that system info works on different operating systems."""
        with patch('platform.system', return_value=os_name):
            result = get_system_info()
            assert result['os_name'] == os_name

    def test_handles_missing_getpass_module(self):
        """Test that system info handles missing getpass gracefully."""
        with patch('getpass.getuser', side_effect=ImportError):
            result = get_system_info()
            # Should fall back to environment variables
            assert 'username' in result
            assert isinstance(result['username'], str)

    def test_handles_missing_environment_variables(self):
        """Test that system info handles missing environment variables."""
        with patch.dict('os.environ', {}, clear=True):
            with patch('getpass.getuser', side_effect=Exception):
                result = get_system_info()
                assert result['username'] == 'unknown'