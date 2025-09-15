"""Tests for json_utils module."""

from __future__ import annotations
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from hypothesis import given, strategies as st

from dev_qol_toolkit import json_utils


class TestLoadJson:
    """Test load_json function."""

    def test_load_valid_json(self, tmp_path: Path):
        """Test loading valid JSON file."""
        test_data = {"name": "test", "value": 42, "items": [1, 2, 3]}
        json_file = tmp_path / "test.json"
        
        with json_file.open("w") as f:
            json.dump(test_data, f)
        
        result = json_utils.load_json(json_file)
        assert result == test_data

    def test_load_json_string_path(self, tmp_path: Path):
        """Test loading JSON with string path."""
        test_data = {"key": "value"}
        json_file = tmp_path / "test.json"
        
        with json_file.open("w") as f:
            json.dump(test_data, f)
        
        result = json_utils.load_json(str(json_file))
        assert result == test_data

    def test_load_nonexistent_file(self, tmp_path: Path):
        """Test loading nonexistent file raises FileNotFoundError."""
        nonexistent = tmp_path / "nonexistent.json"
        
        with pytest.raises(FileNotFoundError):
            json_utils.load_json(nonexistent)

    def test_load_invalid_json(self, tmp_path: Path):
        """Test loading invalid JSON raises JSONDecodeError."""
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text("{ invalid json }")
        
        with pytest.raises(json.JSONDecodeError):
            json_utils.load_json(invalid_json)

    def test_load_empty_file(self, tmp_path: Path):
        """Test loading empty file raises JSONDecodeError."""
        empty_file = tmp_path / "empty.json"
        empty_file.write_text("")
        
        with pytest.raises(json.JSONDecodeError):
            json_utils.load_json(empty_file)


class TestSaveJson:
    """Test save_json function."""

    def test_save_json_pretty(self, tmp_path: Path):
        """Test saving JSON with pretty formatting."""
        test_data = {"name": "test", "value": 42, "items": [3, 1, 2]}
        json_file = tmp_path / "output.json"
        
        json_utils.save_json(test_data, json_file, pretty=True)
        
        assert json_file.exists()
        content = json_file.read_text()
        
        # Check formatting
        assert "  " in content  # Indentation
        assert content.endswith("\n")  # Trailing newline
        
        # Verify data integrity
        loaded = json.loads(content)
        assert loaded == test_data

    def test_save_json_compact(self, tmp_path: Path):
        """Test saving JSON with compact formatting."""
        test_data = {"name": "test", "value": 42}
        json_file = tmp_path / "compact.json"
        
        json_utils.save_json(test_data, json_file, pretty=False)
        
        content = json_file.read_text()
        
        # Check compact formatting
        assert "  " not in content  # No indentation
        assert "\n" not in content  # No newlines
        
        # Verify data integrity
        loaded = json.loads(content)
        assert loaded == test_data

    def test_save_json_creates_parent_dirs(self, tmp_path: Path):
        """Test that save_json creates parent directories."""
        test_data = {"test": True}
        nested_file = tmp_path / "nested" / "dirs" / "test.json"
        
        json_utils.save_json(test_data, nested_file)
        
        assert nested_file.exists()
        assert json_utils.load_json(nested_file) == test_data

    def test_save_json_string_path(self, tmp_path: Path):
        """Test saving JSON with string path."""
        test_data = {"key": "value"}
        json_file_str = str(tmp_path / "string_path.json")
        
        json_utils.save_json(test_data, json_file_str)
        
        assert Path(json_file_str).exists()
        assert json_utils.load_json(json_file_str) == test_data

    def test_save_json_unicode(self, tmp_path: Path):
        """Test saving JSON with unicode characters."""
        test_data = {"message": "Hello 世界", "emoji": "🚀"}
        json_file = tmp_path / "unicode.json"
        
        json_utils.save_json(test_data, json_file)
        
        loaded = json_utils.load_json(json_file)
        assert loaded == test_data

    @given(data=st.recursive(
        st.one_of(
            st.none(),
            st.booleans(),
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.text()
        ),
        lambda children: st.one_of(
            st.lists(children, max_size=3),
            st.dictionaries(st.text(), children, max_size=3)
        ),
        max_leaves=10
    ))
    def test_save_load_roundtrip(self, tmp_path: Path, data):
        """Test save/load roundtrip with various data structures."""
        json_file = tmp_path / "roundtrip.json"
        
        json_utils.save_json(data, json_file)
        loaded = json_utils.load_json(json_file)
        
        assert loaded == data


