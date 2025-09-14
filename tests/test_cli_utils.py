"""Tests for cli_utils module."""

import pytest
from unittest.mock import patch, MagicMock
from dev_qol_toolkit.cli_utils import (
    parse_args,
    confirm,
    select,
    password_prompt,
    multi_select,
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