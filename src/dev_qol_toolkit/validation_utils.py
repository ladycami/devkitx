"""Input validation utilities for the dev-qol-toolkit.

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
    """
    # Placeholder implementation
    raise NotImplementedError("Function will be implemented in task 11.2")


def validate_json_schema(data: Any, schema: dict[str, Any]) -> list[str]:
    """Validate data against JSON schema.
    
    Args:
        data: Data to validate
        schema: JSON schema
        
    Returns:
        List of validation error messages
    """
    # Placeholder implementation
    raise NotImplementedError("Function will be implemented in task 11.2")


class Validator:
    """Rule-based validator for complex validation scenarios."""
    
    def __init__(self) -> None:
        """Initialize validator."""
        # Placeholder implementation
        raise NotImplementedError("Class will be implemented in task 11.2")
    
    def add_rule(self, field: str, validator: Callable[[Any], bool], message: str) -> None:
        """Add validation rule.
        
        Args:
            field: Field name to validate
            validator: Validation function
            message: Error message if validation fails
        """
        # Placeholder implementation
        raise NotImplementedError("Method will be implemented in task 11.2")
    
    def validate(self, data: dict[str, Any]) -> list[str]:
        """Validate data against all rules.
        
        Args:
            data: Data to validate
            
        Returns:
            List of validation error messages
        """
        # Placeholder implementation
        raise NotImplementedError("Method will be implemented in task 11.2")