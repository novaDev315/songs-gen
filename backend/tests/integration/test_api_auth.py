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
