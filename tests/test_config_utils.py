"""Tests for config_utils module."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from devtools_py.config_utils import ConfigManager, load_dotenv, load_yaml_config, load_toml_config


class TestLoadDotenv:
    """Test cases for load_dotenv function."""

    def test_load_simple_env_file(self):
        """Test loading a simple .env file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("KEY1=value1\n")
            f.write("KEY2=value2\n")
            f.write("KEY3=value with spaces\n")
            f.flush()

            result = load_dotenv(f.name)

        Path(f.name).unlink()  # Clean up

        assert result == {"KEY1": "value1", "KEY2": "value2", "KEY3": "value with spaces"}

    def test_load_env_with_quotes(self):
        """Test loading .env file with quoted values."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write('QUOTED_DOUBLE="double quoted value"\n')
            f.write("QUOTED_SINGLE='single quoted value'\n")
            f.write("MIXED_QUOTES=\"value with 'inner' quotes\"\n")
            f.flush()

            result = load_dotenv(f.name)

        Path(f.name).unlink()

        assert result == {
            "QUOTED_DOUBLE": "double quoted value",
            "QUOTED_SINGLE": "single quoted value",
            "MIXED_QUOTES": "value with 'inner' quotes",
        }

    def test_load_env_with_comments_and_empty_lines(self):
        """Test loading .env file with comments and empty lines."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("KEY1 = value1\n")
            f.write("KEY2= value2\n")
            f.write("KEY3 =value3\n")
            f.flush()

            result = load_dotenv(f.name)

        Path(f.name).unlink()

        assert result == {"KEY1": "value1", "KEY2": "value2", "KEY3": "value3"}

    def test_load_env_file_not_found(self):
        """Test loading non-existent .env file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Environment file not found"):
            load_dotenv("nonexistent.env")

    def test_load_env_invalid_syntax(self):
        """Test loading .env file with invalid syntax raises ValueError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("VALID_KEY=value\n")
            f.write("invalid line without equals\n")
            f.flush()

            with pytest.raises(ValueError, match="Invalid syntax"):
                load_dotenv(f.name)

        Path(f.name).unlink()

    def test_load_env_empty_file(self):
        """Test loading empty .env file returns empty dict."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("")
            f.flush()

            result = load_dotenv(f.name)

        Path(f.name).unlink()

        assert result == {}


class TestLoadYamlConfig:
    """Test cases for load_yaml_config function."""

    def test_load_simple_yaml(self):
        """Test loading simple YAML configuration."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write('quoted_string: "hello world"\n')
            f.write("single_quoted: 'test value'\n")
            f.flush()

            result = load_yaml_config(f.name)

        Path(f.name).unlink()

        assert result == {"quoted_string": "hello world", "single_quoted": "test value"}

    def test_load_yaml_with_booleans_and_null(self):
        """Test loading YAML with various boolean and null values."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("integer: 42\n")
            f.write("float_value: 3.14\n")
            f.write("negative: -10\n")
            f.flush()

            result = load_yaml_config(f.name)

        Path(f.name).unlink()

        assert result == {"integer": 42, "float_value": 3.14, "negative": -10}

    def test_load_yaml_file_not_found(self):
        """Test loading non-existent YAML file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="YAML file not found"):
            load_yaml_config("nonexistent.yaml")

    def test_load_yaml_empty_file(self):
        """Test loading empty YAML file returns empty dict."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            f.flush()

            result = load_yaml_config(f.name)

        Path(f.name).unlink()

        assert result == {}

    def test_load_yaml_with_comments(self):
        """Test loading YAML file with comments."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
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
            "section2": {"key3": True},
        }
        assert result == expected

    def test_load_toml_with_quotes(self):
        """Test loading TOML with quoted values."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('double_quoted = "hello world"\n')
            f.write("single_quoted = 'test value'\n")
            f.flush()

            result = load_toml_config(f.name)

        Path(f.name).unlink()

        assert result == {"double_quoted": "hello world", "single_quoted": "test value"}

    def test_load_toml_with_booleans(self):
        """Test loading TOML with boolean values."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("bool_true = true\n")
            f.write("bool_false = false\n")
            f.flush()

            result = load_toml_config(f.name)

        Path(f.name).unlink()

        assert result == {"bool_true": True, "bool_false": False}

    def test_load_toml_with_numbers(self):
        """Test loading TOML with integer and float values."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("integer = 42\n")
            f.write("float_value = 3.14\n")
            f.write("negative = -10\n")
            f.flush()

            result = load_toml_config(f.name)

        Path(f.name).unlink()

        assert result == {"integer": 42, "float_value": 3.14, "negative": -10}

    def test_load_toml_file_not_found(self):
        """Test loading non-existent TOML file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="TOML file not found"):
            load_toml_config("nonexistent.toml")

    def test_load_toml_empty_file(self):
        """Test loading empty TOML file returns empty dict."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("")
            f.flush()

            result = load_toml_config(f.name)

        Path(f.name).unlink()

        assert result == {}

    def test_load_toml_with_comments(self):
        """Test loading TOML file with comments."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("# This is a comment\n")
            f.write("key1 = 'value1'\n")
            f.write("# Another comment\n")
            f.write("key2 = 'value2'\n")
            f.flush()

            result = load_toml_config(f.name)

        Path(f.name).unlink()

        assert result == {"key1": "value1", "key2": "value2"}


