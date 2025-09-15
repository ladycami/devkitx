"""Tests for string_utils module."""

from devtools_py.string_utils import (
    to_pascal_case,
    to_kebab_case,
    validate_email,
    validate_url,
    sanitize_filename,
    template_safe_substitute,
    normalize_whitespace,
    extract_urls,
    truncate_text,
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


class TestTextProcessingFunctions:
    """Test text processing functions."""

    def test_template_safe_substitute_basic(self):
        """Test basic template substitution."""
        assert template_safe_substitute("Hello $name!", name="World") == "Hello World!"
        assert (
            template_safe_substitute("$greeting $name", greeting="Hi", name="Alice") == "Hi Alice"
        )
        assert template_safe_substitute("No variables here") == "No variables here"

    def test_template_safe_substitute_missing_vars(self):
        """Test template substitution with missing variables."""
        assert (
            template_safe_substitute("Hello $name and $missing", name="Bob")
            == "Hello Bob and $missing"
        )
        assert template_safe_substitute("$missing1 and $missing2") == "$missing1 and $missing2"

    def test_template_safe_substitute_braces(self):
        """Test template substitution with braces."""
        assert template_safe_substitute("Hello ${name}!", name="World") == "Hello World!"
        assert (
            template_safe_substitute("${greeting} ${name}", greeting="Hi", name="Alice")
            == "Hi Alice"
        )

    def test_template_safe_substitute_edge_cases(self):
        """Test template substitution edge cases."""
        assert template_safe_substitute("", name="test") == ""
        assert template_safe_substitute(None) == "None"
        assert template_safe_substitute(123) == "123"
        assert template_safe_substitute("$invalid$syntax", name="test") == "$invalid$syntax"

    def test_normalize_whitespace_basic(self):
        """Test basic whitespace normalization."""
        assert normalize_whitespace("  hello    world  ") == "hello world"
        assert normalize_whitespace("normal text") == "normal text"
        assert normalize_whitespace("") == ""

    def test_normalize_whitespace_various_chars(self):
        """Test normalization of various whitespace characters."""
        assert normalize_whitespace("line1\n\n\nline2") == "line1 line2"
        assert normalize_whitespace("tab\t\ttab") == "tab tab"
        assert normalize_whitespace("mixed \t\n  spaces") == "mixed spaces"

    def test_normalize_whitespace_edge_cases(self):
        """Test whitespace normalization edge cases."""
        assert normalize_whitespace("   ") == ""
        assert normalize_whitespace("\n\t\r") == ""
        assert normalize_whitespace(None) == "None"
        assert normalize_whitespace(123) == "123"

    def test_extract_urls_basic(self):
        """Test basic URL extraction."""
        text = "Visit https://example.com for more info"
        assert extract_urls(text) == ["https://example.com"]

        text = "Check http://site1.com and https://site2.org"
        assert extract_urls(text) == ["http://site1.com", "https://site2.org"]

    def test_extract_urls_no_urls(self):
        """Test URL extraction with no URLs."""
        assert extract_urls("No URLs here") == []
        assert extract_urls("") == []
        assert extract_urls("Just some text with www.example.com") == []

    def test_extract_urls_with_punctuation(self):
        """Test URL extraction with trailing punctuation."""
        text = "Visit https://example.com. Also check http://test.org!"
        urls = extract_urls(text)
        assert "https://example.com" in urls
        assert "http://test.org" in urls
        # Should not include punctuation
        assert "https://example.com." not in urls
        assert "http://test.org!" not in urls

    def test_extract_urls_ftp(self):
        """Test FTP URL extraction."""
        text = "Download from ftp://files.example.com/file.txt"
        assert extract_urls(text) == ["ftp://files.example.com/file.txt"]

    def test_extract_urls_edge_cases(self):
        """Test URL extraction edge cases."""
        assert extract_urls(None) == []
        assert extract_urls(123) == []
        assert extract_urls([]) == []

    def test_truncate_text_basic(self):
        """Test basic text truncation."""
        assert truncate_text("Hello World", 10) == "Hello W..."
        assert truncate_text("Short", 10) == "Short"
        assert truncate_text("Exactly10!", 10) == "Exactly10!"

    def test_truncate_text_custom_suffix(self):
        """Test text truncation with custom suffix."""
        assert truncate_text("Long text here", 8, ">>") == "Long t>>"
        assert truncate_text("Test", 8, ">>") == "Test"

    def test_truncate_text_edge_cases(self):
        """Test text truncation edge cases."""
        assert truncate_text("", 5) == ""
        assert truncate_text("Test", 0) == ""
        assert truncate_text("Test", -1) == ""
        assert truncate_text(None, 5) == "None"
        assert truncate_text(123, 5) == "123"

    def test_truncate_text_suffix_longer_than_max(self):
        """Test truncation when suffix is longer than max_length."""
        assert truncate_text("Long text", 3, "...") == "..."
        assert truncate_text("Text", 2, ">>>>") == ">>"
