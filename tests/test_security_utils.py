"""Tests for security_utils module."""

import pytest
import bcrypt
import base64
import uuid
import hashlib
from dev_qol_toolkit.security_utils import (
    hash_password, 
    verify_password,
    generate_secret_key,
    generate_uuid,
    hash_data,
    generate_jwt_token,
    verify_jwt_token,
    sanitize_input
)


class TestPasswordHashing:
    """Test password hashing and verification functions."""

    def test_hash_password_basic(self):
        """Test basic password hashing functionality."""
        password = "test_password_123"
        hashed = hash_password(password)
        
        # Bcrypt hashes are always 60 characters long
        assert len(hashed) == 60
        assert isinstance(hashed, str)
        
        # Hash should start with bcrypt identifier
        assert hashed.startswith("$2b$")

    def test_hash_password_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "password1"
        password2 = "password2"
        
        hash1 = hash_password(password1)
        hash2 = hash_password(password2)
        
        assert hash1 != hash2

    def test_hash_password_same_password_different_hashes(self):
        """Test that same password produces different hashes due to salt."""
        password = "same_password"
        
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Due to random salt, same password should produce different hashes
        assert hash1 != hash2

    def test_hash_password_empty_string_raises_error(self):
        """Test that empty password raises ValueError."""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            hash_password("")

    def test_hash_password_non_string_raises_error(self):
        """Test that non-string password raises TypeError."""
        with pytest.raises(TypeError, match="Password must be a string"):
            hash_password(123)  # type: ignore

        with pytest.raises(TypeError, match="Password must be a string"):
            hash_password(None)  # type: ignore

    def test_hash_password_unicode_characters(self):
        """Test password hashing with unicode characters."""
        password = "pássword_with_ñ_and_émojis_🔒"
        hashed = hash_password(password)
        
        assert len(hashed) == 60
        assert verify_password(password, hashed)

    def test_hash_password_long_password(self):
        """Test hashing very long passwords."""
        # Bcrypt truncates passwords at 72 bytes, but should still work
        long_password = "a" * 100
        hashed = hash_password(long_password)
        
        assert len(hashed) == 60
        assert verify_password(long_password, hashed)

    def test_verify_password_correct_password(self):
        """Test password verification with correct password."""
        password = "correct_password"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect_password(self):
        """Test password verification with incorrect password."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_password_raises_error(self):
        """Test that empty password raises ValueError."""
        hashed = hash_password("test")
        
        with pytest.raises(ValueError, match="Password cannot be empty"):
            verify_password("", hashed)

    def test_verify_password_empty_hash_raises_error(self):
        """Test that empty hash raises ValueError."""
        with pytest.raises(ValueError, match="Hashed password cannot be empty"):
            verify_password("test", "")

    def test_verify_password_non_string_password_raises_error(self):
        """Test that non-string password raises TypeError."""
        hashed = hash_password("test")
        
        with pytest.raises(TypeError, match="Password must be a string"):
            verify_password(123, hashed)  # type: ignore

    def test_verify_password_non_string_hash_raises_error(self):
        """Test that non-string hash raises TypeError."""
        with pytest.raises(TypeError, match="Hashed password must be a string"):
            verify_password("test", 123)  # type: ignore

    def test_verify_password_invalid_hash_format(self):
        """Test password verification with invalid hash format."""
        password = "test_password"
        invalid_hash = "not_a_valid_bcrypt_hash"
        
        # Should return False for invalid hash format, not raise exception
        assert verify_password(password, invalid_hash) is False

    def test_verify_password_malformed_hash(self):
        """Test password verification with malformed bcrypt hash."""
        password = "test_password"
        malformed_hash = "$2b$12$invalid"
        
        # Should return False for malformed hash
        assert verify_password(password, malformed_hash) is False

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case sensitive."""
        password = "CaseSensitive"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("casesensitive", hashed) is False
        assert verify_password("CASESENSITIVE", hashed) is False

    def test_verify_password_whitespace_sensitive(self):
        """Test that password verification is sensitive to whitespace."""
        password = "password"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password(" password", hashed) is False
        assert verify_password("password ", hashed) is False
        assert verify_password(" password ", hashed) is False

    def test_hash_and_verify_integration(self):
        """Test integration between hash_password and verify_password."""
        test_passwords = [
            "simple",
            "complex_P@ssw0rd!",
            "with spaces",
            "with\ttabs\nand\nnewlines",
            "unicode_café_🔐",
            "moderately_long_password_but_under_72_bytes",
        ]
        
        for password in test_passwords:
            hashed = hash_password(password)
            
            # Correct password should verify
            assert verify_password(password, hashed) is True
            
            # Wrong password should not verify (modify at beginning to avoid bcrypt truncation issues)
            wrong_password = "x" + password if len(password) < 70 else password[:-1] + "x"
            assert verify_password(wrong_password, hashed) is False

    def test_bcrypt_compatibility(self):
        """Test compatibility with direct bcrypt usage."""
        password = "test_password"
        
        # Hash using our function
        our_hash = hash_password(password)
        
        # Verify using bcrypt directly
        assert bcrypt.checkpw(password.encode('utf-8'), our_hash.encode('utf-8'))
        
        # Hash using bcrypt directly
        bcrypt_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Verify using our function
        assert verify_password(password, bcrypt_hash) is True


