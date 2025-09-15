#!/usr/bin/env python3
"""
String Utilities Examples

This module demonstrates practical usage of dev_qol_toolkit.string_utils
including case conversions, validation, sanitization, and text processing.
"""

import re
from typing import List, Dict, Any

from dev_qol_toolkit.string_utils import (
    to_pascal_case,
    to_kebab_case,
    to_snake_case,
    to_camel_case,
    template_safe_substitute,
    validate_email,
    validate_url,
    sanitize_filename,
    normalize_whitespace,
    extract_urls,
    truncate_text,
    slugify,
    remove_accents,
    is_palindrome,
    count_words,
    extract_numbers
)


def case_conversion_examples():
    """Demonstrate various case conversion utilities."""
    print("=== Case Conversion Examples ===")
    
    test_strings = [
        "hello_world",
        "HelloWorld", 
        "hello-world",
        "hello world",
        "HELLO_WORLD",
        "camelCaseString",
        "PascalCaseString",
        "kebab-case-string",
        "snake_case_string"
    ]
    
    print("Original → snake_case → camelCase → PascalCase → kebab-case")
    print("-" * 70)
    
    for original in test_strings:
        snake = to_snake_case(original)
        camel = to_camel_case(original)
        pascal = to_pascal_case(original)
        kebab = to_kebab_case(original)
        
        print(f"{original:15} → {snake:15} → {camel:15} → {pascal:15} → {kebab}")
    
    # Edge cases
    print("\n✓ Edge cases:")
    edge_cases = ["", "a", "A", "123", "hello123world", "XML_HTTP_Request"]
    for case in edge_cases:
        print(f"  '{case}' → snake: '{to_snake_case(case)}', pascal: '{to_pascal_case(case)}'")


def template_substitution_examples():
    """Demonstrate safe template substitution."""
    print("\n=== Template Substitution Examples ===")
    
    # Basic template substitution
    template = "Hello {name}, welcome to {platform}!"
    result = template_safe_substitute(template, name="Alice", platform="DevQoL")
    print(f"✓ Basic substitution: {result}")
    
    # Missing variables (safe handling)
    template_with_missing = "Hello {name}, your score is {score} out of {total}!"
    result_partial = template_safe_substitute(
        template_with_missing, 
        name="Bob", 
        score=85,
        default_value="[MISSING]"
    )
    print(f"✓ Missing variable handling: {result_partial}")
    
    # Complex template with nested data
    user_template = """
    User Profile:
    - Name: {user.name}
    - Email: {user.email}
    - Department: {user.department}
    - Joined: {user.join_date}
    """
    
    user_data = {
        "user.name": "Charlie Brown",
        "user.email": "charlie@example.com", 
        "user.department": "Engineering",
        "user.join_date": "2024-01-15"
    }
    
    profile = template_safe_substitute(user_template, **user_data)
    print(f"✓ Complex template:\n{profile}")
    
    # SQL-like template (be careful with injection!)
    sql_template = "SELECT * FROM {table} WHERE {column} = '{value}'"
    safe_sql = template_safe_substitute(
        sql_template,
        table="users",
        column="status", 
        value="active"
    )
    print(f"✓ SQL template (sanitize inputs!): {safe_sql}")


def validation_examples():
    """Demonstrate string validation functions."""
    print("\n=== String Validation Examples ===")
    
    # Email validation
    emails = [
        "valid@example.com",
        "user.name+tag@domain.co.uk",
        "invalid.email",
        "@missing-local.com",
        "missing-at-sign.com",
        "spaces in@email.com",
        ""
    ]
    
    print("Email validation:")
    for email in emails:
        is_valid = validate_email(email)
        status = "✓" if is_valid else "✗"
        print(f"  {status} {email:25} → {is_valid}")
    
    # URL validation
    urls = [
        "https://www.example.com",
        "http://localhost:8080/path",
        "ftp://files.example.com/file.txt",
        "https://sub.domain.com/path?query=value#anchor",
        "not-a-url",
        "http://",
        "https://spaces in url.com",
        ""
    ]
    
    print("\nURL validation:")
    for url in urls:
        is_valid = validate_url(url)
        status = "✓" if is_valid else "✗"
        print(f"  {status} {url:35} → {is_valid}")


