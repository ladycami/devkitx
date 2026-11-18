"""Tests for devkitx.config."""

import json
import os
import tempfile
from pathlib import Path

from devkitx.config import from_env, load, load_file, merge


def test_merge_dicts():
    """Test merging two dictionaries."""
    base = {"a": 1, "b": {"c": 2, "d": 3}}
    override = {"b": {"d": 4}, "e": 5}

    result = merge(base, override)

    assert result == {"a": 1, "b": {"c": 2, "d": 4}, "e": 5}


def test_load_json_file():
    """Test loading JSON file."""
    data = {"name": "test", "value": 42}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        temp_path = f.name

    try:
        result = load_file(temp_path)
        assert result == data
    finally:
        Path(temp_path).unlink()


def test_from_env():
    """Test loading from environment variables."""
    # Set test environment variables
    os.environ["TEST_DB__HOST"] = "localhost"
    os.environ["TEST_DB__PORT"] = "5432"
    os.environ["TEST_DEBUG"] = "true"

    try:
        result = from_env("TEST_")

        expected = {"db": {"host": "localhost", "port": 5432}, "debug": True}
        assert result == expected
    finally:
        # Clean up
        for key in ["TEST_DB__HOST", "TEST_DB__PORT", "TEST_DEBUG"]:
            os.environ.pop(key, None)


def test_load_multiple_files():
    """Test loading and merging multiple files."""
    base_data = {"name": "app", "db": {"host": "localhost"}}
    override_data = {"db": {"port": 5432}, "debug": True}

    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir) / "base.json"
        override_path = Path(temp_dir) / "override.json"

        base_path.write_text(json.dumps(base_data))
        override_path.write_text(json.dumps(override_data))

        result = load(str(base_path), str(override_path))

        expected = {"name": "app", "db": {"host": "localhost", "port": 5432}, "debug": True}
        assert result == expected


def test_load_with_env():
    """Test loading files with environment override."""
    base_data = {"name": "app", "db": {"host": "localhost"}}

    # Set environment variable
    os.environ["APP_DB__PORT"] = "3306"

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(base_data, f)
            temp_path = f.name

        result = load(temp_path, env_prefix="APP_")

        expected = {"name": "app", "db": {"host": "localhost", "port": 3306}}
        assert result == expected

        Path(temp_path).unlink()
    finally:
        os.environ.pop("APP_DB__PORT", None)