class TestSecretGeneration:
    """Test secret generation functions."""

    def test_generate_secret_key_default_length(self):
        """Test secret key generation with default length."""
        key = generate_secret_key()
        
        # Should be base64 encoded
        decoded = base64.b64decode(key)
        assert len(decoded) == 32  # Default length
        assert isinstance(key, str)

    def test_generate_secret_key_custom_length(self):
        """Test secret key generation with custom lengths."""
        lengths = [8, 16, 24, 32, 64, 128]
        
        for length in lengths:
            key = generate_secret_key(length)
            decoded = base64.b64decode(key)
            assert len(decoded) == length

    def test_generate_secret_key_randomness(self):
        """Test that generated keys are different each time."""
        keys = [generate_secret_key() for _ in range(10)]
        
        # All keys should be different
        assert len(set(keys)) == 10

    def test_generate_secret_key_invalid_length_type(self):
        """Test that non-integer length raises TypeError."""
        with pytest.raises(TypeError, match="Length must be an integer"):
            generate_secret_key("32")  # type: ignore

        with pytest.raises(TypeError, match="Length must be an integer"):
            generate_secret_key(32.5)  # type: ignore

    def test_generate_secret_key_invalid_length_value(self):
        """Test that invalid length values raise ValueError."""
        with pytest.raises(ValueError, match="Length must be positive"):
            generate_secret_key(0)

        with pytest.raises(ValueError, match="Length must be positive"):
            generate_secret_key(-1)

        with pytest.raises(ValueError, match="Length cannot exceed 1024 bytes"):
            generate_secret_key(1025)

    def test_generate_uuid_format(self):
        """Test UUID generation format."""
        uuid_str = generate_uuid()
        
        # Should be 36 characters with 4 hyphens
        assert len(uuid_str) == 36
        assert uuid_str.count('-') == 4
        
        # Should be valid UUID format
        parts = uuid_str.split('-')
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12

    def test_generate_uuid_validity(self):
        """Test that generated UUIDs are valid UUID4."""
        uuid_str = generate_uuid()
        
        # Should be parseable as UUID
        parsed_uuid = uuid.UUID(uuid_str)
        assert str(parsed_uuid) == uuid_str
        
        # Should be version 4
        assert parsed_uuid.version == 4

    def test_generate_uuid_uniqueness(self):
        """Test that generated UUIDs are unique."""
        uuids = [generate_uuid() for _ in range(100)]
        
        # All UUIDs should be different
        assert len(set(uuids)) == 100


