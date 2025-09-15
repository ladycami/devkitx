"""Tests for __main__.py CLI module."""

from __future__ import annotations
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from io import StringIO

import pytest
from hypothesis import given, strategies as st

from dev_qol_toolkit.__main__ import (
    main,
    add_json_commands,
    add_file_commands,
    add_string_commands,
    add_config_commands,
    add_system_commands,
    add_security_commands,
    add_time_commands,
    add_validation_commands,
    execute_json_commands,
    execute_file_commands,
    execute_string_commands,
    execute_config_commands,
    execute_system_commands,
    execute_security_commands,
    execute_time_commands,
    execute_validation_commands,
)


class TestMainFunction:
    """Test main CLI entry point."""

    def test_main_no_args(self):
        """Test main with no arguments shows help."""
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code == 2  # argparse error code

    def test_main_invalid_command(self):
        """Test main with invalid command."""
        with pytest.raises(SystemExit) as exc_info:
            main(["invalid"])
        assert exc_info.value.code == 2  # argparse error code

    def test_main_keyboard_interrupt(self):
        """Test main handles KeyboardInterrupt."""
        with patch('dev_qol_toolkit.__main__.execute_json_commands', side_effect=KeyboardInterrupt):
            with patch('builtins.print') as mock_print:
                result = main(["json", "pretty", "test.json"])
                assert result == 130
                mock_print.assert_called_with("\nOperation cancelled by user")

    def test_main_unexpected_exception(self):
        """Test main handles unexpected exceptions."""
        with patch('dev_qol_toolkit.__main__.execute_json_commands', side_effect=RuntimeError("Test error")):
            with patch('builtins.print') as mock_print:
                result = main(["json", "pretty", "test.json"])
                assert result == 1
                mock_print.assert_called_with("Unexpected error: Test error")


class TestJsonCommands:
    """Test JSON CLI commands."""

    def test_json_flatten_command(self, tmp_path: Path):
        """Test JSON flatten command."""
        # Create test JSON file
        test_data = {"a": {"b": [1, {"c": 2}]}}
        json_file = tmp_path / "test.json"
        with json_file.open("w") as f:
            json.dump(test_data, f)

        with patch('builtins.print') as mock_print:
            result = main(["json", "flatten", str(json_file)])
            assert result == 0
            
            # Check that flattened JSON was printed
            printed_output = mock_print.call_args[0][0]
            assert "a.b.0" in printed_output
            assert "a.b.1.c" in printed_output

    def test_json_pretty_command(self, tmp_path: Path):
        """Test JSON pretty print command."""
        test_data = {"name": "test", "value": 42}
        json_file = tmp_path / "test.json"
        with json_file.open("w") as f:
            json.dump(test_data, f)

        with patch('builtins.print') as mock_print:
            result = main(["json", "pretty", str(json_file)])
            assert result == 0
            
            # Check that pretty JSON was printed
            printed_output = mock_print.call_args[0][0]
            assert "name" in printed_output
            assert "test" in printed_output

    def test_json_command_nonexistent_file(self):
        """Test JSON command with nonexistent file."""
        with patch('builtins.print') as mock_print:
            result = main(["json", "pretty", "nonexistent.json"])
            assert result == 1
            
            printed_output = mock_print.call_args[0][0]
            assert "Unexpected error" in printed_output

    def test_execute_json_commands_invalid_subcommand(self):
        """Test execute_json_commands with invalid subcommand."""
        args = Mock()
        args.json_cmd = "invalid"
        
        result = execute_json_commands(args)
        assert result == 1


class TestFileCommands:
    """Test file CLI commands."""

    def test_file_find_command(self, tmp_path: Path):
        """Test file find command."""
        # Create test files
        (tmp_path / "test.txt").write_text("content")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "test.txt").write_text("content")

        with patch('builtins.print') as mock_print:
            result = main(["file", "find", "test.txt", "--root", str(tmp_path)])
            assert result == 0
            
            # Should have printed both files
            assert mock_print.call_count == 2

    def test_file_find_no_matches(self, tmp_path: Path):
        """Test file find with no matches."""
        with patch('builtins.print') as mock_print:
            result = main(["file", "find", "nonexistent.txt", "--root", str(tmp_path)])
            assert result == 0
            
            # Should not print anything
            mock_print.assert_not_called()

    def test_execute_file_commands_invalid_subcommand(self):
        """Test execute_file_commands with invalid subcommand."""
        args = Mock()
        args.file_cmd = "invalid"
        
        result = execute_file_commands(args)
        assert result == 1


