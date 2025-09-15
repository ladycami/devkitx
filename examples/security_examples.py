#!/usr/bin/env python3
"""
Security Utilities Examples

This module demonstrates practical usage of devtools_py.security_utils
including password hashing, JWT tokens, data encryption, and input sanitization.
"""

import os
import time
from typing import Dict, Any, Optional

from devtools_py.security_utils import (
    hash_password,
    verify_password,
    generate_secret_key,
    generate_uuid,
    hash_data,
    generate_jwt_token,
    verify_jwt_token,
    sanitize_input,
    encrypt_data,
    decrypt_data,
    generate_api_key,
    validate_password_strength
)


def password_security_examples():
    """Demonstrate secure password handling."""
    print("=== Password Security Examples ===")
    
    # Password hashing and verification
    passwords = ["password123", "MySecureP@ssw0rd!", "weak", ""]
    
    print("Password hashing and verification:")
    for password in passwords:
        if not password:
            continue
            
        # Hash password
        hashed = hash_password(password)
        print(f"  Password: '{password}'")
        print(f"  Hashed: {hashed[:50]}...")
        
        # Verify correct password
        is_valid = verify_password(password, hashed)
        print(f"  Verification (correct): {is_valid}")
        
        # Verify incorrect password
        is_invalid = verify_password(password + "wrong", hashed)
        print(f"  Verification (incorrect): {is_invalid}")
        print()
    
    # Password strength validation
    print("Password strength validation:")
    test_passwords = [
        "weak",
        "password123",
        "MySecureP@ssw0rd!",
        "VeryLongPasswordWithMixedCaseAndNumbers123!",
        "12345678",
        "abcdefgh",
        "ABCDEFGH",
        "P@ssw0rd"
    ]
    
    for pwd in test_passwords:
        strength = validate_password_strength(pwd)
        print(f"  '{pwd}' → Strength: {strength['score']}/5, Issues: {strength['issues']}")


def token_and_key_generation():
    """Demonstrate token and key generation."""
    print("\n=== Token and Key Generation ===")
    
    # Generate various types of keys
    print("Key generation:")
    
    # Secret keys for different purposes
    secret_key = generate_secret_key(32)  # 32 bytes = 256 bits
    api_key = generate_api_key()
    session_id = generate_uuid()
    
    print(f"  Secret key (32 bytes): {secret_key}")
    print(f"  API key: {api_key}")
    print(f"  Session ID (UUID): {session_id}")
    
    # Generate keys of different lengths
    key_lengths = [16, 32, 64]
    for length in key_lengths:
        key = generate_secret_key(length)
        print(f"  {length}-byte key: {key}")
    
    # Multiple UUIDs (should be unique)
    print("\nUUID uniqueness test:")
    uuids = [generate_uuid() for _ in range(5)]
    for i, uuid in enumerate(uuids, 1):
        print(f"  UUID {i}: {uuid}")
    
    # Verify all UUIDs are unique
    unique_count = len(set(uuids))
    print(f"  Generated {len(uuids)} UUIDs, {unique_count} unique ✓")


def jwt_token_examples():
    """Demonstrate JWT token creation and verification."""
    print("\n=== JWT Token Examples ===")
    
    # Generate a secret key for JWT signing
    jwt_secret = generate_secret_key(32)
    
    # Create JWT tokens with different payloads
    payloads = [
        {
            "user_id": 123,
            "username": "alice",
            "role": "admin",
            "permissions": ["read", "write", "delete"]
        },
        {
            "user_id": 456,
            "username": "bob",
            "role": "user",
            "permissions": ["read"]
        },
        {
            "session_id": generate_uuid(),
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0..."
        }
    ]
    
    print("JWT token creation and verification:")
    
    for i, payload in enumerate(payloads, 1):
        print(f"\n  Example {i}:")
        print(f"    Payload: {payload}")
        
        # Create token with different expiration times
        for expires_in in [3600, 86400]:  # 1 hour, 1 day
            token = generate_jwt_token(payload, jwt_secret, expires_in=expires_in)
            print(f"    Token ({expires_in}s): {token[:50]}...")
            
            # Verify token immediately
            decoded = verify_jwt_token(token, jwt_secret)
            if decoded:
                print(f"    Verified: user_id={decoded.get('user_id', 'N/A')}")
            else:
                print(f"    Verification failed!")
    
    # Test expired token
    print("\n  Expired token test:")
    short_lived_token = generate_jwt_token(
        {"test": "data"}, jwt_secret, expires_in=1
    )
    print(f"    Created token with 1s expiration")
    
    # Wait for expiration
    time.sleep(2)
    
    expired_decoded = verify_jwt_token(short_lived_token, jwt_secret)
    print(f"    Verification after expiration: {expired_decoded is not None}")


