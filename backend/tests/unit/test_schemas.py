"""Integration tests for authentication API endpoints.

Tests complete authentication flow including login, token refresh, and logout.
"""

import pytest
from datetime import datetime, timedelta

from app.api.auth import hash_password, create_refresh_token
from app.models.user import User


# =============================================================================
# Authentication Flow Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.api
class TestAuthenticationFlow:
    """Test complete authentication flow."""

    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpassword123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_username(self, client):
        """Test login with invalid username."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "password123"},
        )

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_invalid_password(self, client, test_user):
        """Test login with invalid password."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_validation_errors(self, client):
        """Test login with validation errors."""
        # Username too short
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "ab", "password": "password123"},
        )
        assert response.status_code == 422

        # Password too short
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "12345"},
        )
        assert response.status_code == 422

        # Missing fields
        response = client.post("/api/v1/auth/login", json={"username": "testuser"})
        assert response.status_code == 422

    def test_login_updates_last_login(self, client, test_db, test_user):
        """Test that login updates last_login timestamp."""
        before_login = datetime.utcnow()

        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpassword123"},
        )

        assert response.status_code == 200

        # Refresh user from database
        test_db.refresh(test_user)

        assert test_user.last_login is not None
        assert test_user.last_login >= before_login

    def test_login_stores_refresh_token_hash(self, client, test_db, test_user):
        """Test that login stores refresh token hash."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpassword123"},
        )

        assert response.status_code == 200

        # Refresh user from database
        test_db.refresh(test_user)

        assert test_user.refresh_token_hash is not None
        assert test_user.refresh_token_expires_at is not None


# =============================================================================
# Token Refresh Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.api
class TestTokenRefresh:
    """Test token refresh functionality."""

    def test_refresh_token_success(self, client, test_db, test_user):
        """Test successful token refresh."""
        # First login to get tokens
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpassword123"},
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh tokens
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        # New tokens should be different from originals
        assert data["refresh_token"] != refresh_token

    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )

        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]

    def test_refresh_token_expired(self, client, test_db, test_user):
        """Test refresh with expired token."""
        # Create expired refresh token
        expired_payload = {
            "sub": test_user.username,
            "exp": datetime.utcnow() - timedelta(days=1),
            "type": "refresh",
        }
        from jose import jwt
        from app.config import get_settings

        settings = get_settings()
        expired_token = jwt.encode(
            expired_payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": expired_token},
        )

        assert response.status_code == 401

    def test_refresh_token_wrong_type(self, client, test_user):
        """Test refresh with access token instead of refresh token."""
        # Login to get access token
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpassword123"},
        )
        access_token = login_response.json()["access_token"]

        # Try to use access token for refresh
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token},
        )

        assert response.status_code == 401

    def test_refresh_token_updates_database(self, client, test_db, test_user):
        """Test that refresh updates stored token hash."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpassword123"},
        )
        refresh_token = login_response.json()["refresh_token"]

        test_db.refresh(test_user)
        old_hash = test_user.refresh_token_hash

        # Refresh tokens
        client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        test_db.refresh(test_user)
        new_hash = test_user.refresh_token_hash

        # Hash should be updated
        assert new_hash != old_hash


# =============================================================================
# Protected Endpoint Access Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.api
class TestProtectedEndpointAccess:
    """Test accessing protected endpoints with authentication."""

    def test_get_current_user_success(self, client, auth_headers, test_user):
        """Test getting current user information."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username
        assert data["role"] == test_user.role
        assert "id" in data
        assert "created_at" in data

    def test_get_current_user_no_token(self, client):
        """Test accessing protected endpoint without token."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 403  # FastAPI HTTPBearer returns 403

    def test_get_current_user_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 401

    def test_get_current_user_expired_token(self, client, expired_token):
        """Test accessing protected endpoint with expired token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401

    def test_get_current_user_malformed_header(self, client):
        """Test accessing protected endpoint with malformed auth header."""
        # Missing "Bearer" prefix
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "some_token"},
        )

        assert response.status_code == 403


# =============================================================================
# Logout Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.api
class TestLogout:
    """Test logout functionality."""

    def test_logout_success(self, client, test_db, test_user, auth_headers):
        """Test successful logout."""
        # First login to set refresh token
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpassword123"},
        )

        test_db.refresh(test_user)
        assert test_user.refresh_token_hash is not None

        # Logout
        response = client.post("/api/v1/auth/logout", headers=auth_headers)

        assert response.status_code == 200
        assert "Logged out successfully" in response.json()["message"]

        # Verify refresh token is cleared
        test_db.refresh(test_user)
        assert test_user.refresh_token_hash is None
        assert test_user.refresh_token_expires_at is None

    def test_logout_no_token(self, client):
        """Test logout without authentication."""
        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 403

    def test_logout_invalid_token(self, client):
        """Test logout with invalid token."""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 401

    def test_logout_prevents_refresh(self, client, test_user):
        """Test that logout prevents token refresh."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpassword123"},
        )
        refresh_token = login_response.json()["refresh_token"]
        access_token = login_response.json()["access_token"]

        # Logout
        client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # Try to refresh with old token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        # Should fail because refresh token was invalidated
        assert response.status_code == 401


# =============================================================================
# Role-Based Access Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.api
class TestRoleBasedAccess:
    """Test role-based access control."""

    def test_regular_user_role(self, client, test_user, auth_headers):
        """Test regular user has correct role."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["role"] == "user"

    def test_admin_user_role(self, client, test_admin, admin_auth_headers):
        """Test admin user has correct role."""
        response = client.get("/api/v1/auth/me", headers=admin_auth_headers)

        assert response.status_code == 200
        assert response.json()["role"] == "admin"


# =============================================================================
# Concurrent Authentication Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.api
class TestConcurrentAuthentication:
    """Test concurrent authentication scenarios."""

    def test_multiple_logins_same_user(self, client, test_db, test_user):
        """Test multiple concurrent logins for same user."""
        # First login
        response1 = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpassword123"},
        )
        token1 = response1.json()["refresh_token"]

        # Second login (should invalidate first refresh token)
        response2 = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpassword123"},
        )
        token2 = response2.json()["refresh_token"]

        assert token1 != token2

        # First token should no longer work
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": token1},
        )
        assert response.status_code == 401

        # Second token should work
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": token2},
        )
        assert response.status_code == 200

    def test_login_refresh_logout_flow(self, client, test_user):
        """Test complete flow: login -> refresh -> logout."""
        # 1. Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpassword123"},
        )
        assert login_response.status_code == 200
        access_token1 = login_response.json()["access_token"]
        refresh_token1 = login_response.json()["refresh_token"]

        # 2. Verify access with first token
        me_response1 = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token1}"},
        )
        assert me_response1.status_code == 200

        # 3. Refresh tokens
        refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token1},
        )
        assert refresh_response.status_code == 200
        access_token2 = refresh_response.json()["access_token"]

        # 4. Verify access with new token
        me_response2 = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token2}"},
        )
        assert me_response2.status_code == 200

        # 5. Logout
        logout_response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token2}"},
        )
        assert logout_response.status_code == 200

        # 6. Verify cannot refresh after logout
        refresh_after_logout = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_response.json()["refresh_token"]},
        )
        assert refresh_after_logout.status_code == 401
