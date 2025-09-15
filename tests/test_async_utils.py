"""Tests for async_utils module."""

import asyncio
import tempfile
import time
from pathlib import Path

import pytest

from devtools_py.async_utils import (
    AsyncFileManager,
    async_to_sync,
    sync_to_async,
    gather_with_limit,
    retry_async,
)


class TestAsyncBridgeFunctions:
    """Test sync/async conversion functions."""

    def test_sync_to_async_basic(self):
        """Test basic sync to async conversion."""

        def sync_function(x: int) -> int:
            return x * 2

        async_func = sync_to_async(sync_function)

        async def test_async():
            result = await async_func(5)
            assert result == 10

        asyncio.run(test_async())

    def test_sync_to_async_with_args_kwargs(self):
        """Test sync to async conversion with args and kwargs."""

        def sync_function(a: int, b: int, multiplier: int = 1) -> int:
            return (a + b) * multiplier

        async_func = sync_to_async(sync_function)

        async def test_async():
            result = await async_func(3, 4, multiplier=2)
            assert result == 14

        asyncio.run(test_async())

    def test_sync_to_async_preserves_function_name(self):
        """Test that sync_to_async preserves function metadata."""

        def original_function(x: int) -> int:
            """Original function docstring."""
            return x

        async_func = sync_to_async(original_function)
        assert async_func.__name__ == "original_function"
        assert "Original function docstring" in async_func.__doc__

    def test_sync_to_async_with_exception(self):
        """Test sync to async conversion handles exceptions."""

        def failing_function():
            raise ValueError("Test error")

        async_func = sync_to_async(failing_function)

        async def test_async():
            with pytest.raises(ValueError, match="Test error"):
                await async_func()

        asyncio.run(test_async())

    def test_async_to_sync_basic(self):
        """Test basic async to sync conversion."""

        async def async_function(x: int) -> int:
            await asyncio.sleep(0.01)  # Small delay to ensure it's truly async
            return x * 2

        sync_func = async_to_sync(async_function)
        result = sync_func(5)
        assert result == 10

    def test_async_to_sync_with_args_kwargs(self):
        """Test async to sync conversion with args and kwargs."""

        async def async_function(a: int, b: int, multiplier: int = 1) -> int:
            await asyncio.sleep(0.01)
            return (a + b) * multiplier

        sync_func = async_to_sync(async_function)
        result = sync_func(3, 4, multiplier=2)
        assert result == 14

    def test_async_to_sync_preserves_function_name(self):
        """Test that async_to_sync preserves function metadata."""

        async def original_async_function(x: int) -> int:
            """Original async function docstring."""
            return x

        sync_func = async_to_sync(original_async_function)
        assert sync_func.__name__ == "original_async_function"
        assert "Original async function docstring" in sync_func.__doc__

    def test_async_to_sync_with_exception(self):
        """Test async to sync conversion handles exceptions."""

        async def failing_async_function():
            await asyncio.sleep(0.01)
            raise ValueError("Async test error")

        sync_func = async_to_sync(failing_async_function)

        with pytest.raises(ValueError, match="Async test error"):
            sync_func()

    def test_roundtrip_conversion(self):
        """Test converting sync -> async -> sync works correctly."""

        def original_sync(x: int) -> int:
            return x * 3

        # Convert sync to async, then back to sync
        async_version = sync_to_async(original_sync)
        back_to_sync = async_to_sync(async_version)

        result = back_to_sync(4)
        assert result == 12

    def test_async_to_sync_in_async_context(self):
        """Test async_to_sync behavior when called from async context."""

        async def inner_async(x: int) -> int:
            await asyncio.sleep(0.01)
            return x * 2

        sync_func = async_to_sync(inner_async)

        async def outer_async():
            # This should work even when called from async context
            return sync_func(6)

        result = asyncio.run(outer_async())
        assert result == 12

    def test_sync_to_async_performance(self):
        """Test that sync_to_async doesn't block the event loop."""

        def slow_sync_function():
            time.sleep(0.1)  # Simulate slow operation
            return "done"

        async_func = sync_to_async(slow_sync_function)

        async def test_concurrent():
            # Start multiple async operations
            tasks = [async_func() for _ in range(3)]
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            end_time = time.time()

            # Should complete in roughly 0.1 seconds (concurrent), not 0.3 (sequential)
            assert end_time - start_time < 0.2
            assert all(result == "done" for result in results)

        asyncio.run(test_concurrent())

    def test_sync_to_async_with_none_return(self):
        """Test sync_to_async with function that returns None."""

        def void_function():
            pass

        async_func = sync_to_async(void_function)

        async def test_async():
            result = await async_func()
            assert result is None

        asyncio.run(test_async())

    def test_async_to_sync_with_none_return(self):
        """Test async_to_sync with function that returns None."""

        async def void_async_function():
            await asyncio.sleep(0.01)

        sync_func = async_to_sync(void_async_function)
        result = sync_func()
        assert result is None


