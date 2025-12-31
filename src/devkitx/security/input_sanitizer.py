"""Input sanitization utilities."""

from __future__ import annotations

import re
import html


def sanitize_html(text: str, allowed_tags: set[str] | None = None) -> str:
    """Sanitize HTML input to prevent XSS attacks.
    
    Args:
        text: HTML text to sanitize
        allowed_tags: Set of allowed HTML tags (default: none)
        
    Returns:
        Sanitized HTML text
        
    Example:
        >>> sanitize_html("<script>alert('xss')</script>Hello")
        "&lt;script&gt;alert('xss')&lt;/script&gt;Hello"
        >>> sanitize_html("<b>Hello</b>", allowed_tags={"b"})
        "<b>Hello</b>"
    """
    if allowed_tags is None:
        # Escape all HTML
        return html.escape(text)
    
    # Simple tag allowlist implementation
    # For production, consider using a library like bleach
    allowed_pattern = "|".join(re.escape(tag) for tag in allowed_tags)
    
    def replace_tag(match: re.Match[str]) -> str:
        tag = match.group(1).lower()
        if tag in allowed_tags or f"/{tag}" in allowed_tags:
            return match.group(0)
        return html.escape(match.group(0))
    
    # Replace disallowed tags
    pattern = r"<(/?\w+)[^>]*>"
    return re.sub(pattern, replace_tag, text)


def sanitize_sql_identifier(identifier: str) -> str:
    """Sanitize SQL identifier to prevent injection.
    
    Args:
        identifier: SQL identifier (table name, column name, etc.)
        
    Returns:
        Sanitized identifier
        
    Raises:
        ValueError: If identifier contains invalid characters
        
    Example:
        >>> sanitize_sql_identifier("user_table")
        "user_table"
        >>> sanitize_sql_identifier("users; DROP TABLE users;")
        Traceback (most recent call last):
        ValueError: Invalid SQL identifier: contains disallowed characters
    """
    # Allow only alphanumeric characters and underscores
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", identifier):
        raise ValueError("Invalid SQL identifier: contains disallowed characters")
    
    # Check for SQL keywords (basic list)
    sql_keywords = {
        "select", "insert", "update", "delete", "drop", "create", "alter",
        "table", "database", "index", "view", "trigger", "procedure", "function",
        "union", "join", "where", "having", "group", "order", "limit", "offset"
    }
    
    if identifier.lower() in sql_keywords:
        raise ValueError(f"Invalid SQL identifier: '{identifier}' is a reserved keyword")
    
    return identifier


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Sanitized filename
        
    Example:
        >>> sanitize_filename("../../../etc/passwd")
        "etc_passwd"
        >>> sanitize_filename("normal_file.txt")
        "normal_file.txt"
    """
    # Remove directory separators and special characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
    
    # Remove path traversal attempts
    sanitized = sanitized.replace("..", "_")
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed_file"
    
    return sanitized