class TestPrettyJson:
    """Test pretty_json function."""

    def test_pretty_json_basic(self):
        """Test basic pretty JSON formatting."""
        data = {"name": "test", "items": [1, 2, 3]}
        
        result = json_utils.pretty_json(data)
        
        assert "  " in result  # Indentation
        assert "name" in result
        assert "items" in result
        
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed == data

    def test_pretty_json_no_color(self):
        """Test pretty JSON without color."""
        data = {"key": "value"}
        
        result = json_utils.pretty_json(data, color=False)
        
        # Should be plain JSON
        assert result == json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)

    def test_pretty_json_with_color_no_pygments(self):
        """Test pretty JSON with color when pygments is not available."""
        data = {"key": "value"}
        
        with patch('dev_qol_toolkit.json_utils.highlight', side_effect=ImportError):
            result = json_utils.pretty_json(data, color=True)
            
            # Should fall back to plain JSON
            expected = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
            assert result == expected

    def test_pretty_json_complex_data(self):
        """Test pretty JSON with complex nested data."""
        data = {
            "users": [
                {"id": 1, "name": "Alice", "active": True},
                {"id": 2, "name": "Bob", "active": False}
            ],
            "metadata": {
                "version": "1.0",
                "created": "2024-01-01"
            }
        }
        
        result = json_utils.pretty_json(data)
        
        # Verify structure is preserved
        parsed = json.loads(result)
        assert parsed == data


class TestDetectJsonl:
    """Test detect_jsonl function."""

    def test_detect_valid_jsonl(self, tmp_path: Path):
        """Test detecting valid JSON Lines file."""
        jsonl_file = tmp_path / "test.jsonl"
        lines = [
            '{"id": 1, "name": "Alice"}',
            '{"id": 2, "name": "Bob"}',
            '{"id": 3, "name": "Charlie"}'
        ]
        jsonl_file.write_text("\n".join(lines))
        
        assert json_utils.detect_jsonl(jsonl_file) is True

    def test_detect_invalid_jsonl(self, tmp_path: Path):
        """Test detecting invalid JSON Lines file."""
        invalid_file = tmp_path / "invalid.jsonl"
        lines = [
            '{"id": 1, "name": "Alice"}',
            'invalid json line',
            '{"id": 3, "name": "Charlie"}'
        ]
        invalid_file.write_text("\n".join(lines))
        
        assert json_utils.detect_jsonl(invalid_file) is False

    def test_detect_jsonl_with_empty_lines(self, tmp_path: Path):
        """Test detecting JSONL with empty lines (should still be valid)."""
        jsonl_file = tmp_path / "with_empty.jsonl"
        lines = [
            '{"id": 1}',
            '',
            '{"id": 2}',
            '   ',  # Whitespace only
            '{"id": 3}'
        ]
        jsonl_file.write_text("\n".join(lines))
        
        assert json_utils.detect_jsonl(jsonl_file) is True

    def test_detect_jsonl_sample_limit(self, tmp_path: Path):
        """Test JSONL detection with sample limit."""
        jsonl_file = tmp_path / "large.jsonl"
        lines = []
        # First 5 lines are valid JSON
        for i in range(5):
            lines.append(f'{{"id": {i}}}')
        # Add invalid line after sample limit
        lines.append('invalid json')
        
        jsonl_file.write_text("\n".join(lines))
        
        # Should detect as valid because it only samples first few lines
        assert json_utils.detect_jsonl(jsonl_file, sample=5) is True

    def test_detect_empty_file(self, tmp_path: Path):
        """Test detecting empty file."""
        empty_file = tmp_path / "empty.jsonl"
        empty_file.write_text("")
        
        assert json_utils.detect_jsonl(empty_file) is True  # Empty file is technically valid JSONL


class TestFlattenJson:
    """Test flatten_json function."""

    def test_flatten_simple_dict(self):
        """Test flattening simple dictionary."""
        data = {"a": 1, "b": 2}
        
        result = json_utils.flatten_json(data)
        
        assert result == {"a": 1, "b": 2}

    def test_flatten_nested_dict(self):
        """Test flattening nested dictionary."""
        data = {"a": {"b": {"c": 1}}}
        
        result = json_utils.flatten_json(data)
        
        assert result == {"a.b.c": 1}

    def test_flatten_with_list(self):
        """Test flattening dictionary with lists."""
        data = {"items": [1, 2, {"nested": 3}]}
        
        result = json_utils.flatten_json(data)
        
        assert result == {
            "items.0": 1,
            "items.1": 2,
            "items.2.nested": 3
        }

    def test_flatten_complex_structure(self):
        """Test flattening complex nested structure."""
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ],
            "metadata": {
                "version": "1.0",
                "settings": {"debug": True}
            }
        }
        
        result = json_utils.flatten_json(data)
        
        expected = {
            "users.0.name": "Alice",
            "users.0.age": 30,
            "users.1.name": "Bob",
            "users.1.age": 25,
            "metadata.version": "1.0",
            "metadata.settings.debug": True
        }
        assert result == expected

    def test_flatten_custom_separator(self):
        """Test flattening with custom separator."""
        data = {"a": {"b": 1}}
        
        result = json_utils.flatten_json(data, sep="/")
        
        assert result == {"a/b": 1}

    def test_flatten_empty_dict(self):
        """Test flattening empty dictionary."""
        result = json_utils.flatten_json({})
        assert result == {}

    def test_flatten_and_unflatten_roundtrip(self):
        """Test flatten/unflatten roundtrip."""
        src = {"a": {"b": [1, {"c": 2}]}}
        flat = json_utils.flatten_json(src)
        assert flat == {"a.b.0": 1, "a.b.1.c": 2}
        back = json_utils.unflatten_json(flat)
        assert back == src


