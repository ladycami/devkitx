"""Tests for log_utils module."""

import logging
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from hypothesis import given, strategies as st

from devtools_py.log_utils import setup_logging, log_time, log_calls


class TestSetupLogging:
    """Test setup_logging function."""

    def test_basic_setup(self):
        """Test basic logger setup."""
        logger = setup_logging(level="DEBUG")

        assert logger.name == "devtools_py"
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_json_format(self):
        """Test JSON format logging."""
        logger = setup_logging(level="INFO", json=True)

        formatter = logger.handlers[0].formatter
        assert '{"time"' in formatter._fmt
        assert '"level"' in formatter._fmt
        assert '"message"' in formatter._fmt

    def test_file_logging(self):
        """Test logging to file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            logger = setup_logging(level="WARNING", to_file=tmp_path)

            # Should have both stream and file handlers
            assert len(logger.handlers) == 2

            # Test that file handler exists
            file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
            assert len(file_handlers) == 1
            assert file_handlers[0].baseFilename == tmp_path

            # Test logging to file
            logger.warning("Test message")
            logger.handlers[1].flush()  # Flush file handler

            with open(tmp_path, "r") as f:
                content = f.read()
                assert "Test message" in content
                assert "WARNING" in content
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_loguru_fallback(self):
        """Test loguru fallback when loguru is not available."""
        # Mock the import to fail
        with patch.dict("sys.modules", {"loguru": None}):
            with patch("devtools_py.log_utils.logging.getLogger") as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger

                logger = setup_logging(use_loguru=True)

                # Should fall back to standard logging
                assert logger == mock_logger

    @given(level=st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]))
    def test_different_log_levels(self, level):
        """Test setup with different log levels."""
        logger = setup_logging(level=level)
        expected_level = getattr(logging, level)
        assert logger.level == expected_level

    def test_invalid_log_level(self):
        """Test setup with invalid log level falls back to INFO."""
        logger = setup_logging(level="INVALID")
        assert logger.level == logging.INFO

    def test_handler_clearing(self):
        """Test that existing handlers are cleared."""
        logger = logging.getLogger("devtools_py")
        # Add a dummy handler
        dummy_handler = logging.StreamHandler()
        logger.addHandler(dummy_handler)

        # Setup logging should clear existing handlers
        setup_logging()

        # Should only have the new handler
        assert len(logger.handlers) == 1
        assert dummy_handler not in logger.handlers


class TestLogTime:
    """Test log_time context manager."""

    def test_log_time_basic(self):
        """Test basic log_time functionality."""
        logger = Mock()

        with log_time("test_operation", logger=logger):
            time.sleep(0.01)  # Small delay to ensure measurable time

        logger.info.assert_called_once()
        call_args = logger.info.call_args[0]
        # Check the format string and arguments
        assert "%s took %.2f ms" == call_args[0]
        assert call_args[1] == "test_operation"
        assert isinstance(call_args[2], float)  # duration

    def test_log_time_default_name(self):
        """Test log_time with default name."""
        logger = Mock()

        with log_time(logger=logger):
            pass

        logger.info.assert_called_once()
        call_args = logger.info.call_args[0]
        assert "%s took %.2f ms" == call_args[0]
        assert call_args[1] == "block"

    def test_log_time_default_logger(self):
        """Test log_time with default logger."""
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            with log_time("test"):
                pass

            mock_get_logger.assert_called_with("devtools_py")
            mock_logger.info.assert_called_once()

    def test_log_time_with_exception(self):
        """Test log_time when exception occurs."""
        logger = Mock()

        with pytest.raises(ValueError):
            with log_time("failing_operation", logger=logger):
                raise ValueError("Test error")

        # Should still log the time even when exception occurs
        logger.info.assert_called_once()
        call_args = logger.info.call_args[0]
        assert "%s took %.2f ms" == call_args[0]
        assert call_args[1] == "failing_operation"

    @given(name=st.text(min_size=1, max_size=50))
    def test_log_time_various_names(self, name):
        """Test log_time with various operation names."""
        logger = Mock()

        with log_time(name, logger=logger):
            pass

        logger.info.assert_called_once()
        call_args = logger.info.call_args[0]
        assert "%s took %.2f ms" == call_args[0]
        assert call_args[1] == name


class TestLogCalls:
    """Test log_calls decorator."""

    def test_log_calls_basic(self):
        """Test basic log_calls functionality."""
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            @log_calls
            def test_function(x, y=10):
                return x + y

            result = test_function(5, y=15)

            assert result == 20
            assert mock_logger.debug.call_count == 2

            # Check call logging
            first_call = mock_logger.debug.call_args_list[0][0]
            assert "Calling %s args=%r kwargs=%r" == first_call[0]
            assert first_call[1] == "test_function"
            assert first_call[2] == (5,)
            assert first_call[3] == {"y": 15}

            # Check return logging
            second_call = mock_logger.debug.call_args_list[1][0]
            assert "Returned %s -> %r" == second_call[0]
            assert second_call[1] == "test_function"
            assert second_call[2] == 20

    def test_log_calls_no_args(self):
        """Test log_calls with function that takes no arguments."""
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            @log_calls
            def no_args_function():
                return "hello"

            result = no_args_function()

            assert result == "hello"
            assert mock_logger.debug.call_count == 2

    def test_log_calls_with_exception(self):
        """Test log_calls when function raises exception."""
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            @log_calls
            def failing_function():
                raise ValueError("Test error")

            with pytest.raises(ValueError):
                failing_function()

            # Should log the call but not the return
            assert mock_logger.debug.call_count == 1
            call_args = mock_logger.debug.call_args[0]
            assert "Calling %s args=%r kwargs=%r" == call_args[0]
            assert call_args[1] == "failing_function"

    def test_log_calls_preserves_function_metadata(self):
        """Test that log_calls preserves function metadata."""

        @log_calls
        def documented_function(x: int) -> str:
            """This is a test function."""
            return str(x)

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This is a test function."

    @given(
        args=st.lists(st.integers(), min_size=0, max_size=5),
        kwargs=st.dictionaries(
            st.text(min_size=1, max_size=10), st.integers(), min_size=0, max_size=3
        ),
    )
    def test_log_calls_various_arguments(self, args, kwargs):
        """Test log_calls with various argument combinations."""
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            @log_calls
            def flexible_function(*args, **kwargs):
                return sum(args) + sum(kwargs.values())

            result = flexible_function(*args, **kwargs)
            expected = sum(args) + sum(kwargs.values())

            assert result == expected
            assert mock_logger.debug.call_count == 2


class TestLogUtilsIntegration:
    """Integration tests for log_utils module."""

    def test_setup_and_use_logger(self):
        """Test setting up logger and using it with decorators."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Setup logger
            logger = setup_logging(level="DEBUG", to_file=tmp_path)

            @log_calls
            def test_operation(value):
                with log_time("inner_operation", logger=logger):
                    return value * 2

            result = test_operation(21)

            assert result == 42

            # Flush all handlers
            for handler in logger.handlers:
                handler.flush()

            # Check log file content
            with open(tmp_path, "r") as f:
                content = f.read()
                assert "Calling test_operation" in content
                assert "inner_operation took" in content
                assert "Returned test_operation -> 42" in content
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_multiple_loggers_isolation(self):
        """Test that multiple logger setups don't interfere."""
        logger1 = setup_logging(level="INFO")
        logger2 = setup_logging(level="ERROR")

        # Both should be the same logger instance (singleton behavior)
        assert logger1 is logger2
        assert logger1.level == logging.ERROR  # Last setup wins