def data_hashing_examples():
    """Demonstrate data hashing for integrity checking."""
    print("\n=== Data Hashing Examples ===")
    
    # Hash different types of data
    test_data = [
        "Simple string",
        "Unicode string with émojis 🔒🔑",
        '{"json": "data", "number": 42}',
        "Very long string " * 100,
        ""
    ]
    
    algorithms = ["md5", "sha1", "sha256", "sha512"]
    
    print("Data hashing with different algorithms:")
    
    for data in test_data[:3]:  # Show first 3 examples
        print(f"\n  Data: '{data[:50]}{'...' if len(data) > 50 else ''}'")
        
        for algorithm in algorithms:
            hash_value = hash_data(data, algorithm=algorithm)
            print(f"    {algorithm.upper()}: {hash_value}")
    
    # File integrity checking example
    print("\n  File integrity checking:")
    
    # Simulate file content
    file_contents = [
        "Original file content",
        "Modified file content",
        "Original file content"  # Same as first
    ]
    
    hashes = []
    for i, content in enumerate(file_contents):
        hash_value = hash_data(content, algorithm="sha256")
        hashes.append(hash_value)
        print(f"    File version {i+1}: {hash_value}")
    
    # Check for changes
    print(f"    File 1 == File 3: {hashes[0] == hashes[2]} ✓")
    print(f"    File 1 == File 2: {hashes[0] == hashes[1]} (content changed)")


def input_sanitization_examples():
    """Demonstrate input sanitization and validation."""
    print("\n=== Input Sanitization Examples ===")
    
    # Dangerous inputs that need sanitization
    dangerous_inputs = [
        "<script>alert('XSS')</script>",
        "'; DROP TABLE users; --",
        "../../../etc/passwd",
        "user@domain.com<script>alert(1)</script>",
        "Normal input with <b>HTML</b> tags",
        "Input with\nnewlines\tand\ttabs",
        "Unicode: café naïve résumé 🔒",
        ""
    ]
    
    print("HTML/Script sanitization:")
    for dangerous_input in dangerous_inputs:
        sanitized = sanitize_input(dangerous_input, mode="html")
        print(f"  Input:  '{dangerous_input}'")
        print(f"  Output: '{sanitized}'")
        print()
    
    # Filename sanitization
    print("Filename sanitization:")
    dangerous_filenames = [
        "normal_file.txt",
        "../../../etc/passwd",
        "file<with>bad:chars.txt",
        "file|with*wildcards?.doc",
        "very_long_filename_" + "x" * 200 + ".txt",
        "file\nwith\nnewlines.txt"
    ]
    
    for filename in dangerous_filenames:
        sanitized = sanitize_input(filename, mode="filename")
        print(f"  '{filename[:50]}...' → '{sanitized}'")
    
    # SQL injection prevention
    print("\nSQL injection prevention:")
    sql_inputs = [
        "normal_username",
        "admin'; DROP TABLE users; --",
        "user' OR '1'='1",
        "'; SELECT * FROM passwords; --"
    ]
    
    for sql_input in sql_inputs:
        sanitized = sanitize_input(sql_input, mode="sql")
        print(f"  '{sql_input}' → '{sanitized}'")


