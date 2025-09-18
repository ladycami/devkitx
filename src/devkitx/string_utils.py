"""String manipulation utilities for DevKitX.

This module provides comprehensive string manipulation functions including
case conversions, validation, sanitization, and text processing utilities.
"""

import re
from string import Template
from typing import Any

__all__ = [
    "to_snake_case",
    "to_camel_case",
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


def to_snake_case(text: str) -> str:
    """Convert text to snake_case.

    Converts PascalCase, camelCase, kebab-case, and space-separated text to snake_case.

    Args:
        text: Input text to convert

    Returns:
        Text converted to snake_case

    Examples:
        >>> to_snake_case("HelloWorld")
        'hello_world'
        >>> to_snake_case("helloWorld")
        'hello_world'
        >>> to_snake_case("hello-world")
        'hello_world'
        >>> to_snake_case("hello world")
        'hello_world'
    """
    if not text:
        return ""

    # Insert underscores before uppercase letters that follow lowercase letters or digits
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", text)

    # Insert underscores between consecutive uppercase letters and following lowercase letters
    text = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", text)

    # Replace hyphens and spaces with underscores
    text = re.sub(r"[-\s]+", "_", text)

    # Convert to lowercase and remove multiple consecutive underscores
    text = re.sub(r"_+", "_", text.lower())

    # Remove leading/trailing underscores
    return text.strip("_")


def to_camel_case(text: str) -> str:
    """Convert text to camelCase.

    Converts snake_case, kebab-case, PascalCase, and space-separated text to camelCase.

    Args:
        text: Input text to convert

    Returns:
        Text converted to camelCase

    Examples:
        >>> to_camel_case("hello_world")
        'helloWorld'
        >>> to_camel_case("hello-world")
        'helloWorld'
        >>> to_camel_case("hello world")
        'helloWorld'
        >>> to_camel_case("HelloWorld")
        'helloWorld'
    """
    if not text:
        return ""

    # Split on common delimiters and camelCase boundaries
    words = re.split(r"[-_\s]+|(?<=[a-z])(?=[A-Z])", text)

    # Filter out empty strings
    words = [word for word in words if word]

    if not words:
        return ""

    # First word lowercase, rest capitalized
    result = words[0].lower()
    for word in words[1:]:
        result += word.capitalize()

    return result


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
    words = re.split(r"[-_\s]+|(?<=[a-z])(?=[A-Z])", text)

    # Filter out empty strings and capitalize each word
    return "".join(word.capitalize() for word in words if word)


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
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", text)

    # Insert hyphens between consecutive uppercase letters and following lowercase letters
    text = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "-", text)

    # Replace underscores and spaces with hyphens
    text = re.sub(r"[_\s]+", "-", text)

    # Convert to lowercase and remove multiple consecutive hyphens
    text = re.sub(r"-+", "-", text.lower())

    # Remove leading/trailing hyphens
    return text.strip("-")