class TestStringCommands:
    """Test string CLI commands."""

    @pytest.mark.parametrize("case_type,input_text,expected_contains", [
        ("snake", "CamelCase", "camel_case"),
        ("camel", "snake_case", "snakeCase"),
        ("pascal", "snake_case", "SnakeCase"),
        ("kebab", "CamelCase", "camel-case"),
    ])
    def test_string_convert_command(self, case_type, input_text, expected_contains):
        """Test string case conversion commands."""
        with patch('builtins.print') as mock_print:
            result = main(["string", "convert", input_text, "--to", case_type])
            assert result == 0
            
            printed_output = mock_print.call_args[0][0]
            assert expected_contains in printed_output

    def test_string_convert_invalid_case(self):
        """Test string convert with invalid case type."""
        args = Mock()
        args.string_cmd = "convert"
        args.text = "test"
        args.to = "invalid"
        
        result = execute_string_commands(args)
        assert result == 1

    @pytest.mark.parametrize("validation_type,input_text,expected", [
        ("email", "test@example.com", "Valid"),
        ("email", "invalid-email", "Invalid"),
        ("url", "https://example.com", "Valid"),
        ("url", "not-a-url", "Invalid"),
    ])
    def test_string_validate_command(self, validation_type, input_text, expected):
        """Test string validation commands."""
        with patch('builtins.print') as mock_print:
            result = main(["string", "validate", input_text, "--type", validation_type])
            assert result == 0
            
            printed_output = mock_print.call_args[0][0]
            assert expected in printed_output

    def test_string_validate_invalid_type(self):
        """Test string validate with invalid type."""
        args = Mock()
        args.string_cmd = "validate"
        args.text = "test"
        args.type = "invalid"
        
        result = execute_string_commands(args)
        assert result == 1

    def test_string_sanitize_command(self):
        """Test string sanitize filename command."""
        with patch('builtins.print') as mock_print:
            result = main(["string", "sanitize", "file<>name?.txt"])
            assert result == 0
            
            # Should have printed sanitized filename
            mock_print.assert_called_once()

    def test_execute_string_commands_invalid_subcommand(self):
        """Test execute_string_commands with invalid subcommand."""
        args = Mock()
        args.string_cmd = "invalid"
        
        result = execute_string_commands(args)
        assert result == 1


