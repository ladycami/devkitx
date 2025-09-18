"""Tests for JSON flattening functionality."""

import pytest
from devkitx.json_utils.flatten import flatten_json, unflatten_json


class TestFlattenJson:
    """Test cases for flatten_json function."""
    
    def test_flatten_basic_dict(self):
        """Test flattening a basic nested dictionary."""
        nested = {"user": {"name": "John", "age": 30}}
        result = flatten_json(nested)
        expected = {"user.name": "John", "user.age": 30}
        assert result == expected
    
    def test_flatten_with_list(self):
        """Test flattening dictionary containing lists."""
        nested = {"items": [1, 2, 3], "meta": {"count": 3}}
        result = flatten_json(nested)
        expected = {
            "items.0": 1,
            "items.1": 2, 
            "items.2": 3,
            "meta.count": 3
        }
        assert result == expected
    
    def test_flatten_deeply_nested(self):
        """Test flattening deeply nested structures."""
        nested = {
            "user": {
                "profile": {
                    "personal": {"name": "John", "age": 30},
                    "settings": {"theme": "dark"}
                }
            }
        }
        result = flatten_json(nested)
        expected = {
            "user.profile.personal.name": "John",
            "user.profile.personal.age": 30,
            "user.profile.settings.theme": "dark"
        }
        assert result == expected
    
    def test_flatten_custom_separator(self):
        """Test flattening with custom separator."""
        nested = {"user": {"name": "John", "age": 30}}
        result = flatten_json(nested, sep="_")
        expected = {"user_name": "John", "user_age": 30}
        assert result == expected
    
    def test_flatten_primitive_value(self):
        """Test flattening primitive values."""
        assert flatten_json(42) == {"": 42}
        assert flatten_json("hello") == {"": "hello"}
        assert flatten_json(None) == {"": None}
        assert flatten_json(True) == {"": True}
    
    def test_flatten_empty_structures(self):
        """Test flattening empty structures."""
        assert flatten_json({}) == {}
        assert flatten_json([]) == {}
    
    def test_flatten_mixed_types(self):
        """Test flattening with mixed data types."""
        nested = {
            "string": "value",
            "number": 42,
            "boolean": True,
            "null": None,
            "list": [1, "two", {"three": 3}],
            "dict": {"nested": "value"}
        }
        result = flatten_json(nested)
        expected = {
            "string": "value",
            "number": 42,
            "boolean": True,
            "null": None,
            "list.0": 1,
            "list.1": "two",
            "list.2.three": 3,
            "dict.nested": "value"
        }
        assert result == expected


class TestUnflattenJson:
    """Test cases for unflatten_json function."""
    
    def test_unflatten_basic_dict(self):
        """Test unflattening basic dot-notation keys."""
        flat = {"user.name": "John", "user.age": 30}
        result = unflatten_json(flat)
        expected = {"user": {"name": "John", "age": 30}}
        assert result == expected
    
    def test_unflatten_with_lists(self):
        """Test unflattening keys that represent list indices."""
        flat = {"items.0": 1, "items.1": 2, "items.2": 3}
        result = unflatten_json(flat)
        expected = {"items": [1, 2, 3]}
        assert result == expected
    
    def test_unflatten_mixed_structures(self):
        """Test unflattening mixed dict and list structures."""
        flat = {
            "user.name": "John",
            "user.items.0": "first",
            "user.items.1": "second",
            "meta.count": 2
        }
        result = unflatten_json(flat)
        expected = {
            "user": {
                "name": "John",
                "items": ["first", "second"]
            },
            "meta": {"count": 2}
        }
        assert result == expected
    
    def test_unflatten_custom_separator(self):
        """Test unflattening with custom separator."""
        flat = {"user_name": "John", "user_age": 30}
        result = unflatten_json(flat, sep="_")
        expected = {"user": {"name": "John", "age": 30}}
        assert result == expected
    
    def test_unflatten_conflicting_paths_raises_error(self):
        """Test that conflicting path types raise TypeError."""
        # Try to set dict key on list path
        flat = {"items.0": 1, "items.name": "conflict"}
        with pytest.raises(TypeError, match="Cannot set dict key on a list path"):
            unflatten_json(flat)
    
    def test_roundtrip_consistency(self):
        """Test that flatten -> unflatten produces consistent results."""
        original = {
            "user": {
                "name": "John",
                "details": {"age": 30, "city": "NYC"},
                "items": [1, 2, {"nested": "value"}]
            },
            "meta": {"version": "1.0"}
        }
        
        flattened = flatten_json(original)
        unflattened = unflatten_json(flattened)
        
        assert unflattened == original