def encryption_examples():
    """Demonstrate data encryption and decryption."""
    print("\n=== Data Encryption Examples ===")
    
    # Generate encryption key
    encryption_key = generate_secret_key(32)  # 256-bit key
    print(f"Encryption key: {encryption_key}")
    
    # Data to encrypt
    sensitive_data = [
        "Credit card: 4532-1234-5678-9012",
        "SSN: 123-45-6789",
        "Password: MySecretPassword123!",
        '{"api_key": "sk_live_abc123", "secret": "xyz789"}',
        "Personal note: This is confidential information"
    ]
    
    print("\nEncryption and decryption:")
    
    for data in sensitive_data:
        print(f"\n  Original: '{data}'")
        
        # Encrypt data
        encrypted = encrypt_data(data, encryption_key)
        print(f"  Encrypted: {encrypted}")
        
        # Decrypt data
        decrypted = decrypt_data(encrypted, encryption_key)
        print(f"  Decrypted: '{decrypted}'")
        
        # Verify integrity
        matches = data == decrypted
        print(f"  Integrity check: {matches} ✓")
    
    # Test with wrong key
    print("\n  Wrong key test:")
    wrong_key = generate_secret_key(32)
    test_data = "Secret message"
    
    encrypted_data = encrypt_data(test_data, encryption_key)
    print(f"    Encrypted with correct key: {encrypted_data}")
    
    try:
        wrong_decrypt = decrypt_data(encrypted_data, wrong_key)
        print(f"    Decrypted with wrong key: {wrong_decrypt}")
    except Exception as e:
        print(f"    Decryption with wrong key failed: {type(e).__name__}")


def api_security_examples():
    """Demonstrate API security patterns."""
    print("\n=== API Security Examples ===")
    
    # API key management
    print("API key management:")
    
    # Generate API keys for different services
    services = ["payment_service", "email_service", "analytics_service"]
    api_keys = {}
    
    for service in services:
        api_key = generate_api_key(prefix=service[:4].upper())
        api_keys[service] = api_key
        print(f"  {service}: {api_key}")
    
    # Rate limiting tokens
    print("\nRate limiting with JWT:")
    
    rate_limit_secret = generate_secret_key(32)
    
    # Create rate limit token
    rate_limit_payload = {
        "user_id": 123,
        "requests_remaining": 100,
        "reset_time": int(time.time()) + 3600  # 1 hour from now
    }
    
    rate_token = generate_jwt_token(
        rate_limit_payload, 
        rate_limit_secret, 
        expires_in=3600
    )
    
    print(f"  Rate limit token: {rate_token[:50]}...")
    
    # Verify and check rate limit
    decoded_rate = verify_jwt_token(rate_token, rate_limit_secret)
    if decoded_rate:
        remaining = decoded_rate.get("requests_remaining", 0)
        reset_time = decoded_rate.get("reset_time", 0)
        print(f"  Requests remaining: {remaining}")
        print(f"  Reset time: {reset_time}")
    
    # Session management
    print("\nSession management:")
    
    session_secret = generate_secret_key(32)
    
    # Create session token
    session_payload = {
        "session_id": generate_uuid(),
        "user_id": 456,
        "login_time": int(time.time()),
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0 (compatible)"
    }
    
    session_token = generate_jwt_token(
        session_payload,
        session_secret,
        expires_in=86400  # 24 hours
    )
    
    print(f"  Session token: {session_token[:50]}...")
    
    # Verify session
    decoded_session = verify_jwt_token(session_token, session_secret)
    if decoded_session:
        print(f"  Session ID: {decoded_session['session_id']}")
        print(f"  User ID: {decoded_session['user_id']}")
        print(f"  Login time: {decoded_session['login_time']}")


def security_best_practices():
    """Demonstrate security best practices."""
    print("\n=== Security Best Practices ===")
    
    print("Best practices for secure applications:")
    
    practices = [
        "1. Always hash passwords with salt (bcrypt/scrypt/argon2)",
        "2. Use cryptographically secure random number generation",
        "3. Implement proper session management with expiration",
        "4. Sanitize all user inputs to prevent injection attacks",
        "5. Use HTTPS for all sensitive data transmission",
        "6. Implement rate limiting to prevent abuse",
        "7. Store secrets in environment variables, not code",
        "8. Use JWT tokens for stateless authentication",
        "9. Implement proper error handling (don't leak info)",
        "10. Regular security audits and dependency updates"
    ]
    
    for practice in practices:
        print(f"  {practice}")
    
    # Example secure configuration
    print("\nExample secure configuration:")
    
    secure_config = {
        "password_policy": {
            "min_length": 12,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_numbers": True,
            "require_symbols": True,
            "max_age_days": 90
        },
        "session_config": {
            "timeout_minutes": 30,
            "secure_cookies": True,
            "same_site": "strict",
            "http_only": True
        },
        "rate_limiting": {
            "requests_per_minute": 60,
            "burst_limit": 10,
            "ban_duration_minutes": 15
        },
        "encryption": {
            "algorithm": "AES-256-GCM",
            "key_rotation_days": 30,
            "backup_keys": 3
        }
    }
    
    for category, settings in secure_config.items():
        print(f"\n  {category}:")
        for key, value in settings.items():
            print(f"    {key}: {value}")


