"""Performance benchmark tests for devtools_py."""

from __future__ import annotations
import time
import statistics
from pathlib import Path
from typing import Callable, Any

import pytest

from devtools_py import (
    json_utils,
    file_utils,
    string_utils,
    security_utils,
    data_utils,
    validation_utils,
)


class PerformanceBenchmark:
    """Helper class for performance benchmarking."""

    def __init__(self, name: str, target_time: float = 1.0):
        self.name = name
        self.target_time = target_time
        self.measurements = []

    def measure(self, func: Callable[[], Any], iterations: int = 10) -> dict[str, float]:
        """Measure function performance over multiple iterations."""
        times = []

        for _ in range(iterations):
            start_time = time.perf_counter()
            func()
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        return {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "stdev": statistics.stdev(times) if len(times) > 1 else 0.0,
        }

    def assert_performance(self, stats: dict[str, float]) -> None:
        """Assert that performance meets target."""
        assert stats["mean"] < self.target_time, (
            f"{self.name} performance too slow: {stats['mean']:.3f}s "
            f"(target: {self.target_time:.3f}s)"
        )


class TestJSONPerformance:
    """Performance tests for JSON utilities."""

    def test_json_save_load_performance(self, tmp_path: Path):
        """Test JSON save/load performance with various data sizes."""
        benchmark = PerformanceBenchmark("JSON save/load", target_time=0.5)

        # Small data
        small_data = {"key": "value", "number": 42}
        small_file = tmp_path / "small.json"

        def small_save_load():
            json_utils.save_json(small_data, small_file)
            return json_utils.load_json(small_file)

        stats = benchmark.measure(small_save_load, iterations=100)
        benchmark.assert_performance(stats)

        # Medium data
        medium_data = {
            "users": [{"id": i, "name": f"User {i}"} for i in range(100)],
            "config": {f"key_{i}": f"value_{i}" for i in range(50)},
        }
        medium_file = tmp_path / "medium.json"

        def medium_save_load():
            json_utils.save_json(medium_data, medium_file)
            return json_utils.load_json(medium_file)

        benchmark.target_time = 0.1
        stats = benchmark.measure(medium_save_load, iterations=10)
        benchmark.assert_performance(stats)

    def test_json_flatten_unflatten_performance(self):
        """Test JSON flatten/unflatten performance."""
        benchmark = PerformanceBenchmark("JSON flatten/unflatten", target_time=0.2)

        # Create nested data
        nested_data = {
            "level1": {
                "level2": {"level3": {f"key_{i}": f"value_{i}" for i in range(50)}},
                "array": [{"item": i, "data": f"data_{i}"} for i in range(20)],
            }
        }

        def flatten_unflatten():
            flattened = json_utils.flatten_json(nested_data)
            return json_utils.unflatten_json(flattened)

        stats = benchmark.measure(flatten_unflatten, iterations=50)
        benchmark.assert_performance(stats)

    def test_json_pretty_print_performance(self):
        """Test JSON pretty print performance."""
        benchmark = PerformanceBenchmark("JSON pretty print", target_time=0.1)

        # Large data structure
        large_data = {
            "metadata": {"version": "1.0", "created": "2024-01-01"},
            "data": [
                {
                    "id": i,
                    "attributes": {
                        "name": f"Item {i}",
                        "tags": [f"tag{j}" for j in range(i % 5)],
                        "properties": {f"prop_{j}": j * i for j in range(3)},
                    },
                }
                for i in range(100)
            ],
        }

        def pretty_print():
            return json_utils.pretty_json(large_data)

        stats = benchmark.measure(pretty_print, iterations=20)
        benchmark.assert_performance(stats)