class TestAsyncUtilsIntegration:
    """Integration tests for async utilities."""

    def test_mixed_sync_async_workflow(self):
        """Test a workflow mixing sync and async functions."""

        def process_data(data: list[int]) -> list[int]:
            return [x * 2 for x in data]

        async def fetch_data() -> list[int]:
            await asyncio.sleep(0.01)
            return [1, 2, 3, 4, 5]

        async def save_data(data: list[int]) -> str:
            await asyncio.sleep(0.01)
            return f"Saved {len(data)} items"

        # Convert functions for mixed usage
        async_process = sync_to_async(process_data)
        sync_fetch = async_to_sync(fetch_data)
        sync_save = async_to_sync(save_data)

        # Test sync workflow
        data = sync_fetch()
        processed = process_data(data)
        result = sync_save(processed)
        assert result == "Saved 5 items"
        assert processed == [2, 4, 6, 8, 10]

        # Test async workflow
        async def async_workflow():
            data = await fetch_data()
            processed = await async_process(data)
            result = await save_data(processed)
            return result, processed

        result, processed = asyncio.run(async_workflow())
        assert result == "Saved 5 items"
        assert processed == [2, 4, 6, 8, 10]


class TestAsyncFileManager:
    """Test AsyncFileManager class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def async_fm(self):
        """Create AsyncFileManager instance."""
        return AsyncFileManager()

    def test_init_default_encoding(self):
        """Test AsyncFileManager initialization with default encoding."""
        fm = AsyncFileManager()
        assert fm.encoding == "utf-8"

    def test_init_custom_encoding(self):
        """Test AsyncFileManager initialization with custom encoding."""
        fm = AsyncFileManager(encoding="latin-1")
        assert fm.encoding == "latin-1"

    def test_read_write_text_basic(self, async_fm, temp_dir):
        """Test basic text read/write operations."""
        test_file = temp_dir / "test.txt"
        test_content = "Hello, async world!"

        async def test_async():
            await async_fm.write_text(test_file, test_content)
            content = await async_fm.read_text(test_file)
            assert content == test_content

        asyncio.run(test_async())

    def test_read_write_text_with_encoding(self, temp_dir):
        """Test text operations with custom encoding."""
        fm = AsyncFileManager(encoding="latin-1")
        test_file = temp_dir / "test_encoding.txt"
        test_content = "Héllo, wörld!"

        async def test_async():
            await fm.write_text(test_file, test_content)
            content = await fm.read_text(test_file)
            assert content == test_content

        asyncio.run(test_async())

    def test_write_text_creates_parents(self, async_fm, temp_dir):
        """Test that write_text creates parent directories."""
        nested_file = temp_dir / "nested" / "deep" / "test.txt"
        test_content = "Nested file content"

        async def test_async():
            await async_fm.write_text(nested_file, test_content, create_parents=True)
            assert nested_file.exists()
            content = await async_fm.read_text(nested_file)
            assert content == test_content

        asyncio.run(test_async())

    def test_write_text_no_create_parents(self, async_fm, temp_dir):
        """Test write_text with create_parents=False."""
        nested_file = temp_dir / "nonexistent" / "test.txt"
        test_content = "Should fail"

        async def test_async():
            with pytest.raises(FileNotFoundError):
                await async_fm.write_text(nested_file, test_content, create_parents=False)

        asyncio.run(test_async())

    def test_read_write_bytes(self, async_fm, temp_dir):
        """Test binary read/write operations."""
        test_file = temp_dir / "test.bin"
        test_content = b"Binary content \x00\x01\x02"

        async def test_async():
            await async_fm.write_bytes(test_file, test_content)
            content = await async_fm.read_bytes(test_file)
            assert content == test_content

        asyncio.run(test_async())

    def test_copy_file(self, async_fm, temp_dir):
        """Test file copying."""
        source_file = temp_dir / "source.txt"
        dest_file = temp_dir / "destination.txt"
        test_content = "Content to copy"

        async def test_async():
            await async_fm.write_text(source_file, test_content)
            await async_fm.copy_file(source_file, dest_file)

            source_content = await async_fm.read_text(source_file)
            dest_content = await async_fm.read_text(dest_file)

            assert source_content == dest_content == test_content

        asyncio.run(test_async())

    def test_copy_file_creates_parents(self, async_fm, temp_dir):
        """Test that copy_file creates parent directories."""
        source_file = temp_dir / "source.txt"
        dest_file = temp_dir / "nested" / "deep" / "destination.txt"
        test_content = "Content to copy"

        async def test_async():
            await async_fm.write_text(source_file, test_content)
            await async_fm.copy_file(source_file, dest_file, create_parents=True)

            dest_content = await async_fm.read_text(dest_file)
            assert dest_content == test_content

        asyncio.run(test_async())

    def test_exists(self, async_fm, temp_dir):
        """Test file existence checking."""
        existing_file = temp_dir / "exists.txt"
        nonexistent_file = temp_dir / "does_not_exist.txt"

        async def test_async():
            await async_fm.write_text(existing_file, "I exist")

            assert await async_fm.exists(existing_file) is True
            assert await async_fm.exists(nonexistent_file) is False

        asyncio.run(test_async())

    def test_mkdir(self, async_fm, temp_dir):
        """Test directory creation."""
        new_dir = temp_dir / "new_directory"
        nested_dir = temp_dir / "nested" / "deep" / "directory"

        async def test_async():
            await async_fm.mkdir(new_dir)
            assert new_dir.is_dir()

            await async_fm.mkdir(nested_dir, parents=True)
            assert nested_dir.is_dir()

        asyncio.run(test_async())

    def test_mkdir_exist_ok(self, async_fm, temp_dir):
        """Test mkdir with exist_ok parameter."""
        new_dir = temp_dir / "test_dir"

        async def test_async():
            await async_fm.mkdir(new_dir)

            # Should not raise with exist_ok=True (default)
            await async_fm.mkdir(new_dir, exist_ok=True)

            # Should raise with exist_ok=False
            with pytest.raises(FileExistsError):
                await async_fm.mkdir(new_dir, exist_ok=False)

        asyncio.run(test_async())

    def test_remove(self, async_fm, temp_dir):
        """Test file removal."""
        test_file = temp_dir / "to_remove.txt"

        async def test_async():
            await async_fm.write_text(test_file, "Remove me")
            assert await async_fm.exists(test_file)

            await async_fm.remove(test_file)
            assert not await async_fm.exists(test_file)

        asyncio.run(test_async())

    def test_remove_nonexistent(self, async_fm, temp_dir):
        """Test removing nonexistent file raises error."""
        nonexistent_file = temp_dir / "does_not_exist.txt"

        async def test_async():
            with pytest.raises(FileNotFoundError):
                await async_fm.remove(nonexistent_file)

        asyncio.run(test_async())

    def test_list_dir(self, async_fm, temp_dir):
        """Test directory listing."""
        # Create some test files
        files = ["file1.txt", "file2.txt", "file3.txt"]

        async def test_async():
            for filename in files:
                await async_fm.write_text(temp_dir / filename, f"Content of {filename}")

            contents = await async_fm.list_dir(temp_dir)
            content_names = {path.name for path in contents}

            assert len(contents) >= len(files)  # May have other files
            for filename in files:
                assert filename in content_names

        asyncio.run(test_async())

    def test_list_dir_nonexistent(self, async_fm, temp_dir):
        """Test listing nonexistent directory raises error."""
        nonexistent_dir = temp_dir / "does_not_exist"

        async def test_async():
            with pytest.raises(FileNotFoundError):
                await async_fm.list_dir(nonexistent_dir)

        asyncio.run(test_async())

    def test_concurrent_operations(self, async_fm, temp_dir):
        """Test that multiple async operations can run concurrently."""
        files = [temp_dir / f"concurrent_{i}.txt" for i in range(5)]

        async def test_async():
            # Start multiple write operations concurrently
            write_tasks = [
                async_fm.write_text(file_path, f"Content {i}") for i, file_path in enumerate(files)
            ]

            start_time = time.time()
            await asyncio.gather(*write_tasks)
            write_time = time.time() - start_time

            # Read all files concurrently
            read_tasks = [async_fm.read_text(file_path) for file_path in files]

            start_time = time.time()
            contents = await asyncio.gather(*read_tasks)
            read_time = time.time() - start_time

            # Verify contents
            for i, content in enumerate(contents):
                assert content == f"Content {i}"

            # Operations should be reasonably fast (concurrent, not sequential)
            assert write_time < 1.0  # Should be much faster than 5 seconds
            assert read_time < 1.0

        asyncio.run(test_async())

    def test_error_handling(self, async_fm, temp_dir):
        """Test error handling in async operations."""

        async def test_async():
            # Test reading nonexistent file
            with pytest.raises(FileNotFoundError):
                await async_fm.read_text(temp_dir / "nonexistent.txt")

            # Test reading bytes from nonexistent file
            with pytest.raises(FileNotFoundError):
                await async_fm.read_bytes(temp_dir / "nonexistent.bin")

            # Test copying nonexistent file
            with pytest.raises(FileNotFoundError):
                await async_fm.copy_file(temp_dir / "nonexistent.txt", temp_dir / "destination.txt")

        asyncio.run(test_async())


class TestAsyncUtilityFunctions:
    """Test async utility functions."""

    def test_gather_with_limit_basic(self):
        """Test basic gather_with_limit functionality."""

        async def slow_task(value: int, delay: float = 0.01) -> int:
            await asyncio.sleep(delay)
            return value * 2

        async def test_async():
            tasks = [slow_task(i) for i in range(5)]
            results = await gather_with_limit(3, *tasks)
            assert results == [0, 2, 4, 6, 8]

        asyncio.run(test_async())

    def test_gather_with_limit_empty(self):
        """Test gather_with_limit with empty input."""

        async def test_async():
            results = await gather_with_limit(3)
            assert results == []

        asyncio.run(test_async())

    def test_gather_with_limit_invalid_limit(self):
        """Test gather_with_limit with invalid limit."""

        async def dummy_task():
            return 1

        async def test_async():
            with pytest.raises(ValueError, match="Limit must be at least 1"):
                await gather_with_limit(0, dummy_task())

        asyncio.run(test_async())

    def test_gather_with_limit_concurrency(self):
        """Test that gather_with_limit actually limits concurrency."""
        concurrent_count = 0
        max_concurrent = 0

        async def monitored_task(task_id: int) -> int:
            nonlocal concurrent_count, max_concurrent
            concurrent_count += 1
            max_concurrent = max(max_concurrent, concurrent_count)

            await asyncio.sleep(0.05)  # Simulate work

            concurrent_count -= 1
            return task_id

        async def test_async():
            nonlocal max_concurrent
            max_concurrent = 0

            tasks = [monitored_task(i) for i in range(10)]
            results = await gather_with_limit(3, *tasks)

            assert results == list(range(10))
            assert max_concurrent <= 3  # Should never exceed limit

        asyncio.run(test_async())

    def test_gather_with_limit_exception_handling(self):
        """Test gather_with_limit handles exceptions properly."""

        async def failing_task(should_fail: bool) -> str:
            await asyncio.sleep(0.01)
            if should_fail:
                raise ValueError("Task failed")
            return "success"

        async def test_async():
            tasks = [
                failing_task(False),
                failing_task(True),
                failing_task(False),
            ]

            with pytest.raises(ValueError, match="Task failed"):
                await gather_with_limit(2, *tasks)

        asyncio.run(test_async())

    def test_retry_async_success_first_try(self):
        """Test retry_async when function succeeds on first try."""
        call_count = 0

        async def successful_func(value: int) -> int:
            nonlocal call_count
            call_count += 1
            return value * 2

        async def test_async():
            nonlocal call_count
            call_count = 0

            result = await retry_async(successful_func, retries=3, delay=0.01, value=5)
            assert result == 10
            assert call_count == 1

        asyncio.run(test_async())

    def test_retry_async_success_after_retries(self):
        """Test retry_async when function succeeds after some failures."""
        call_count = 0

        async def eventually_successful_func(value: int) -> int:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return value * 2

        async def test_async():
            nonlocal call_count
            call_count = 0

            result = await retry_async(
                eventually_successful_func,
                retries=3,
                delay=0.01,
                exceptions=(ConnectionError,),
                value=5,
            )
            assert result == 10
            assert call_count == 3

        asyncio.run(test_async())

    def test_retry_async_all_attempts_fail(self):
        """Test retry_async when all attempts fail."""
        call_count = 0

        async def always_failing_func() -> str:
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        async def test_async():
            nonlocal call_count
            call_count = 0

            with pytest.raises(ValueError, match="Always fails"):
                await retry_async(
                    always_failing_func, retries=2, delay=0.01, exceptions=(ValueError,)
                )

            assert call_count == 3  # Initial + 2 retries

        asyncio.run(test_async())

    def test_retry_async_specific_exceptions(self):
        """Test retry_async only retries on specific exceptions."""
        call_count = 0

        async def mixed_failure_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Retryable error")
            else:
                raise ValueError("Non-retryable error")

        async def test_async():
            nonlocal call_count
            call_count = 0

            # Should not retry ValueError
            with pytest.raises(ValueError, match="Non-retryable error"):
                await retry_async(
                    mixed_failure_func, retries=3, delay=0.01, exceptions=(ConnectionError,)
                )

            assert (
                call_count == 2
            )  # First call raises ConnectionError (retried), second raises ValueError (not retried)

        asyncio.run(test_async())

    def test_retry_async_backoff_factor(self):
        """Test retry_async backoff factor."""
        call_times = []

        async def timing_func() -> str:
            call_times.append(time.time())
            raise ConnectionError("Always fails")

        async def test_async():
            nonlocal call_times
            call_times = []

            with pytest.raises(ConnectionError):
                await retry_async(
                    timing_func,
                    retries=2,
                    delay=0.1,
                    backoff_factor=2.0,
                    exceptions=(ConnectionError,),
                )

            assert len(call_times) == 3  # Initial + 2 retries

            # Check that delays are approximately correct (with some tolerance)
            if len(call_times) >= 2:
                delay1 = call_times[1] - call_times[0]
                assert 0.08 <= delay1 <= 0.15  # ~0.1 seconds

            if len(call_times) >= 3:
                delay2 = call_times[2] - call_times[1]
                assert 0.18 <= delay2 <= 0.25  # ~0.2 seconds (2x backoff)

        asyncio.run(test_async())

    def test_retry_async_with_kwargs(self):
        """Test retry_async with function arguments."""

        async def func_with_args(a: int, b: int, multiplier: int = 1) -> int:
            return (a + b) * multiplier

        async def test_async():
            result = await retry_async(
                func_with_args, retries=1, delay=0.01, a=3, b=4, multiplier=2
            )
            assert result == 14

        asyncio.run(test_async())
