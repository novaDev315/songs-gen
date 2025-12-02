"""Unit tests for admin initialization service.

Tests for creating admin user on first run.
"""

from unittest.mock import AsyncMock, MagicMock, patch, Mock
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.init_admin import create_admin_user, pwd_context
from app.models.user import User


@pytest.mark.unit
@pytest.mark.asyncio
class TestInitAdminService:
    """Test admin initialization functionality."""

    async def test_create_admin_user_when_not_exists(self):
        """Test creating admin user when it doesn't exist."""
        # Create mock session
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # No admin exists
        mock_session.execute.return_value = mock_result

        # Create mock session local that returns our mock session
        mock_session_local = MagicMock()
        mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_local.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch('app.services.init_admin.get_session_local', return_value=mock_session_local):
            with patch('app.services.init_admin.settings') as mock_settings:
                mock_settings.ADMIN_USERNAME = "admin"
                mock_settings.ADMIN_PASSWORD = "testpassword123"

                await create_admin_user()

                # Verify user was added
                mock_session.add.assert_called_once()
                added_user = mock_session.add.call_args[0][0]
                assert isinstance(added_user, User)
                assert added_user.username == "admin"
                assert added_user.role == "admin"
                # Password should be hashed
                assert added_user.password_hash != "testpassword123"
                assert pwd_context.verify("testpassword123", added_user.password_hash)

                # Verify commit was called
                mock_session.commit.assert_called_once()

    async def test_create_admin_user_when_exists(self):
        """Test that admin user is not created if already exists."""
        # Create mock existing admin
        existing_admin = User(
            id=1,
            username="admin",
            password_hash="existing_hash",
            role="admin",
        )

        # Create mock session
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_admin
        mock_session.execute.return_value = mock_result

        mock_session_local = MagicMock()
        mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_local.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch('app.services.init_admin.get_session_local', return_value=mock_session_local):
            with patch('app.services.init_admin.settings') as mock_settings:
                mock_settings.ADMIN_USERNAME = "admin"
                mock_settings.ADMIN_PASSWORD = "testpassword123"

                await create_admin_user()

                # Verify no user was added
                mock_session.add.assert_not_called()
                # Commit should not be called since no changes
                mock_session.commit.assert_not_called()

    async def test_create_admin_user_handles_exception(self):
        """Test that exceptions during admin creation are handled gracefully."""
        # Create mock session that raises an exception
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute.side_effect = Exception("Database connection error")

        mock_session_local = MagicMock()
        mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_local.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch('app.services.init_admin.get_session_local', return_value=mock_session_local):
            with patch('app.services.init_admin.settings') as mock_settings:
                mock_settings.ADMIN_USERNAME = "admin"
                mock_settings.ADMIN_PASSWORD = "testpassword123"

                # Should not raise, just log error
                await create_admin_user()

                # Rollback should be called on error
                mock_session.rollback.assert_called_once()

    async def test_create_admin_user_with_custom_username(self):
        """Test creating admin user with custom username from settings."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        mock_session_local = MagicMock()
        mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_local.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch('app.services.init_admin.get_session_local', return_value=mock_session_local):
            with patch('app.services.init_admin.settings') as mock_settings:
                mock_settings.ADMIN_USERNAME = "superadmin"
                mock_settings.ADMIN_PASSWORD = "securepass456"

                await create_admin_user()

                added_user = mock_session.add.call_args[0][0]
                assert added_user.username == "superadmin"
                assert pwd_context.verify("securepass456", added_user.password_hash)


@pytest.mark.unit
class TestPwdContext:
    """Test password context configuration."""

    def test_password_hashing(self):
        """Test that passwords are properly hashed."""
        password = "testpassword123"
        hashed = pwd_context.hash(password)

        assert hashed != password
        assert pwd_context.verify(password, hashed)
        assert not pwd_context.verify("wrongpassword", hashed)

    def test_password_hashing_uses_bcrypt(self):
        """Test that bcrypt is used for hashing."""
        password = "testpassword"
        hashed = pwd_context.hash(password)

        # Bcrypt hashes start with $2b$
        assert hashed.startswith("$2b$")

    def test_different_passwords_produce_different_hashes(self):
        """Test that different passwords produce different hashes."""
        hash1 = pwd_context.hash("password1")
        hash2 = pwd_context.hash("password2")

        assert hash1 != hash2

    def test_same_password_produces_different_hashes(self):
        """Test that same password produces different hashes (salt)."""
        password = "samepassword"
        hash1 = pwd_context.hash(password)
        hash2 = pwd_context.hash(password)

        # Different hashes due to random salt
        assert hash1 != hash2
        # But both should verify correctly
        assert pwd_context.verify(password, hash1)
        assert pwd_context.verify(password, hash2)