class TestStringPerformance:
    """Performance tests for string utilities."""

    def test_case_conversion_performance(self):
        """Test string case conversion performance."""
        benchmark = PerformanceBenchmark("String case conversion", target_time=0.1)

        # Test strings of various lengths
        test_strings = [
            "simple_string",
            "this_is_a_longer_string_with_many_words",
            "VeryLongPascalCaseStringWithManyWordsAndComplexStructure",
            "extremely-long-kebab-case-string-with-many-hyphens-and-words-for-testing",
        ] * 25  # 100 strings total

        def convert_all_cases():
            results = []
            for s in test_strings:
                results.extend(
                    [
                        string_utils.to_snake_case(s),
                        string_utils.to_camel_case(s),
                        string_utils.to_pascal_case(s),
                        string_utils.to_kebab_case(s),
                    ]
                )
            return results

        stats = benchmark.measure(convert_all_cases, iterations=10)
        benchmark.assert_performance(stats)

    def test_string_validation_performance(self):
        """Test string validation performance."""
        benchmark = PerformanceBenchmark("String validation", target_time=0.2)

        # Mix of valid and invalid emails/URLs
        test_data = [
            ("test@example.com", "https://example.com"),
            ("invalid-email", "not-a-url"),
            ("user.name+tag@domain.co.uk", "https://subdomain.example.com/path?query=value"),
            ("", ""),
            ("@invalid", "http://"),
        ] * 50  # 250 pairs total

        def validate_all():
            results = []
            for email, url in test_data:
                results.extend([string_utils.validate_email(email), string_utils.validate_url(url)])
            return results

        stats = benchmark.measure(validate_all, iterations=20)
        benchmark.assert_performance(stats)

    def test_string_sanitization_performance(self):
        """Test string sanitization performance."""
        benchmark = PerformanceBenchmark("String sanitization", target_time=0.05)

        # Filenames with various problematic characters
        problematic_filenames = [
            "file<>name?.txt",
            "path/with\\slashes.doc",
            "file:with|pipes*.pdf",
            "normal_filename.txt",
            "file with spaces and (parentheses).jpg",
        ] * 50  # 250 filenames total

        def sanitize_all():
            return [string_utils.sanitize_filename(name) for name in problematic_filenames]

        stats = benchmark.measure(sanitize_all, iterations=50)
        benchmark.assert_performance(stats)


class TestFilePerformance:
    """Performance tests for file utilities."""

    def test_file_creation_performance(self, tmp_path: Path):
        """Test file creation performance."""
        benchmark = PerformanceBenchmark("File creation", target_time=1.0)

        file_content = "x" * 1024  # 1KB content

        def create_files():
            for i in range(50):
                file_path = tmp_path / f"perf_test_{i}.txt"
                file_utils.atomic_write(file_path, file_content)

        stats = benchmark.measure(create_files, iterations=5)
        benchmark.assert_performance(stats)

    def test_file_search_performance(self, tmp_path: Path):
        """Test file search performance."""
        benchmark = PerformanceBenchmark("File search", target_time=0.5)

        # Create many files first
        for i in range(100):
            (tmp_path / f"test_{i}.txt").write_text("content")
            (tmp_path / f"data_{i}.json").write_text("{}")
            (tmp_path / f"script_{i}.py").write_text("# comment")

        def search_files():
            txt_files = file_utils.glob_ext(tmp_path, "txt")
            json_files = file_utils.glob_ext(tmp_path, "json")
            py_files = file_utils.glob_ext(tmp_path, "py")
            return len(txt_files) + len(json_files) + len(py_files)

        stats = benchmark.measure(search_files, iterations=20)
        benchmark.assert_performance(stats)

    def test_file_copy_performance(self, tmp_path: Path):
        """Test file copy performance."""
        benchmark = PerformanceBenchmark("File copy", target_time=0.5)

        # Create source files
        source_dir = tmp_path / "source"
        dest_dir = tmp_path / "dest"
        file_utils.ensure_dir(source_dir)
        file_utils.ensure_dir(dest_dir)

        large_content = "x" * 10240  # 10KB content
        source_files = []

        for i in range(20):
            source_file = source_dir / f"large_file_{i}.txt"
            file_utils.atomic_write(source_file, large_content)
            source_files.append(source_file)

        def copy_files():
            for i, source_file in enumerate(source_files):
                dest_file = dest_dir / f"copy_{i}.txt"
                file_utils.copy_file(source_file, dest_file)

        stats = benchmark.measure(copy_files, iterations=5)
        benchmark.assert_performance(stats)


