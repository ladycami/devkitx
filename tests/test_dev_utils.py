"""Tests for dev_utils module."""

import io
import json
import time
from contextlib import redirect_stdout
from datetime import datetime
from unittest.mock import patch

import pytest

from devtools_py.dev_utils import (
    MockHTTPServer,
    benchmark_functions,
    generate_test_data,
    pretty_print_object,
    profile_memory,
    time_function,
)


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

    @patch("tracemalloc.start")
    @patch("tracemalloc.stop")
    @patch("tracemalloc.get_traced_memory")
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


class TestPrettyPrintObject:
    """Test cases for pretty_print_object function."""

    def test_pretty_print_simple_dict(self):
        """Test pretty printing a simple dictionary."""
        data = {"name": "John", "age": 30}
        result = pretty_print_object(data)

        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed == data

        # Should be formatted (contain newlines)
        assert "\n" in result

    def test_pretty_print_nested_dict(self):
        """Test pretty printing nested dictionary within depth limit."""
        data = {"user": {"name": "John", "details": {"city": "NYC", "country": "USA"}}}
        result = pretty_print_object(data, max_depth=3)

        # Should preserve all data within depth limit
        parsed = json.loads(result)
        assert parsed == data

    def test_pretty_print_depth_limit(self):
        """Test that depth limit truncates deep nesting."""
        data = {"level1": {"level2": {"level3": {"level4": "too deep"}}}}
        result = pretty_print_object(data, max_depth=2)

        # Should truncate at max_depth
        assert "too deep" not in result
        assert "<dict with" in result

    def test_pretty_print_list(self):
        """Test pretty printing lists."""
        data = [1, 2, {"nested": "value"}]
        result = pretty_print_object(data)

        parsed = json.loads(result)
        assert parsed == data

    def test_pretty_print_complex_types(self):
        """Test pretty printing with non-JSON serializable types."""

        class CustomClass:
            def __init__(self, value):
                self.value = value

            def __repr__(self):
                return f"CustomClass({self.value})"

        data = {"custom": CustomClass(42)}
        result = pretty_print_object(data)

        # Should handle non-serializable objects gracefully
        assert "CustomClass(42)" in result

    def test_pretty_print_empty_containers(self):
        """Test pretty printing empty containers."""
        data = {"empty_dict": {}, "empty_list": [], "empty_str": ""}
        result = pretty_print_object(data)

        parsed = json.loads(result)
        assert parsed == data


class TestGenerateTestData:
    """Test cases for generate_test_data function."""

    def test_generate_basic_types(self):
        """Test generating data for basic types."""
        schema = {"name": str, "age": int, "height": float, "active": bool}

        data = generate_test_data(schema, count=5)

        assert len(data) == 5
        for record in data:
            assert isinstance(record["name"], str)
            assert isinstance(record["age"], int)
            assert isinstance(record["height"], float)
            assert isinstance(record["active"], bool)

    def test_generate_string_data(self):
        """Test string generation properties."""
        schema = {"text": str}
        data = generate_test_data(schema, count=10)

        # All strings should be different lengths (with high probability)
        lengths = [len(record["text"]) for record in data]
        assert min(lengths) >= 5
        assert max(lengths) <= 15

    def test_generate_numeric_data(self):
        """Test numeric data generation."""
        schema = {"number": int, "decimal": float}
        data = generate_test_data(schema, count=10)

        for record in data:
            assert 1 <= record["number"] <= 1000
            assert 0.0 <= record["decimal"] <= 1000.0

    def test_generate_datetime_data(self):
        """Test datetime generation."""
        schema = {"created_at": datetime}
        data = generate_test_data(schema, count=5)

        for record in data:
            assert isinstance(record["created_at"], datetime)
            # Should be within reasonable range
            assert record["created_at"].year >= 2023

    def test_generate_collection_data(self):
        """Test list and dict generation."""
        schema = {"tags": list, "metadata": dict}
        data = generate_test_data(schema, count=3)

        for record in data:
            assert isinstance(record["tags"], list)
            assert isinstance(record["metadata"], dict)
            assert 1 <= len(record["tags"]) <= 5
            assert 1 <= len(record["metadata"]) <= 3

    def test_generate_unknown_type(self):
        """Test handling of unknown types."""

        class CustomType:
            pass

        schema = {"custom": CustomType}
        data = generate_test_data(schema, count=2)

        for record in data:
            assert isinstance(record["custom"], str)
            assert "CustomType_value" in record["custom"]

    def test_generate_empty_schema(self):
        """Test generating data with empty schema."""
        data = generate_test_data({}, count=3)

        assert len(data) == 3
        for record in data:
            assert record == {}

    def test_generate_zero_count(self):
        """Test generating zero records."""
        schema = {"name": str}
        data = generate_test_data(schema, count=0)

        assert data == []