class TestConfigCommands:
    """Test configuration CLI commands."""

    def test_config_load_json(self, tmp_path: Path):
        """Test config load JSON command."""
        test_data = {"key": "value", "number": 42}
        config_file = tmp_path / "config.json"
        with config_file.open("w") as f:
            json.dump(test_data, f)

        with patch('builtins.print') as mock_print:
            result = main(["config", "load", str(config_file)])
            assert result == 0
            
            printed_output = mock_print.call_args[0][0]
            assert "key" in printed_output
            assert "value" in printed_output

    def test_config_load_with_format(self, tmp_path: Path):
        """Test config load with explicit format."""
        test_data = {"key": "value"}
        config_file = tmp_path / "config.txt"  # Non-standard extension
        with config_file.open("w") as f:
            json.dump(test_data, f)

        with patch('builtins.print') as mock_print:
            result = main(["config", "load", str(config_file), "--format", "json"])
            assert result == 0

    def test_config_load_unsupported_format(self, tmp_path: Path):
        """Test config load with unsupported format."""
        config_file = tmp_path / "config.xyz"
        config_file.write_text("content")

        with patch('builtins.print') as mock_print:
            result = main(["config", "load", str(config_file)])
            assert result == 1
            
            printed_output = mock_print.call_args[0][0]
            assert "Unsupported format" in printed_output

    def test_config_load_error(self, tmp_path: Path):
        """Test config load with file error."""
        config_file = tmp_path / "invalid.json"
        config_file.write_text("invalid json")

        with patch('builtins.print') as mock_print:
            result = main(["config", "load", str(config_file)])
            assert result == 1
            
            printed_output = mock_print.call_args[0][0]
            assert "Error loading config" in printed_output

    def test_config_merge_command(self, tmp_path: Path):
        """Test config merge command."""
        # Create multiple config files
        config1 = tmp_path / "config1.json"
        config2 = tmp_path / "config2.json"
        
        with config1.open("w") as f:
            json.dump({"a": 1, "b": {"x": 1}}, f)
        with config2.open("w") as f:
            json.dump({"b": {"y": 2}, "c": 3}, f)

        with patch('builtins.print') as mock_print:
            result = main(["config", "merge", str(config1), str(config2)])
            assert result == 0
            
            # Should print merged config
            printed_output = mock_print.call_args[0][0]
            merged_data = json.loads(printed_output)
            assert merged_data["a"] == 1
            assert merged_data["b"]["x"] == 1
            assert merged_data["b"]["y"] == 2
            assert merged_data["c"] == 3

    def test_config_merge_with_output(self, tmp_path: Path):
        """Test config merge with output file."""
        config1 = tmp_path / "config1.json"
        output_file = tmp_path / "merged.json"
        
        with config1.open("w") as f:
            json.dump({"key": "value"}, f)

        with patch('builtins.print') as mock_print:
            result = main(["config", "merge", str(config1), "--output", str(output_file)])
            assert result == 0
            
            # Should save to file and print confirmation
            assert output_file.exists()
            printed_output = mock_print.call_args[0][0]
            assert "saved to" in printed_output

    def test_config_merge_unsupported_format(self, tmp_path: Path):
        """Test config merge with unsupported file format."""
        config_file = tmp_path / "config.xyz"
        config_file.write_text("content")

        with patch('builtins.print') as mock_print:
            result = main(["config", "merge", str(config_file)])
            assert result == 1
            
            printed_output = mock_print.call_args[0][0]
            assert "Unsupported file format" in printed_output

    def test_config_merge_error(self, tmp_path: Path):
        """Test config merge with error."""
        config_file = tmp_path / "invalid.json"
        config_file.write_text("invalid json")

        with patch('builtins.print') as mock_print:
            result = main(["config", "merge", str(config_file)])
            assert result == 1
            
            printed_output = mock_print.call_args[0][0]
            assert "Error merging configs" in printed_output

    def test_execute_config_commands_invalid_subcommand(self):
        """Test execute_config_commands with invalid subcommand."""
        args = Mock()
        args.config_cmd = "invalid"
        
        result = execute_config_commands(args)
        assert result == 1