def common_vulnerabilities():
    """Demonstrate protection against common vulnerabilities."""
    print("\n=== Common Vulnerabilities and Protection ===")
    
    print("Protection against common attacks:")
    
    # SQL Injection
    print("\n1. SQL Injection Protection:")
    malicious_inputs = [
        "admin'; DROP TABLE users; --",
        "' OR '1'='1' --",
        "'; SELECT password FROM users WHERE username='admin'; --"
    ]
    
    for malicious in malicious_inputs:
        safe_input = sanitize_input(malicious, mode="sql")
        print(f"  Malicious: '{malicious}'")
        print(f"  Sanitized: '{safe_input}'")
    
    # XSS Protection
    print("\n2. Cross-Site Scripting (XSS) Protection:")
    xss_inputs = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src='javascript:alert(\"XSS\")'></iframe>"
    ]
    
    for xss in xss_inputs:
        safe_xss = sanitize_input(xss, mode="html")
        print(f"  XSS attempt: '{xss}'")
        print(f"  Sanitized: '{safe_xss}'")
    
    # Path Traversal Protection
    print("\n3. Path Traversal Protection:")
    path_attacks = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "/etc/shadow",
        "....//....//....//etc/passwd"
    ]
    
    for path in path_attacks:
        safe_path = sanitize_input(path, mode="filename")
        print(f"  Path attack: '{path}'")
        print(f"  Sanitized: '{safe_path}'")


def limitations_and_considerations():
    """Document security limitations and considerations."""
    print("\n=== Security Limitations and Considerations ===")
    
    print("Important security considerations:")
    
    considerations = [
        "1. This toolkit provides basic security utilities, not enterprise-grade security",
        "2. Always use established cryptographic libraries for production systems",
        "3. Security is only as strong as the weakest link in your system",
        "4. Regular security audits and penetration testing are essential",
        "5. Keep all dependencies updated to patch security vulnerabilities",
        "6. Implement defense in depth - multiple layers of security",
        "7. Never store secrets in code or version control",
        "8. Use proper key management systems for production",
        "9. Implement proper logging and monitoring for security events",
        "10. Train developers on secure coding practices"
    ]
    
    for consideration in considerations:
        print(f"  {consideration}")
    
    print("\nLimitations of this toolkit:")
    limitations = [
        "- Basic password hashing (use dedicated libraries like bcrypt for production)",
        "- Simple JWT implementation (consider libraries like PyJWT for advanced features)",
        "- Basic input sanitization (use specialized libraries for complex scenarios)",
        "- No advanced cryptographic features (digital signatures, key exchange, etc.)",
        "- No built-in rate limiting or intrusion detection",
        "- No secure key storage or hardware security module integration"
    ]
    
    for limitation in limitations:
        print(f"  {limitation}")
    
    print("\nRecommended production libraries:")
    recommendations = [
        "- Password hashing: bcrypt, scrypt, argon2",
        "- JWT tokens: PyJWT, python-jose",
        "- Cryptography: cryptography, PyCryptodome",
        "- Input validation: cerberus, marshmallow",
        "- Web security: django-security, flask-security",
        "- Rate limiting: flask-limiter, django-ratelimit"
    ]
    
    for recommendation in recommendations:
        print(f"  {recommendation}")


if __name__ == "__main__":
    """Run all examples."""
    print("Dev QoL Toolkit - Security Utilities Examples")
    print("=" * 55)
    
    password_security_examples()
    token_and_key_generation()
    jwt_token_examples()
    data_hashing_examples()
    input_sanitization_examples()
    encryption_examples()
    api_security_examples()
    security_best_practices()
    common_vulnerabilities()
    limitations_and_considerations()
    
    print("\n" + "=" * 55)
    print("All security utilities examples completed!")
    print("\n⚠️  IMPORTANT: These are basic security utilities.")
    print("   Use established cryptographic libraries for production systems!")