class TestBenchmarkFunctions:
    """Test cases for benchmark_functions function."""

    def test_benchmark_single_function(self):
        """Test benchmarking a single function."""

        def test_func():
            return sum([1, 2, 3, 4, 5])

        results = benchmark_functions(test_func, iterations=10)

        assert len(results) == 1
        assert "test_func" in results
        assert isinstance(results["test_func"], float)
        assert results["test_func"] > 0

    def test_benchmark_multiple_functions(self):
        """Test benchmarking multiple functions."""

        def fast_func():
            return 1 + 1

        def slow_func():
            time.sleep(0.001)  # Small delay
            return 2 + 2

        results = benchmark_functions(fast_func, slow_func, iterations=5)

        assert len(results) == 2
        assert "fast_func" in results
        assert "slow_func" in results

        # Slow function should take longer (though this might be flaky)
        assert results["slow_func"] > results["fast_func"]

    def test_benchmark_with_different_iterations(self):
        """Test benchmarking with different iteration counts."""

        def simple_func():
            return len([1, 2, 3])

        results_few = benchmark_functions(simple_func, iterations=5)
        results_many = benchmark_functions(simple_func, iterations=50)

        # Both should have the same function
        assert "simple_func" in results_few
        assert "simple_func" in results_many

        # Results should be positive numbers
        assert results_few["simple_func"] > 0
        assert results_many["simple_func"] > 0

    def test_benchmark_function_with_exception(self):
        """Test that benchmark handles functions that raise exceptions."""

        def failing_func():
            raise ValueError("Test error")

        # Should propagate the exception
        with pytest.raises(ValueError, match="Test error"):
            benchmark_functions(failing_func, iterations=1)

    def test_benchmark_preserves_function_names(self):
        """Test that benchmark uses actual function names."""

        def custom_named_function():
            return "result"

        results = benchmark_functions(custom_named_function, iterations=3)

        assert "custom_named_function" in results


class TestMockHTTPServer:
    """Test cases for MockHTTPServer class."""

    def test_server_initialization(self):
        """Test server initialization."""
        responses = {"/test": {"message": "hello"}}
        server = MockHTTPServer(responses)

        assert server.responses == responses
        assert server.server is None
        assert server.thread is None
        assert server.port is None

    def test_server_start_and_stop(self):
        """Test starting and stopping the server."""
        responses = {"/api/test": {"status": "ok"}}
        server = MockHTTPServer(responses)

        # Start server
        url = server.start()
        assert url.startswith("http://localhost:")
        assert server.server is not None
        assert server.thread is not None
        assert server.port is not None

        # Stop server
        server.stop()
        assert server.server is None
        assert server.thread is None
        assert server.port is None

    def test_server_double_start_raises_error(self):
        """Test that starting an already running server raises an error."""
        responses = {"/test": {"data": "value"}}
        server = MockHTTPServer(responses)

        server.start()

        with pytest.raises(RuntimeError, match="Server is already running"):
            server.start()

        server.stop()

    def test_server_stop_when_not_running(self):
        """Test that stopping a non-running server doesn't raise an error."""
        responses = {"/test": {"data": "value"}}
        server = MockHTTPServer(responses)

        # Should not raise an error
        server.stop()

    @pytest.mark.asyncio
    async def test_server_http_requests(self):
        """Test making HTTP requests to the mock server."""
        import httpx

        responses = {
            "/api/users": {"users": [{"id": 1, "name": "John"}]},
            "/api/status": {"status": "running"},
        }
        server = MockHTTPServer(responses)

        try:
            url = server.start()

            # Test GET request to existing endpoint
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/api/users")
                assert response.status_code == 200
                data = response.json()
                assert data == {"users": [{"id": 1, "name": "John"}]}

                # Test GET request to another endpoint
                response = await client.get(f"{url}/api/status")
                assert response.status_code == 200
                data = response.json()
                assert data == {"status": "running"}

                # Test GET request to non-existent endpoint
                response = await client.get(f"{url}/api/nonexistent")
                assert response.status_code == 404
                data = response.json()
                assert data == {"error": "Not found"}

        finally:
            server.stop()

    @pytest.mark.asyncio
    async def test_server_post_requests(self):
        """Test POST requests to the mock server."""
        import httpx

        responses = {"/api/create": {"id": 123, "created": True}}
        server = MockHTTPServer(responses)

        try:
            url = server.start()

            async with httpx.AsyncClient() as client:
                # Test POST request
                response = await client.post(f"{url}/api/create", json={"name": "test"})
                assert response.status_code == 200
                data = response.json()
                assert data == {"id": 123, "created": True}

        finally:
            server.stop()

    def test_server_with_string_responses(self):
        """Test server with non-dict responses."""
        responses = {"/api/simple": "simple string response"}
        server = MockHTTPServer(responses)

        # Should initialize without error
        assert server.responses == responses
