"""Tests for validation utilities."""

import pytest
from dev_qol_toolkit.validation_utils import (
    validate_schema,
    validate_range,
    validate_length,
    validate_regex,
    validate_json_schema,
    Validator,
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


class TestValidateRegex:
    """Tests for validate_regex function."""
    
    def test_valid_regex_match(self):
        """Test validation with valid regex matches."""
        assert validate_regex("hello123", r"^[a-z]+\d+$") is True
        assert validate_regex("test@example.com", r"^[^@]+@[^@]+\.[^@]+$") is True
        assert validate_regex("ABC123", r"^[A-Z]+\d+$") is True
    
    def test_invalid_regex_match(self):
        """Test validation with invalid regex matches."""
        assert validate_regex("Hello123", r"^[a-z]+\d+$") is False
        assert validate_regex("invalid-email", r"^[^@]+@[^@]+\.[^@]+$") is False
        assert validate_regex("abc123", r"^[A-Z]+\d+$") is False
    
    def test_invalid_input_types(self):
        """Test validation with invalid input types."""
        assert validate_regex(123, r"^\d+$") is False
        assert validate_regex("123", 123) is False
        assert validate_regex(None, r".*") is False
        assert validate_regex("test", None) is False
    
    def test_invalid_regex_pattern(self):
        """Test validation with invalid regex pattern."""
        assert validate_regex("test", r"[") is False  # Invalid regex
        assert validate_regex("test", r"*") is False  # Invalid regex
    
    def test_empty_strings(self):
        """Test validation with empty strings."""
        assert validate_regex("", r"^$") is True
        assert validate_regex("", r".*") is True
        assert validate_regex("", r".+") is False


class TestValidateJsonSchema:
    """Tests for validate_json_schema function."""
    
    def test_valid_object_schema(self):
        """Test validation with valid object schema."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "age": {"type": "integer", "minimum": 0}
            },
            "required": ["name"]
        }
        
        data = {"name": "John", "age": 30}
        errors = validate_json_schema(data, schema)
        assert errors == []
    
    def test_missing_required_property(self):
        """Test validation with missing required property."""
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"]
        }
        
        data = {"age": 30}
        errors = validate_json_schema(data, schema)
        assert len(errors) == 1
        assert "Missing required property: name" in errors
    
    def test_wrong_type(self):
        """Test validation with wrong type."""
        schema = {
            "type": "object",
            "properties": {"age": {"type": "integer"}}
        }
        
        data = {"age": "30"}
        errors = validate_json_schema(data, schema)
        assert len(errors) == 1
        assert "Expected integer, got str" in errors[0]
    
    def test_string_constraints(self):
        """Test validation with string constraints."""
        schema = {
            "type": "object",
            "properties": {
                "short": {"type": "string", "minLength": 5},
                "long": {"type": "string", "maxLength": 3},
                "pattern": {"type": "string", "pattern": r"^[A-Z]+$"}
            }
        }
        
        data = {"short": "hi", "long": "toolong", "pattern": "abc"}
        errors = validate_json_schema(data, schema)
        assert len(errors) == 3
        assert any("String too short" in error for error in errors)
        assert any("String too long" in error for error in errors)
        assert any("does not match pattern" in error for error in errors)
    
    def test_number_constraints(self):
        """Test validation with number constraints."""
        schema = {
            "type": "object",
            "properties": {
                "small": {"type": "integer", "minimum": 10},
                "large": {"type": "number", "maximum": 5}
            }
        }
        
        data = {"small": 5, "large": 10}
        errors = validate_json_schema(data, schema)
        assert len(errors) == 2
        assert any("Value too small" in error for error in errors)
        assert any("Value too large" in error for error in errors)
    
    def test_array_validation(self):
        """Test validation with array schema."""
        schema = {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 2,
            "maxItems": 4
        }
        
        # Valid array
        errors = validate_json_schema(["a", "b"], schema)
        assert errors == []
        
        # Too few items
        errors = validate_json_schema(["a"], schema)
        assert len(errors) == 1
        assert "Array too short" in errors[0]
        
        # Too many items
        errors = validate_json_schema(["a", "b", "c", "d", "e"], schema)
        assert len(errors) == 1
        assert "Array too long" in errors[0]
        
        # Wrong item type
        errors = validate_json_schema(["a", 123], schema)
        assert len(errors) == 1
        assert "Expected string, got int" in errors[0]
    
    def test_nested_object_validation(self):
        """Test validation with nested objects."""
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"}
                    },
                    "required": ["name"]
                }
            }
        }
        
        # Valid nested object
        data = {"user": {"name": "John", "age": 30}}
        errors = validate_json_schema(data, schema)
        assert errors == []
        
        # Missing required nested property
        data = {"user": {"age": 30}}
        errors = validate_json_schema(data, schema)
        assert len(errors) == 1
        assert "Missing required property: name" in errors


class TestValidator:
    """Tests for Validator class."""
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        validator = Validator()
        assert validator.get_fields() == []
    
    def test_add_rule(self):
        """Test adding validation rules."""
        validator = Validator()
        validator.add_rule("email", lambda x: "@" in str(x), "Invalid email")
        
        assert "email" in validator.get_fields()
    
    def test_add_rule_invalid_params(self):
        """Test adding rules with invalid parameters."""
        validator = Validator()
        
        with pytest.raises(ValueError, match="Field name must be a string"):
            validator.add_rule(123, lambda x: True, "message")
        
        with pytest.raises(ValueError, match="Validator must be callable"):
            validator.add_rule("field", "not_callable", "message")
        
        with pytest.raises(ValueError, match="Message must be a string"):
            validator.add_rule("field", lambda x: True, 123)
    
    def test_validate_success(self):
        """Test successful validation."""
        validator = Validator()
        validator.add_rule("email", lambda x: "@" in str(x), "Invalid email")
        validator.add_rule("age", lambda x: isinstance(x, int) and x >= 0, "Invalid age")
        
        data = {"email": "test@example.com", "age": 25}
        errors = validator.validate(data)
        assert errors == []
    
    def test_validate_failures(self):
        """Test validation failures."""
        validator = Validator()
        validator.add_rule("email", lambda x: "@" in str(x), "Invalid email")
        validator.add_rule("age", lambda x: isinstance(x, int) and x >= 0, "Invalid age")
        
        data = {"email": "invalid", "age": -5}
        errors = validator.validate(data)
        assert len(errors) == 2
        assert "email: Invalid email" in errors
        assert "age: Invalid age" in errors
    
    def test_validate_missing_fields(self):
        """Test validation with missing fields."""
        validator = Validator()
        validator.add_rule("required_field", lambda x: x is not None, "Field is required")
        
        data = {}
        errors = validator.validate(data)
        assert len(errors) == 1
        assert "required_field: Field is required" in errors
    
    def test_validate_exception_handling(self):
        """Test validation with exceptions in validator functions."""
        validator = Validator()
        validator.add_rule("field", lambda x: x.upper(), "Should not fail")  # Will raise AttributeError for non-strings
        
        data = {"field": 123}
        errors = validator.validate(data)
        assert len(errors) == 1
        assert "field: Validation error" in errors[0]
    
    def test_validate_invalid_data_type(self):
        """Test validation with invalid data type."""
        validator = Validator()
        validator.add_rule("field", lambda x: True, "message")
        
        errors = validator.validate("not_a_dict")
        assert len(errors) == 1
        assert "Data must be a dictionary" in errors
    
    def test_multiple_rules_same_field(self):
        """Test multiple rules for the same field."""
        validator = Validator()
        validator.add_rule("password", lambda x: len(str(x)) >= 8, "Password too short")
        validator.add_rule("password", lambda x: any(c.isupper() for c in str(x)), "Password needs uppercase")
        
        data = {"password": "short"}
        errors = validator.validate(data)
        assert len(errors) == 2
        assert "password: Password too short" in errors
        assert "password: Password needs uppercase" in errors
    
    def test_clear_rules(self):
        """Test clearing all rules."""
        validator = Validator()
        validator.add_rule("field1", lambda x: True, "message1")
        validator.add_rule("field2", lambda x: True, "message2")
        
        assert len(validator.get_fields()) == 2
        
        validator.clear_rules()
        assert validator.get_fields() == []
    
    def test_remove_field_rules(self):
        """Test removing rules for specific field."""
        validator = Validator()
        validator.add_rule("field1", lambda x: True, "message1")
        validator.add_rule("field2", lambda x: True, "message2")
        
        validator.remove_field_rules("field1")
        assert validator.get_fields() == ["field2"]
        
        # Removing non-existent field should not raise error
        validator.remove_field_rules("nonexistent")
        assert validator.get_fields() == ["field2"]