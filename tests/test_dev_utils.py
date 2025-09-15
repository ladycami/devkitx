"""Tests for dev_utils module."""

import io
import sys
import time
from contextlib import redirect_stdout
from unittest.mock import patch

import pytest

from dev_qol_toolkit.dev_utils import profile_memory, time_function


class TestTimeFunctionDecorator:
    """Test cases for time_function decorator."""

    def test_time_function_basic(self):
        """Test that time_function decorator works and prints timing."""
        @time_function
        def test_func():
            time.sleep(0.01)  # Small delay to ensure measurable time
            return "result"

        # Capture stdout to check timing output
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            result = test_func()

        # Check function result is preserved
        assert result == "result"

        # Check timing output is printed
        output = captured_output.getvalue()
        assert "test_func took" in output
        assert "s" in output  # Should end with 's' for seconds

    def test_time_function_with_args(self):
        """Test time_function decorator with function arguments."""
        @time_function
        def add_numbers(a, b, multiplier=1):
            return (a + b) * multiplier

        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            result = add_numbers(2, 3, multiplier=2)

        assert result == 10
        output = captured_output.getvalue()
        assert "add_numbers took" in output

    def test_time_function_preserves_exceptions(self):
        """Test that time_function decorator preserves exceptions."""
        @time_function
        def failing_func():
            raise ValueError("Test error")

        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            with pytest.raises(ValueError, match="Test error"):
                failing_func()

        # Should still print timing even when exception occurs
        output = captured_output.getvalue()
        assert "failing_func took" in output

    def test_time_function_preserves_metadata(self):
        """Test that time_function decorator preserves function metadata."""
        @time_function
        def documented_func():
            """This is a test function."""
            return "test"

        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == "This is a test function."


class TestProfileMemoryDecorator:
    """Test cases for profile_memory decorator."""

    def test_profile_memory_basic(self):
        """Test that profile_memory decorator works and prints memory usage."""
        @profile_memory
        def memory_func():
            # Create some data to use memory
            data = [i for i in range(1000)]
            return len(data)

        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            result = memory_func()

        # Check function result is preserved
        assert result == 1000

        # Check memory output is printed
        output = captured_output.getvalue()
        assert "memory_func memory usage" in output
        assert "Current:" in output
        assert "Peak:" in output
        assert "MB" in output

    def test_profile_memory_with_args(self):
        """Test profile_memory decorator with function arguments."""
        @profile_memory
        def create_list(size):
            return list(range(size))

        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            result = create_list(500)

        assert len(result) == 500
        output = captured_output.getvalue()
        assert "create_list memory usage" in output

    def test_profile_memory_preserves_exceptions(self):
        """Test that profile_memory decorator preserves exceptions."""
        @profile_memory
        def failing_memory_func():
            data = [1, 2, 3]  # Use some memory
            raise RuntimeError("Memory test error")

        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            with pytest.raises(RuntimeError, match="Memory test error"):
                failing_memory_func()

        # Should still print memory usage even when exception occurs
        output = captured_output.getvalue()
        assert "failing_memory_func memory usage" in output

    def test_profile_memory_preserves_metadata(self):
        """Test that profile_memory decorator preserves function metadata."""
        @profile_memory
        def documented_memory_func():
            """This function uses memory."""
            return [1, 2, 3]

        assert documented_memory_func.__name__ == "documented_memory_func"
        assert documented_memory_func.__doc__ == "This function uses memory."

    @patch('tracemalloc.start')
    @patch('tracemalloc.stop')
    @patch('tracemalloc.get_traced_memory')
    def test_profile_memory_tracemalloc_calls(self, mock_get_traced, mock_stop, mock_start):
        """Test that profile_memory correctly uses tracemalloc."""
        mock_get_traced.return_value = (1024 * 1024, 2 * 1024 * 1024)  # 1MB current, 2MB peak

        @profile_memory
        def test_func():
            return "test"

        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            result = test_func()

        assert result == "test"
        mock_start.assert_called_once()
        mock_stop.assert_called_once()
        mock_get_traced.assert_called_once()

        output = captured_output.getvalue()
        assert "Current: 1.00MB" in output
        assert "Peak: 2.00MB" in output


class TestDecoratorCombination:
    """Test cases for combining decorators."""

    def test_combined_decorators(self):
        """Test that time_function and profile_memory can be combined."""
        @time_function
        @profile_memory
        def combined_func():
            data = list(range(100))
            time.sleep(0.01)
            return len(data)

        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            result = combined_func()

        assert result == 100
        output = captured_output.getvalue()
        
        # Should have both timing and memory output
        assert "combined_func took" in output
        assert "combined_func memory usage" in output