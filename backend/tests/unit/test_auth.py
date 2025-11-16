"""Unit tests for authentication functionality.

Tests JWT token creation/validation, password hashing, and authentication logic.
"""

import pytest
from datetime import datetime, timedelta
from jose import jwt, JWTError

from app.api.auth import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
)
from app.config import get_settings


# =============================================================================
# Password Hashing Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.auth
class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password_creates_different_hashes(self):
        """Test that same password creates different hashes (due to salt)."""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2
        assert len(hash1) > 0
        assert len(hash2) > 0

    def test_hash_password_bcrypt_format(self):
        """Test that password hash uses bcrypt format."""
        password = "testpassword123"
        hashed = hash_password(password)

        # Bcrypt hashes start with $2b$ and are 60 characters
        assert hashed.startswith("$2b$")
        assert len(hashed) == 60

    def test_verify_password_success(self):
        """Test successful password verification."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """Test failed password verification with wrong password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_string(self):
        """Test password verification with empty string."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password("", hashed) is False

    def test_hash_password_special_characters(self):
        """Test hashing password with special characters."""
        password = "p@$$w0rd!#%&*()_+-={}[]|:;<>?,./"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_hash_password_unicode(self):
        """Test hashing password with unicode characters."""
        password = "пароль密码🔒"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    @pytest.mark.parametrize(
        "password",
        [
            "short",
            "a" * 100,
            "Password123!",
            "12345678",
            "UPPERCASE",
            "lowercase",
            "MixedCase123",
        ],
    )
    def test_hash_password_various_lengths(self, password):
        """Test hashing passwords of various lengths and complexity."""
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True


# =============================================================================
# JWT Access Token Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.auth
class TestAccessToken:
    """Test access token creation and validation."""

    def test_create_access_token_success(self):
        """Test creating a valid access token."""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_payload(self):
        """Test access token contains correct payload."""
        settings = get_settings()
        data = {"sub": "testuser"}
        token = create_access_token(data)

        # Decode without verification for testing
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        assert payload["sub"] == "testuser"
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_create_access_token_expiration(self):
        """Test access token has correct expiration time."""
        settings = get_settings()
        data = {"sub": "testuser"}
        before_creation = datetime.utcnow()
        token = create_access_token(data)
        after_creation = datetime.utcnow()

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_exp_min = before_creation + timedelta(
            minutes=settings.JWT_EXPIRE_MINUTES
        )
        expected_exp_max = after_creation + timedelta(
            minutes=settings.JWT_EXPIRE_MINUTES
        )

        # Expiration should be within the expected range
        assert expected_exp_min <= exp_time <= expected_exp_max

    def test_create_access_token_additional_claims(self):
        """Test access token with additional claims."""
        settings = get_settings()
        data = {"sub": "testuser", "role": "admin", "custom": "value"}
        token = create_access_token(data)

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"
        assert payload["custom"] == "value"

    def test_decode_access_token_success(self):
        """Test decoding a valid access token."""
        settings = get_settings()
        data = {"sub": "testuser"}
        token = create_access_token(data)

        # Should not raise exception
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        assert payload["sub"] == "testuser"

    def test_decode_access_token_invalid_signature(self):
        """Test decoding token with invalid signature fails."""
        settings = get_settings()
        data = {"sub": "testuser"}
        token = create_access_token(data)

        # Modify token to invalidate signature
        parts = token.split(".")
        parts[2] = parts[2][::-1]  # Reverse signature
        invalid_token = ".".join(parts)

        with pytest.raises(JWTError):
            jwt.decode(
                invalid_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )

    def test_decode_access_token_wrong_secret(self):
        """Test decoding token with wrong secret key fails."""
        settings = get_settings()
        data = {"sub": "testuser"}
        token = create_access_token(data)

        with pytest.raises(JWTError):
            jwt.decode(token, "wrong_secret_key", algorithms=[settings.JWT_ALGORITHM])

    def test_decode_expired_access_token(self):
        """Test decoding expired access token fails."""
        settings = get_settings()

        # Create token that expired 1 hour ago
        data = {"sub": "testuser"}
        payload = {
            **data,
            "exp": datetime.utcnow() - timedelta(hours=1),
            "type": "access",
        }
        expired_token = jwt.encode(
            payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

        with pytest.raises(JWTError):
            jwt.decode(
                expired_token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )


# =============================================================================
# JWT Refresh Token Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.auth
class TestRefreshToken:
    """Test refresh token creation and validation."""

    def test_create_refresh_token_success(self):
        """Test creating a valid refresh token."""
        data = {"sub": "testuser"}
        token = create_refresh_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token_payload(self):
        """Test refresh token contains correct payload."""
        settings = get_settings()
        data = {"sub": "testuser"}
        token = create_refresh_token(data)

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        assert payload["sub"] == "testuser"
        assert payload["type"] == "refresh"
        assert "exp" in payload

    def test_create_refresh_token_expiration(self):
        """Test refresh token has longer expiration than access token."""
        settings = get_settings()
        data = {"sub": "testuser"}
        before_creation = datetime.utcnow()
        token = create_refresh_token(data)
        after_creation = datetime.utcnow()

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_exp_min = before_creation + timedelta(
            days=settings.JWT_REFRESH_EXPIRE_DAYS
        )
        expected_exp_max = after_creation + timedelta(
            days=settings.JWT_REFRESH_EXPIRE_DAYS
        )

        # Expiration should be within the expected range (7 days)
        assert expected_exp_min <= exp_time <= expected_exp_max

    def test_refresh_token_longer_than_access_token(self):
        """Test refresh token lifetime is longer than access token."""
        settings = get_settings()
        data = {"sub": "testuser"}

        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)

        access_payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        refresh_payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        access_exp = datetime.fromtimestamp(access_payload["exp"])
        refresh_exp = datetime.fromtimestamp(refresh_payload["exp"])

        # Refresh token should expire much later than access token
        assert refresh_exp > access_exp
        # Should be at least 6 days difference (7 days refresh vs 15 min access)
        assert (refresh_exp - access_exp).days >= 6


# =============================================================================
# Token Type Differentiation Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.auth
class TestTokenTypes:
    """Test differentiation between access and refresh tokens."""

    def test_access_token_has_correct_type(self):
        """Test access token is marked with 'access' type."""
        settings = get_settings()
        data = {"sub": "testuser"}
        token = create_access_token(data)

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        assert payload["type"] == "access"

    def test_refresh_token_has_correct_type(self):
        """Test refresh token is marked with 'refresh' type."""
        settings = get_settings()
        data = {"sub": "testuser"}
        token = create_refresh_token(data)

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        assert payload["type"] == "refresh"

    def test_tokens_are_different(self):
        """Test access and refresh tokens are different."""
        data = {"sub": "testuser"}
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)

        assert access_token != refresh_token


# =============================================================================
# Edge Cases and Security Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.auth
class TestAuthEdgeCases:
    """Test edge cases and security scenarios."""

    def test_empty_username(self):
        """Test token creation with empty username."""
        data = {"sub": ""}
        token = create_access_token(data)

        settings = get_settings()
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        assert payload["sub"] == ""

    def test_special_characters_in_username(self):
        """Test token creation with special characters in username."""
        data = {"sub": "user@example.com"}
        token = create_access_token(data)

        settings = get_settings()
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        assert payload["sub"] == "user@example.com"

    def test_very_long_username(self):
        """Test token creation with very long username."""
        data = {"sub": "a" * 1000}
        token = create_access_token(data)

        settings = get_settings()
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        assert payload["sub"] == "a" * 1000

    def test_null_bytes_in_password(self):
        """Test password hashing with null bytes."""
        # Bcrypt handles null bytes by truncating at first null
        password = "password\x00truncated"
        hashed = hash_password(password)

        # Password up to null byte should work
        assert verify_password("password\x00anything", hashed) is True

    def test_token_tampering_detection(self):
        """Test that tampering with token payload is detected."""
        settings = get_settings()
        data = {"sub": "testuser"}
        token = create_access_token(data)

        # Tamper with payload (change username in middle part)
        parts = token.split(".")
        # This will invalidate the signature
        parts[1] = parts[1][::-1]  # Reverse payload
        tampered_token = ".".join(parts)

        with pytest.raises(JWTError):
            jwt.decode(
                tampered_token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )

    @pytest.mark.parametrize(
        "malformed_token",
        [
            "",
            "not.a.token",
            "only.two",
            "too.many.parts.here.extra",
            "invalid_base64!@#$",
        ],
    )
    def test_malformed_token(self, malformed_token):
        """Test that malformed tokens are rejected."""
        settings = get_settings()

        with pytest.raises((JWTError, Exception)):
            jwt.decode(
                malformed_token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