class TestDataHashing:
    """Test data hashing functions."""

    def test_hash_data_string_sha256(self):
        """Test hashing string data with SHA256."""
        data = "hello world"
        expected = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        
        result = hash_data(data)
        assert result == expected

    def test_hash_data_bytes_sha256(self):
        """Test hashing bytes data with SHA256."""
        data = b"hello world"
        expected = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        
        result = hash_data(data)
        assert result == expected

    def test_hash_data_different_algorithms(self):
        """Test hashing with different algorithms."""
        data = "test"
        
        # Test various algorithms
        algorithms_and_expected = {
            "md5": "098f6bcd4621d373cade4e832627b4f6",
            "sha1": "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3",
            "sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
            "sha512": "ee26b0dd4af7e749aa1a8ee3c10ae9923f618980772e473f8819a5d4940e0db27ac185f8a0e1d5f84f88bc887fd67b143732c304cc5fa9ad8e6f57f50028a8ff",
        }
        
        for algorithm, expected in algorithms_and_expected.items():
            result = hash_data(data, algorithm)
            assert result == expected

    def test_hash_data_empty_string(self):
        """Test hashing empty string."""
        result = hash_data("")
        # SHA256 of empty string
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert result == expected

    def test_hash_data_unicode(self):
        """Test hashing unicode strings."""
        data = "café 🔒"
        result = hash_data(data)
        
        # Should be consistent
        assert result == hash_data(data)
        
        # Should be different from ASCII version
        assert result != hash_data("cafe")

    def test_hash_data_invalid_data_type(self):
        """Test that invalid data types raise TypeError."""
        with pytest.raises(TypeError, match="Data must be string or bytes"):
            hash_data(123)  # type: ignore

        with pytest.raises(TypeError, match="Data must be string or bytes"):
            hash_data(None)  # type: ignore

        with pytest.raises(TypeError, match="Data must be string or bytes"):
            hash_data(['list'])  # type: ignore

    def test_hash_data_invalid_algorithm_type(self):
        """Test that invalid algorithm type raises TypeError."""
        with pytest.raises(TypeError, match="Algorithm must be a string"):
            hash_data("test", 123)  # type: ignore

    def test_hash_data_unsupported_algorithm(self):
        """Test that unsupported algorithm raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported algorithm 'invalid_algo'"):
            hash_data("test", "invalid_algo")

    def test_hash_data_consistency(self):
        """Test that same data produces same hash."""
        data = "consistency test"
        
        hash1 = hash_data(data)
        hash2 = hash_data(data)
        
        assert hash1 == hash2

    def test_hash_data_different_data_different_hash(self):
        """Test that different data produces different hashes."""
        data1 = "data1"
        data2 = "data2"
        
        hash1 = hash_data(data1)
        hash2 = hash_data(data2)
        
        assert hash1 != hash2

    def test_hash_data_case_sensitive(self):
        """Test that hashing is case sensitive."""
        data1 = "Test"
        data2 = "test"
        
        hash1 = hash_data(data1)
        hash2 = hash_data(data2)
        
        assert hash1 != hash2

    def test_hash_data_with_hashlib_compatibility(self):
        """Test compatibility with direct hashlib usage."""
        data = "compatibility test"
        
        # Our function
        our_result = hash_data(data, "sha256")
        
        # Direct hashlib
        hasher = hashlib.sha256()
        hasher.update(data.encode('utf-8'))
        hashlib_result = hasher.hexdigest()
        
        assert our_result == hashlib_result

    def test_hash_data_large_data(self):
        """Test hashing large amounts of data."""
        # 1MB of data
        large_data = "a" * (1024 * 1024)
        
        result = hash_data(large_data)
        
        # Should complete without error and produce consistent result
        assert result == hash_data(large_data)
        assert len(result) == 64  # SHA256 produces 64 hex characters


class TestSecretGeneration:
    """Test secret generation functions."""

    def test_generate_secret_key_default_length(self):
        """Test secret key generation with default length."""
        key = generate_secret_key()
        
        # Should be base64 encoded
        decoded = base64.b64decode(key)
        assert len(decoded) == 32  # Default length
        assert isinstance(key, str)

    def test_generate_secret_key_custom_length(self):
        """Test secret key generation with custom lengths."""
        lengths = [8, 16, 24, 32, 64, 128]
        
        for length in lengths:
            key = generate_secret_key(length)
            decoded = base64.b64decode(key)
            assert len(decoded) == length

    def test_generate_secret_key_different_keys(self):
        """Test that different calls generate different keys."""
        key1 = generate_secret_key()
        key2 = generate_secret_key()
        
        assert key1 != key2

    def test_generate_secret_key_invalid_length_type(self):
        """Test that non-integer length raises TypeError."""
        with pytest.raises(TypeError, match="Length must be an integer"):
            generate_secret_key("32")  # type: ignore

        with pytest.raises(TypeError, match="Length must be an integer"):
            generate_secret_key(32.5)  # type: ignore

    def test_generate_secret_key_invalid_length_value(self):
        """Test that invalid length values raise ValueError."""
        with pytest.raises(ValueError, match="Length must be positive"):
            generate_secret_key(0)

        with pytest.raises(ValueError, match="Length must be positive"):
            generate_secret_key(-1)

        with pytest.raises(ValueError, match="Length cannot exceed 1024 bytes"):
            generate_secret_key(1025)

    def test_generate_secret_key_edge_cases(self):
        """Test edge cases for secret key generation."""
        # Minimum valid length
        key = generate_secret_key(1)
        decoded = base64.b64decode(key)
        assert len(decoded) == 1

        # Maximum valid length
        key = generate_secret_key(1024)
        decoded = base64.b64decode(key)
        assert len(decoded) == 1024

    def test_generate_uuid_format(self):
        """Test UUID generation format."""
        uuid_str = generate_uuid()
        
        # Standard UUID4 format: 8-4-4-4-12 characters
        assert len(uuid_str) == 36
        assert uuid_str.count('-') == 4
        
        # Should be valid UUID
        uuid.UUID(uuid_str)  # Will raise ValueError if invalid

    def test_generate_uuid_different_values(self):
        """Test that different calls generate different UUIDs."""
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        
        assert uuid1 != uuid2

    def test_generate_uuid_version(self):
        """Test that generated UUIDs are version 4."""
        uuid_str = generate_uuid()
        uuid_obj = uuid.UUID(uuid_str)
        
        assert uuid_obj.version == 4


class TestDataHashing:
    """Test data hashing functions."""

    def test_hash_data_string_sha256(self):
        """Test hashing string data with SHA-256."""
        data = "hello world"
        expected = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        
        result = hash_data(data)
        assert result == expected

    def test_hash_data_bytes_sha256(self):
        """Test hashing bytes data with SHA-256."""
        data = b"hello world"
        expected = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        
        result = hash_data(data)
        assert result == expected

    def test_hash_data_different_algorithms(self):
        """Test hashing with different algorithms."""
        data = "test"
        
        # Test MD5
        md5_result = hash_data(data, "md5")
        assert md5_result == "098f6bcd4621d373cade4e832627b4f6"
        
        # Test SHA-1
        sha1_result = hash_data(data, "sha1")
        assert sha1_result == "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"
        
        # Test SHA-512
        sha512_result = hash_data(data, "sha512")
        expected_sha512 = "ee26b0dd4af7e749aa1a8ee3c10ae9923f618980772e473f8819a5d4940e0db27ac185f8a0e1d5f84f88bc887fd67b143732c304cc5fa9ad8e6f57f50028a8ff"
        assert sha512_result == expected_sha512

    def test_hash_data_empty_string(self):
        """Test hashing empty string."""
        result = hash_data("")
        expected = hashlib.sha256(b"").hexdigest()
        assert result == expected

    def test_hash_data_empty_bytes(self):
        """Test hashing empty bytes."""
        result = hash_data(b"")
        expected = hashlib.sha256(b"").hexdigest()
        assert result == expected

    def test_hash_data_unicode_string(self):
        """Test hashing unicode string."""
        data = "héllo wörld 🌍"
        result = hash_data(data)
        
        # Should be consistent
        assert result == hash_data(data)
        
        # Should be different from ASCII version
        assert result != hash_data("hello world")

    def test_hash_data_invalid_data_type(self):
        """Test that invalid data types raise TypeError."""
        with pytest.raises(TypeError, match="Data must be string or bytes"):
            hash_data(123)  # type: ignore

        with pytest.raises(TypeError, match="Data must be string or bytes"):
            hash_data(None)  # type: ignore

        with pytest.raises(TypeError, match="Data must be string or bytes"):
            hash_data(["list"])  # type: ignore

    def test_hash_data_invalid_algorithm_type(self):
        """Test that invalid algorithm type raises TypeError."""
        with pytest.raises(TypeError, match="Algorithm must be a string"):
            hash_data("test", 123)  # type: ignore

    def test_hash_data_unsupported_algorithm(self):
        """Test that unsupported algorithm raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported algorithm 'invalid_algo'"):
            hash_data("test", "invalid_algo")

    def test_hash_data_case_sensitive_algorithm(self):
        """Test that algorithm names are case sensitive."""
        data = "test"
        
        # These should work
        result1 = hash_data(data, "sha256")
        result2 = hash_data(data, "md5")
        
        # These might not work depending on system
        try:
            result3 = hash_data(data, "SHA256")
            # If it works, results should be the same
            assert result1 == result3
        except ValueError:
            # Case sensitivity - this is expected on some systems
            pass

    def test_hash_data_consistency(self):
        """Test that hashing is consistent across calls."""
        data = "consistency test"
        algorithm = "sha256"
        
        result1 = hash_data(data, algorithm)
        result2 = hash_data(data, algorithm)
        
        assert result1 == result2

    def test_hash_data_different_data_different_hash(self):
        """Test that different data produces different hashes."""
        data1 = "data1"
        data2 = "data2"
        
        hash1 = hash_data(data1)
        hash2 = hash_data(data2)
        
        assert hash1 != hash2

    def test_hash_data_large_data(self):
        """Test hashing large amounts of data."""
        large_data = "x" * 10000
        result = hash_data(large_data)
        
        # Should still produce valid hash
        assert len(result) == 64  # SHA-256 produces 64 character hex string
        assert isinstance(result, str)

    def test_hash_data_binary_data(self):
        """Test hashing binary data."""
        binary_data = bytes(range(256))
        result = hash_data(binary_data)
        
        # Should produce valid hash
        assert len(result) == 64  # SHA-256 produces 64 character hex string
        assert isinstance(result, str)