class TestSystemCommands:
    """Test system CLI commands."""

    def test_system_info_table_format(self):
        """Test system info command with table format."""
        with patch('dev_qol_toolkit.system_utils.get_system_info') as mock_sys_info:
            with patch('dev_qol_toolkit.system_utils.get_python_info') as mock_py_info:
                mock_sys_info.return_value = {"os": "Linux"}
                mock_py_info.return_value = {"python_version": "3.10"}
                
                with patch('builtins.print') as mock_print:
                    result = main(["system", "info"])
                    assert result == 0
                    
                    # Should print table format
                    assert mock_print.call_count >= 2  # At least 2 info items

    def test_system_info_json_format(self):
        """Test system info command with JSON format."""
        with patch('dev_qol_toolkit.system_utils.get_system_info') as mock_sys_info:
            with patch('dev_qol_toolkit.system_utils.get_python_info') as mock_py_info:
                mock_sys_info.return_value = {"os": "Linux"}
                mock_py_info.return_value = {"python_version": "3.10"}
                
                with patch('builtins.print') as mock_print:
                    result = main(["system", "info", "--format", "json"])
                    assert result == 0
                    
                    # Should print JSON
                    printed_output = mock_print.call_args[0][0]
                    assert "os" in printed_output
                    assert "python_version" in printed_output

    def test_system_info_error(self):
        """Test system info command with error."""
        with patch('dev_qol_toolkit.system_utils.get_system_info', side_effect=Exception("Test error")):
            with patch('builtins.print') as mock_print:
                result = main(["system", "info"])
                assert result == 1
                
                printed_output = mock_print.call_args[0][0]
                assert "Error getting system info" in printed_output

    def test_system_run_command(self):
        """Test system run command."""
        mock_result = Mock()
        mock_result.stdout = "command output"
        mock_result.stderr = ""
        mock_result.returncode = 0
        
        with patch('dev_qol_toolkit.system_utils.run_command', return_value=mock_result) as mock_run:
            with patch('builtins.print') as mock_print:
                result = main(["system", "run", "echo", "hello"])
                assert result == 0
                
                mock_print.assert_called_with("command output")
                mock_run.assert_called_once_with(["echo", "hello"], timeout=None)

    def test_system_run_command_with_stderr(self):
        """Test system run command with stderr output."""
        mock_result = Mock()
        mock_result.stdout = "output"
        mock_result.stderr = "error output"
        mock_result.returncode = 0
        
        with patch('dev_qol_toolkit.system_utils.run_command', return_value=mock_result):
            with patch('builtins.print') as mock_print:
                result = main(["system", "run", "command"])
                assert result == 0
                
                # Should print both stdout and stderr
                assert mock_print.call_count == 2
                calls = [call[0][0] for call in mock_print.call_args_list]
                assert "output" in calls[0]
                assert "STDERR: error output" in calls[1]

    def test_system_run_command_with_timeout(self):
        """Test system run command with timeout."""
        mock_result = Mock()
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_result.returncode = 0
        
        with patch('dev_qol_toolkit.system_utils.run_command', return_value=mock_result) as mock_run:
            with patch('builtins.print'):
                result = main(["system", "run", "--timeout", "30", "command"])
                assert result == 0
                
                # Should pass timeout to run_command
                mock_run.assert_called_once_with(["command"], timeout=30.0)

    def test_system_run_command_error(self):
        """Test system run command with error."""
        with patch('dev_qol_toolkit.system_utils.run_command', side_effect=Exception("Command failed")):
            with patch('builtins.print') as mock_print:
                result = main(["system", "run", "command"])
                assert result == 1
                
                printed_output = mock_print.call_args[0][0]
                assert "Error running command" in printed_output

    def test_system_find_exec_found(self):
        """Test system find executable when found."""
        with patch('dev_qol_toolkit.system_utils.find_executable', return_value="/usr/bin/python"):
            with patch('builtins.print') as mock_print:
                result = main(["system", "find-exec", "python"])
                assert result == 0
                
                mock_print.assert_called_with("/usr/bin/python")

    def test_system_find_exec_not_found(self):
        """Test system find executable when not found."""
        with patch('dev_qol_toolkit.system_utils.find_executable', return_value=None):
            with patch('builtins.print') as mock_print:
                result = main(["system", "find-exec", "nonexistent"])
                assert result == 1
                
                printed_output = mock_print.call_args[0][0]
                assert "not found" in printed_output

    def test_system_find_exec_error(self):
        """Test system find executable with error."""
        with patch('dev_qol_toolkit.system_utils.find_executable', side_effect=Exception("Search failed")):
            with patch('builtins.print') as mock_print:
                result = main(["system", "find-exec", "command"])
                assert result == 1
                
                printed_output = mock_print.call_args[0][0]
                assert "Error finding executable" in printed_output

    def test_execute_system_commands_invalid_subcommand(self):
        """Test execute_system_commands with invalid subcommand."""
        args = Mock()
        args.system_cmd = "invalid"
        
        result = execute_system_commands(args)
        assert result == 1


