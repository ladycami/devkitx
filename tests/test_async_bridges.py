"""Tests for async bridge utilities."""

import asyncio
import pytest
from devkitx.async_utils.bridges import async_to_sync, sync_to_async


class TestAsyncToSync:
    """Test cases for async_to_sync function."""
    
    def test_async_to_sync_basic(self):
        """Test converting basic async function to sync."""
        async def async_add_one(x: int) -> int:
            await asyncio.sleep(0.001)  # Minimal async work
            return x + 1
        
        sync_fn = async_to_sync(async_add_one)
        result = sync_fn(2)
        assert result == 3
    
    def test_async_to_sync_with_multiple_args(self):
        """Test async_to_sync with multiple arguments."""
        async def async_multiply(x: int, y: int) -> int:
            await asyncio.sleep(0.001)
            return x * y
        
        sync_fn = async_to_sync(async_multiply)
        result = sync_fn(3, 4)
        assert result == 12
    
    def test_async_to_sync_with_kwargs(self):
        """Test async_to_sync with keyword arguments."""
        async def async_greet(name: str, greeting: str = "Hello") -> str:
            await asyncio.sleep(0.001)
            return f"{greeting}, {name}!"
        
        sync_fn = async_to_sync(async_greet)
        result = sync_fn("John", greeting="Hi")
        assert result == "Hi, John!"
    
    def test_async_to_sync_preserves_exceptions(self):
        """Test that async_to_sync preserves exceptions."""
        async def async_error():
            await asyncio.sleep(0.001)
            raise ValueError("Test error")
        
        sync_fn = async_to_sync(async_error)
        with pytest.raises(ValueError, match="Test error"):
            sync_fn()
    
    def test_async_to_sync_from_running_loop(self):
        """Test async_to_sync when called from within a running event loop."""
        async def async_add_one(x: int) -> int:
            await asyncio.sleep(0.001)
            return x + 1
        
        async def test_within_loop():
            sync_fn = async_to_sync(async_add_one)
            # This should work even from within an async context
            result = sync_fn(5)
            return result
        
        # Run the test within an event loop
        result = asyncio.run(test_within_loop())
        assert result == 6


class TestSyncToAsync:
    """Test cases for sync_to_async function."""
    
    @pytest.mark.asyncio
    async def test_sync_to_async_basic(self):
        """Test converting basic sync function to async."""
        def sync_multiply_two(x: int) -> int:
            return x * 2
        
        async_fn = sync_to_async(sync_multiply_two)
        result = await async_fn(3)
        assert result == 6
    
    @pytest.mark.asyncio
    async def test_sync_to_async_with_multiple_args(self):
        """Test sync_to_async with multiple arguments."""
        def sync_add(x: int, y: int, z: int = 0) -> int:
            return x + y + z
        
        async_fn = sync_to_async(sync_add)
        result = await async_fn(1, 2, z=3)
        assert result == 6
    
    @pytest.mark.asyncio
    async def test_sync_to_async_preserves_exceptions(self):
        """Test that sync_to_async preserves exceptions."""
        def sync_error():
            raise RuntimeError("Sync error")
        
        async_fn = sync_to_async(sync_error)
        with pytest.raises(RuntimeError, match="Sync error"):
            await async_fn()
    
    @pytest.mark.asyncio
    async def test_sync_to_async_cpu_intensive(self):
        """Test sync_to_async with CPU-intensive operation."""
        def cpu_intensive_task(n: int) -> int:
            # Simple CPU-intensive task
            total = 0
            for i in range(n):
                total += i
            return total
        
        async_fn = sync_to_async(cpu_intensive_task)
        result = await async_fn(1000)
        expected = sum(range(1000))
        assert result == expected
    
    @pytest.mark.asyncio
    async def test_sync_to_async_concurrent_execution(self):
        """Test that sync_to_async allows concurrent execution."""
        def slow_sync_task(delay_ms: int, value: int) -> int:
            import time
            time.sleep(delay_ms / 1000.0)  # Convert ms to seconds
            return value * 2
        
        async_fn = sync_to_async(slow_sync_task)
        
        # Run multiple tasks concurrently
        tasks = [
            async_fn(10, 1),  # 10ms delay, return 2
            async_fn(10, 2),  # 10ms delay, return 4
            async_fn(10, 3),  # 10ms delay, return 6
        ]
        
        import time
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Should complete in roughly 10ms (concurrent) rather than 30ms (sequential)
        elapsed_ms = (end_time - start_time) * 1000
        assert elapsed_ms < 50  # Allow some overhead, but should be much less than 30ms
        assert results == [2, 4, 6]


class TestBridgeIntegration:
    """Integration tests for bridge utilities."""
    
    def test_roundtrip_async_to_sync_to_async(self):
        """Test converting async -> sync -> async."""
        async def original_async(x: int) -> int:
            await asyncio.sleep(0.001)
            return x + 10
        
        # Convert async -> sync -> async
        sync_version = async_to_sync(original_async)
        async_version = sync_to_async(sync_version)
        
        # Test the roundtrip
        async def test_roundtrip():
            result = await async_version(5)
            return result
        
        result = asyncio.run(test_roundtrip())
        assert result == 15
    
    def test_roundtrip_sync_to_async_to_sync(self):
        """Test converting sync -> async -> sync."""
        def original_sync(x: int) -> int:
            return x + 20
        
        # Convert sync -> async -> sync
        async_version = sync_to_async(original_sync)
        sync_version = async_to_sync(async_version)
        
        # Test the roundtrip
        result = sync_version(5)
        assert result == 25