class TestSecurityPerformance:
    """Performance tests for security utilities."""

    def test_password_hashing_performance(self):
        """Test password hashing performance."""
        benchmark = PerformanceBenchmark(
            "Password hashing", target_time=5.0
        )  # Hashing is intentionally slow

        passwords = [f"password_{i}_with_complexity!" for i in range(10)]

        def hash_passwords():
            return [security_utils.hash_password(pwd) for pwd in passwords]

        stats = benchmark.measure(hash_passwords, iterations=3)
        benchmark.assert_performance(stats)

    def test_data_hashing_performance(self):
        """Test data hashing performance."""
        benchmark = PerformanceBenchmark("Data hashing", target_time=0.1)

        # Various data sizes
        small_data = "small test data"
        medium_data = "x" * 1024  # 1KB
        large_data = "x" * 10240  # 10KB

        test_data = [small_data] * 50 + [medium_data] * 20 + [large_data] * 5

        def hash_data():
            return [security_utils.hash_data(data) for data in test_data]

        stats = benchmark.measure(hash_data, iterations=10)
        benchmark.assert_performance(stats)

    def test_secret_generation_performance(self):
        """Test secret generation performance."""
        benchmark = PerformanceBenchmark("Secret generation", target_time=0.1)

        def generate_secrets():
            return [security_utils.generate_secret_key(32) for _ in range(100)]

        stats = benchmark.measure(generate_secrets, iterations=20)
        benchmark.assert_performance(stats)


class TestDataPerformance:
    """Performance tests for data utilities."""

    def test_deep_merge_performance(self):
        """Test deep merge performance."""
        benchmark = PerformanceBenchmark("Deep merge", target_time=0.2)

        # Create complex nested dictionaries
        dict1 = {
            "level1": {
                "level2": {
                    f"key_{i}": {"value": i, "metadata": {"created": f"2024-{i:02d}-01"}}
                    for i in range(50)
                }
            },
            "arrays": {"numbers": list(range(100)), "strings": [f"item_{i}" for i in range(50)]},
        }

        dict2 = {
            "level1": {
                "level2": {
                    f"key_{i}": {"updated": True, "metadata": {"modified": f"2024-{i:02d}-15"}}
                    for i in range(25, 75)  # Overlap with dict1
                }
            },
            "arrays": {"booleans": [True, False] * 25},
            "new_section": {"data": "new"},
        }

        def merge_dicts():
            return data_utils.deep_merge(dict1, dict2)

        stats = benchmark.measure(merge_dicts, iterations=20)
        benchmark.assert_performance(stats)

    def test_data_filtering_performance(self):
        """Test data filtering performance."""
        benchmark = PerformanceBenchmark("Data filtering", target_time=0.1)

        # Large dictionary with mixed data types
        large_dict = {
            f"key_{i}": {
                "id": i,
                "active": i % 2 == 0,
                "value": i * 1.5,
                "category": f"cat_{i % 5}",
                "metadata": {"created": i, "tags": [f"tag_{j}" for j in range(i % 3)]},
            }
            for i in range(200)
        }

        def filter_data():
            # Filter for active items
            active_filter = lambda k, v: isinstance(v, dict) and v.get("active", False)
            filtered = data_utils.filter_dict(large_dict, active_filter)

            # Group by category
            items = list(filtered.values())
            grouped = data_utils.group_by(items, lambda x: x["category"])

            return len(grouped)

        stats = benchmark.measure(filter_data, iterations=30)
        benchmark.assert_performance(stats)


class TestValidationPerformance:
    """Performance tests for validation utilities."""

    def test_range_validation_performance(self):
        """Test range validation performance."""
        benchmark = PerformanceBenchmark("Range validation", target_time=0.05)

        # Large number of values to validate
        test_values = list(range(-500, 1500))  # 2000 values

        def validate_ranges():
            results = []
            for val in test_values:
                results.extend(
                    [
                        validation_utils.validate_range(val, 0, 1000),
                        validation_utils.validate_range(val, -100, 100),
                        validation_utils.validate_range(val, 500, 1500),
                    ]
                )
            return results

        stats = benchmark.measure(validate_ranges, iterations=20)
        benchmark.assert_performance(stats)

    def test_length_validation_performance(self):
        """Test length validation performance."""
        benchmark = PerformanceBenchmark("Length validation", target_time=0.05)

        # Strings of various lengths
        test_strings = [
            "short",
            "medium length string",
            "this is a much longer string with many words and characters",
            "x" * 100,  # Very long string
            "",  # Empty string
        ] * 200  # 1000 strings total

        def validate_lengths():
            results = []
            for s in test_strings:
                results.extend(
                    [
                        validation_utils.validate_length(s, 0, 50),
                        validation_utils.validate_length(s, 5, 25),
                        validation_utils.validate_length(s, 10, 200),
                    ]
                )
            return results

        stats = benchmark.measure(validate_lengths, iterations=30)
        benchmark.assert_performance(stats)


