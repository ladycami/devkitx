"""Load, merge, and validate configuration from multiple sources.

Folded into devkitx from the standalone `configmerge` 1.0.0 package
(MIT, same author). Public names are unchanged.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

__all__ = ["load", "load_file", "merge", "from_env"]


def load(*paths: str | Path, env_prefix: str | None = None) -> dict[str, Any]:
    """Load and merge configuration from multiple files and environment.

    Files are merged in order (later files override earlier).
    Environment variables with env_prefix are applied last.

    Args:
        *paths: Configuration file paths (JSON, YAML, TOML)
        env_prefix: Environment variable prefix (e.g., "APP_")

    Returns:
        Merged configuration dictionary

    Example:
        >>> config = load("config.yaml", "config.local.yaml", env_prefix="APP_")
        >>> # Merges base config, local overrides, then APP_* env vars
    """
    result: dict[str, Any] = {}

    for path in paths:
        path = Path(path)
        if path.exists():
            file_config = load_file(path)
            result = merge(result, file_config)

    if env_prefix:
        env_config = from_env(env_prefix)
        result = merge(result, env_config)

    return result


def load_file(path: str | Path) -> dict[str, Any]:
    """Load configuration from a single file.

    Auto-detects format from extension:
    - .json → JSON
    - .yaml, .yml → YAML (requires pyyaml)
    - .toml → TOML (requires tomli on Python < 3.11)
    - .env → dotenv format

    Args:
        path: Path to configuration file

    Returns:
        Configuration dictionary

    Raises:
        ValueError: Unknown file extension
        ImportError: Required parser not installed
    """
    path = Path(path)
    suffix = path.suffix.lower()
    content = path.read_text(encoding="utf-8")

    if suffix == ".json":
        return _require_mapping(json.loads(content), path)

    elif suffix in (".yaml", ".yml"):
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "YAML support requires pyyaml. Install with: pip install 'devkitx[yaml]'"
            ) from None
        return _require_mapping(yaml.safe_load(content) or {}, path)

    elif suffix == ".toml":
        if sys.version_info >= (3, 11):
            import tomllib
        else:
            try:
                import tomli as tomllib
            except ImportError:
                raise ImportError(
                    "TOML support requires tomli on Python < 3.11. "
                    "Install with: pip install 'devkitx[toml]'"
                ) from None
        return tomllib.loads(content)

    elif suffix == ".env":
        return _parse_dotenv(content)

    else:
        raise ValueError(f"Unknown config format: {suffix}")


def _require_mapping(data: Any, path: Path) -> dict[str, Any]:
    """Config files must contain a mapping at the top level."""
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level config must be a mapping, got {type(data).__name__}")
    return data


def merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two configuration dictionaries.

    Override values replace base values. Nested dicts are merged recursively.
    Lists are replaced, not concatenated.

    Args:
        base: Base configuration
        override: Override configuration

    Returns:
        Merged configuration

    Example:
        >>> base = {"db": {"host": "localhost", "port": 5432}}
        >>> override = {"db": {"port": 5433}, "debug": True}
        >>> merge(base, override)
        {'db': {'host': 'localhost', 'port': 5433}, 'debug': True}
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = value

    return result


def from_env(prefix: str) -> dict[str, Any]:
    """Load configuration from environment variables.

    Variables are converted to nested dicts using "__" as separator.
    Values are parsed as JSON if possible, otherwise kept as strings.

    Args:
        prefix: Environment variable prefix (e.g., "APP_")

    Returns:
        Configuration dictionary

    Example:
        >>> # With APP_DB__HOST=localhost and APP_DB__PORT=5432
        >>> from_env("APP_")  # doctest: +SKIP
        {'db': {'host': 'localhost', 'port': 5432}}
    """
    result: dict[str, Any] = {}
    prefix = prefix.upper()

    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue

        # Remove prefix and convert to lowercase
        key = key[len(prefix) :].lower()

        # Parse value (try JSON, fall back to string)
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            parsed_value = value

        # Handle nested keys (DB__HOST → db.host)
        parts = key.split("__")
        current = result
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = parsed_value

    return result


def _parse_dotenv(content: str) -> dict[str, Any]:
    """Parse dotenv format content."""
    result: dict[str, Any] = {}

    for line in content.splitlines():
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        # Parse KEY=VALUE
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()

            # Remove quotes if present
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]

            result[key] = value

    return result