def sanitization_examples():
    """Demonstrate string sanitization utilities."""
    print("\n=== String Sanitization Examples ===")
    
    # Filename sanitization
    filenames = [
        "normal_file.txt",
        "file with spaces.doc",
        "file/with\\slashes.pdf",
        "file:with*special?chars.txt",
        "file<with>pipes|and\"quotes.csv",
        "very_long_filename_that_exceeds_normal_limits_and_should_be_truncated.txt",
        "файл_с_unicode.txt",
        ""
    ]
    
    print("Filename sanitization:")
    for filename in filenames:
        sanitized = sanitize_filename(filename)
        print(f"  '{filename}' → '{sanitized}'")
    
    # Whitespace normalization
    texts_with_whitespace = [
        "  normal text  ",
        "text\twith\ttabs",
        "text\nwith\nnewlines",
        "text   with    multiple    spaces",
        "mixed\t  \n  whitespace\r\n  text",
        ""
    ]
    
    print("\nWhitespace normalization:")
    for text in texts_with_whitespace:
        normalized = normalize_whitespace(text)
        print(f"  '{repr(text)}' → '{normalized}'")
    
    # Remove accents
    accented_texts = [
        "café",
        "naïve",
        "résumé", 
        "piñata",
        "Zürich",
        "François",
        "São Paulo"
    ]
    
    print("\nAccent removal:")
    for text in accented_texts:
        clean = remove_accents(text)
        print(f"  '{text}' → '{clean}'")


def text_processing_examples():
    """Demonstrate text processing utilities."""
    print("\n=== Text Processing Examples ===")
    
    # URL extraction
    text_with_urls = """
    Check out these websites:
    - https://www.example.com for examples
    - Visit http://localhost:8080/api for the API
    - FTP files at ftp://files.example.com
    - Email me at user@domain.com (not a URL)
    - Invalid: not-a-url.com
    """
    
    urls = extract_urls(text_with_urls)
    print("✓ Extracted URLs:")
    for url in urls:
        print(f"  - {url}")
    
    # Text truncation
    long_text = "This is a very long text that needs to be truncated for display purposes in UI components."
    
    truncation_examples = [
        (long_text, 30, "..."),
        (long_text, 50, " [more]"),
        (long_text, 20, ""),
        ("Short text", 50, "...")
    ]
    
    print("\nText truncation:")
    for text, max_len, suffix in truncation_examples:
        truncated = truncate_text(text, max_len, suffix)
        print(f"  Max {max_len:2d}: '{truncated}'")
    
    # Slugification for URLs
    titles = [
        "My Blog Post Title",
        "Special Characters: @#$%^&*()",
        "Unicode: café naïve résumé",
        "Numbers and Spaces: 123 ABC 456",
        "Multiple    Spaces    Here"
    ]
    
    print("\nSlugification:")
    for title in titles:
        slug = slugify(title)
        print(f"  '{title}' → '{slug}'")
    
    # Word counting
    texts = [
        "Simple sentence.",
        "Multiple words in this sentence here.",
        "Hyphenated-words and contractions don't count as multiple.",
        "Numbers like 123 and symbols @#$ are handled.",
        ""
    ]
    
    print("\nWord counting:")
    for text in texts:
        count = count_words(text)
        print(f"  '{text}' → {count} words")


def pattern_matching_examples():
    """Demonstrate pattern matching and extraction."""
    print("\n=== Pattern Matching Examples ===")
    
    # Number extraction
    texts_with_numbers = [
        "I have 5 apples and 3.14 oranges",
        "The temperature is -10.5°C",
        "Call me at 555-123-4567",
        "Version 2.1.3 released",
        "No numbers here!",
        "Mixed: 1st place, 2nd runner-up, 3.0 rating"
    ]
    
    print("Number extraction:")
    for text in texts_with_numbers:
        numbers = extract_numbers(text)
        print(f"  '{text}' → {numbers}")
    
    # Palindrome detection
    palindrome_candidates = [
        "racecar",
        "A man a plan a canal Panama",
        "race a car",
        "hello",
        "Madam",
        "Was it a rat I saw?",
        ""
    ]
    
    print("\nPalindrome detection:")
    for text in palindrome_candidates:
        is_pal = is_palindrome(text)
        status = "✓" if is_pal else "✗"
        print(f"  {status} '{text}' → {is_pal}")


