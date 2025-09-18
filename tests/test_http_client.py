"""Tests for HTTP client utilities."""

import pytest
from unittest.mock import patch, MagicMock

# Test both with and without httpx available
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    httpx = None
    HTTPX_AVAILABLE = False


class TestHttpClientDefaults:
    """Test HTTP client factory functions and their defaults."""
    
    @pytest.mark.skipif(not HTTPX_AVAILABLE, reason="httpx not available")
    def test_make_client_defaults(self):
        """Test that make_client creates client with safe defaults."""
        from devkitx.http_utils.client import make_client
        
        client = make_client()
        
        # Check timeout defaults
        assert client.timeout.connect == 10.0
        assert client.timeout.read == 15.0
        
        # Check connection limits via transport
        transport = client._transport
        assert transport._pool._max_keepalive_connections == 10
        assert transport._pool._max_connections == 100
        
        # Check other defaults
        assert client.base_url == ""
        assert client.follow_redirects is True
        
        client.close()
    
    @pytest.mark.skipif(not HTTPX_AVAILABLE, reason="httpx not available")
    def test_make_async_client_defaults(self):
        """Test that make_async_client creates client with safe defaults."""
        from devkitx.http_utils.client import make_async_client
        
        client = make_async_client()
        
        # Check timeout defaults
        assert client.timeout.connect == 10.0
        assert client.timeout.read == 15.0
        
        # Check connection limits via transport
        transport = client._transport
        assert transport._pool._max_keepalive_connections == 10
        assert transport._pool._max_connections == 100
        
        # Check other defaults
        assert client.base_url == ""
        assert client.follow_redirects is True
    
    @pytest.mark.skipif(not HTTPX_AVAILABLE, reason="httpx not available")
    def test_make_client_custom_config(self):
        """Test make_client with custom configuration."""
        from devkitx.http_utils.client import make_client
        
        custom_timeout = httpx.Timeout(5.0, read=10.0)
        custom_limits = httpx.Limits(max_keepalive_connections=5, max_connections=50)
        custom_headers = {"User-Agent": "test-client"}
        
        client = make_client(
            base_url="https://api.example.com",
            timeout=custom_timeout,
            limits=custom_limits,
            headers=custom_headers
        )
        
        assert client.base_url == "https://api.example.com"
        assert client.timeout.connect == 5.0
        assert client.timeout.read == 10.0
        
        # Check connection limits via transport
        transport = client._transport
        assert transport._pool._max_keepalive_connections == 5
        assert transport._pool._max_connections == 50
        
        assert client.headers["User-Agent"] == "test-client"
        
        client.close()
    
    @pytest.mark.skipif(not HTTPX_AVAILABLE, reason="httpx not available")
    def test_make_async_client_custom_config(self):
        """Test make_async_client with custom configuration."""
        from devkitx.http_utils.client import make_async_client
        
        custom_timeout = httpx.Timeout(5.0, read=10.0)
        custom_limits = httpx.Limits(max_keepalive_connections=5, max_connections=50)
        custom_headers = {"Authorization": "Bearer token"}
        
        client = make_async_client(
            base_url="https://api.example.com",
            timeout=custom_timeout,
            limits=custom_limits,
            headers=custom_headers
        )
        
        assert client.base_url == "https://api.example.com"
        assert client.timeout.connect == 5.0
        assert client.timeout.read == 10.0
        
        # Check connection limits via transport
        transport = client._transport
        assert transport._pool._max_keepalive_connections == 5
        assert transport._pool._max_connections == 50
        
        assert client.headers["Authorization"] == "Bearer token"
    
    def test_make_client_without_httpx_raises_import_error(self):
        """Test that make_client raises ImportError when httpx is not available."""
        # Mock httpx as unavailable
        with patch('devkitx.http_utils.client._HTTPX_AVAILABLE', False):
            from devkitx.http_utils.client import make_client
            
            with pytest.raises(ImportError, match="HTTP utilities require the 'http' extra"):
                make_client()
    
    def test_make_async_client_without_httpx_raises_import_error(self):
        """Test that make_async_client raises ImportError when httpx is not available."""
        # Mock httpx as unavailable
        with patch('devkitx.http_utils.client._HTTPX_AVAILABLE', False):
            from devkitx.http_utils.client import make_async_client
            
            with pytest.raises(ImportError, match="HTTP utilities require the 'http' extra"):
                make_async_client()


class TestHttpClientIntegration:
    """Integration tests for HTTP client functionality."""
    
    @pytest.mark.skipif(not HTTPX_AVAILABLE, reason="httpx not available")
    def test_client_can_make_request(self):
        """Test that created client can make actual HTTP requests."""
        from devkitx.http_utils.client import make_client
        
        # Use a reliable test endpoint
        client = make_client()
        
        try:
            # Test with httpbin.org which is commonly used for HTTP testing
            response = client.get("https://httpbin.org/json")
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("application/json")
            
            # Verify we can parse JSON response
            data = response.json()
            assert isinstance(data, dict)
            
        except Exception as e:
            # If httpbin.org is not available, skip this test
            pytest.skip(f"HTTP test endpoint not available: {e}")
        finally:
            client.close()
    
    @pytest.mark.skipif(not HTTPX_AVAILABLE, reason="httpx not available")
    @pytest.mark.asyncio
    async def test_async_client_can_make_request(self):
        """Test that created async client can make actual HTTP requests."""
        from devkitx.http_utils.client import make_async_client
        
        # Use a reliable test endpoint
        async with make_async_client() as client:
            try:
                # Test with httpbin.org which is commonly used for HTTP testing
                response = await client.get("https://httpbin.org/json")
                assert response.status_code == 200
                assert response.headers["content-type"].startswith("application/json")
                
                # Verify we can parse JSON response
                data = response.json()
                assert isinstance(data, dict)
                
            except Exception as e:
                # If httpbin.org is not available, skip this test
                pytest.skip(f"HTTP test endpoint not available: {e}")
    
    @pytest.mark.skipif(not HTTPX_AVAILABLE, reason="httpx not available")
    def test_client_timeout_behavior(self):
        """Test that client respects timeout settings."""
        from devkitx.http_utils.client import make_client
        
        # Create client with very short timeout
        short_timeout = httpx.Timeout(0.001)  # 1ms timeout
        client = make_client(timeout=short_timeout)
        
        try:
            # This should timeout quickly
            with pytest.raises((httpx.TimeoutException, httpx.ConnectTimeout)):
                client.get("https://httpbin.org/delay/1")  # 1 second delay
        finally:
            client.close()


class TestHttpUtilsImportHandling:
    """Test import handling for HTTP utilities."""
    
    def test_http_utils_import_with_httpx(self):
        """Test that http_utils imports work when httpx is available."""
        if not HTTPX_AVAILABLE:
            pytest.skip("httpx not available")
        
        # Should import without errors
        from devkitx.http_utils import make_client, make_async_client, with_retries
        
        # Functions should be callable
        assert callable(make_client)
        assert callable(make_async_client)
        assert callable(with_retries)
    
    def test_http_utils_import_without_httpx(self):
        """Test that http_utils handles missing httpx gracefully."""
        # This test is more complex because the module is already imported
        # Instead, let's test the error handling in the client functions directly
        with patch('devkitx.http_utils.client._HTTPX_AVAILABLE', False):
            from devkitx.http_utils.client import make_client, make_async_client
            
            # But calling the functions should raise ImportError
            with pytest.raises(ImportError, match="HTTP utilities require the 'http' extra"):
                make_client()
            
            with pytest.raises(ImportError, match="HTTP utilities require the 'http' extra"):
                make_async_client()