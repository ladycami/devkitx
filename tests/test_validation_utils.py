"""Tests for validation utilities."""

import pytest
from dev_qol_toolkit.validation_utils import (
    validate_schema,
    validate_range,
    validate_length,
)


class TestValidateSchema:
    """Tests for validate_schema function."""
    
    def test_valid_schema(self):
        """Test validation with valid data."""
        schema = {"name": str, "age": int, "active": bool}
        data = {"name": "John", "age": 30, "active": True}
        
        errors = validate_schema(data, schema)
        assert errors == []
    
    def test_missing_field(self):
        """Test validation with missing required field."""
        schema = {"name": str, "age": int}
        data = {"name": "John"}
        
        errors = validate_schema(data, schema)
        assert len(errors) == 1
        assert 'Missing required field "age"' in errors
    
    def test_wrong_type(self):
        """Test validation with wrong type."""
        schema = {"name": str, "age": int}
        data = {"name": "John", "age": "30"}
        
        errors = validate_schema(data, schema)
        assert len(errors) == 1
        assert 'Field "age": expected int, got str' in errors
    
    def test_multiple_errors(self):
        """Test validation with multiple errors."""
        schema = {"name": str, "age": int, "active": bool}
        data = {"name": 123, "age": "30"}
        
        errors = validate_schema(data, schema)
        assert len(errors) == 3
        assert any('Field "name": expected str, got int' in error for error in errors)
        assert any('Field "age": expected int, got str' in error for error in errors)
        assert any('Missing required field "active"' in error for error in errors)
    
    def test_empty_schema(self):
        """Test validation with empty schema."""
        schema = {}
        data = {"name": "John"}
        
        errors = validate_schema(data, schema)
        assert errors == []
    
    def test_empty_data(self):
        """Test validation with empty data."""
        schema = {"name": str}
        data = {}
        
        errors = validate_schema(data, schema)
        assert len(errors) == 1
        assert 'Missing required field "name"' in errors


class TestValidateRange:
    """Tests for validate_range function."""
    
    def test_valid_range_int(self):
        """Test validation with valid integer in range."""
        assert validate_range(5, 1, 10) is True
        assert validate_range(1, 1, 10) is True  # Min boundary
        assert validate_range(10, 1, 10) is True  # Max boundary
    
    def test_valid_range_float(self):
        """Test validation with valid float in range."""
        assert validate_range(5.5, 1.0, 10.0) is True
        assert validate_range(1.0, 1.0, 10.0) is True
        assert validate_range(10.0, 1.0, 10.0) is True
    
    def test_invalid_range_below_min(self):
        """Test validation with value below minimum."""
        assert validate_range(0, 1, 10) is False
        assert validate_range(-5, 1, 10) is False
    
    def test_invalid_range_above_max(self):
        """Test validation with value above maximum."""
        assert validate_range(11, 1, 10) is False
        assert validate_range(100, 1, 10) is False
    
    def test_invalid_value_type(self):
        """Test validation with invalid value type."""
        assert validate_range("5", 1, 10) is False
        assert validate_range(None, 1, 10) is False
        assert validate_range([5], 1, 10) is False
    
    def test_invalid_range_params(self):
        """Test validation with invalid range parameters."""
        assert validate_range(5, "1", 10) is False
        assert validate_range(5, 1, "10") is False
        assert validate_range(5, None, 10) is False
    
    def test_invalid_range_order(self):
        """Test validation with min > max."""
        assert validate_range(5, 10, 1) is False
    
    def test_mixed_int_float(self):
        """Test validation with mixed int and float types."""
        assert validate_range(5, 1.0, 10) is True
        assert validate_range(5.5, 1, 10.0) is True


class TestValidateLength:
    """Tests for validate_length function."""
    
    def test_valid_length(self):
        """Test validation with valid length."""
        assert validate_length("hello", 3, 10) is True
        assert validate_length("hi", 2, 10) is True  # Min boundary
        assert validate_length("1234567890", 3, 10) is True  # Max boundary
    
    def test_invalid_length_too_short(self):
        """Test validation with text too short."""
        assert validate_length("hi", 3, 10) is False
        assert validate_length("", 1, 10) is False
    
    def test_invalid_length_too_long(self):
        """Test validation with text too long."""
        assert validate_length("hello world!", 3, 10) is False
        assert validate_length("this is way too long", 3, 10) is False
    
    def test_no_max_length(self):
        """Test validation with no maximum length limit."""
        assert validate_length("hello", 3) is True
        assert validate_length("this is a very long string", 3) is True
        assert validate_length("hi", 3) is False  # Still below min
    
    def test_zero_min_length(self):
        """Test validation with zero minimum length."""
        assert validate_length("", 0, 10) is True
        assert validate_length("hello", 0, 10) is True
    
    def test_invalid_text_type(self):
        """Test validation with non-string input."""
        assert validate_length(123, 3, 10) is False
        assert validate_length(None, 3, 10) is False
        assert validate_length(["hello"], 3, 10) is False
    
    def test_invalid_length_params(self):
        """Test validation with invalid length parameters."""
        assert validate_length("hello", -1, 10) is False
        assert validate_length("hello", "3", 10) is False
        assert validate_length("hello", 3, -1) is False
        assert validate_length("hello", 3, "10") is False
    
    def test_invalid_length_order(self):
        """Test validation with min_len > max_len."""
        assert validate_length("hello", 10, 3) is False
    
    def test_equal_min_max_length(self):
        """Test validation with equal min and max length."""
        assert validate_length("hello", 5, 5) is True
        assert validate_length("hi", 5, 5) is False
        assert validate_length("toolong", 5, 5) is False