class TestUnflattenJson:
    """Test unflatten_json function."""

    def test_unflatten_simple_dict(self):
        """Test unflattening simple flat dictionary."""
        flat = {"a": 1, "b": 2}
        
        result = json_utils.unflatten_json(flat)
        
        assert result == {"a": 1, "b": 2}

    def test_unflatten_nested_dict(self):
        """Test unflattening nested structure."""
        flat = {"a.b.c": 1, "a.b.d": 2, "a.e": 3}
        
        result = json_utils.unflatten_json(flat)
        
        expected = {
            "a": {
                "b": {"c": 1, "d": 2},
                "e": 3
            }
        }
        assert result == expected

    def test_unflatten_with_lists(self):
        """Test unflattening structure with lists."""
        flat = {
            "items.0": "first",
            "items.1": "second",
            "items.2.nested": "value"
        }
        
        result = json_utils.unflatten_json(flat)
        
        expected = {
            "items": ["first", "second", {"nested": "value"}]
        }
        assert result == expected

    def test_unflatten_custom_separator(self):
        """Test unflattening with custom separator."""
        flat = {"a/b/c": 1}
        
        result = json_utils.unflatten_json(flat, sep="/")
        
        assert result == {"a": {"b": {"c": 1}}}

    def test_unflatten_sparse_list(self):
        """Test unflattening sparse list (with gaps)."""
        flat = {"items.0": "first", "items.3": "fourth"}
        
        result = json_utils.unflatten_json(flat)
        
        expected = {"items": ["first", None, None, "fourth"]}
        assert result == expected

    def test_unflatten_empty_dict(self):
        """Test unflattening empty dictionary."""
        result = json_utils.unflatten_json({})
        assert result == {}

    def test_unflatten_type_error_dict_on_list(self):
        """Test unflatten raises TypeError when trying to set dict key on list path."""
        flat = {"items.0": 1, "items.key": "value"}  # Mixed list/dict access
        
        with pytest.raises(TypeError, match="Cannot set dict key on a list path"):
            json_utils.unflatten_json(flat)

    def test_unflatten_type_error_list_on_dict(self):
        """Test unflatten raises TypeError when trying to set list index on dict path."""
        flat = {"data.key": "value", "data.0": "item"}  # Mixed dict/list access
        
        with pytest.raises(TypeError, match="Cannot set list index on a dict path"):
            json_utils.unflatten_json(flat)

    @given(
        data=st.recursive(
            st.one_of(
                st.none(),
                st.booleans(),
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                st.text()
            ),
            lambda children: st.one_of(
                st.lists(children, max_size=3),
                st.dictionaries(st.text().filter(lambda x: "." not in x), children, max_size=3)
            ),
            max_leaves=8
        )
    )
    def test_flatten_unflatten_roundtrip_property(self, data):
        """Property-based test for flatten/unflatten roundtrip."""
        if isinstance(data, dict):
            flattened = json_utils.flatten_json(data)
            unflattened = json_utils.unflatten_json(flattened)
            assert unflattened == data


class TestJsonUtilsIntegration:
    """Integration tests for json_utils module."""

    def test_complete_workflow(self, tmp_path: Path):
        """Test complete JSON workflow."""
        # Original data
        data = {
            "config": {
                "database": {"host": "localhost", "port": 5432},
                "features": ["auth", "logging", "metrics"]
            },
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"}
            ]
        }
        
        # Save to file
        json_file = tmp_path / "config.json"
        json_utils.save_json(data, json_file)
        
        # Load back
        loaded = json_utils.load_json(json_file)
        assert loaded == data
        
        # Pretty print
        pretty = json_utils.pretty_json(loaded)
        assert json.loads(pretty) == data
        
        # Flatten and unflatten
        flattened = json_utils.flatten_json(loaded)
        unflattened = json_utils.unflatten_json(flattened)
        assert unflattened == data
        
        # Create JSONL version
        jsonl_file = tmp_path / "users.jsonl"
        jsonl_lines = [json.dumps(user) for user in data["users"]]
        jsonl_file.write_text("\n".join(jsonl_lines))
        
        # Detect JSONL
        assert json_utils.detect_jsonl(jsonl_file) is True