"""Configuration management utilities for DevKitX.

This module provides utilities for loading, managing, and validating
configuration from various sources including JSON, YAML, TOML, and .env files.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, TypeVar

T = TypeVar("T")

__all__ = [
    "ConfigManager",
    "load_dotenv",
    "load_yaml_config",
    "load_toml_config",
]


class ConfigManager:
    """Configuration manager for handling multiple config sources."""

    def __init__(self, config_paths: list[str | Path]) -> None:
        """Initialize ConfigManager with config file paths.

        Args:
            config_paths: List of configuration file paths
        """
        self.config_paths = [Path(p) for p in config_paths]
        self._config: dict[str, Any] = {}
        self._loaded = False

    def load(self) -> dict[str, Any]:
        """Load configuration from all sources.

        Returns:
            Merged configuration dictionary

        Raises:
            ValueError: If no valid configuration files are found
        """
        self._config = {}
        loaded_any = False

        for config_path in self.config_paths:
            if not config_path.exists():
                continue

            try:
                if config_path.suffix.lower() in [".env"]:
                    config_data = load_dotenv(config_path)
                elif config_path.suffix.lower() in [".yaml", ".yml"]:
                    config_data = load_yaml_config(config_path)
                elif config_path.suffix.lower() in [".toml"]:
                    config_data = load_toml_config(config_path)
                elif config_path.suffix.lower() in [".json"]:
                    with open(config_path, "r", encoding="utf-8") as f:
                        config_data = json.load(f)
                else:
                    # Try to detect format by content
                    config_data = self._auto_detect_format(config_path)

                # Merge configuration data
                self._deep_merge(self._config, config_data)
                loaded_any = True

            except Exception as e:
                # Log warning but continue with other files
                print(f"Warning: Failed to load config from {config_path}: {e}")
                continue

        if not loaded_any and self.config_paths:
            raise ValueError("No valid configuration files could be loaded")

        self._loaded = True
        return self._config.copy()

    def get(self, key: str, default: Any = None, type_hint: type[T] | None = None) -> T:
        """Get configuration value with optional type casting.

        Args:
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if key not found
            type_hint: Type to cast the value to

        Returns:
            Configuration value
        """
        if not self._loaded:
            self.load()

        # Support dot notation for nested keys
        value = self._config
        for key_part in key.split("."):
            if isinstance(value, dict) and key_part in value:
                value = value[key_part]
            else:
                value = default
                break

        # Type casting if requested
        if type_hint is not None and value is not default:
            try:
                if type_hint is bool:
                    # Handle string boolean values
                    if isinstance(value, str):
                        return value.lower() in ("true", "1", "yes", "on")  # type: ignore
                    return bool(value)  # type: ignore
                elif type_hint in (int, float, str):
                    return type_hint(value)  # type: ignore
                else:
                    return value  # type: ignore
            except (ValueError, TypeError):
                return default  # type: ignore

        return value  # type: ignore

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.

        Args:
            key: Configuration key (supports dot notation for nested keys)
            value: Value to set
        """
        if not self._loaded:
            self.load()

        # Support dot notation for nested keys
        config = self._config
        key_parts = key.split(".")

        # Navigate to the parent of the target key
        for key_part in key_parts[:-1]:
            if key_part not in config:
                config[key_part] = {}
            elif not isinstance(config[key_part], dict):
                config[key_part] = {}
            config = config[key_part]

        # Set the final value
        config[key_parts[-1]] = value

    def save(self, path: str | Path | None = None) -> None:
        """Save configuration to file.

        Args:
            path: Optional path to save to, uses first config path if None

        Raises:
            ValueError: If no path is provided and no config paths are available
        """
        if not self._loaded:
            self.load()

        if path is None:
            if not self.config_paths:
                raise ValueError("No path provided and no config paths available")
            save_path = self.config_paths[0]
        else:
            save_path = Path(path)

        # Determine format from file extension
        if save_path.suffix.lower() in [".json"]:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)
        elif save_path.suffix.lower() in [".yaml", ".yml"]:
            self._save_as_yaml(save_path)
        elif save_path.suffix.lower() in [".toml"]:
            self._save_as_toml(save_path)
        elif save_path.suffix.lower() in [".env"]:
            self._save_as_env(save_path)
        else:
            # Default to JSON
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)

    def merge_env_vars(self, prefix: str = "") -> None:
        """Merge environment variables into configuration.

        Args:
            prefix: Prefix for environment variables to include
        """
        if not self._loaded:
            self.load()

        for key, value in os.environ.items():
            if prefix and not key.startswith(prefix):
                continue

            # Remove prefix if specified
            config_key = key[len(prefix) :] if prefix else key

            # Convert environment variable name to config key
            # e.g., MY_APP_DATABASE_URL -> my_app.database.url
            config_key = config_key.lower().replace("_", ".")

            # Set the value using dot notation
            self.set(config_key, value)

    def _deep_merge(self, target: dict[str, Any], source: dict[str, Any]) -> None:
        """Deep merge source dictionary into target dictionary."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    def _auto_detect_format(self, path: Path) -> dict[str, Any]:
        """Auto-detect configuration file format by content."""
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        # Try JSON first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Try YAML
        if ":" in content:
            try:
                return _parse_simple_yaml(path)
            except Exception:
                pass

        # Try TOML
        if "=" in content:
            try:
                return _parse_simple_toml(path)
            except Exception:
                pass

        # Try .env format
        try:
            return load_dotenv(path)
        except Exception:
            pass

        raise ValueError(f"Could not determine format for {path}")

    def _save_as_yaml(self, path: Path) -> None:
        """Save configuration as YAML format."""
        try:
            import yaml

            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(self._config, f, default_flow_style=False)
        except ImportError:
            # Fallback to simple YAML format
            with open(path, "w", encoding="utf-8") as f:
                self._write_simple_yaml(f, self._config)

    def _save_as_toml(self, path: Path) -> None:
        """Save configuration as TOML format."""
        try:
            import tomli_w

            with open(path, "wb") as f:
                tomli_w.dump(self._config, f)
        except ImportError:
            # Fallback to simple TOML format
            with open(path, "w", encoding="utf-8") as f:
                self._write_simple_toml(f, self._config)

    def _save_as_env(self, path: Path) -> None:
        """Save configuration as .env format."""
        with open(path, "w", encoding="utf-8") as f:
            self._write_env_format(f, self._config)

    def _write_simple_yaml(self, f, data: dict[str, Any], indent: int = 0) -> None:
        """Write simple YAML format."""
        for key, value in data.items():
            if isinstance(value, dict):
                f.write(f"{'  ' * indent}{key}:\n")
                self._write_simple_yaml(f, value, indent + 1)
            else:
                f.write(f"{'  ' * indent}{key}: {self._yaml_value(value)}\n")

    def _write_simple_toml(self, f, data: dict[str, Any]) -> None:
        """Write simple TOML format."""
        # Write top-level keys first
        for key, value in data.items():
            if not isinstance(value, dict):
                f.write(f"{key} = {self._toml_value(value)}\n")

        # Write sections
        for key, value in data.items():
            if isinstance(value, dict):
                f.write(f"\n[{key}]\n")
                for sub_key, sub_value in value.items():
                    f.write(f"{sub_key} = {self._toml_value(sub_value)}\n")

    def _write_env_format(self, f, data: dict[str, Any], prefix: str = "") -> None:
        """Write .env format."""
        for key, value in data.items():
            if isinstance(value, dict):
                new_prefix = f"{prefix}{key.upper()}_" if prefix else f"{key.upper()}_"
                self._write_env_format(f, value, new_prefix)
            else:
                env_key = f"{prefix}{key.upper()}"
                f.write(f"{env_key}={value}\n")

    def _yaml_value(self, value: Any) -> str:
        """Format value for YAML output."""
        if isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, str):
            return f"'{value}'"
        else:
            return str(value)

    def _toml_value(self, value: Any) -> str:
        """Format value for TOML output."""
        if isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, str):
            return f"'{value}'"
        else:
            return str(value)


def load_dotenv(path: str | Path) -> dict[str, str]:
    """Load environment variables from .env file.

    Args:
        path: Path to .env file

    Returns:
        Dictionary of environment variables

    Raises:
        FileNotFoundError: If the .env file doesn't exist
        ValueError: If the .env file contains invalid syntax
    """
    env_path = Path(path)
    if not env_path.exists():
        raise FileNotFoundError(f"Environment file not found: {env_path}")

    env_vars = {}

    with open(env_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Match KEY=VALUE pattern
            match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$", line)
            if not match:
                raise ValueError(f"Invalid syntax in {env_path} at line {line_num}: {line}")

            key, value = match.groups()

            # Handle quoted values
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

            env_vars[key] = value

    return env_vars


def load_yaml_config(path: str | Path) -> dict[str, Any]:
    """Load configuration from YAML file.

    Note: This is a basic YAML parser that handles simple cases.
    For complex YAML files, consider using the 'pyyaml' library.

    Args:
        path: Path to YAML file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If the YAML file doesn't exist
        ValueError: If the YAML file contains invalid syntax
    """
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise FileNotFoundError(f"YAML file not found: {yaml_path}")

    try:
        # Try to import yaml first
        import yaml

        with open(yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        # Fallback to basic YAML parsing for simple cases
        return _parse_simple_yaml(yaml_path)


def load_toml_config(path: str | Path) -> dict[str, Any]:
    """Load configuration from TOML file.

    Args:
        path: Path to TOML file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If the TOML file doesn't exist
        ValueError: If the TOML file contains invalid syntax
    """
    toml_path = Path(path)
    if not toml_path.exists():
        raise FileNotFoundError(f"TOML file not found: {toml_path}")

    try:
        # Try to use tomllib (Python 3.11+) or tomli
        try:
            import tomllib

            with open(toml_path, "rb") as f:
                return tomllib.load(f)
        except ImportError:
            import tomli

            with open(toml_path, "rb") as f:
                return tomli.load(f)
    except ImportError:
        # Fallback to basic TOML parsing for simple cases
        return _parse_simple_toml(toml_path)


def _parse_simple_yaml(path: Path) -> dict[str, Any]:
    """Basic YAML parser for simple key-value pairs and lists.

    This is a fallback parser that handles basic YAML syntax.
    For complex YAML files, install the 'pyyaml' library.
    """
    config = {}
    current_section = config

    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.rstrip()

            # Skip empty lines and comments
            if not line or line.strip().startswith("#"):
                continue

            # Handle simple key-value pairs
            if ":" in line and not line.startswith(" "):
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if value:
                    current_section[key] = _parse_yaml_value(value)
                else:
                    # This might be a section header
                    current_section[key] = {}

    return config


def _parse_simple_toml(path: Path) -> dict[str, Any]:
    """Basic TOML parser for simple key-value pairs and sections.

    This is a fallback parser that handles basic TOML syntax.
    For complex TOML files, install the 'tomli' library.
    """
    config = {}
    current_section = config

    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Handle section headers [section]
            if line.startswith("[") and line.endswith("]"):
                section_name = line[1:-1]
                current_section = config.setdefault(section_name, {})
                continue

            # Handle key-value pairs
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                current_section[key] = _parse_toml_value(value)

    return config


def _parse_yaml_value(value: str) -> Any:
    """Parse a YAML value string into appropriate Python type."""
    value = value.strip()

    # Handle quoted strings
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]

    # Handle booleans
    if value.lower() in ("true", "yes", "on"):
        return True
    if value.lower() in ("false", "no", "off"):
        return False

    # Handle null
    if value.lower() in ("null", "none", "~", ""):
        return None

    # Try to parse as number
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        pass

    # Return as string
    return value


def _parse_toml_value(value: str) -> Any:
    """Parse a TOML value string into appropriate Python type."""
    value = value.strip()

    # Handle quoted strings
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]

    # Handle booleans
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False

    # Try to parse as number
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        pass

    # Return as string
    return value
