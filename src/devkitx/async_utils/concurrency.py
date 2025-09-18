"""Async concurrency control utilities for DevKitX.

This module provides utilities for controlling concurrency in async operations,
including semaphore-based limiting for async operations.
"""

import asyncio
from typing import Awaitable, TypeVar

T = TypeVar("T")

__all__ = [
    "gather_with_limit",
]


async def gather_with_limit(limit: int, *awaitables: Awaitable[T]) -> list[T]:
    """Execute awaitables with concurrency limit using semaphore.
    
    Executes multiple awaitable objects concurrently but limits the number
    of concurrent operations to prevent overwhelming the system.
    
    Args:
        limit: Maximum number of concurrent operations
        *awaitables: Awaitable objects to gather
        
    Returns:
        List of results in the same order as input awaitables
        
    Raises:
        ValueError: If limit is less than 1
        
    Example:
        >>> async def fetch_data(url: str) -> str:
        ...     await asyncio.sleep(0.1)  # Simulate API call
        ...     return f"Data from {url}"
        >>> 
        >>> urls = [f"http://api.example.com/{i}" for i in range(10)]
        >>> tasks = [fetch_data(url) for url in urls]
        >>> results = await gather_with_limit(3, *tasks)  # Max 3 concurrent
    """
    if limit < 1:
        raise ValueError("Limit must be at least 1")
        
    if not awaitables:
        return []
    
    # Use asyncio.Semaphore to limit concurrency
    semaphore = asyncio.Semaphore(limit)
    
    async def _guarded(awaitable: Awaitable[T]) -> T:
        async with semaphore:
            return await awaitable
    
    # Wrap all awaitables with semaphore and gather results
    return await asyncio.gather(*(_guarded(aw) for aw in awaitables))