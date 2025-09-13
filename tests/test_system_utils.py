"""Tests for system_utils module."""

import platform
import sys
from unittest.mock import patch

import pytest

from dev_qol_toolkit.system_utils import get_python_info, get_system_info


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