def advanced_use_cases():
    """Demonstrate advanced real-world use cases."""
    print("\n=== Advanced Use Cases ===")
    
    # Data cleaning pipeline
    def clean_user_input(raw_input: str) -> str:
        """Example data cleaning pipeline."""
        # 1. Normalize whitespace
        cleaned = normalize_whitespace(raw_input)
        
        # 2. Remove accents for ASCII compatibility
        cleaned = remove_accents(cleaned)
        
        # 3. Create URL-friendly slug
        slug = slugify(cleaned)
        
        return slug
    
    user_inputs = [
        "  My Café Blog Post  ",
        "François's résumé",
        "São Paulo Travel Guide"
    ]
    
    print("Data cleaning pipeline:")
    for raw in user_inputs:
        clean = clean_user_input(raw)
        print(f"  '{raw}' → '{clean}'")
    
    # Configuration template processing
    config_template = """
    # Application Configuration
    app_name: {app_name}
    debug: {debug}
    database_url: postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}
    redis_url: redis://{redis_host}:{redis_port}/0
    secret_key: {secret_key}
    """
    
    config_vars = {
        "app_name": "MyApp",
        "debug": "false",
        "db_user": "app_user",
        "db_pass": "secure_password",
        "db_host": "localhost",
        "db_port": "5432",
        "db_name": "myapp_db",
        "redis_host": "localhost", 
        "redis_port": "6379",
        "secret_key": "your-secret-key-here"
    }
    
    config = template_safe_substitute(config_template, **config_vars)
    print("✓ Configuration template processing:")
    print(config)


def performance_considerations():
    """Demonstrate performance considerations."""
    print("\n=== Performance Considerations ===")
    
    print("Performance tips:")
    print("1. Case conversions: O(n) time complexity")
    print("2. Regex operations (email/URL validation): Can be expensive for large texts")
    print("3. Unicode operations (accent removal): Slower than ASCII-only operations")
    print("4. Template substitution: Linear with template size and variable count")
    
    # Demonstrate efficient batch processing
    def process_strings_efficiently(strings: List[str]) -> List[str]:
        """Example of efficient batch string processing."""
        # Pre-compile regex patterns for reuse
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        results = []
        for s in strings:
            # Process each string
            processed = normalize_whitespace(s)
            processed = to_snake_case(processed)
            results.append(processed)
        
        return results
    
    print("✓ Use pre-compiled regex patterns for batch processing")
    print("✓ Chain operations to minimize intermediate string creation")


def limitations_and_gotchas():
    """Document known limitations and gotchas."""
    print("\n=== Limitations and Gotchas ===")
    
    print("Known limitations:")
    print("1. Case conversion may not handle all edge cases (e.g., acronyms)")
    print("2. Email validation is basic - use dedicated libraries for production")
    print("3. URL validation doesn't check if URL actually exists")
    print("4. Filename sanitization may vary by operating system")
    print("5. Unicode handling depends on Python's unicodedata module")
    
    # Demonstrate edge cases
    print("\nEdge cases to be aware of:")
    
    # Case conversion edge cases
    edge_case_strings = ["XMLHttpRequest", "iPhone", "iOS", "API_KEY"]
    print("Case conversion edge cases:")
    for s in edge_case_strings:
        print(f"  '{s}' → snake: '{to_snake_case(s)}', camel: '{to_camel_case(s)}'")
    
    # Validation limitations
    print("\nValidation limitations:")
    print("  - 'test@localhost' → valid email format but may not be deliverable")
    print("  - 'http://999.999.999.999' → valid URL format but invalid IP")
    print("  - Very long domains may pass validation but exceed DNS limits")
    
    print("\nBest practices:")
    print("- Always validate user input at multiple layers")
    print("- Use dedicated libraries for critical validation (email, URLs)")
    print("- Test edge cases specific to your use case")
    print("- Consider internationalization requirements")
    print("- Sanitize data before storage and display")


if __name__ == "__main__":
    """Run all examples."""
    print("Dev QoL Toolkit - String Utilities Examples")
    print("=" * 50)
    
    case_conversion_examples()
    template_substitution_examples()
    validation_examples()
    sanitization_examples()
    text_processing_examples()
    pattern_matching_examples()
    advanced_use_cases()
    performance_considerations()
    limitations_and_gotchas()
    
    print("\n" + "=" * 50)
    print("All string utilities examples completed!")