class TestConfigManager:
    """Test cases for ConfigManager class."""

    def test_config_manager_initialization(self):
        """Test ConfigManager initialization."""
        paths = ["config1.json", "config2.yaml"]
        manager = ConfigManager(paths)

        assert len(manager.config_paths) == 2
        assert manager.config_paths[0] == Path("config1.json")
        assert manager.config_paths[1] == Path("config2.yaml")

    def test_load_single_json_config(self):
        """Test loading a single JSON configuration file."""
        config_data = {"key1": "value1", "key2": 42, "nested": {"key3": True}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()

            manager = ConfigManager([f.name])
            result = manager.load()

        Path(f.name).unlink()

        assert result == config_data

    def test_load_multiple_config_files(self):
        """Test loading and merging multiple configuration files."""
        config1 = {"key1": "value1", "shared": {"a": 1}}
        config2 = {"key2": "value2", "shared": {"b": 2}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f1:
            json.dump(config1, f1)
            f1.flush()

            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f2:
                json.dump(config2, f2)
                f2.flush()

                manager = ConfigManager([f1.name, f2.name])
                result = manager.load()

        Path(f1.name).unlink()
        Path(f2.name).unlink()

        expected = {"key1": "value1", "key2": "value2", "shared": {"a": 1, "b": 2}}
        assert result == expected

    def test_get_simple_key(self):
        """Test getting simple configuration values."""
        config_data = {"key1": "value1", "key2": 42, "key3": True}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()

            manager = ConfigManager([f.name])
            manager.load()

            assert manager.get("key1") == "value1"
            assert manager.get("key2") == 42
            assert manager.get("key3") is True
            assert manager.get("nonexistent") is None
            assert manager.get("nonexistent", "default") == "default"

        Path(f.name).unlink()

    def test_get_nested_key_with_dot_notation(self):
        """Test getting nested configuration values using dot notation."""
        config_data = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {"username": "user", "password": "pass"},
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()

            manager = ConfigManager([f.name])
            manager.load()

            assert manager.get("database.host") == "localhost"
            assert manager.get("database.port") == 5432
            assert manager.get("database.credentials.username") == "user"
            assert manager.get("database.credentials.password") == "pass"
            assert manager.get("database.nonexistent") is None
            assert manager.get("nonexistent.key", "default") == "default"

        Path(f.name).unlink()

    def test_get_with_type_casting(self):
        """Test getting values with type casting."""
        config_data = {
            "string_number": "42",
            "string_float": "3.14",
            "string_bool_true": "true",
            "string_bool_false": "false",
            "number": 100,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()

            manager = ConfigManager([f.name])
            manager.load()

            assert manager.get("string_number", type_hint=int) == 42
            assert manager.get("string_float", type_hint=float) == 3.14
            assert manager.get("string_bool_true", type_hint=bool) is True
            assert manager.get("string_bool_false", type_hint=bool) is False
            assert manager.get("number", type_hint=str) == "100"

        Path(f.name).unlink()

    def test_set_simple_key(self):
        """Test setting simple configuration values."""
        manager = ConfigManager([])
        manager.load()  # Initialize empty config

        manager.set("key1", "value1")
        manager.set("key2", 42)
        manager.set("key3", True)

        assert manager.get("key1") == "value1"
        assert manager.get("key2") == 42
        assert manager.get("key3") is True

    def test_set_nested_key_with_dot_notation(self):
        """Test setting nested configuration values using dot notation."""
        manager = ConfigManager([])
        manager.load()  # Initialize empty config

        manager.set("database.host", "localhost")
        manager.set("database.port", 5432)
        manager.set("database.credentials.username", "user")

        assert manager.get("database.host") == "localhost"
        assert manager.get("database.port") == 5432
        assert manager.get("database.credentials.username") == "user"

    def test_merge_env_vars(self):
        """Test merging environment variables."""
        # Set some test environment variables
        os.environ["TEST_DATABASE_HOST"] = "env-host"
        os.environ["TEST_DATABASE_PORT"] = "3306"
        os.environ["OTHER_VAR"] = "should-not-be-included"

        try:
            manager = ConfigManager([])
            manager.load()
            manager.merge_env_vars("TEST_")

            assert manager.get("database.host") == "env-host"
            assert manager.get("database.port") == "3306"
            assert manager.get("other.var") is None

        finally:
            # Clean up environment variables
            os.environ.pop("TEST_DATABASE_HOST", None)
            os.environ.pop("TEST_DATABASE_PORT", None)
            os.environ.pop("OTHER_VAR", None)

    def test_merge_env_vars_no_prefix(self):
        """Test merging all environment variables without prefix."""
        # Set a test environment variable
        os.environ["CUSTOM_CONFIG_VALUE"] = "test-value"

        try:
            manager = ConfigManager([])
            manager.load()
            manager.merge_env_vars()

            # Should include the custom variable
            assert manager.get("custom.config.value") == "test-value"

        finally:
            os.environ.pop("CUSTOM_CONFIG_VALUE", None)

    def test_save_json_config(self):
        """Test saving configuration as JSON."""
        config_data = {"key1": "value1", "key2": 42}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()

            manager = ConfigManager([f.name])
            manager.load()
            manager.set("key3", "new_value")

            # Save to a new file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as save_f:
                manager.save(save_f.name)

                # Verify saved content
                with open(save_f.name, "r") as verify_f:
                    saved_data = json.load(verify_f)

            Path(save_f.name).unlink()

        Path(f.name).unlink()

        expected = {"key1": "value1", "key2": 42, "key3": "new_value"}
        assert saved_data == expected

    def test_save_without_path_uses_first_config_path(self):
        """Test saving without specifying path uses first config path."""
        config_data = {"key1": "value1"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()

            manager = ConfigManager([f.name])
            manager.load()
            manager.set("key2", "value2")
            manager.save()  # Should save to f.name

            # Verify the file was updated
            with open(f.name, "r") as verify_f:
                saved_data = json.load(verify_f)

        Path(f.name).unlink()

        expected = {"key1": "value1", "key2": "value2"}
        assert saved_data == expected

    def test_load_nonexistent_files_raises_error(self):
        """Test loading non-existent files raises ValueError."""
        manager = ConfigManager(["nonexistent1.json", "nonexistent2.yaml"])

        with pytest.raises(ValueError, match="No valid configuration files could be loaded"):
            manager.load()

    def test_load_mixed_existing_and_nonexistent_files(self):
        """Test loading mix of existing and non-existent files."""
        config_data = {"key1": "value1"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()

            # Mix existing and non-existent files
            manager = ConfigManager(["nonexistent.json", f.name, "another_nonexistent.yaml"])
            result = manager.load()

        Path(f.name).unlink()

        assert result == config_data

    def test_auto_load_on_get_when_not_loaded(self):
        """Test that get() automatically loads config if not already loaded."""
        config_data = {"key1": "value1"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()

            manager = ConfigManager([f.name])
            # Don't call load() explicitly
            result = manager.get("key1")

        Path(f.name).unlink()

        assert result == "value1"

    def test_auto_load_on_set_when_not_loaded(self):
        """Test that set() automatically loads config if not already loaded."""
        config_data = {"existing_key": "existing_value"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()

            manager = ConfigManager([f.name])
            # Don't call load() explicitly
            manager.set("new_key", "new_value")

            assert manager.get("existing_key") == "existing_value"
            assert manager.get("new_key") == "new_value"

        Path(f.name).unlink()


class TestConfigFormats:
    """Test cases for different config file formats."""

    def test_json_config_loading(self):
        """Test that JSON configs can be loaded using json module."""
        config_data = {"key1": "value1", "key2": 42, "key3": True}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()

            # Load using standard json module
            with open(f.name, "r") as json_file:
                result = json.load(json_file)

        Path(f.name).unlink()

        assert result == config_data

    def test_pathlib_path_support(self):
        """Test that all functions support pathlib.Path objects."""
        # Test .env file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("KEY=value\n")
            f.flush()

            result = load_dotenv(Path(f.name))
            assert result == {"KEY": "value"}

        Path(f.name).unlink()

        # Test YAML file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("key: value\n")
            f.flush()

            result = load_yaml_config(Path(f.name))
            assert result == {"key": "value"}

        Path(f.name).unlink()

        # Test TOML file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("key = 'value'\n")
            f.flush()

            result = load_toml_config(Path(f.name))
            assert result == {"key": "value"}

        Path(f.name).unlink()

    def test_config_manager_with_different_formats(self):
        """Test ConfigManager with different file formats."""
        # Create different format files
        json_data = {"json_key": "json_value", "shared": {"json": True}}
        yaml_data = "yaml_key: yaml_value\nshared:\n  yaml: true"
        toml_data = "toml_key = 'toml_value'\n[shared]\nyaml = false\ntoml = true"
        env_data = "ENV_KEY=env_value\nSHARED_ENV=true"

        files_to_cleanup = []

        try:
            # JSON file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump(json_data, f)
                f.flush()
                json_path = f.name
                files_to_cleanup.append(json_path)

            # YAML file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                f.write(yaml_data)
                f.flush()
                yaml_path = f.name
                files_to_cleanup.append(yaml_path)

            # TOML file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
                f.write(toml_data)
                f.flush()
                toml_path = f.name
                files_to_cleanup.append(toml_path)

            # ENV file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
                f.write(env_data)
                f.flush()
                env_path = f.name
                files_to_cleanup.append(env_path)

            # Load all formats
            manager = ConfigManager([json_path, yaml_path, toml_path, env_path])
            result = manager.load()

            # Verify merged results
            assert result["json_key"] == "json_value"
            assert result["yaml_key"] == "yaml_value"
            assert result["toml_key"] == "toml_value"
            assert result["ENV_KEY"] == "env_value"
            assert result["SHARED_ENV"] == "true"

            # Check merged shared section
            assert "shared" in result
            assert result["shared"]["json"] is True
            assert result["shared"]["yaml"] is False  # TOML overrode this to false
            assert result["shared"]["toml"] is True

        finally:
            # Clean up files
            for file_path in files_to_cleanup:
                Path(file_path).unlink(missing_ok=True)