class TestSecurityCommands:
    """Test security CLI commands."""

    def test_security_hash_command(self):
        """Test security hash command."""
        with patch('dev_qol_toolkit.security_utils.hash_data', return_value="abcd1234"):
            with patch('builtins.print') as mock_print:
                result = main(["security", "hash", "test data"])
                assert result == 0
                
                mock_print.assert_called_with("abcd1234")

    def test_security_hash_with_algorithm(self):
        """Test security hash command with specific algorithm."""
        with patch('dev_qol_toolkit.security_utils.hash_data', return_value="hash_result") as mock_hash:
            result = main(["security", "hash", "data", "--algorithm", "sha512"])
            assert result == 0
            
            mock_hash.assert_called_once_with("data", "sha512")

    def test_security_hash_error(self):
        """Test security hash command with error."""
        with patch('dev_qol_toolkit.security_utils.hash_data', side_effect=Exception("Hash failed")):
            with patch('builtins.print') as mock_print:
                result = main(["security", "hash", "data"])
                assert result == 1
                
                printed_output = mock_print.call_args[0][0]
                assert "Error hashing data" in printed_output

    def test_security_generate_secret_command(self):
        """Test security generate secret command."""
        with patch('dev_qol_toolkit.security_utils.generate_secret_key', return_value="secret123"):
            with patch('builtins.print') as mock_print:
                result = main(["security", "generate-secret"])
                assert result == 0
                
                mock_print.assert_called_with("secret123")

    def test_security_generate_secret_with_length(self):
        """Test security generate secret command with custom length."""
        with patch('dev_qol_toolkit.security_utils.generate_secret_key', return_value="secret") as mock_gen:
            result = main(["security", "generate-secret", "--length", "64"])
            assert result == 0
            
            mock_gen.assert_called_once_with(64)

    def test_security_generate_secret_error(self):
        """Test security generate secret command with error."""
        with patch('dev_qol_toolkit.security_utils.generate_secret_key', side_effect=Exception("Generation failed")):
            with patch('builtins.print') as mock_print:
                result = main(["security", "generate-secret"])
                assert result == 1
                
                printed_output = mock_print.call_args[0][0]
                assert "Error generating secret" in printed_output

    def test_security_generate_uuid_command(self):
        """Test security generate UUID command."""
        with patch('dev_qol_toolkit.security_utils.generate_uuid', return_value="uuid-1234"):
            with patch('builtins.print') as mock_print:
                result = main(["security", "generate-uuid"])
                assert result == 0
                
                mock_print.assert_called_with("uuid-1234")

    def test_security_generate_uuid_error(self):
        """Test security generate UUID command with error."""
        with patch('dev_qol_toolkit.security_utils.generate_uuid', side_effect=Exception("UUID failed")):
            with patch('builtins.print') as mock_print:
                result = main(["security", "generate-uuid"])
                assert result == 1
                
                printed_output = mock_print.call_args[0][0]
                assert "Error generating UUID" in printed_output

    def test_execute_security_commands_invalid_subcommand(self):
        """Test execute_security_commands with invalid subcommand."""
        args = Mock()
        args.security_cmd = "invalid"
        
        result = execute_security_commands(args)
        assert result == 1


