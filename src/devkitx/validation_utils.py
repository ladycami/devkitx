"""Input validation utilities for DevKitX.

This module provides utilities for data validation, schema checking,
and input sanitization.
"""

from typing import Any, Callable

__all__ = [
    "validate_schema",
    "validate_range",
    "validate_length",
    "validate_regex",
    "validate_json_schema",
    "Validator",
]


def validate_schema(data: dict[str, Any], schema: dict[str, type]) -> list[str]:
    """Validate data against type schema.

    Args:
        data: Data to validate
        schema: Schema defining expected types

    Returns:
        List of validation error messages

    Example:
        >>> schema = {"name": str, "age": int, "active": bool}
        >>> data = {"name": "John", "age": 30, "active": True}
        >>> validate_schema(data, schema)
        []
        >>> data = {"name": "John", "age": "30", "active": True}
        >>> validate_schema(data, schema)
        ['Field "age": expected int, got str']
    """
    errors = []

    # Check for missing required fields
    for field, expected_type in schema.items():
        if field not in data:
            errors.append(f'Missing required field "{field}"')
            continue

        # Check type
        value = data[field]
        if not isinstance(value, expected_type):
            actual_type = type(value).__name__
            expected_type_name = expected_type.__name__
            errors.append(f'Field "{field}": expected {expected_type_name}, got {actual_type}')

    return errors


def validate_range(value: int | float, min_val: int | float, max_val: int | float) -> bool:
    """Validate that value is within specified range.

    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        True if value is in range, False otherwise

    Example:
        >>> validate_range(5, 1, 10)
        True
        >>> validate_range(15, 1, 10)
        False
        >>> validate_range(0, 1, 10)
        False
    """
    if not isinstance(value, (int, float)):
        return False

    if not isinstance(min_val, (int, float)) or not isinstance(max_val, (int, float)):
        return False

    if min_val > max_val:
        return False

    return min_val <= value <= max_val


def validate_length(text: str, min_len: int = 0, max_len: int | None = None) -> bool:
    """Validate text length.

    Args:
        text: Text to validate
        min_len: Minimum length
        max_len: Maximum length (None for no limit)

    Returns:
        True if length is valid, False otherwise

    Example:
        >>> validate_length("hello", 3, 10)
        True
        >>> validate_length("hi", 3, 10)
        False
        >>> validate_length("hello world!", 3, 10)
        False
        >>> validate_length("hello", 3)  # No max limit
        True
    """
    if not isinstance(text, str):
        return False

    if not isinstance(min_len, int) or min_len < 0:
        return False

    if max_len is not None and (not isinstance(max_len, int) or max_len < 0):
        return False

    if max_len is not None and min_len > max_len:
        return False

    text_len = len(text)

    if text_len < min_len:
        return False

    if max_len is not None and text_len > max_len:
        return False

    return True


def validate_regex(text: str, pattern: str) -> bool:
    """Validate text against regex pattern.

    Args:
        text: Text to validate
        pattern: Regex pattern

    Returns:
        True if text matches pattern, False otherwise

    Example:
        >>> validate_regex("hello123", r"^[a-z]+\\d+$")
        True
        >>> validate_regex("Hello123", r"^[a-z]+\\d+$")
        False
        >>> validate_regex("test@example.com", r"^[^@]+@[^@]+\\.[^@]+$")
        True
    """
    import re

    if not isinstance(text, str) or not isinstance(pattern, str):
        return False

    try:
        return bool(re.match(pattern, text))
    except re.error:
        # Invalid regex pattern
        return False


