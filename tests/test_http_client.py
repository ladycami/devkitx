"""Tests for devkitx.http_client."""

import httpx
import pytest

from devkitx.http_client import AsyncClient, Client


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
    custom_timeout = httpx.Timeout(10.0, connect=1.0, read=5.0)
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


def _mock_transport() -> httpx.MockTransport:
    return httpx.MockTransport(lambda request: httpx.Response(200))


@pytest.mark.parametrize(
    "url",
    ["http://example.com/", "http://localhost.evil.com/", "http://evil.com/?next=localhost"],
)
def test_plain_http_to_remote_host_warns(url):
    from devkitx.http_client import SecurityWarning

    with Client(transport=_mock_transport()) as client, pytest.warns(SecurityWarning):
        client.get(url)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/",
        "http://localhost:8000/",
        "http://127.0.0.1/",
        "http://[::1]/",
        "http://app.localhost/",
    ],
)
def test_https_and_loopback_do_not_warn(url):
    import warnings

    with Client(transport=_mock_transport()) as client, warnings.catch_warnings():
        warnings.simplefilter("error")
        client.get(url)


def test_request_accepts_httpx_url_objects():
    with Client(transport=_mock_transport()) as client:
        assert client.request("GET", httpx.URL("https://example.com/")).status_code == 200


@pytest.mark.asyncio
async def test_async_client_warns_on_plain_http():
    from devkitx.http_client import SecurityWarning

    async with AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(200))) as client:
        with pytest.warns(SecurityWarning):
            await client.get("http://example.com/")
