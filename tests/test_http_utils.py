"""Tests for http_utils module."""

import asyncio
import tempfile
import time
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
import httpx
from hypothesis import given, strategies as st

from dev_qol_toolkit.http_utils import (
    AsyncAPIClient,
    BaseAPIClient,
    api_request,
    async_api_request,
    async_batch_requests,
    async_download_file,
    _merge_headers,
    _sleep_backoff,
    _async_sleep_backoff,
    RETRY_STATUSES,
)


class TestAsyncAPIRequest:
    """Test async_api_request function."""

    @pytest.mark.asyncio
    async def test_successful_json_response(self):
        """Test successful JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"success": True, "data": "test"}
        mock_response.raise_for_status = Mock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.request.return_value = mock_response

            result = await async_api_request("GET", "https://api.example.com/test")
            
            assert result == {"success": True, "data": "test"}
            mock_client.request.assert_called_once_with(
                "GET", 
                "https://api.example.com/test",
                headers={"accept": "application/json"},
                json=None,
                params=None
            )

    @pytest.mark.asyncio
    async def test_successful_text_response(self):
        """Test successful text response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.text = "Plain text response"
        mock_response.raise_for_status = Mock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.request.return_value = mock_response

            result = await async_api_request("GET", "https://api.example.com/test")
            
            assert result == "Plain text response"

    @pytest.mark.asyncio
    async def test_request_with_parameters(self):
        """Test request with various parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"created": True}
        mock_response.raise_for_status = Mock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.request.return_value = mock_response

            result = await async_api_request(
                "POST",
                "https://api.example.com/users",
                headers={"Authorization": "Bearer token"},
                json_body={"name": "John", "email": "john@example.com"},
                params={"format": "json"},
                timeout=30.0
            )
            
            assert result == {"created": True}
            mock_client.request.assert_called_once_with(
                "POST",
                "https://api.example.com/users",
                headers={"accept": "application/json", "Authorization": "Bearer token"},
                json={"name": "John", "email": "john@example.com"},
                params={"format": "json"}
            )

    @pytest.mark.asyncio
    async def test_retry_on_server_error(self):
        """Test retry behavior on server errors."""
        # First call returns 500, second call succeeds
        responses = [
            Mock(status_code=500, headers={}),
            Mock(status_code=200, headers={"content-type": "application/json"})
        ]
        responses[0].raise_for_status = Mock(side_effect=httpx.HTTPStatusError("Server Error", request=Mock(), response=responses[0]))
        responses[1].json.return_value = {"success": True}
        responses[1].raise_for_status = Mock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.request.side_effect = responses

            with patch("dev_qol_toolkit.http_utils._async_sleep_backoff") as mock_sleep:
                result = await async_api_request("GET", "https://api.example.com/test", retries=2)
                
                assert result == {"success": True}
                assert mock_client.request.call_count == 2
                mock_sleep.assert_called_once_with(1)


class TestAsyncAPIClient:
    """Test AsyncAPIClient class."""

    def test_init(self):
        """Test AsyncAPIClient initialization."""
        client = AsyncAPIClient("https://api.example.com", headers={"Auth": "token"}, timeout=30.0)
        
        assert client.base_url == "https://api.example.com"
        assert client.headers == {"Auth": "token"}
        assert client.timeout == 30.0

    def test_url_construction(self):
        """Test URL construction."""
        client = AsyncAPIClient("https://api.example.com/")
        
        assert client._url("users") == "https://api.example.com/users"
        assert client._url("/users") == "https://api.example.com/users"
        assert client._url("users/123") == "https://api.example.com/users/123"

    @pytest.mark.asyncio
    async def test_get_request(self):
        """Test GET request."""
        with patch("dev_qol_toolkit.http_utils.async_api_request") as mock_request:
            mock_request.return_value = {"data": "test"}
            
            client = AsyncAPIClient("https://api.example.com", headers={"Auth": "token"}, timeout=25.0)
            result = await client.get("users/123", params={"include": "profile"})
            
            assert result == {"data": "test"}
            mock_request.assert_called_once_with(
                "GET",
                "https://api.example.com/users/123",
                headers={"Auth": "token"},
                timeout=25.0,
                params={"include": "profile"}
            )

    @pytest.mark.asyncio
    async def test_post_request(self):
        """Test POST request."""
        with patch("dev_qol_toolkit.http_utils.async_api_request") as mock_request:
            mock_request.return_value = {"created": True, "id": 123}
            
            client = AsyncAPIClient("https://api.example.com")
            result = await client.post("users", json_body={"name": "John"})
            
            assert result == {"created": True, "id": 123}
            mock_request.assert_called_once_with(
                "POST",
                "https://api.example.com/users",
                headers={},
                timeout=15.0,
                json_body={"name": "John"}
            )

    @pytest.mark.asyncio
    async def test_all_http_methods(self):
        """Test all HTTP methods."""
        with patch("dev_qol_toolkit.http_utils.async_api_request") as mock_request:
            mock_request.return_value = {"success": True}
            
            client = AsyncAPIClient("https://api.example.com")
            
            # Test all methods
            await client.get("test")
            await client.post("test")
            await client.put("test")
            await client.delete("test")
            await client.patch("test")
            
            assert mock_request.call_count == 5
            
            # Check that correct methods were called
            calls = mock_request.call_args_list
            methods = [call[0][0] for call in calls]  # First argument of each call
            assert methods == ["GET", "POST", "PUT", "DELETE", "PATCH"]


class TestAsyncBatchRequests:
    """Test async_batch_requests function."""

    @pytest.mark.asyncio
    async def test_batch_requests_basic(self):
        """Test basic batch requests functionality."""
        requests = [
            ("GET", "https://api.example.com/users/1", {}),
            ("GET", "https://api.example.com/users/2", {}),
            ("POST", "https://api.example.com/users", {"json_body": {"name": "John"}}),
        ]
        
        expected_responses = [
            {"id": 1, "name": "User 1"},
            {"id": 2, "name": "User 2"},
            {"id": 3, "name": "John", "created": True}
        ]

        with patch("dev_qol_toolkit.http_utils.async_api_request") as mock_request:
            mock_request.side_effect = expected_responses
            
            results = await async_batch_requests(requests, concurrency_limit=2)
            
            assert results == expected_responses
            assert mock_request.call_count == 3

    @pytest.mark.asyncio
    async def test_batch_requests_with_defaults(self):
        """Test batch requests with default parameters."""
        requests = [
            ("GET", "https://api.example.com/users/1", {}),
            ("GET", "https://api.example.com/users/2", {"timeout": 30.0}),
        ]

        with patch("dev_qol_toolkit.http_utils.async_api_request") as mock_request:
            mock_request.return_value = {"success": True}
            
            await async_batch_requests(
                requests, 
                concurrency_limit=5,
                headers={"Auth": "token"},
                retries=2
            )
            
            # Check that default parameters were merged
            calls = mock_request.call_args_list
            
            # First call should have default headers and retries
            assert calls[0][1]["headers"] == {"Auth": "token"}
            assert calls[0][1]["retries"] == 2
            
            # Second call should override timeout but keep other defaults
            assert calls[1][1]["headers"] == {"Auth": "token"}
            assert calls[1][1]["retries"] == 2
            assert calls[1][1]["timeout"] == 30.0

    @pytest.mark.asyncio
    async def test_batch_requests_empty(self):
        """Test batch requests with empty input."""
        results = await async_batch_requests([], concurrency_limit=5)
        assert results == []


class TestAsyncDownloadFile:
    """Test async_download_file function."""

    @pytest.mark.asyncio
    async def test_download_file_success(self):
        """Test successful file download."""
        test_content = b"This is test file content"
        
        # Mock the response
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.content = test_content

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "downloaded_file.txt"
            
            with patch("httpx.AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value.__aenter__.return_value = mock_client
                mock_client.get.return_value = mock_response

                await async_download_file(
                    "https://example.com/file.txt",
                    str(file_path),
                    headers={"User-Agent": "test"},
                    timeout=60.0,
                    chunk_size=1024
                )
                
                # Verify file was created and has correct content
                assert file_path.exists()
                assert file_path.read_bytes() == test_content
                
                # Verify correct API calls
                mock_client.get.assert_called_once_with(
                    "https://example.com/file.txt",
                    headers={"User-Agent": "test"}
                )

    @pytest.mark.asyncio
    async def test_download_file_http_error(self):
        """Test download file with HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock(side_effect=httpx.HTTPStatusError("Not Found", request=Mock(), response=Mock()))

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "downloaded_file.txt"
            
            with patch("httpx.AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value.__aenter__.return_value = mock_client
                mock_client.get.return_value = mock_response

                with pytest.raises(httpx.HTTPStatusError):
                    await async_download_file(
                        "https://example.com/nonexistent.txt",
                        str(file_path)
                    )
                
                # File should not be created on error
                assert not file_path.exists()


class TestMergeHeaders:
    """Test _merge_headers utility function."""

    def test_merge_none_headers(self):
        """Test merging when both headers are None."""
        result = _merge_headers(None, None)
        assert result == {}

    def test_merge_base_only(self):
        """Test merging with only base headers."""
        base = {"Authorization": "Bearer token"}
        result = _merge_headers(base, None)
        assert result == base

    def test_merge_extra_only(self):
        """Test merging with only extra headers."""
        extra = {"Content-Type": "application/json"}
        result = _merge_headers(None, extra)
        assert result == extra

    def test_merge_both_headers(self):
        """Test merging both base and extra headers."""
        base = {"Authorization": "Bearer token"}
        extra = {"Content-Type": "application/json"}
        result = _merge_headers(base, extra)
        
        expected = {"Authorization": "Bearer token", "Content-Type": "application/json"}
        assert result == expected

    def test_merge_overlapping_headers(self):
        """Test merging with overlapping headers (extra should win)."""
        base = {"Authorization": "Bearer old", "Accept": "text/plain"}
        extra = {"Authorization": "Bearer new", "Content-Type": "application/json"}
        result = _merge_headers(base, extra)
        
        expected = {
            "Authorization": "Bearer new",
            "Accept": "text/plain",
            "Content-Type": "application/json"
        }
        assert result == expected


class TestSleepBackoff:
    """Test _sleep_backoff utility function."""

    def test_sleep_backoff_progression(self):
        """Test that backoff delays increase exponentially."""
        with patch('time.sleep') as mock_sleep:
            _sleep_backoff(1)
            _sleep_backoff(2)
            _sleep_backoff(3)
            
            calls = [call[0][0] for call in mock_sleep.call_args_list]
            
            # Should be exponential: 0.25, 0.5, 1.0
            assert calls[0] == 0.25
            assert calls[1] == 0.5
            assert calls[2] == 1.0

    def test_sleep_backoff_cap(self):
        """Test that backoff delay is capped."""
        with patch('time.sleep') as mock_sleep:
            _sleep_backoff(10, cap=2.0)  # Should be capped at 2.0
            
            mock_sleep.assert_called_once_with(2.0)

    def test_sleep_backoff_custom_base(self):
        """Test backoff with custom base delay."""
        with patch('time.sleep') as mock_sleep:
            _sleep_backoff(2, base=1.0)  # Should be 1.0 * 2^(2-1) = 2.0
            
            mock_sleep.assert_called_once_with(2.0)


class TestAsyncSleepBackoff:
    """Test _async_sleep_backoff utility function."""

    @pytest.mark.asyncio
    async def test_async_sleep_backoff_progression(self):
        """Test that async backoff delays increase exponentially."""
        with patch('asyncio.sleep') as mock_sleep:
            await _async_sleep_backoff(1)
            await _async_sleep_backoff(2)
            await _async_sleep_backoff(3)
            
            calls = [call[0][0] for call in mock_sleep.call_args_list]
            
            # Should be exponential: 0.25, 0.5, 1.0
            assert calls[0] == 0.25
            assert calls[1] == 0.5
            assert calls[2] == 1.0

    @pytest.mark.asyncio
    async def test_async_sleep_backoff_cap(self):
        """Test that async backoff delay is capped."""
        with patch('asyncio.sleep') as mock_sleep:
            await _async_sleep_backoff(10, cap=2.0)  # Should be capped at 2.0
            
            mock_sleep.assert_called_once_with(2.0)


class TestApiRequest:
    """Test sync api_request function."""

    def test_successful_json_response(self):
        """Test successful JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"success": True, "data": "test"}
        mock_response.raise_for_status = Mock()

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value.__enter__.return_value = mock_client
            mock_client.request.return_value = mock_response

            result = api_request("GET", "https://api.example.com/test")
            
            assert result == {"success": True, "data": "test"}
            mock_client.request.assert_called_once_with(
                "GET", 
                "https://api.example.com/test",
                headers={"accept": "application/json"},
                json=None,
                params=None
            )

    def test_successful_text_response(self):
        """Test successful text response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.text = "Plain text response"
        mock_response.raise_for_status = Mock()

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value.__enter__.return_value = mock_client
            mock_client.request.return_value = mock_response

            result = api_request("GET", "https://api.example.com/test")
            
            assert result == "Plain text response"

    def test_request_with_parameters(self):
        """Test request with various parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"created": True}
        mock_response.raise_for_status = Mock()

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value.__enter__.return_value = mock_client
            mock_client.request.return_value = mock_response

            result = api_request(
                "POST",
                "https://api.example.com/users",
                headers={"Authorization": "Bearer token"},
                json_body={"name": "John", "email": "john@example.com"},
                params={"format": "json"},
                timeout=30.0
            )
            
            assert result == {"created": True}
            mock_client.request.assert_called_once_with(
                "POST",
                "https://api.example.com/users",
                headers={"accept": "application/json", "Authorization": "Bearer token"},
                json={"name": "John", "email": "john@example.com"},
                params={"format": "json"}
            )

    def test_retry_on_server_error(self):
        """Test retry behavior on server errors."""
        # First call returns 500, second call succeeds
        responses = [
            Mock(status_code=500, headers={}),
            Mock(status_code=200, headers={"content-type": "application/json"})
        ]
        responses[0].raise_for_status = Mock(side_effect=httpx.HTTPStatusError("Server Error", request=Mock(), response=responses[0]))
        responses[1].json.return_value = {"success": True}
        responses[1].raise_for_status = Mock()

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value.__enter__.return_value = mock_client
            mock_client.request.side_effect = responses

            with patch("dev_qol_toolkit.http_utils._sleep_backoff") as mock_sleep:
                result = api_request("GET", "https://api.example.com/test", retries=2)
                
                assert result == {"success": True}
                assert mock_client.request.call_count == 2
                mock_sleep.assert_called_once_with(1)

    def test_retry_status_codes(self):
        """Test that specific status codes trigger retries."""
        for status_code in RETRY_STATUSES:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_response.headers = {}

            with patch("httpx.Client") as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value.__enter__.return_value = mock_client
                mock_client.request.return_value = mock_response

                with patch("dev_qol_toolkit.http_utils._sleep_backoff") as mock_sleep:
                    with pytest.raises(httpx.HTTPStatusError):
                        api_request("GET", "https://api.example.com/test", retries=2)
                    
                    # Should have retried
                    assert mock_client.request.call_count == 2
                    mock_sleep.assert_called_once_with(1)

    def test_no_retry_on_client_error(self):
        """Test that client errors (4xx) don't trigger retries."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {}
        mock_response.raise_for_status = Mock(side_effect=httpx.HTTPStatusError("Not Found", request=Mock(), response=mock_response))

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value.__enter__.return_value = mock_client
            mock_client.request.return_value = mock_response

            with pytest.raises(httpx.HTTPStatusError):
                api_request("GET", "https://api.example.com/test", retries=3)
            
            # Should not have retried
            assert mock_client.request.call_count == 1

    def test_exception_retry_and_reraise(self):
        """Test that exceptions are retried and then re-raised."""
        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value.__enter__.return_value = mock_client
            mock_client.request.side_effect = httpx.ConnectError("Connection failed")

            with patch("dev_qol_toolkit.http_utils._sleep_backoff") as mock_sleep:
                with pytest.raises(httpx.ConnectError):
                    api_request("GET", "https://api.example.com/test", retries=2)
                
                # Should have retried
                assert mock_client.request.call_count == 2
                assert mock_sleep.call_count == 2


class TestBaseAPIClient:
    """Test BaseAPIClient class."""

    def test_init(self):
        """Test BaseAPIClient initialization."""
        client = BaseAPIClient("https://api.example.com", headers={"Auth": "token"}, timeout=30.0)
        
        assert client.base_url == "https://api.example.com"
        assert client.headers == {"Auth": "token"}
        assert client.timeout == 30.0

    def test_init_strips_trailing_slash(self):
        """Test that trailing slash is stripped from base URL."""
        client = BaseAPIClient("https://api.example.com/")
        assert client.base_url == "https://api.example.com"

    def test_url_construction(self):
        """Test URL construction."""
        client = BaseAPIClient("https://api.example.com/")
        
        assert client._url("users") == "https://api.example.com/users"
        assert client._url("/users") == "https://api.example.com/users"
        assert client._url("users/123") == "https://api.example.com/users/123"

    def test_get_request(self):
        """Test GET request."""
        with patch("dev_qol_toolkit.http_utils.api_request") as mock_request:
            mock_request.return_value = {"data": "test"}
            
            client = BaseAPIClient("https://api.example.com", headers={"Auth": "token"}, timeout=25.0)
            result = client.get("users/123", params={"include": "profile"})
            
            assert result == {"data": "test"}
            mock_request.assert_called_once_with(
                "GET",
                "https://api.example.com/users/123",
                headers={"Auth": "token"},
                params={"include": "profile"}
            )

    def test_post_request(self):
        """Test POST request."""
        with patch("dev_qol_toolkit.http_utils.api_request") as mock_request:
            mock_request.return_value = {"created": True, "id": 123}
            
            client = BaseAPIClient("https://api.example.com")
            result = client.post("users", json_body={"name": "John"})
            
            assert result == {"created": True, "id": 123}
            mock_request.assert_called_once_with(
                "POST",
                "https://api.example.com/users",
                headers={},
                json_body={"name": "John"}
            )

    def test_all_http_methods(self):
        """Test all HTTP methods."""
        with patch("dev_qol_toolkit.http_utils.api_request") as mock_request:
            mock_request.return_value = {"success": True}
            
            client = BaseAPIClient("https://api.example.com")
            
            # Test all methods
            client.get("test")
            client.post("test")
            client.put("test")
            client.delete("test")
            
            assert mock_request.call_count == 4
            
            # Check that correct methods were called
            calls = mock_request.call_args_list
            methods = [call[0][0] for call in calls]  # First argument of each call
            assert methods == ["GET", "POST", "PUT", "DELETE"]

    @given(
        path=st.text(min_size=1, max_size=50).filter(lambda x: "/" not in x),
        timeout=st.floats(min_value=1.0, max_value=60.0)
    )
    def test_client_with_various_parameters(self, path, timeout):
        """Test client with various parameters."""
        with patch("dev_qol_toolkit.http_utils.api_request") as mock_request:
            mock_request.return_value = {"success": True}
            
            client = BaseAPIClient("https://api.example.com", timeout=timeout)
            client.get(path)
            
            mock_request.assert_called_once_with(
                "GET",
                f"https://api.example.com/{path}",
                headers={}
            )