def validate_json_schema(data: Any, schema: dict[str, Any]) -> list[str]:
    """Validate data against JSON schema.

    This is a basic JSON schema validator that supports common validation rules.

    Args:
        data: Data to validate
        schema: JSON schema with validation rules

    Returns:
        List of validation error messages

    Example:
        >>> schema = {
        ...     "type": "object",
        ...     "properties": {
        ...         "name": {"type": "string", "minLength": 1},
        ...         "age": {"type": "integer", "minimum": 0}
        ...     },
        ...     "required": ["name"]
        ... }
        >>> validate_json_schema({"name": "John", "age": 30}, schema)
        []
        >>> validate_json_schema({"age": 30}, schema)
        ['Missing required property: name']
    """
    errors = []

    def _validate_type(value: Any, expected_type: str, path: str = "") -> None:
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None),
        }

        if expected_type not in type_map:
            errors.append(f"Unknown type '{expected_type}' at {path or 'root'}")
            return

        expected_python_type = type_map[expected_type]
        if not isinstance(value, expected_python_type):
            actual_type = type(value).__name__
            errors.append(f"Expected {expected_type}, got {actual_type} at {path or 'root'}")

    def _validate_object(obj: Any, obj_schema: dict[str, Any], path: str = "") -> None:
        if not isinstance(obj, dict):
            return

        # Check required properties
        required = obj_schema.get("required", [])
        for prop in required:
            if prop not in obj:
                errors.append(f"Missing required property: {prop}")

        # Validate properties
        properties = obj_schema.get("properties", {})
        for prop, prop_schema in properties.items():
            if prop in obj:
                prop_path = f"{path}.{prop}" if path else prop
                _validate_value(obj[prop], prop_schema, prop_path)

    def _validate_array(arr: Any, arr_schema: dict[str, Any], path: str = "") -> None:
        if not isinstance(arr, list):
            return

        # Check array length constraints
        if "minItems" in arr_schema and len(arr) < arr_schema["minItems"]:
            errors.append(
                f"Array too short at {path or 'root'}: minimum {arr_schema['minItems']} items"
            )

        if "maxItems" in arr_schema and len(arr) > arr_schema["maxItems"]:
            errors.append(
                f"Array too long at {path or 'root'}: maximum {arr_schema['maxItems']} items"
            )

        # Validate items
        if "items" in arr_schema:
            item_schema = arr_schema["items"]
            for i, item in enumerate(arr):
                item_path = f"{path}[{i}]" if path else f"[{i}]"
                _validate_value(item, item_schema, item_path)

    def _validate_string(value: Any, str_schema: dict[str, Any], path: str = "") -> None:
        if not isinstance(value, str):
            return

        if "minLength" in str_schema and len(value) < str_schema["minLength"]:
            errors.append(
                f"String too short at {path or 'root'}: minimum {str_schema['minLength']} characters"
            )

        if "maxLength" in str_schema and len(value) > str_schema["maxLength"]:
            errors.append(
                f"String too long at {path or 'root'}: maximum {str_schema['maxLength']} characters"
            )

        if "pattern" in str_schema:
            import re

            try:
                if not re.match(str_schema["pattern"], value):
                    errors.append(f"String does not match pattern at {path or 'root'}")
            except re.error:
                errors.append(f"Invalid regex pattern in schema at {path or 'root'}")

    def _validate_number(value: Any, num_schema: dict[str, Any], path: str = "") -> None:
        if not isinstance(value, (int, float)):
            return

        if "minimum" in num_schema and value < num_schema["minimum"]:
            errors.append(f"Value too small at {path or 'root'}: minimum {num_schema['minimum']}")

        if "maximum" in num_schema and value > num_schema["maximum"]:
            errors.append(f"Value too large at {path or 'root'}: maximum {num_schema['maximum']}")

    def _validate_value(value: Any, value_schema: dict[str, Any], path: str = "") -> None:
        # Validate type
        if "type" in value_schema:
            _validate_type(value, value_schema["type"], path)

        # Type-specific validations
        if isinstance(value, dict) and value_schema.get("type") == "object":
            _validate_object(value, value_schema, path)
        elif isinstance(value, list) and value_schema.get("type") == "array":
            _validate_array(value, value_schema, path)
        elif isinstance(value, str) and value_schema.get("type") == "string":
            _validate_string(value, value_schema, path)
        elif isinstance(value, (int, float)) and value_schema.get("type") in ("integer", "number"):
            _validate_number(value, value_schema, path)

    # Start validation
    _validate_value(data, schema)

    return errors


class Validator:
    """Rule-based validator for complex validation scenarios.

    Example:
        >>> validator = Validator()
        >>> validator.add_rule("email", lambda x: "@" in str(x), "Invalid email format")
        >>> validator.add_rule("age", lambda x: isinstance(x, int) and x >= 0, "Age must be a non-negative integer")
        >>> errors = validator.validate({"email": "test@example.com", "age": 25})
        >>> len(errors)
        0
        >>> errors = validator.validate({"email": "invalid", "age": -5})
        >>> len(errors)
        2
    """

    def __init__(self) -> None:
        """Initialize validator."""
        self._rules: dict[str, list[tuple[Callable[[Any], bool], str]]] = {}

    def add_rule(self, field: str, validator: Callable[[Any], bool], message: str) -> None:
        """Add validation rule.

        Args:
            field: Field name to validate
            validator: Validation function that returns True if valid
            message: Error message if validation fails
        """
        if not isinstance(field, str):
            raise ValueError("Field name must be a string")

        if not callable(validator):
            raise ValueError("Validator must be callable")

        if not isinstance(message, str):
            raise ValueError("Message must be a string")

        if field not in self._rules:
            self._rules[field] = []

        self._rules[field].append((validator, message))

    def validate(self, data: dict[str, Any]) -> list[str]:
        """Validate data against all rules.

        Args:
            data: Data to validate

        Returns:
            List of validation error messages
        """
        if not isinstance(data, dict):
            return ["Data must be a dictionary"]

        errors = []

        for field, rules in self._rules.items():
            value = data.get(field)

            for validator_func, error_message in rules:
                try:
                    if not validator_func(value):
                        errors.append(f"{field}: {error_message}")
                except Exception as e:
                    errors.append(f"{field}: Validation error - {str(e)}")

        return errors

    def clear_rules(self) -> None:
        """Clear all validation rules."""
        self._rules.clear()

    def remove_field_rules(self, field: str) -> None:
        """Remove all rules for a specific field.

        Args:
            field: Field name to remove rules for
        """
        if field in self._rules:
            del self._rules[field]

    def get_fields(self) -> list[str]:
        """Get list of fields that have validation rules.

        Returns:
            List of field names
        """
        return list(self._rules.keys())
