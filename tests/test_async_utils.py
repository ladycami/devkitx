"""Tests for async_utils module."""

import asyncio
import time
from unittest.mock import patch

import pytest

from dev_qol_toolkit.async_utils import async_to_sync, sync_to_async


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