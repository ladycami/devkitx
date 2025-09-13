"""Tests for config_utils module."""

import json
import tempfile
from pathlib import Path

import pytest

from dev_qol_toolkit.config_utils import load_dotenv, load_yaml_config, load_toml_config


class TestLoadDotenv:
    """Test cases for load_dotenv function."""

    def test_load_simple_env_file(self):
        """Test loading a simple .env file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("KEY1=value1\n")
            f.write("KEY2=value2\n")
            f.write("KEY3=value with spaces\n")
            f.flush()
            
            result = load_dotenv(f.name)
            
        Path(f.name).unlink()  # Clean up
        
        assert result == {
            "KEY1": "value1",
            "KEY2": "value2", 
            "KEY3": "value with spaces"
        }

    def test_load_env_with_quotes(self):
        """Test loading .env file with quoted values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('QUOTED_DOUBLE="double quoted value"\n')
            f.write("QUOTED_SINGLE='single quoted value'\n")
            f.write('MIXED_QUOTES="value with \'inner\' quotes"\n')
            f.flush()
            
            result = load_dotenv(f.name)
            
        Path(f.name).unlink()
        
        assert result == {
            "QUOTED_DOUBLE": "double quoted value",
            "QUOTED_SINGLE": "single quoted value",
            "MIXED_QUOTES": "value with 'inner' quotes"
        }

    def test_load_env_with_comments_and_empty_lines(self):
        """Test loading .env file with comments and empty lines."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("# This is a comment\n")
            f.write("\n")
            f.write("KEY1=value1\n")
            f.write("# Another comment\n")
            f.write("KEY2=value2\n")
            f.write("\n")
            f.flush()
            
            result = load_dotenv(f.name)
            
        Path(f.name).unlink()
        
        assert result == {"KEY1": "value1", "KEY2": "value2"}

    def test_load_env_with_spaces_around_equals(self):
        """Test loading .env file with spaces around equals sign."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("KEY1 = value1\n")
            f.write("KEY2= value2\n")
            f.write("KEY3 =value3\n")
            f.flush()
            
            result = load_dotenv(f.name)
            
        Path(f.name).unlink()
        
        assert result == {
            "KEY1": "value1",
            "KEY2": "value2",
            "KEY3": "value3"
        }

    def test_load_env_file_not_found(self):
        """Test loading non-existent .env file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Environment file not found"):
            load_dotenv("nonexistent.env")

    def test_load_env_invalid_syntax(self):
        """Test loading .env file with invalid syntax raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("VALID_KEY=value\n")
            f.write("invalid line without equals\n")
            f.flush()
            
            with pytest.raises(ValueError, match="Invalid syntax"):
                load_dotenv(f.name)
                
        Path(f.name).unlink()

    def test_load_env_empty_file(self):
        """Test loading empty .env file returns empty dict."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("")
            f.flush()
            
            result = load_dotenv(f.name)
            
        Path(f.name).unlink()
        
        assert result == {}


class TestLoadYamlConfig:
    """Test cases for load_yaml_config function."""

    def test_load_simple_yaml(self):
        """Test loading simple YAML configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("key1: value1\n")
            f.write("key2: 42\n")
            f.write("key3: true\n")
            f.flush()
            
            result = load_yaml_config(f.name)
            
        Path(f.name).unlink()
        
        expected = {"key1": "value1", "key2": 42, "key3": True}
        assert result == expected

    def test_load_yaml_with_quotes(self):
        """Test loading YAML with quoted values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('quoted_string: "hello world"\n')
            f.write("single_quoted: 'test value'\n")
            f.flush()
            
            result = load_yaml_config(f.name)
            
        Path(f.name).unlink()
        
        assert result == {
            "quoted_string": "hello world",
            "single_quoted": "test value"
        }

    def test_load_yaml_with_booleans_and_null(self):
        """Test loading YAML with various boolean and null values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("bool_true: true\n")
            f.write("bool_false: false\n")
            f.write("bool_yes: yes\n")
            f.write("bool_no: no\n")
            f.write("null_value: null\n")
            f.write("none_value: none\n")
            f.write("tilde_null: ~\n")
            f.flush()
            
            result = load_yaml_config(f.name)
            
        Path(f.name).unlink()
        
        assert result["bool_true"] is True
        assert result["bool_false"] is False
        assert result["bool_yes"] is True
        assert result["bool_no"] is False
        assert result["null_value"] is None
        assert result["none_value"] is None
        assert result["tilde_null"] is None

    def test_load_yaml_with_numbers(self):
        """Test loading YAML with integer and float values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("integer: 42\n")
            f.write("float_value: 3.14\n")
            f.write("negative: -10\n")
            f.flush()
            
            result = load_yaml_config(f.name)
            
        Path(f.name).unlink()
        
        assert result == {
            "integer": 42,
            "float_value": 3.14,
            "negative": -10
        }

    def test_load_yaml_file_not_found(self):
        """Test loading non-existent YAML file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="YAML file not found"):
            load_yaml_config("nonexistent.yaml")

    def test_load_yaml_empty_file(self):
        """Test loading empty YAML file returns empty dict."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            f.flush()
            
            result = load_yaml_config(f.name)
            
        Path(f.name).unlink()
        
        assert result == {}

    def test_load_yaml_with_comments(self):
        """Test loading YAML file with comments."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("# This is a comment\n")
            f.write("key1: value1\n")
            f.write("# Another comment\n")
            f.write("key2: value2\n")
            f.flush()
            
            result = load_yaml_config(f.name)
            
        Path(f.name).unlink()
        
        assert result == {"key1": "value1", "key2": "value2"}


