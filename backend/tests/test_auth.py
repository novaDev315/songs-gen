    )

    assert response.status_code == 401


def test_refresh_token(client: TestClient, test_user: User):
    """Test token refresh flow."""
    # Login first
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "testpassword123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    # Refresh token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    # New refresh token should be different (always regenerated)
    assert data["refresh_token"] != refresh_token


def test_refresh_token_invalid(client: TestClient):
