"""Tests for http_utils module."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
import httpx

from dev_qol_toolkit.http_utils import (
    AsyncAPIClient,
    async_api_request,
    async_batch_requests,
    async_download_file,
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