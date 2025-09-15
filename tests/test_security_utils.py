"""Tests for security_utils module."""

import pytest
import bcrypt
from dev_qol_toolkit.security_utils import hash_password, verify_password


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