class TestTimeCommands:
    """Test time CLI commands."""

    def test_time_parse_command(self):
        """Test time parse command."""
        from datetime import datetime
        mock_date = datetime(2024, 1, 15, 14, 30)
        
        with patch('dev_qol_toolkit.time_utils.parse_date', return_value=mock_date):
            with patch('builtins.print') as mock_print:
                result = main(["time", "parse", "2024-01-15 14:30:00"])
                assert result == 0
                
                printed_output = mock_print.call_args[0][0]
                assert "2024-01-15T14:30:00" in printed_output

    def test_time_parse_with_format(self):
        """Test time parse command with specific format."""
        from datetime import datetime
        mock_date = datetime(2024, 1, 15)
        
        with patch('dev_qol_toolkit.time_utils.parse_date', return_value=mock_date) as mock_parse:
            result = main(["time", "parse", "15/01/2024", "--format", "%d/%m/%Y"])
            assert result == 0
            
            mock_parse.assert_called_once_with("15/01/2024", ["%d/%m/%Y"])

    def test_time_parse_error(self):
        """Test time parse command with error."""
        with patch('dev_qol_toolkit.time_utils.parse_date', side_effect=Exception("Parse failed")):
            with patch('builtins.print') as mock_print:
                result = main(["time", "parse", "invalid date"])
                assert result == 1
                
                printed_output = mock_print.call_args[0][0]
                assert "Error parsing date" in printed_output

    def test_time_duration_command(self):
        """Test time duration command."""
        with patch('dev_qol_toolkit.time_utils.format_duration', return_value="1h 30m"):
            with patch('builtins.print') as mock_print:
                result = main(["time", "duration", "5400"])
                assert result == 0
                
                mock_print.assert_called_with("1h 30m")

    def test_time_duration_error(self):
        """Test time duration command with error."""
        with patch('dev_qol_toolkit.time_utils.format_duration', side_effect=Exception("Format failed")):
            with patch('builtins.print') as mock_print:
                result = main(["time", "duration", "3600"])
                assert result == 1
                
                printed_output = mock_print.call_args[0][0]
                assert "Error formatting duration" in printed_output

    def test_time_business_day_command(self):
        """Test time business day command."""
        with patch('dev_qol_toolkit.time_utils.is_business_day', return_value=True):
            with patch('builtins.print') as mock_print:
                result = main(["time", "business-day", "2024-01-15"])
                assert result == 0
                
                mock_print.assert_called_with("Yes")

    def test_time_business_day_not_business(self):
        """Test time business day command for non-business day."""
        with patch('dev_qol_toolkit.time_utils.is_business_day', return_value=False):
            with patch('builtins.print') as mock_print:
                result = main(["time", "business-day", "2024-01-14"])  # Sunday
                assert result == 0
                
                mock_print.assert_called_with("No")

    def test_time_business_day_error(self):
        """Test time business day command with error."""
        with patch('builtins.print') as mock_print:
            result = main(["time", "business-day", "invalid-date"])
            assert result == 1
            
            printed_output = mock_print.call_args[0][0]
            assert "Error checking business day" in printed_output

    def test_execute_time_commands_invalid_subcommand(self):
        """Test execute_time_commands with invalid subcommand."""
        args = Mock()
        args.time_cmd = "invalid"
        
        result = execute_time_commands(args)
        assert result == 1


class TestValidationCommands:
    """Test validation CLI commands."""

    def test_validation_range_valid(self):
        """Test validation range command with valid value."""
        with patch('dev_qol_toolkit.validation_utils.validate_range', return_value=True):
            with patch('builtins.print') as mock_print:
                result = main(["validate", "range", "5", "--min", "1", "--max", "10"])
                assert result == 0
                
                mock_print.assert_called_with("Valid")

    def test_validation_range_invalid(self):
        """Test validation range command with invalid value."""
        with patch('dev_qol_toolkit.validation_utils.validate_range', return_value=False):
            with patch('builtins.print') as mock_print:
                result = main(["validate", "range", "15", "--min", "1", "--max", "10"])
                assert result == 0
                
                mock_print.assert_called_with("Invalid")

    def test_validation_range_error(self):
        """Test validation range command with error."""
        with patch('dev_qol_toolkit.validation_utils.validate_range', side_effect=Exception("Validation failed")):
            with patch('builtins.print') as mock_print:
                result = main(["validate", "range", "5", "--min", "1", "--max", "10"])
                assert result == 1
                
                printed_output = mock_print.call_args[0][0]
                assert "Error validating range" in printed_output

    def test_validation_length_valid(self):
        """Test validation length command with valid text."""
        with patch('dev_qol_toolkit.validation_utils.validate_length', return_value=True):
            with patch('builtins.print') as mock_print:
                result = main(["validate", "length", "hello", "--min", "3", "--max", "10"])
                assert result == 0
                
                mock_print.assert_called_with("Valid")

    def test_validation_length_invalid(self):
        """Test validation length command with invalid text."""
        with patch('dev_qol_toolkit.validation_utils.validate_length', return_value=False):
            with patch('builtins.print') as mock_print:
                result = main(["validate", "length", "hi", "--min", "5"])
                assert result == 0
                
                mock_print.assert_called_with("Invalid")

    def test_validation_length_error(self):
        """Test validation length command with error."""
        with patch('dev_qol_toolkit.validation_utils.validate_length', side_effect=Exception("Length check failed")):
            with patch('builtins.print') as mock_print:
                result = main(["validate", "length", "text", "--min", "1"])
                assert result == 1
                
                printed_output = mock_print.call_args[0][0]
                assert "Error validating length" in printed_output

    def test_execute_validation_commands_invalid_subcommand(self):
        """Test execute_validation_commands with invalid subcommand."""
        args = Mock()
        args.validation_cmd = "invalid"
        
        result = execute_validation_commands(args)
        assert result == 1


