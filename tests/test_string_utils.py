"""Tests for string_utils module."""

import pytest
from dev_qol_toolkit.string_utils import (
    to_pascal_case, 
    to_kebab_case,
    validate_email,
    validate_url,
    sanitize_filename
)


class TestCaseConversions:
    """Test case conversion functions."""

    def test_to_pascal_case_basic(self):
        """Test basic PascalCase conversion."""
        assert to_pascal_case("hello_world") == "HelloWorld"
        assert to_pascal_case("hello-world") == "HelloWorld"
        assert to_pascal_case("hello world") == "HelloWorld"
        assert to_pascal_case("helloWorld") == "HelloWorld"
        assert to_pascal_case("HelloWorld") == "HelloWorld"

    def test_to_pascal_case_edge_cases(self):
        """Test PascalCase conversion edge cases."""
        assert to_pascal_case("") == ""
        assert to_pascal_case("a") == "A"
        assert to_pascal_case("A") == "A"
        assert to_pascal_case("hello") == "Hello"
        assert to_pascal_case("HELLO") == "Hello"

    def test_to_pascal_case_multiple_delimiters(self):
        """Test PascalCase with multiple delimiters."""
        assert to_pascal_case("hello__world") == "HelloWorld"
        assert to_pascal_case("hello--world") == "HelloWorld"
        assert to_pascal_case("hello  world") == "HelloWorld"
        assert to_pascal_case("hello_-world") == "HelloWorld"

    def test_to_pascal_case_numbers(self):
        """Test PascalCase with numbers."""
        assert to_pascal_case("hello_world_123") == "HelloWorld123"
        assert to_pascal_case("test_123_abc") == "Test123Abc"
        assert to_pascal_case("123_test") == "123Test"

    def test_to_pascal_case_special_chars(self):
        """Test PascalCase with special characters."""
        assert to_pascal_case("hello_world!") == "HelloWorld!"
        assert to_pascal_case("test@example") == "Test@example"

    def test_to_kebab_case_basic(self):
        """Test basic kebab-case conversion."""
        assert to_kebab_case("HelloWorld") == "hello-world"
        assert to_kebab_case("hello_world") == "hello-world"
        assert to_kebab_case("hello world") == "hello-world"
        assert to_kebab_case("helloWorld") == "hello-world"
        assert to_kebab_case("hello-world") == "hello-world"

    def test_to_kebab_case_edge_cases(self):
        """Test kebab-case conversion edge cases."""
        assert to_kebab_case("") == ""
        assert to_kebab_case("a") == "a"
        assert to_kebab_case("A") == "a"
        assert to_kebab_case("hello") == "hello"
        assert to_kebab_case("HELLO") == "hello"

    def test_to_kebab_case_multiple_delimiters(self):
        """Test kebab-case with multiple delimiters."""
        assert to_kebab_case("hello__world") == "hello-world"
        assert to_kebab_case("hello--world") == "hello-world"
        assert to_kebab_case("hello  world") == "hello-world"
        assert to_kebab_case("hello_-world") == "hello-world"

    def test_to_kebab_case_numbers(self):
        """Test kebab-case with numbers."""
        assert to_kebab_case("HelloWorld123") == "hello-world123"
        assert to_kebab_case("test123ABC") == "test123-abc"
        assert to_kebab_case("123Test") == "123-test"

    def test_to_kebab_case_consecutive_caps(self):
        """Test kebab-case with consecutive capital letters."""
        assert to_kebab_case("XMLHttpRequest") == "xml-http-request"
        assert to_kebab_case("HTMLParser") == "html-parser"
        assert to_kebab_case("JSONData") == "json-data"

    def test_to_kebab_case_leading_trailing_delimiters(self):
        """Test kebab-case removes leading/trailing delimiters."""
        assert to_kebab_case("_hello_world_") == "hello-world"
        assert to_kebab_case(" hello world ") == "hello-world"
        assert to_kebab_case("-hello-world-") == "hello-world"

    def test_to_kebab_case_special_chars(self):
        """Test kebab-case with special characters."""
        assert to_kebab_case("HelloWorld!") == "hello-world!"
        assert to_kebab_case("Test@Example") == "test@example"


