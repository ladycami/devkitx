"""Development and debugging utilities for DevKitX.

This module provides utilities for profiling, debugging, testing,
and development workflow enhancement.
"""

import functools
import json
import random
import string
import threading
import time
import tracemalloc
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable, TypeVar
from urllib.parse import urlparse

T = TypeVar("T")

__all__ = [
    "time_function",
    "profile_memory",
    "pretty_print_object",
    "generate_test_data",
    "benchmark_functions",
    "MockHTTPServer",
]


def time_function(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to time function execution.

    Args:
        func: Function to time

    Returns:
        Decorated function that prints execution time

    Example:
        >>> @time_function
        ... def slow_function():
        ...     time.sleep(0.1)
        ...     return "done"
        >>> result = slow_function()  # Prints: slow_function took 0.1001s
        >>> result
        'done'
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            print(f"{func.__name__} took {execution_time:.4f}s")

    return wrapper


def profile_memory(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to profile memory usage of function.

    Args:
        func: Function to profile

    Returns:
        Decorated function that prints memory usage

    Example:
        >>> @profile_memory
        ... def memory_intensive():
        ...     data = [i for i in range(10000)]
        ...     return len(data)
        >>> result = memory_intensive()  # Prints memory usage info
        >>> result
        10000
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        # Start memory tracing
        tracemalloc.start()

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # Get memory usage
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            # Convert bytes to MB for readability
            current_mb = current / 1024 / 1024
            peak_mb = peak / 1024 / 1024

            print(
                f"{func.__name__} memory usage - Current: {current_mb:.2f}MB, Peak: {peak_mb:.2f}MB"
            )

    return wrapper


def pretty_print_object(obj: Any, max_depth: int = 3) -> str:
    """Pretty print object with depth limit.

    Args:
        obj: Object to print
        max_depth: Maximum depth to traverse

    Returns:
        Pretty-printed string representation

    Example:
        >>> data = {"name": "John", "age": 30, "nested": {"city": "NYC"}}
        >>> print(pretty_print_object(data))
        {
          "name": "John",
          "age": 30,
          "nested": {
            "city": "NYC"
          }
        }
    """

    def _truncate_if_needed(obj: Any, current_depth: int) -> Any:
        """Recursively truncate object if max depth is exceeded."""
        if isinstance(obj, dict):
            if current_depth >= max_depth:
                return f"<dict with {len(obj)} items>"
            return {
                key: _truncate_if_needed(value, current_depth + 1) for key, value in obj.items()
            }
        elif isinstance(obj, list):
            if current_depth >= max_depth:
                return f"<list with {len(obj)} items>"
            return [_truncate_if_needed(item, current_depth + 1) for item in obj]
        elif isinstance(obj, tuple):
            if current_depth >= max_depth:
                return f"<tuple with {len(obj)} items>"
            return tuple(_truncate_if_needed(item, current_depth + 1) for item in obj)
        elif isinstance(obj, set):
            if current_depth >= max_depth:
                return f"<set with {len(obj)} items>"
            return {_truncate_if_needed(item, current_depth + 1) for item in obj}
        else:
            return obj

    # Truncate the object based on max_depth
    truncated_obj = _truncate_if_needed(obj, 0)

    # Try to use JSON for pretty printing if possible
    try:
        return json.dumps(truncated_obj, indent=2, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        # Fallback to repr if JSON serialization fails
        return repr(truncated_obj)


def generate_test_data(schema: dict[str, type], count: int = 10) -> list[dict[str, Any]]:
    """Generate test data based on schema.

    Args:
        schema: Schema defining data structure and types
        count: Number of test records to generate

    Returns:
        List of generated test data records

    Example:
        >>> schema = {"name": str, "age": int, "active": bool}
        >>> data = generate_test_data(schema, count=2)
        >>> len(data)
        2
        >>> all(isinstance(record["name"], str) for record in data)
        True
    """

    def _generate_value(data_type: type) -> Any:
        """Generate a random value for the given type."""
        if data_type is str:
            # Generate random string
            length = random.randint(5, 15)
            return "".join(random.choices(string.ascii_letters + string.digits, k=length))

        elif data_type is int:
            return random.randint(1, 1000)

        elif data_type is float:
            return round(random.uniform(0.0, 1000.0), 2)

        elif data_type is bool:
            return random.choice([True, False])

        elif data_type == datetime:
            # Generate random datetime in the past year
            start_date = datetime(2023, 1, 1)
            end_date = datetime.now()
            time_between = end_date - start_date
            days_between = time_between.days
            random_days = random.randrange(days_between)
            return start_date + timedelta(days=random_days)

        elif data_type is list:
            # Generate list of random strings
            list_length = random.randint(1, 5)
            return [_generate_value(str) for _ in range(list_length)]

        elif data_type is dict:
            # Generate simple dict with string keys and values
            dict_size = random.randint(1, 3)
            return {f"key_{i}": _generate_value(str) for i in range(dict_size)}

        else:
            # For unknown types, return a string representation
            return f"<{data_type.__name__}_value>"

    # Generate the specified number of records
    test_data = []
    for _ in range(count):
        record = {}
        for field_name, field_type in schema.items():
            record[field_name] = _generate_value(field_type)
        test_data.append(record)

    return test_data


def benchmark_functions(*funcs: Callable[[], Any], iterations: int = 1000) -> dict[str, float]:
    """Benchmark multiple functions.

    Args:
        *funcs: Functions to benchmark
        iterations: Number of iterations to run

    Returns:
        Dictionary mapping function names to average execution times

    Example:
        >>> def fast_func():
        ...     return sum([1, 2, 3])
        >>> def slow_func():
        ...     return sum(range(100))
        >>> results = benchmark_functions(fast_func, slow_func, iterations=100)
        >>> len(results)
        2
        >>> 'fast_func' in results
        True
    """
    results = {}

    for func in funcs:
        total_time = 0.0

        # Warm up run
        func()

        # Benchmark runs
        for _ in range(iterations):
            start_time = time.perf_counter()
            func()
            end_time = time.perf_counter()
            total_time += end_time - start_time

        # Calculate average time
        average_time = total_time / iterations
        results[func.__name__] = average_time

    return results


class MockHTTPServer:
    """Mock HTTP server for testing.

    Example:
        >>> responses = {
        ...     "/api/users": {"users": [{"id": 1, "name": "John"}]},
        ...     "/api/status": {"status": "ok"}
        ... }
        >>> server = MockHTTPServer(responses)
        >>> url = server.start()
        >>> # Make requests to url + "/api/users"
        >>> server.stop()
    """

    def __init__(self, responses: dict[str, Any]) -> None:
        """Initialize mock server with predefined responses.

        Args:
            responses: Dictionary mapping endpoints to responses
        """
        self.responses = responses
        self.server = None
        self.thread = None
        self.port = None

    def _create_handler(self):
        """Create a request handler class with access to responses."""
        responses = self.responses

        class MockRequestHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                # Suppress default logging
                pass

            def do_GET(self):
                """Handle GET requests."""
                parsed_url = urlparse(self.path)
                path = parsed_url.path

                if path in responses:
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()

                    response_data = responses[path]
                    if isinstance(response_data, dict):
                        response_json = json.dumps(response_data)
                    else:
                        response_json = str(response_data)

                    self.wfile.write(response_json.encode("utf-8"))
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"error": "Not found"}')

            def do_POST(self):
                """Handle POST requests."""
                parsed_url = urlparse(self.path)
                path = parsed_url.path

                # Read the request body (even if we don't use it)
                content_length = int(self.headers.get("Content-Length", 0))
                if content_length > 0:
                    self.rfile.read(content_length)

                if path in responses:
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()

                    response_data = responses[path]
                    if isinstance(response_data, dict):
                        response_json = json.dumps(response_data)
                    else:
                        response_json = str(response_data)

                    self.wfile.write(response_json.encode("utf-8"))
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"error": "Not found"}')

        return MockRequestHandler

    def start(self) -> str:
        """Start the mock server.

        Returns:
            Server URL
        """
        if self.server is not None:
            raise RuntimeError("Server is already running")

        # Find an available port
        self.server = HTTPServer(("localhost", 0), self._create_handler())
        self.port = self.server.server_address[1]

        # Start server in a separate thread
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

        return f"http://localhost:{self.port}"

    def stop(self) -> None:
        """Stop the mock server."""
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()
            self.server = None

        if self.thread is not None:
            self.thread.join(timeout=1.0)
            self.thread = None

        self.port = None
