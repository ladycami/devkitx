"""Tests for cli_utils module."""

import time
import pytest
from unittest.mock import patch
from devtools_py.cli_utils import (
    parse_args,
    confirm,
    select,
    password_prompt,
    multi_select,
    progress_bar,
    spinner,
    colored_text,
    table_format,
)


class TestParseArgs:
    """Test parse_args function."""

    def test_parse_args_basic_types(self):
        """Test parsing basic argument types."""
        schema = {
            "--input": str,
            "--count": int,
            "--verbose": bool,
        }

        with patch("sys.argv", ["test", "--input", "file.txt", "--count", "5", "--verbose"]):
            args = parse_args(schema)
            assert args.input == "file.txt"
            assert args.count == 5
            assert args.verbose is True

    def test_parse_args_with_defaults(self):
        """Test parsing arguments with default values."""
        schema = {
            "--input": (str, "default.txt"),
            "--count": (int, 3),
            "--verbose": (bool, False),
        }

        with patch("sys.argv", ["test"]):
            args = parse_args(schema)
            assert args.input == "default.txt"
            assert args.count == 3
            assert args.verbose is False


class TestConfirm:
    """Test confirm function."""

    @patch("builtins.input", return_value="y")
    def test_confirm_yes(self, mock_input):
        """Test confirm with yes response."""
        result = confirm("Continue?")
        assert result is True
        mock_input.assert_called_once_with("Continue? [Y/n] ")

    @patch("builtins.input", return_value="n")
    def test_confirm_no(self, mock_input):
        """Test confirm with no response."""
        result = confirm("Continue?")
        assert result is False

    @patch("builtins.input", return_value="")
    def test_confirm_default_true(self, mock_input):
        """Test confirm with empty input and default True."""
        result = confirm("Continue?", default=True)
        assert result is True

    @patch("builtins.input", return_value="")
    def test_confirm_default_false(self, mock_input):
        """Test confirm with empty input and default False."""
        result = confirm("Continue?", default=False)
        assert result is False

    @patch("builtins.input", side_effect=["invalid", "yes"])
    def test_confirm_invalid_then_valid(self, mock_input):
        """Test confirm with invalid input followed by valid input."""
        result = confirm("Continue?")
        assert result is True
        assert mock_input.call_count == 2


class TestSelect:
    """Test select function."""

    @patch("builtins.input", return_value="1")
    @patch("builtins.print")
    def test_select_first_option(self, mock_print, mock_input):
        """Test selecting first option."""
        options = ["option1", "option2", "option3"]
        result = select(options)
        assert result == "option1"
        mock_input.assert_called_once_with("Choose: [1-3] ")

    @patch("builtins.input", return_value="3")
    @patch("builtins.print")
    def test_select_last_option(self, mock_print, mock_input):
        """Test selecting last option."""
        options = ["red", "green", "blue"]
        result = select(options, "Pick a color:")
        assert result == "blue"
        mock_input.assert_called_once_with("Pick a color: [1-3] ")

    @patch("builtins.input", side_effect=["0", "4", "2"])
    @patch("builtins.print")
    def test_select_invalid_then_valid(self, mock_print, mock_input):
        """Test select with invalid inputs followed by valid input."""
        options = ["a", "b", "c"]
        result = select(options)
        assert result == "b"
        assert mock_input.call_count == 3

    def test_select_empty_options(self):
        """Test select with empty options list."""
        with pytest.raises(ValueError, match="options must not be empty"):
            select([])


class TestPasswordPrompt:
    """Test password_prompt function."""

    @patch("getpass.getpass", return_value="secret123")
    def test_password_prompt_basic(self, mock_getpass):
        """Test basic password prompt."""
        result = password_prompt("Enter password:")
        assert result == "secret123"
        mock_getpass.assert_called_once_with("Enter password: ")

    @patch("getpass.getpass", side_effect=["secret123", "secret123"])
    def test_password_prompt_with_confirmation_match(self, mock_getpass):
        """Test password prompt with matching confirmation."""
        result = password_prompt("Enter password:", confirm=True)
        assert result == "secret123"
        assert mock_getpass.call_count == 2
        mock_getpass.assert_any_call("Enter password: ")
        mock_getpass.assert_any_call("Confirm password: ")

    @patch("getpass.getpass", side_effect=["secret123", "different"])
    def test_password_prompt_with_confirmation_mismatch(self, mock_getpass):
        """Test password prompt with mismatched confirmation."""
        with pytest.raises(ValueError, match="Passwords do not match"):
            password_prompt("Enter password:", confirm=True)


