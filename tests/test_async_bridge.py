"""Tests for devkitx.async_bridge."""

import asyncio
import pytest
from devkitx.async_bridge import async_to_sync, sync_to_async


def test_async_to_sync():
    """Test converting async function to sync."""
    async def async_add(a, b):
        await asyncio.sleep(0.01)
        return a + b
    
    sync_add = async_to_sync(async_add)
    result = sync_add(2, 3)
    assert result == 5


@pytest.mark.asyncio
async def test_sync_to_async():
    """Test converting sync function to async."""
    def sync_multiply(a, b):
        return a * b
    
    async_multiply = sync_to_async(sync_multiply)
    result = await async_multiply(3, 4)
    assert result == 12


def test_async_to_sync_with_kwargs():
    """Test async_to_sync with keyword arguments."""
    async def async_greet(name, greeting="Hello"):
        await asyncio.sleep(0.01)
        return f"{greeting}, {name}!"
    
    sync_greet = async_to_sync(async_greet)
    result = sync_greet("World", greeting="Hi")
    assert result == "Hi, World!"


@pytest.mark.asyncio
async def test_sync_to_async_with_kwargs():
    """Test sync_to_async with keyword arguments."""
    def sync_format(template, **kwargs):
        return template.format(**kwargs)
    
    async_format = sync_to_async(sync_format)
    result = await async_format("Hello, {name}!", name="Alice")
    assert result == "Hello, Alice!"