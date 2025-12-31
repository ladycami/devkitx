"""String manipulation utilities."""

from __future__ import annotations

import re


def to_snake_case(text: str) -> str:
    """Convert string to snake_case.
    
    Args:
        text: String to convert
        
    Returns:
        snake_case string
        
    Example:
        >>> to_snake_case("CamelCase")
        'camel_case'
        >>> to_snake_case("kebab-case")
        'kebab_case'
    """
    # Handle camelCase and PascalCase
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)
    # Handle kebab-case
    text = text.replace('-', '_')
    # Handle spaces
    text = text.replace(' ', '_')
    # Convert to lowercase and remove multiple underscores
    text = re.sub(r'_+', '_', text.lower())
    return text.strip('_')


def to_camel_case(text: str) -> str:
    """Convert string to camelCase.
    
    Args:
        text: String to convert
        
    Returns:
        camelCase string
        
    Example:
        >>> to_camel_case("snake_case")
        'snakeCase'
        >>> to_camel_case("kebab-case")
        'kebabCase'
    """
    # Split on underscores, hyphens, and spaces
    words = re.split(r'[_\-\s]+', text.lower())
    if not words:
        return ""
    
    # First word lowercase, rest title case
    return words[0] + ''.join(word.capitalize() for word in words[1:])


def to_pascal_case(text: str) -> str:
    """Convert string to PascalCase.
    
    Args:
        text: String to convert
        
    Returns:
        PascalCase string
        
    Example:
        >>> to_pascal_case("snake_case")
        'SnakeCase'
        >>> to_pascal_case("kebab-case")
        'KebabCase'
    """
    # Split on underscores, hyphens, and spaces
    words = re.split(r'[_\-\s]+', text.lower())
    return ''.join(word.capitalize() for word in words if word)


def to_kebab_case(text: str) -> str:
    """Convert string to kebab-case.
    
    Args:
        text: String to convert
        
    Returns:
        kebab-case string
        
    Example:
        >>> to_kebab_case("CamelCase")
        'camel-case'
        >>> to_kebab_case("snake_case")
        'snake-case'
    """
    # Handle camelCase and PascalCase
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', text)
    # Handle underscores
    text = text.replace('_', '-')
    # Handle spaces
    text = text.replace(' ', '-')
    # Convert to lowercase and remove multiple hyphens
    text = re.sub(r'-+', '-', text.lower())
    return text.strip('-')


def truncate(text: str, length: int, suffix: str = "...") -> str:
    """Truncate string to specified length.
    
    Args:
        text: String to truncate
        length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
        
    Example:
        >>> truncate("Hello world", 8)
        'Hello...'
        >>> truncate("Short", 10)
        'Short'
    """
    if len(text) <= length:
        return text
    
    return text[:length - len(suffix)] + suffix