class TestMultiSelect:
    """Test multi_select function."""

    @patch("builtins.input", return_value="1,3")
    @patch("builtins.print")
    def test_multi_select_multiple_options(self, mock_print, mock_input):
        """Test selecting multiple options."""
        options = ["red", "green", "blue", "yellow"]
        result = multi_select(options)
        assert result == ["red", "blue"]

    @patch("builtins.input", return_value="all")
    @patch("builtins.print")
    def test_multi_select_all_options(self, mock_print, mock_input):
        """Test selecting all options."""
        options = ["a", "b", "c"]
        result = multi_select(options)
        assert result == ["a", "b", "c"]

    @patch("builtins.input", return_value="2")
    @patch("builtins.print")
    def test_multi_select_single_option(self, mock_print, mock_input):
        """Test selecting single option."""
        options = ["option1", "option2", "option3"]
        result = multi_select(options, "Pick one:")
        assert result == ["option2"]

    @patch("builtins.input", return_value="1,1,3,1")
    @patch("builtins.print")
    def test_multi_select_duplicates_removed(self, mock_print, mock_input):
        """Test that duplicate selections are removed while preserving order."""
        options = ["a", "b", "c"]
        result = multi_select(options)
        assert result == ["a", "c"]  # Duplicates removed, order preserved

    @patch("builtins.input", side_effect=["0,5", "invalid", "1,2"])
    @patch("builtins.print")
    def test_multi_select_invalid_then_valid(self, mock_print, mock_input):
        """Test multi_select with invalid inputs followed by valid input."""
        options = ["x", "y", "z"]
        result = multi_select(options)
        assert result == ["x", "y"]
        assert mock_input.call_count == 3

    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    def test_multi_select_empty_input_continues(self, mock_print, mock_input):
        """Test that empty input continues the loop."""
        options = ["a", "b"]
        # Mock will return empty string indefinitely, so we need to limit calls
        mock_input.side_effect = ["", "1"]
        result = multi_select(options)
        assert result == ["a"]

    def test_multi_select_empty_options(self):
        """Test multi_select with empty options list."""
        with pytest.raises(ValueError, match="options must not be empty"):
            multi_select([])


class TestProgressBar:
    """Test progress_bar function."""

    def test_progress_bar_with_list(self):
        """Test progress bar with a list."""
        items = [1, 2, 3, 4, 5]
        result = list(progress_bar(items, "Testing"))
        assert result == items

    def test_progress_bar_with_generator(self):
        """Test progress bar with a generator."""

        def gen():
            for i in range(3):
                yield i

        result = list(progress_bar(gen(), "Testing", total=3))
        assert result == [0, 1, 2]

    def test_progress_bar_empty_desc(self):
        """Test progress bar with empty description."""
        items = [1, 2]
        result = list(progress_bar(items))
        assert result == items


class TestSpinner:
    """Test spinner context manager."""

    def test_spinner_basic(self):
        """Test basic spinner functionality."""
        with spinner("Testing..."):
            time.sleep(0.1)  # Brief pause to let spinner run
        # If we get here without exception, spinner worked
        assert True

    def test_spinner_with_exception(self):
        """Test spinner handles exceptions properly."""
        with pytest.raises(ValueError):
            with spinner("Testing..."):
                raise ValueError("Test error")


class TestColoredText:
    """Test colored_text function."""

    def test_colored_text_basic(self):
        """Test basic colored text."""
        result = colored_text("Hello", "red")
        assert "Hello" in result
        # Result should contain ANSI escape codes for color or be at least the original text
        assert len(result) >= len("Hello")

    def test_colored_text_bold(self):
        """Test bold colored text."""
        result = colored_text("Bold", "green", bold=True)
        assert "Bold" in result
        assert len(result) >= len("Bold")

    def test_colored_text_different_colors(self):
        """Test different color options."""
        colors = ["red", "green", "blue", "yellow", "magenta", "cyan"]
        for color in colors:
            result = colored_text("Test", color)
            assert "Test" in result


class TestTableFormat:
    """Test table_format function."""

    def test_table_format_basic(self):
        """Test basic table formatting."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = table_format(data)
        assert "Alice" in result
        assert "Bob" in result
        assert "30" in result
        assert "25" in result

    def test_table_format_with_headers(self):
        """Test table formatting with custom headers."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        headers = ["Name", "Age"]
        result = table_format(data, headers)
        assert "Name" in result
        assert "Age" in result
        assert "Alice" in result

    def test_table_format_empty_data(self):
        """Test table formatting with empty data."""
        result = table_format([])
        assert result == ""

    def test_table_format_missing_keys(self):
        """Test table formatting with missing keys in some rows."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob"}]  # Missing age
        result = table_format(data)
        assert "Alice" in result
        assert "Bob" in result
        # Should handle missing values gracefully
