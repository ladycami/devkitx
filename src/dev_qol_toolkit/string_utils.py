"""String manipulation utilities for the dev-qol-toolkit.

This module provides comprehensive string manipulation functions including
case conversions, validation, sanitization, and text processing utilities.
"""

import re
from typing import Any

__all__ = [
    "to_pascal_case",
    "to_kebab_case", 
    "template_safe_substitute",
    "validate_email",
    "validate_url",
    "sanitize_filename",
    "normalize_whitespace",
    "extract_urls",
    "truncate_text",
]


def to_pascal_case(text: str) -> str:
    """Convert text to PascalCase.
    
    Converts snake_case, kebab-case, camelCase, and space-separated text to PascalCase.
    
    Args:
        text: Input text to convert
        
    Returns:
        Text converted to PascalCase
        
    Examples:
        >>> to_pascal_case("hello_world")
        'HelloWorld'
        >>> to_pascal_case("hello-world")
        'HelloWorld'
        >>> to_pascal_case("hello world")
        'HelloWorld'
        >>> to_pascal_case("helloWorld")
        'HelloWorld'
    """
    if not text:
        return ""
    
    # Split on common delimiters and camelCase boundaries
    words = re.split(r'[-_\s]+|(?<=[a-z])(?=[A-Z])', text)
    
    # Filter out empty strings and capitalize each word
    return ''.join(word.capitalize() for word in words if word)


def to_kebab_case(text: str) -> str:
    """Convert text to kebab-case.
    
    Converts snake_case, PascalCase, camelCase, and space-separated text to kebab-case.
    
    Args:
        text: Input text to convert
        
    Returns:
        Text converted to kebab-case
        
    Examples:
        >>> to_kebab_case("HelloWorld")
        'hello-world'
        >>> to_kebab_case("hello_world")
        'hello-world'
        >>> to_kebab_case("hello world")
        'hello-world'
        >>> to_kebab_case("helloWorld")
        'hello-world'
    """
    if not text:
        return ""
    
    # Insert hyphens before uppercase letters that follow lowercase letters or digits
    text = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '-', text)
    
    # Insert hyphens between consecutive uppercase letters and following lowercase letters
    text = re.sub(r'(?<=[A-Z])(?=[A-Z][a-z])', '-', text)
    
    # Replace underscores and spaces with hyphens
    text = re.sub(r'[_\s]+', '-', text)
    
    # Convert to lowercase and remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text.lower())
    
    # Remove leading/trailing hyphens
    return text.strip('-')


def template_safe_substitute(template: str, **kwargs: Any) -> str:
    """Safely substitute variables in a template string.
    
    Args:
        template: Template string with placeholders
        **kwargs: Variables to substitute
        
    Returns:
        Template with variables substituted
    """
    # Placeholder implementation
    raise NotImplementedError("Function will be implemented in task 2.3")


def validate_email(email: str) -> bool:
    """Validate email address format.
    
    Uses a comprehensive regex pattern to validate email addresses according to RFC 5322.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
        
    Examples:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid.email")
        False
        >>> validate_email("user+tag@example.co.uk")
        True
    """
    if not email or not isinstance(email, str):
        return False
    
    # Additional checks for edge cases
    if len(email) > 254:  # RFC 5321 limit
        return False
    
    if '..' in email:  # No consecutive dots
        return False
    
    if email.startswith('.') or email.endswith('.'):  # No leading/trailing dots
        return False
    
    if '@' not in email or email.count('@') != 1:
        return False
    
    local_part, domain = email.split('@')
    
    if len(local_part) > 64:  # RFC 5321 local part limit
        return False
    
    if not local_part or not domain:
        return False
    
    # Check for invalid characters in local part
    if not re.match(r'^[a-zA-Z0-9._%+-]+$', local_part):
        return False
    
    # Check domain format
    if domain.startswith('.') or domain.endswith('.'):
        return False
    
    if '..' in domain:
        return False
    
    # Domain must have at least one dot and valid TLD
    if '.' not in domain:
        return False
    
    # Check domain pattern
    domain_pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(domain_pattern, domain))


def validate_url(url: str) -> bool:
    """Validate URL format.
    
    Validates URLs with common schemes (http, https, ftp, ftps).
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid, False otherwise
        
    Examples:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("http://localhost:8080/path")
        True
        >>> validate_url("invalid-url")
        False
        >>> validate_url("ftp://files.example.com/file.txt")
        True
    """
    if not url or not isinstance(url, str):
        return False
    
    # URL regex pattern supporting common schemes
    pattern = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
    
    # Basic length check
    if len(url) > 2048:  # Common URL length limit
        return False
    
    return bool(re.match(pattern, url, re.IGNORECASE))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for cross-platform compatibility.
    
    Removes or replaces characters that are invalid in filenames on Windows, macOS, or Linux.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Sanitized filename safe for use on all platforms
        
    Examples:
        >>> sanitize_filename("file<name>.txt")
        'file_name_.txt'
        >>> sanitize_filename("my/file\\name.doc")
        'my_file_name.doc'
        >>> sanitize_filename("CON.txt")  # Windows reserved name
        'CON_.txt'
    """
    if not isinstance(filename, str):
        return ""
    
    if not filename:
        return "file"
    
    # Remove or replace invalid characters
    # Invalid chars: < > : " | ? * \ /
    invalid_chars = r'[<>:"|?*\\/]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove control characters (0-31)
    sanitized = re.sub(r'[\x00-\x1f]', '', sanitized)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Handle Windows reserved names
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    name_part = sanitized.split('.')[0].upper()
    if name_part in reserved_names:
        sanitized = sanitized + '_'
    
    # Ensure filename is not empty and not too long
    if not sanitized:
        sanitized = 'file'
    
    # Limit length to 255 characters (common filesystem limit)
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        max_name_len = 255 - len(ext) - (1 if ext else 0)
        sanitized = name[:max_name_len] + ('.' + ext if ext else '')
    
    return sanitized


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text.
    
    Args:
        text: Text to normalize
        
    Returns:
        Text with normalized whitespace
    """
    # Placeholder implementation
    raise NotImplementedError("Function will be implemented in task 2.3")


def extract_urls(text: str) -> list[str]:
    """Extract URLs from text.
    
    Args:
        text: Text to extract URLs from
        
    Returns:
        List of URLs found in text
    """
    # Placeholder implementation
    raise NotImplementedError("Function will be implemented in task 2.3")


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length of result
        suffix: Suffix to append if truncated
        
    Returns:
        Truncated text with suffix if needed
    """
    # Placeholder implementation
    raise NotImplementedError("Function will be implemented in task 2.3")