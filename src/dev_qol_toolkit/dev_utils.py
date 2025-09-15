"""Development and debugging utilities for the dev-qol-toolkit.

This module provides utilities for profiling, debugging, testing,
and development workflow enhancement.
"""

import functools
import json
import random
import string
import time
import tracemalloc
from datetime import datetime, timedelta
from typing import Any, Callable, TypeVar

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
            
            print(f"{func.__name__} memory usage - Current: {current_mb:.2f}MB, Peak: {peak_mb:.2f}MB")
    
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
                key: _truncate_if_needed(value, current_depth + 1)
                for key, value in obj.items()
            }
        elif isinstance(obj, list):
            if current_depth >= max_depth:
                return f"<list with {len(obj)} items>"
            return [
                _truncate_if_needed(item, current_depth + 1)
                for item in obj
            ]
        elif isinstance(obj, tuple):
            if current_depth >= max_depth:
                return f"<tuple with {len(obj)} items>"
            return tuple(
                _truncate_if_needed(item, current_depth + 1)
                for item in obj
            )
        elif isinstance(obj, set):
            if current_depth >= max_depth:
                return f"<set with {len(obj)} items>"
            return {
                _truncate_if_needed(item, current_depth + 1)
                for item in obj
            }
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
        if data_type == str:
            # Generate random string
            length = random.randint(5, 15)
            return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        
        elif data_type == int:
            return random.randint(1, 1000)
        
        elif data_type == float:
            return round(random.uniform(0.0, 1000.0), 2)
        
        elif data_type == bool:
            return random.choice([True, False])
        
        elif data_type == datetime:
            # Generate random datetime in the past year
            start_date = datetime(2023, 1, 1)
            end_date = datetime.now()
            time_between = end_date - start_date
            days_between = time_between.days
            random_days = random.randrange(days_between)
            return start_date + timedelta(days=random_days)
        
        elif data_type == list:
            # Generate list of random strings
            list_length = random.randint(1, 5)
            return [_generate_value(str) for _ in range(list_length)]
        
        elif data_type == dict:
            # Generate simple dict with string keys and values
            dict_size = random.randint(1, 3)
            return {
                f"key_{i}": _generate_value(str)
                for i in range(dict_size)
            }
        
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
    """
    # Placeholder implementation
    raise NotImplementedError("Function will be implemented in task 8.3")


class MockHTTPServer:
    """Mock HTTP server for testing."""
    
    def __init__(self, responses: dict[str, Any]) -> None:
        """Initialize mock server with predefined responses.
        
        Args:
            responses: Dictionary mapping endpoints to responses
        """
        # Placeholder implementation
        raise NotImplementedError("Class will be implemented in task 8.3")
    
    def start(self) -> str:
        """Start the mock server.
        
        Returns:
            Server URL
        """
        # Placeholder implementation
        raise NotImplementedError("Method will be implemented in task 8.3")
    
    def stop(self) -> None:
        """Stop the mock server."""
        # Placeholder implementation
        raise NotImplementedError("Method will be implemented in task 8.3")