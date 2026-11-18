"""Tests for devkitx.http_client."""

import pytest
import httpx
from devkitx.http_client import Client, AsyncClient, safe_get


def test_client_has_defaults():
    """Test that Client has production-ready defaults."""
    client = Client()
    
    # Check timeout defaults
    assert client.timeout.connect == 5.0
    assert client.timeout.read == 30.0
    assert client.timeout.write == 30.0
    assert client.timeout.pool == 10.0
    
    # Check limits
    assert client.limits.max_connections == 100
    assert client.limits.max_keepalive_connections == 20
    
    # Check other defaults
    assert client.follow_redirects is True
    assert client.verify is True


def test_async_client_has_defaults():
    """Test that AsyncClient has production-ready defaults."""
    client = AsyncClient()
    
    # Check timeout defaults
    assert client.timeout.connect == 5.0
    assert client.timeout.read == 30.0
    assert client.timeout.write == 30.0
    assert client.timeout.pool == 10.0
    
    # Check limits
    assert client.limits.max_connections == 100
    assert client.limits.max_keepalive_connections == 20


def test_client_custom_timeout():
    """Test that custom timeout overrides defaults."""
    custom_timeout = httpx.Timeout(connect=1.0, read=5.0)
    client = Client(timeout=custom_timeout)
    
    assert client.timeout.connect == 1.0
    assert client.timeout.read == 5.0


def test_client_custom_limits():
    """Test that custom limits override defaults."""
    custom_limits = httpx.Limits(max_connections=50)
    client = Client(limits=custom_limits)
    
    assert client.limits.max_connections == 50


@pytest.mark.asyncio
async def test_async_client_context_manager():
    """Test AsyncClient as context manager."""
    async with AsyncClient() as client:
        assert isinstance(client, httpx.AsyncClient)
        # Client should be properly configured
        assert client.timeout.connect == 5.0