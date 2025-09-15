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
    hash_data
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