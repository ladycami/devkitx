"""Tests for DevKitX security module."""

import pytest
from devkitx.security import SecretsScanner, SecretMatch
from devkitx.security.input_sanitizer import sanitize_html, sanitize_sql_identifier


class TestSecretsScanner:
    """Test secrets scanner functionality."""
    
    def test_detect_aws_access_key(self):
        """Test detection of AWS access keys."""
        scanner = SecretsScanner()
        code = 'AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"'
        
        matches = scanner.scan_text(code)
        
        assert len(matches) == 1
        assert matches[0].secret_type == "aws_access_key"
        assert matches[0].severity == "critical"
        assert "AKIA" in matches[0].value
    
    def test_detect_api_key(self):
        """Test detection of API keys."""
        scanner = SecretsScanner()
        code = 'api_key = "sk-1234567890abcdef1234567890abcdef"'
        
        matches = scanner.scan_text(code)
        
        assert len(matches) >= 1
        api_key_match = next((m for m in matches if m.secret_type == "api_key"), None)
        assert api_key_match is not None
        assert api_key_match.severity == "high"
    
    def test_ignore_comments(self):
        """Test that comments are ignored."""
        scanner = SecretsScanner()
        code = '# AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"'
        
        matches = scanner.scan_text(code)
        
        assert len(matches) == 0
    
    def test_detect_jwt_token(self):
        """Test detection of JWT tokens."""
        scanner = SecretsScanner()
        # Fake but realistic JWT structure
        code = 'token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"'
        
        matches = scanner.scan_text(code)
        
        jwt_match = next((m for m in matches if m.secret_type == "jwt_token"), None)
        assert jwt_match is not None
        assert jwt_match.severity == "high"
    
    def test_redacted_output(self):
        """Test that secrets are properly redacted."""
        match = SecretMatch(
            secret_type="api_key",
            value="sk-1234567890abcdef1234567890abcdef",
            line_number=1,
            file_path="test.py",
            severity="high"
        )
        
        redacted = match.redacted
        assert redacted.startswith("sk-1")
        assert redacted.endswith("cdef")
        assert "****" in redacted or "***" in redacted


class TestInputSanitizer:
    """Test input sanitization functions."""
    
    def test_sanitize_html_escape_all(self):
        """Test HTML sanitization with no allowed tags."""
        html = "<script>alert('xss')</script>Hello <b>world</b>"
        
        result = sanitize_html(html)
        
        assert "&lt;script&gt;" in result
        assert "&lt;b&gt;" in result
        assert "Hello" in result
        assert "world" in result
    
    def test_sanitize_html_with_allowed_tags(self):
        """Test HTML sanitization with allowed tags."""
        html = "<script>alert('xss')</script>Hello <b>world</b>"
        
        result = sanitize_html(html, allowed_tags={"b"})
        
        assert "&lt;script&gt;" in result
        assert "<b>world</b>" in result
        assert "Hello" in result
    
    def test_sanitize_sql_identifier_valid(self):
        """Test SQL identifier sanitization with valid input."""
        identifier = "user_table"
        
        result = sanitize_sql_identifier(identifier)
        
        assert result == "user_table"
    
    def test_sanitize_sql_identifier_invalid_chars(self):
        """Test SQL identifier sanitization with invalid characters."""
        identifier = "users; DROP TABLE users;"
        
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            sanitize_sql_identifier(identifier)
    
    def test_sanitize_sql_identifier_reserved_keyword(self):
        """Test SQL identifier sanitization with reserved keywords."""
        identifier = "select"
        
        with pytest.raises(ValueError, match="reserved keyword"):
            sanitize_sql_identifier(identifier)