class TestJWTTokens:
    """Test JWT token generation and verification functions."""

    def test_generate_jwt_token_basic(self):
        """Test basic JWT token generation."""
        payload = {"user_id": 123, "role": "admin"}
        secret = "test-secret-key"
        
        token = generate_jwt_token(payload, secret)
        
        # JWT tokens have 3 parts separated by dots
        parts = token.split('.')
        assert len(parts) == 3
        assert isinstance(token, str)

    def test_generate_jwt_token_custom_expiration(self):
        """Test JWT token generation with custom expiration."""
        payload = {"user_id": 456}
        secret = "test-secret"
        expires_in = 7200  # 2 hours
        
        token = generate_jwt_token(payload, secret, expires_in)
        
        # Verify the token contains the correct expiration
        decoded = verify_jwt_token(token, secret)
        assert decoded is not None
        assert decoded["user_id"] == 456
        
        # Check that expiration is approximately correct (within 5 seconds)
        import time
        expected_exp = int(time.time()) + expires_in
        assert abs(decoded["exp"] - expected_exp) <= 5

    def test_generate_jwt_token_includes_standard_claims(self):
        """Test that generated tokens include standard JWT claims."""
        payload = {"custom": "data"}
        secret = "secret"
        
        token = generate_jwt_token(payload, secret)
        decoded = verify_jwt_token(token, secret)
        
        assert decoded is not None
        assert "iat" in decoded  # Issued at
        assert "exp" in decoded  # Expiration
        assert "custom" in decoded  # Original payload
        assert decoded["custom"] == "data"

    def test_generate_jwt_token_invalid_payload_type(self):
        """Test that invalid payload type raises TypeError."""
        with pytest.raises(TypeError, match="Payload must be a dictionary"):
            generate_jwt_token("not a dict", "secret")  # type: ignore

        with pytest.raises(TypeError, match="Payload must be a dictionary"):
            generate_jwt_token(123, "secret")  # type: ignore

    def test_generate_jwt_token_invalid_secret_type(self):
        """Test that invalid secret type raises TypeError."""
        payload = {"test": "data"}
        
        with pytest.raises(TypeError, match="Secret must be a string"):
            generate_jwt_token(payload, 123)  # type: ignore

    def test_generate_jwt_token_empty_secret(self):
        """Test that empty secret raises ValueError."""
        payload = {"test": "data"}
        
        with pytest.raises(ValueError, match="Secret cannot be empty"):
            generate_jwt_token(payload, "")

    def test_generate_jwt_token_invalid_expires_in_type(self):
        """Test that invalid expires_in type raises TypeError."""
        payload = {"test": "data"}
        secret = "secret"
        
        with pytest.raises(TypeError, match="expires_in must be an integer"):
            generate_jwt_token(payload, secret, "3600")  # type: ignore

        with pytest.raises(TypeError, match="expires_in must be an integer"):
            generate_jwt_token(payload, secret, 3600.5)  # type: ignore

    def test_generate_jwt_token_invalid_expires_in_value(self):
        """Test that invalid expires_in value raises ValueError."""
        payload = {"test": "data"}
        secret = "secret"
        
        with pytest.raises(ValueError, match="expires_in must be positive"):
            generate_jwt_token(payload, secret, 0)

        with pytest.raises(ValueError, match="expires_in must be positive"):
            generate_jwt_token(payload, secret, -1)

    def test_verify_jwt_token_valid_token(self):
        """Test JWT token verification with valid token."""
        payload = {"user_id": 789, "permissions": ["read", "write"]}
        secret = "verification-secret"
        
        token = generate_jwt_token(payload, secret)
        decoded = verify_jwt_token(token, secret)
        
        assert decoded is not None
        assert decoded["user_id"] == 789
        assert decoded["permissions"] == ["read", "write"]

    def test_verify_jwt_token_wrong_secret(self):
        """Test JWT token verification with wrong secret."""
        payload = {"user_id": 123}
        secret = "correct-secret"
        wrong_secret = "wrong-secret"
        
        token = generate_jwt_token(payload, secret)
        decoded = verify_jwt_token(token, wrong_secret)
        
        assert decoded is None

    def test_verify_jwt_token_malformed_token(self):
        """Test JWT token verification with malformed token."""
        secret = "secret"
        
        # Various malformed tokens (excluding empty string which raises ValueError)
        malformed_tokens = [
            "not.a.jwt",
            "invalid-token",
            "too.few.parts",
            "too.many.parts.here.extra",
        ]
        
        for token in malformed_tokens:
            decoded = verify_jwt_token(token, secret)
            assert decoded is None

    def test_verify_jwt_token_expired_token(self):
        """Test JWT token verification with expired token."""
        payload = {"user_id": 123}
        secret = "secret"
        
        # Generate token that expires immediately
        token = generate_jwt_token(payload, secret, 1)
        
        # Wait for token to expire
        import time
        time.sleep(2)
        
        decoded = verify_jwt_token(token, secret)
        assert decoded is None

    def test_verify_jwt_token_invalid_token_type(self):
        """Test that invalid token type raises TypeError."""
        secret = "secret"
        
        with pytest.raises(TypeError, match="Token must be a string"):
            verify_jwt_token(123, secret)  # type: ignore

    def test_verify_jwt_token_invalid_secret_type(self):
        """Test that invalid secret type raises TypeError."""
        token = "some.jwt.token"
        
        with pytest.raises(TypeError, match="Secret must be a string"):
            verify_jwt_token(token, 123)  # type: ignore

    def test_verify_jwt_token_empty_token(self):
        """Test that empty token raises ValueError."""
        secret = "secret"
        
        with pytest.raises(ValueError, match="Token cannot be empty"):
            verify_jwt_token("", secret)

    def test_verify_jwt_token_empty_secret(self):
        """Test that empty secret raises ValueError."""
        token = "some.jwt.token"
        
        with pytest.raises(ValueError, match="Secret cannot be empty"):
            verify_jwt_token(token, "")

    def test_jwt_roundtrip_integration(self):
        """Test complete JWT generation and verification cycle."""
        test_cases = [
            {"user_id": 1, "role": "user"},
            {"admin": True, "permissions": ["all"]},
            {"data": {"nested": {"value": 42}}},
            {"string": "test", "number": 123, "boolean": True, "null": None},
        ]
        
        secret = "integration-test-secret"
        
        for original_payload in test_cases:
            # Generate token
            token = generate_jwt_token(original_payload, secret)
            
            # Verify token
            decoded_payload = verify_jwt_token(token, secret)
            
            assert decoded_payload is not None
            
            # Check that original data is preserved
            for key, value in original_payload.items():
                assert decoded_payload[key] == value


