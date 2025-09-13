from __future__ import annotations
from dev_qol_toolkit import data_utils

def test_case_conversions():
    assert data_utils.to_snake("SpamEggs") == "spam_eggs"
    assert data_utils.to_camel("spam_eggs") == "spamEggs"


def test_deep_merge_simple():
    """Test basic deep merge functionality."""
    dict1 = {"a": 1, "b": 2}
    dict2 = {"b": 3, "c": 4}
    result = data_utils.deep_merge(dict1, dict2)
    
    expected = {"a": 1, "b": 3, "c": 4}
    assert result == expected
    
    # Ensure original dictionaries are not modified
    assert dict1 == {"a": 1, "b": 2}
    assert dict2 == {"b": 3, "c": 4}


def test_deep_merge_nested():
    """Test deep merge with nested dictionaries."""
    dict1 = {
        "a": 1,
        "b": {
            "c": 2,
            "d": 3
        },
        "e": 5
    }
    dict2 = {
        "b": {
            "c": 4,
            "f": 6
        },
        "g": 7
    }
    
    result = data_utils.deep_merge(dict1, dict2)
    expected = {
        "a": 1,
        "b": {
            "c": 4,  # dict2 value takes precedence
            "d": 3,  # preserved from dict1
            "f": 6   # added from dict2
        },
        "e": 5,
        "g": 7
    }
    
    assert result == expected


def test_deep_merge_empty_dicts():
    """Test deep merge with empty dictionaries."""
    assert data_utils.deep_merge({}, {"a": 1}) == {"a": 1}
    assert data_utils.deep_merge({"a": 1}, {}) == {"a": 1}
    assert data_utils.deep_merge({}, {}) == {}


def test_deep_merge_non_dict_values():
    """Test deep merge when values are not dictionaries."""
    dict1 = {"a": {"b": 1}}
    dict2 = {"a": "string"}  # Non-dict value
    
    result = data_utils.deep_merge(dict1, dict2)
    assert result == {"a": "string"}  # dict2 value replaces dict1 value


def test_deep_diff_simple():
    """Test basic deep diff functionality."""
    dict1 = {"a": 1, "b": 2, "c": 3}
    dict2 = {"a": 1, "b": 4, "d": 5}
    
    result = data_utils.deep_diff(dict1, dict2)
    
    expected = {
        "added": {"d": 5},
        "removed": {"c": 3},
        "modified": {"b": {"old": 2, "new": 4}},
        "unchanged": {"a": 1}
    }
    
    assert result == expected


def test_deep_diff_nested():
    """Test deep diff with nested dictionaries."""
    dict1 = {
        "a": 1,
        "b": {
            "c": 2,
            "d": 3
        },
        "e": 5
    }
    dict2 = {
        "a": 1,
        "b": {
            "c": 4,  # modified
            "d": 3,  # unchanged
            "f": 6   # added
        },
        "g": 7  # added at root level
    }
    
    result = data_utils.deep_diff(dict1, dict2)
    
    expected = {
        "added": {"g": 7},
        "removed": {"e": 5},
        "modified": {
            "b": {
                "added": {"f": 6},
                "removed": {},
                "modified": {"c": {"old": 2, "new": 4}},
                "unchanged": {"d": 3}
            }
        },
        "unchanged": {"a": 1}
    }
    
    assert result == expected


def test_deep_diff_identical():
    """Test deep diff with identical dictionaries."""
    dict1 = {"a": 1, "b": {"c": 2}}
    dict2 = {"a": 1, "b": {"c": 2}}
    
    result = data_utils.deep_diff(dict1, dict2)
    
    expected = {
        "added": {},
        "removed": {},
        "modified": {},
        "unchanged": {"a": 1, "b": {"c": 2}}
    }
    
    assert result == expected


def test_deep_diff_empty_dicts():
    """Test deep diff with empty dictionaries."""
    result = data_utils.deep_diff({}, {})
    expected = {
        "added": {},
        "removed": {},
        "modified": {},
        "unchanged": {}
    }
    assert result == expected
    
    result = data_utils.deep_diff({"a": 1}, {})
    expected = {
        "added": {},
        "removed": {"a": 1},
        "modified": {},
        "unchanged": {}
    }
    assert result == expected


def test_deep_diff_type_changes():
    """Test deep diff when value types change."""
    dict1 = {"a": {"b": 1}}
    dict2 = {"a": "string"}
    
    result = data_utils.deep_diff(dict1, dict2)
    
    expected = {
        "added": {},
        "removed": {},
        "modified": {"a": {"old": {"b": 1}, "new": "string"}},
        "unchanged": {}
    }
    
    assert result == expected