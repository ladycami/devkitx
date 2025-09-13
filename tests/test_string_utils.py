"""Tests for string_utils module."""

import pytest
from dev_qol_toolkit.string_utils import to_pascal_case, to_kebab_case


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