class TestValidationFunctions:
    """Test validation functions."""

    def test_validate_email_valid(self):
        """Test valid email addresses."""
        valid_emails = [
            "user@example.com",
            "test.email@domain.co.uk",
            "user+tag@example.org",
            "firstname.lastname@company.com",
            "user123@test-domain.net",
            "a@b.co",
        ]
        for email in valid_emails:
            assert validate_email(email), f"Expected {email} to be valid"

    def test_validate_email_invalid(self):
        """Test invalid email addresses."""
        invalid_emails = [
            "",
            "invalid.email",
            "@example.com",
            "user@",
            "user..name@example.com",
            ".user@example.com",
            "user@example.",
            "user@.example.com",
            "user@example..com",
            "a" * 65 + "@example.com",  # Local part too long
            "user@" + "a" * 250 + ".com",  # Total length too long
        ]
        for email in invalid_emails:
            assert not validate_email(email), f"Expected {email} to be invalid"

    def test_validate_email_edge_cases(self):
        """Test email validation edge cases."""
        assert not validate_email(None)
        assert not validate_email(123)
        assert not validate_email([])

    def test_validate_url_valid(self):
        """Test valid URLs."""
        valid_urls = [
            "https://example.com",
            "http://localhost:8080",
            "https://sub.domain.com/path/to/resource",
            "http://192.168.1.1:3000/api",
            "ftp://files.example.com/file.txt",
            "https://example.com/path?query=value&other=123",
            "http://example.com/path#fragment",
        ]
        for url in valid_urls:
            assert validate_url(url), f"Expected {url} to be valid"

    def test_validate_url_invalid(self):
        """Test invalid URLs."""
        invalid_urls = [
            "",
            "invalid-url",
            "http://",
            "https://",
            "ftp://",
            "example.com",
            "www.example.com",
            "http:// example.com",  # Space in URL
            "http://ex ample.com",  # Space in domain
        ]
        for url in invalid_urls:
            assert not validate_url(url), f"Expected {url} to be invalid"

    def test_validate_url_edge_cases(self):
        """Test URL validation edge cases."""
        assert not validate_url(None)
        assert not validate_url(123)
        assert not validate_url([])
        # Test very long URL
        long_url = "https://example.com/" + "a" * 2050
        assert not validate_url(long_url)


class TestSanitizationFunctions:
    """Test sanitization functions."""

    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization."""
        assert sanitize_filename("normal_file.txt") == "normal_file.txt"
        assert sanitize_filename("file with spaces.doc") == "file with spaces.doc"

    def test_sanitize_filename_invalid_chars(self):
        """Test sanitization of invalid characters."""
        assert sanitize_filename("file<name>.txt") == "file_name_.txt"
        assert sanitize_filename("my/file\\name.doc") == "my_file_name.doc"
        assert sanitize_filename('file"name|test?.pdf') == "file_name_test_.pdf"
        assert sanitize_filename("file:name*test.txt") == "file_name_test.txt"

    def test_sanitize_filename_reserved_names(self):
        """Test handling of Windows reserved names."""
        assert sanitize_filename("CON.txt") == "CON.txt_"
        assert sanitize_filename("PRN.doc") == "PRN.doc_"
        assert sanitize_filename("AUX") == "AUX_"
        assert sanitize_filename("COM1.log") == "COM1.log_"
        assert sanitize_filename("LPT1.dat") == "LPT1.dat_"

    def test_sanitize_filename_edge_cases(self):
        """Test filename sanitization edge cases."""
        assert sanitize_filename("") == "file"
        assert sanitize_filename("   ") == "file"
        assert sanitize_filename("...") == "file"
        assert sanitize_filename(" .file. ") == "file"
        assert sanitize_filename(None) == ""
        assert sanitize_filename(123) == ""

    def test_sanitize_filename_long_names(self):
        """Test handling of very long filenames."""
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name)
        assert len(result) <= 255
        assert result.endswith(".txt")

    def test_sanitize_filename_control_chars(self):
        """Test removal of control characters."""
        filename_with_control = "file\x00\x01\x1fname.txt"
        result = sanitize_filename(filename_with_control)
        assert result == "filename.txt"