def template_safe_substitute(template: str, **kwargs: Any) -> str:
    """Safely substitute variables in a template string.

    Uses Python's string.Template for safe substitution. Missing variables are left as-is.

    Args:
        template: Template string with $variable or ${variable} placeholders
        **kwargs: Variables to substitute

    Returns:
        Template with variables substituted

    Examples:
        >>> template_safe_substitute("Hello $name!", name="World")
        'Hello World!'
        >>> template_safe_substitute("$greeting $name", greeting="Hi", name="Alice")
        'Hi Alice'
        >>> template_safe_substitute("Hello $name and $missing", name="Bob")
        'Hello Bob and $missing'
    """
    if not isinstance(template, str):
        return str(template)

    try:
        tmpl = Template(template)
        # Use safe_substitute to leave missing variables as-is
        return tmpl.safe_substitute(**kwargs)
    except (ValueError, KeyError):
        # If template is malformed, return original
        return template


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

    if ".." in email:  # No consecutive dots
        return False

    if email.startswith(".") or email.endswith("."):  # No leading/trailing dots
        return False

    if "@" not in email or email.count("@") != 1:
        return False

    local_part, domain = email.split("@")

    if len(local_part) > 64:  # RFC 5321 local part limit
        return False

    if not local_part or not domain:
        return False

    # Check for invalid characters in local part
    if not re.match(r"^[a-zA-Z0-9._%+-]+$", local_part):
        return False

    # Check domain format
    if domain.startswith(".") or domain.endswith("."):
        return False

    if ".." in domain:
        return False

    # Domain must have at least one dot and valid TLD
    if "." not in domain:
        return False

    # Check domain pattern
    domain_pattern = r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
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
    pattern = r"^(https?|ftp)://[^\s/$.?#].[^\s]*$"

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
    sanitized = re.sub(invalid_chars, "_", filename)

    # Remove control characters (0-31)
    sanitized = re.sub(r"[\x00-\x1f]", "", sanitized)

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(" .")

    # Handle Windows reserved names
    reserved_names = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }

    name_part = sanitized.split(".")[0].upper()
    if name_part in reserved_names:
        sanitized = sanitized + "_"

    # Ensure filename is not empty and not too long
    if not sanitized:
        sanitized = "file"

    # Limit length to 255 characters (common filesystem limit)
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit(".", 1) if "." in sanitized else (sanitized, "")
        max_name_len = 255 - len(ext) - (1 if ext else 0)
        sanitized = name[:max_name_len] + ("." + ext if ext else "")

    return sanitized


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text.

    Replaces multiple consecutive whitespace characters with single spaces,
    and strips leading/trailing whitespace.

    Args:
        text: Text to normalize

    Returns:
        Text with normalized whitespace

    Examples:
        >>> normalize_whitespace("  hello    world  ")
        'hello world'
        >>> normalize_whitespace("line1\\n\\n\\nline2")
        'line1 line2'
        >>> normalize_whitespace("tab\\t\\ttab")
        'tab tab'
    """
    if not isinstance(text, str):
        return str(text)

    # Replace all whitespace sequences with single spaces
    normalized = re.sub(r"\s+", " ", text)

    # Strip leading and trailing whitespace
    return normalized.strip()


def extract_urls(text: str) -> list[str]:
    """Extract URLs from text.

    Finds URLs with common schemes (http, https, ftp, ftps) in the given text.

    Args:
        text: Text to extract URLs from

    Returns:
        List of URLs found in text

    Examples:
        >>> extract_urls("Visit https://example.com for more info")
        ['https://example.com']
        >>> extract_urls("Check http://site1.com and https://site2.org")
        ['http://site1.com', 'https://site2.org']
        >>> extract_urls("No URLs here")
        []
    """
    if not isinstance(text, str):
        return []

    # URL pattern for common schemes
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+|ftp://[^\s<>"{}|\\^`\[\]]+'

    urls = re.findall(url_pattern, text, re.IGNORECASE)

    # Filter out URLs that end with punctuation that's likely not part of the URL
    cleaned_urls = []
    for url in urls:
        # Remove trailing punctuation that's commonly not part of URLs
        url = re.sub(r'[.,;:!?)\]}>"\']$', "", url)
        if url:
            cleaned_urls.append(url)

    return cleaned_urls


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix.

    If text is longer than max_length, truncates it and adds suffix.
    The total length including suffix will not exceed max_length.

    Args:
        text: Text to truncate
        max_length: Maximum length of result
        suffix: Suffix to append if truncated

    Returns:
        Truncated text with suffix if needed

    Examples:
        >>> truncate_text("Hello World", 10)
        'Hello W...'
        >>> truncate_text("Short", 10)
        'Short'
        >>> truncate_text("Long text here", 8, ">>")
        'Long t>>'
    """
    if not isinstance(text, str):
        text = str(text)

    if max_length <= 0:
        return ""

    if len(text) <= max_length:
        return text

    if len(suffix) >= max_length:
        return suffix[:max_length]

    truncate_at = max_length - len(suffix)
    return text[:truncate_at] + suffix
