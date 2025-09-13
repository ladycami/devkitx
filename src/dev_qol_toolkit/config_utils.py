"""Configuration management utilities for the dev-qol-toolkit.

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
        # Placeholder implementation
        raise NotImplementedError("Class will be implemented in task 4.2")
    
    def load(self) -> dict[str, Any]:
        """Load configuration from all sources.
        
        Returns:
            Merged configuration dictionary
        """
        # Placeholder implementation
        raise NotImplementedError("Method will be implemented in task 4.2")
    
    def get(self, key: str, default: Any = None, type_hint: type[T] | None = None) -> T:
        """Get configuration value with optional type casting.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            type_hint: Type to cast the value to
            
        Returns:
            Configuration value
        """
        # Placeholder implementation
        raise NotImplementedError("Method will be implemented in task 4.2")
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        # Placeholder implementation
        raise NotImplementedError("Method will be implemented in task 4.2")
    
    def save(self, path: str | Path | None = None) -> None:
        """Save configuration to file.
        
        Args:
            path: Optional path to save to, uses first config path if None
        """
        # Placeholder implementation
        raise NotImplementedError("Method will be implemented in task 4.2")
    
    def merge_env_vars(self, prefix: str = "") -> None:
        """Merge environment variables into configuration.
        
        Args:
            prefix: Prefix for environment variables to include
        """
        # Placeholder implementation
        raise NotImplementedError("Method will be implemented in task 4.2")


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
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Match KEY=VALUE pattern
            match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$', line)
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
        with open(yaml_path, 'r', encoding='utf-8') as f:
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
            with open(toml_path, 'rb') as f:
                return tomllib.load(f)
        except ImportError:
            import tomli
            with open(toml_path, 'rb') as f:
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
    
    with open(path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.rstrip()
            
            # Skip empty lines and comments
            if not line or line.strip().startswith('#'):
                continue
            
            # Handle simple key-value pairs
            if ':' in line and not line.startswith(' '):
                key, value = line.split(':', 1)
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
    
    with open(path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Handle section headers [section]
            if line.startswith('[') and line.endswith(']'):
                section_name = line[1:-1]
                current_section = config.setdefault(section_name, {})
                continue
            
            # Handle key-value pairs
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                current_section[key] = _parse_toml_value(value)
    
    return config


def _parse_yaml_value(value: str) -> Any:
    """Parse a YAML value string into appropriate Python type."""
    value = value.strip()
    
    # Handle quoted strings
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    
    # Handle booleans
    if value.lower() in ('true', 'yes', 'on'):
        return True
    if value.lower() in ('false', 'no', 'off'):
        return False
    
    # Handle null
    if value.lower() in ('null', 'none', '~', ''):
        return None
    
    # Try to parse as number
    try:
        if '.' in value:
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
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    
    # Handle booleans
    if value.lower() == 'true':
        return True
    if value.lower() == 'false':
        return False
    
    # Try to parse as number
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        pass
    
    # Return as string
    return value