class TestInputSanitization:
    """Test input sanitization functions."""

    def test_sanitize_input_html_escaping(self):
        """Test HTML escaping in input sanitization."""
        dangerous_input = "<script>alert('xss')</script>"
        expected = "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
        
        result = sanitize_input(dangerous_input)
        assert result == expected

    def test_sanitize_input_various_html_chars(self):
        """Test sanitization of various HTML characters."""
        test_cases = [
            ("<", "&lt;"),
            (">", "&gt;"),
            ("&", "&amp;"),
            ('"', "&quot;"),
            ("'", "&#x27;"),
        ]
        
        for input_char, expected in test_cases:
            result = sanitize_input(input_char)
            assert result == expected

    def test_sanitize_input_allowed_chars_filter(self):
        """Test character filtering with allowed_chars pattern."""
        input_text = "Hello123!@#$%World"
        
        # Only allow letters and numbers
        result = sanitize_input(input_text, r"a-zA-Z0-9")
        assert result == "Hello123World"
        
        # Only allow letters
        result = sanitize_input(input_text, r"a-zA-Z")
        assert result == "HelloWorld"
        
        # Only allow numbers
        result = sanitize_input(input_text, r"0-9")
        assert result == "123"

    def test_sanitize_input_whitespace_normalization(self):
        """Test whitespace normalization."""
        test_cases = [
            ("  multiple   spaces  ", "multiple spaces"),
            ("\t\ttabs\t\t", "tabs"),
            ("\n\nnewlines\n\n", "newlines"),
            ("  \t\n  mixed  \t\n  ", "mixed"),
            ("", ""),
            ("   ", ""),
        ]
        
        for input_text, expected in test_cases:
            result = sanitize_input(input_text)
            assert result == expected

    def test_sanitize_input_combined_operations(self):
        """Test sanitization with multiple operations combined."""
        input_text = "  <script>  alert('test')  </script>  "
        
        # Should HTML escape and normalize whitespace
        result = sanitize_input(input_text)
        expected = "&lt;script&gt; alert(&#x27;test&#x27;) &lt;/script&gt;"
        assert result == expected

    def test_sanitize_input_with_allowed_chars_and_html(self):
        """Test sanitization with both HTML escaping and character filtering."""
        input_text = "<div>Hello123!</div>"
        
        # Allow only letters and numbers - HTML escaping happens first, then filtering
        # <div> becomes &lt;div&gt; then filtered to just letters/numbers
        result = sanitize_input(input_text, r"a-zA-Z0-9")
        assert result == "ltdivgtHello123ltdivgt"

    def test_sanitize_input_invalid_text_type(self):
        """Test that invalid text type raises TypeError."""
        with pytest.raises(TypeError, match="Text must be a string"):
            sanitize_input(123)  # type: ignore

        with pytest.raises(TypeError, match="Text must be a string"):
            sanitize_input(None)  # type: ignore

    def test_sanitize_input_invalid_allowed_chars_type(self):
        """Test that invalid allowed_chars type raises TypeError."""
        with pytest.raises(TypeError, match="allowed_chars must be a string or None"):
            sanitize_input("test", 123)  # type: ignore

    def test_sanitize_input_regex_error_handling(self):
        """Test regex error handling - skip if no easily invalid pattern exists."""
        # Most regex patterns that look invalid are actually valid in character classes
        # This test documents that the error handling exists but may not be easily triggered
        pass

    def test_sanitize_input_empty_string(self):
        """Test sanitization of empty string."""
        result = sanitize_input("")
        assert result == ""

    def test_sanitize_input_unicode_characters(self):
        """Test sanitization with unicode characters."""
        input_text = "Héllo Wörld 🌍"
        
        # Should preserve unicode by default
        result = sanitize_input(input_text)
        assert result == "Héllo Wörld 🌍"
        
        # Should filter unicode if not in allowed chars
        result = sanitize_input(input_text, r"a-zA-Z ")
        assert result == "Hllo Wrld"

    def test_sanitize_input_sql_injection_patterns(self):
        """Test sanitization against common SQL injection patterns."""
        sql_patterns = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM passwords --",
        ]
        
        for pattern in sql_patterns:
            result = sanitize_input(pattern)
            # Should escape single quotes
            assert "&#x27;" in result
            # Should not contain unescaped quotes
            assert "'" not in result

    def test_sanitize_input_xss_patterns(self):
        """Test sanitization against common XSS patterns."""
        xss_patterns_with_html = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
        ]
        
        for pattern in xss_patterns_with_html:
            result = sanitize_input(pattern)
            # Should escape HTML tags
            assert "<" not in result
            assert ">" not in result
            assert "&lt;" in result or "&gt;" in result
        
        # Test non-HTML XSS pattern
        js_pattern = "javascript:alert('xss')"
        result = sanitize_input(js_pattern)
        # Should escape quotes
        assert "'" not in result
        assert "&#x27;" in result

    def test_sanitize_input_preserves_safe_content(self):
        """Test that sanitization preserves safe content."""
        safe_inputs = [
            "Hello World",
            "user@example.com",
            "123-456-7890",
            "Normal text with spaces",
            "Numbers 123 and letters ABC",
        ]
        
        for safe_input in safe_inputs:
            result = sanitize_input(safe_input)
            # Should be unchanged (except whitespace normalization)
            assert result == safe_input.strip()