class TestLoadTomlConfig:
    """Test cases for load_toml_config function."""

    def test_load_simple_toml(self):
        """Test loading simple TOML configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("key1 = 'value1'\n")
            f.write("key2 = 42\n")
            f.write("key3 = true\n")
            f.flush()
            
            result = load_toml_config(f.name)
            
        Path(f.name).unlink()
        
        expected = {"key1": "value1", "key2": 42, "key3": True}
        assert result == expected

    def test_load_toml_with_sections(self):
        """Test loading TOML with sections."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("global_key = 'global_value'\n")
            f.write("\n")
            f.write("[section1]\n")
            f.write("key1 = 'value1'\n")
            f.write("key2 = 42\n")
            f.write("\n")
            f.write("[section2]\n")
            f.write("key3 = true\n")
            f.flush()
            
            result = load_toml_config(f.name)
            
        Path(f.name).unlink()
        
        expected = {
            "global_key": "global_value",
            "section1": {"key1": "value1", "key2": 42},
            "section2": {"key3": True}
        }
        assert result == expected

    def test_load_toml_with_quotes(self):
        """Test loading TOML with quoted values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write('double_quoted = "hello world"\n')
            f.write("single_quoted = 'test value'\n")
            f.flush()
            
            result = load_toml_config(f.name)
            
        Path(f.name).unlink()
        
        assert result == {
            "double_quoted": "hello world",
            "single_quoted": "test value"
        }

    def test_load_toml_with_booleans(self):
        """Test loading TOML with boolean values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("bool_true = true\n")
            f.write("bool_false = false\n")
            f.flush()
            
            result = load_toml_config(f.name)
            
        Path(f.name).unlink()
        
        assert result == {"bool_true": True, "bool_false": False}

    def test_load_toml_with_numbers(self):
        """Test loading TOML with integer and float values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("integer = 42\n")
            f.write("float_value = 3.14\n")
            f.write("negative = -10\n")
            f.flush()
            
            result = load_toml_config(f.name)
            
        Path(f.name).unlink()
        
        assert result == {
            "integer": 42,
            "float_value": 3.14,
            "negative": -10
        }

    def test_load_toml_file_not_found(self):
        """Test loading non-existent TOML file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="TOML file not found"):
            load_toml_config("nonexistent.toml")

    def test_load_toml_empty_file(self):
        """Test loading empty TOML file returns empty dict."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("")
            f.flush()
            
            result = load_toml_config(f.name)
            
        Path(f.name).unlink()
        
        assert result == {}

    def test_load_toml_with_comments(self):
        """Test loading TOML file with comments."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("# This is a comment\n")
            f.write("key1 = 'value1'\n")
            f.write("# Another comment\n")
            f.write("key2 = 'value2'\n")
            f.flush()
            
            result = load_toml_config(f.name)
            
        Path(f.name).unlink()
        
        assert result == {"key1": "value1", "key2": "value2"}


class TestConfigFormats:
    """Test cases for different config file formats."""

    def test_json_config_loading(self):
        """Test that JSON configs can be loaded using json module."""
        config_data = {"key1": "value1", "key2": 42, "key3": True}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            f.flush()
            
            # Load using standard json module
            with open(f.name, 'r') as json_file:
                result = json.load(json_file)
                
        Path(f.name).unlink()
        
        assert result == config_data

    def test_pathlib_path_support(self):
        """Test that all functions support pathlib.Path objects."""
        # Test .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("KEY=value\n")
            f.flush()
            
            result = load_dotenv(Path(f.name))
            assert result == {"KEY": "value"}
            
        Path(f.name).unlink()
        
        # Test YAML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("key: value\n")
            f.flush()
            
            result = load_yaml_config(Path(f.name))
            assert result == {"key": "value"}
            
        Path(f.name).unlink()
        
        # Test TOML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("key = 'value'\n")
            f.flush()
            
            result = load_toml_config(Path(f.name))
            assert result == {"key": "value"}
            
        Path(f.name).unlink()