class TestCommandRegistration:
    """Test command registration functions."""

    def test_add_json_commands(self):
        """Test adding JSON commands to parser."""
        import argparse
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        
        add_json_commands(subparsers)
        
        # Should be able to parse JSON commands
        args = parser.parse_args(["json", "pretty", "test.json"])
        assert args.command == "json"
        assert args.json_cmd == "pretty"

    def test_add_file_commands(self):
        """Test adding file commands to parser."""
        import argparse
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        
        add_file_commands(subparsers)
        
        # Should be able to parse file commands
        args = parser.parse_args(["file", "find", "test.txt"])
        assert args.command == "file"
        assert args.file_cmd == "find"

    def test_add_string_commands(self):
        """Test adding string commands to parser."""
        import argparse
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        
        add_string_commands(subparsers)
        
        # Should be able to parse string commands
        args = parser.parse_args(["string", "convert", "test", "--to", "snake"])
        assert args.command == "string"
        assert args.string_cmd == "convert"

    def test_add_config_commands(self):
        """Test adding config commands to parser."""
        import argparse
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        
        add_config_commands(subparsers)
        
        # Should be able to parse config commands
        args = parser.parse_args(["config", "load", "config.json"])
        assert args.command == "config"
        assert args.config_cmd == "load"

    def test_add_system_commands(self):
        """Test adding system commands to parser."""
        import argparse
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        
        add_system_commands(subparsers)
        
        # Should be able to parse system commands
        args = parser.parse_args(["system", "info"])
        assert args.command == "system"
        assert args.system_cmd == "info"

    def test_add_security_commands(self):
        """Test adding security commands to parser."""
        import argparse
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        
        add_security_commands(subparsers)
        
        # Should be able to parse security commands
        args = parser.parse_args(["security", "hash", "data"])
        assert args.command == "security"
        assert args.security_cmd == "hash"

    def test_add_time_commands(self):
        """Test adding time commands to parser."""
        import argparse
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        
        add_time_commands(subparsers)
        
        # Should be able to parse time commands
        args = parser.parse_args(["time", "parse", "2024-01-01"])
        assert args.command == "time"
        assert args.time_cmd == "parse"

    def test_add_validation_commands(self):
        """Test adding validation commands to parser."""
        import argparse
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        
        add_validation_commands(subparsers)
        
        # Should be able to parse validation commands
        args = parser.parse_args(["validate", "range", "5", "--min", "1", "--max", "10"])
        assert args.command == "validate"
        assert args.validation_cmd == "range"


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    def test_complete_json_workflow(self, tmp_path: Path):
        """Test complete JSON workflow through CLI."""
        # Create test data
        original_data = {
            "users": [{"name": "Alice", "age": 30}],
            "config": {"debug": True}
        }
        
        json_file = tmp_path / "test.json"
        with json_file.open("w") as f:
            json.dump(original_data, f)
        
        # Test pretty print
        with patch('builtins.print') as mock_print:
            result = main(["json", "pretty", str(json_file)])
            assert result == 0
            
            # Verify output contains expected data
            output = mock_print.call_args[0][0]
            assert "Alice" in output
            assert "debug" in output
        
        # Test flatten
        with patch('builtins.print') as mock_print:
            result = main(["json", "flatten", str(json_file)])
            assert result == 0
            
            # Verify flattened structure
            output = mock_print.call_args[0][0]
            assert "users.0.name" in output

    @given(
        text=st.text(min_size=1, max_size=50).filter(lambda x: x.isalnum()),
        case_type=st.sampled_from(["snake", "camel", "pascal", "kebab"])
    )
    def test_string_conversion_property(self, text, case_type):
        """Property-based test for string conversion commands."""
        with patch('builtins.print') as mock_print:
            result = main(["string", "convert", text, "--to", case_type])
            assert result == 0
            
            # Should have printed something
            mock_print.assert_called_once()