class TestMemoryUsage:
    """Memory usage tests for critical operations."""

    def test_json_memory_usage(self, tmp_path: Path):
        """Test memory usage of JSON operations."""
        import tracemalloc

        # Large data structure
        large_data = {
            "items": [
                {
                    "id": i,
                    "data": f"item_{i}_" + "x" * 100,  # ~100 chars per item
                    "metadata": {
                        "tags": [f"tag_{j}" for j in range(5)],
                        "properties": {f"prop_{k}": k for k in range(10)},
                    },
                }
                for i in range(1000)  # 1000 items
            ]
        }

        json_file = tmp_path / "large_memory_test.json"

        # Measure memory usage during save
        tracemalloc.start()
        json_utils.save_json(large_data, json_file)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Memory usage should be reasonable (less than 50MB for this data size)
        assert (
            peak < 50 * 1024 * 1024
        ), f"JSON save used too much memory: {peak / 1024 / 1024:.1f}MB"

        # Measure memory usage during load
        tracemalloc.start()
        loaded_data = json_utils.load_json(json_file)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        assert (
            peak < 50 * 1024 * 1024
        ), f"JSON load used too much memory: {peak / 1024 / 1024:.1f}MB"
        assert loaded_data == large_data

    def test_string_processing_memory_usage(self):
        """Test memory usage of string processing operations."""
        import tracemalloc

        # Large number of strings
        test_strings = [f"test_string_number_{i}_with_some_content" for i in range(10000)]

        tracemalloc.start()

        # Process all strings
        results = []
        for s in test_strings:
            results.extend(
                [
                    string_utils.to_snake_case(s),
                    string_utils.to_camel_case(s),
                    string_utils.to_pascal_case(s),
                    string_utils.to_kebab_case(s),
                ]
            )

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Memory usage should be reasonable (less than 100MB)
        assert (
            peak < 100 * 1024 * 1024
        ), f"String processing used too much memory: {peak / 1024 / 1024:.1f}MB"
        assert len(results) == 40000  # 4 conversions * 10000 strings


class TestConcurrencyPerformance:
    """Test performance under concurrent access."""

    @pytest.mark.asyncio
    async def test_async_file_operations_performance(self, tmp_path: Path):
        """Test async file operations performance."""
        from devtools_py.async_utils import AsyncFileManager

        benchmark = PerformanceBenchmark("Async file operations", target_time=1.0)

        async_manager = AsyncFileManager()
        test_content = "test content for async operations"

        async def async_file_ops():
            tasks = []
            for i in range(20):
                file_path = tmp_path / f"async_test_{i}.txt"
                # Write file
                await async_manager.write_text(file_path, f"{test_content}_{i}")
                # Read file back
                content = await async_manager.read_text(file_path)
                assert f"{test_content}_{i}" in content

        def run_async_ops():
            import asyncio

            return asyncio.run(async_file_ops())

        stats = benchmark.measure(run_async_ops, iterations=5)
        benchmark.assert_performance(stats)


# Utility function to run all performance tests
def run_performance_suite():
    """Run all performance tests and generate a report."""
    import subprocess
    import sys

    print("Running performance test suite...")

    # Run performance tests
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_performance.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
    )

    print("Performance Test Results:")
    print("=" * 50)
    print(result.stdout)

    if result.stderr:
        print("Errors:")
        print(result.stderr)

    return result.returncode == 0


if __name__ == "__main__":
    run_performance_suite()
