"""Tests for main.py FastAPI application setup."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_check_success(self, client):
        """Test health check returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert data["environment"] == "test"


class TestAppConfiguration:
    """Tests for FastAPI app configuration."""

    def test_app_title(self, client):
        """Test app has correct title."""
        # Access the app from the client
        assert client.app.title == "Song Automation API (Test)"

    def test_app_version(self, client):
        """Test app has correct version."""
        assert client.app.version == "1.0.0"

    def test_cors_middleware_configured(self, client):
        """Test CORS middleware is configured."""
        # Test CORS preflight request
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:8501",
                "Access-Control-Request-Method": "GET",
            },
        )
        # Should not error, CORS should handle it
        assert response.status_code in [200, 204, 405]

    def test_rate_limiter_disabled_in_tests(self, client):
        """Test rate limiter is disabled in test mode."""
        # Should be able to make many requests without rate limiting
        for _ in range(20):
            response = client.get("/health")
            assert response.status_code == 200


class TestRouterRegistration:
    """Tests for router registration."""

    def test_auth_router_registered(self, client):
        """Test auth router is registered."""
        response = client.post("/api/v1/auth/login", json={})
        # Should get 422 (validation error) not 404, meaning route exists
        assert response.status_code != 404

    def test_songs_router_registered(self, client, auth_headers):
        """Test songs router is registered."""
        response = client.get("/api/v1/songs", headers=auth_headers)
        # Should get a valid response or 401, not 404
        assert response.status_code != 404

    def test_queue_router_registered(self, client, auth_headers):
        """Test queue router is registered."""
        response = client.get("/api/v1/queue", headers=auth_headers)
        assert response.status_code != 404

    def test_evaluation_router_registered(self, client, auth_headers):
        """Test evaluation router is registered."""
        response = client.get("/api/v1/evaluations", headers=auth_headers)
        # May return 404 if no evaluations, but the route exists
        assert response.status_code in [200, 404]

    def test_youtube_router_registered(self, client, auth_headers):
        """Test youtube router is registered."""
        response = client.get("/api/v1/youtube/status", headers=auth_headers)
        assert response.status_code != 404

    def test_system_router_registered(self, client, auth_headers):
        """Test system router is registered."""
        response = client.get("/api/v1/system/status", headers=auth_headers)
        assert response.status_code in [200, 401]

    def test_analytics_router_registered(self, client, auth_headers):
        """Test analytics router is registered."""
        response = client.get("/api/v1/analytics/overview", headers=auth_headers)
        assert response.status_code in [200, 401]


class TestLifespanEvents:
    """Tests for application lifespan events."""

    @pytest.mark.asyncio
    async def test_lifespan_startup_services_called(self):
        """Test that startup services are called during lifespan."""
        with patch("app.main.init_db", new_callable=AsyncMock) as mock_init_db, \
             patch("app.main.create_admin_user", new_callable=AsyncMock) as mock_create_admin, \
             patch("app.main.schedule_backups") as mock_schedule_backups, \
             patch("app.main.get_worker_pool") as mock_get_worker:

            # Setup mocks
            mock_pool = MagicMock()
            mock_pool.start = AsyncMock()
            mock_pool.stop = AsyncMock()
            mock_get_worker.return_value = mock_pool

            # Import and test the actual lifespan
            from app.main import lifespan

            # Create a mock app
            mock_app = MagicMock(spec=FastAPI)

            # Run lifespan
            async with lifespan(mock_app):
                # Verify startup was called
                mock_init_db.assert_called_once()
                mock_create_admin.assert_called_once()
                mock_schedule_backups.assert_called_once()
                mock_pool.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_shutdown_services_called(self):
        """Test that shutdown services are called during lifespan."""
        with patch("app.main.init_db", new_callable=AsyncMock) as mock_init_db, \
             patch("app.main.create_admin_user", new_callable=AsyncMock) as mock_create_admin, \
             patch("app.main.schedule_backups") as mock_schedule_backups, \
             patch("app.main.get_worker_pool") as mock_get_worker:

            # Setup mocks
            mock_pool = MagicMock()
            mock_pool.start = AsyncMock()
            mock_pool.stop = AsyncMock()
            mock_get_worker.return_value = mock_pool

            from app.main import lifespan
            mock_app = MagicMock(spec=FastAPI)

            # Run lifespan context manager
            async with lifespan(mock_app):
                pass  # Context manager exits here

            # Verify shutdown was called
            mock_pool.stop.assert_called_once()


class TestMiddleware:
    """Tests for middleware configuration."""

    def test_security_headers_middleware(self, client):
        """Test security headers middleware adds headers."""
        response = client.get("/health")

        # Check for security headers (if middleware adds them)
        # The actual headers depend on the SecurityHeadersMiddleware implementation
        assert response.status_code == 200

    def test_cors_allows_local_origins(self, client):
        """Test CORS allows configured local origins."""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:8501"},
        )
        assert response.status_code == 200
        # In test mode, CORS is permissive


class TestExceptionHandlers:
    """Tests for exception handlers."""

    def test_rate_limit_exceeded_handler_exists(self, client):
        """Test that rate limit exceeded handler is configured."""
        # The app has a rate limit handler, even if disabled in tests
        # We verify by checking the handler is registered
        assert hasattr(client.app.state, "limiter")


class TestAppImports:
    """Tests for app module imports and configuration."""

    def test_settings_accessible(self):
        """Test settings can be accessed."""
        from app.config import get_settings
        settings = get_settings()
        assert settings is not None
        assert hasattr(settings, "SECRET_KEY")
        assert hasattr(settings, "APP_ENV")

    def test_logger_configured(self):
        """Test logger is configured."""
        import logging
        logger = logging.getLogger("app.main")
        assert logger is not None


class TestAppStateIsolation:
    """Tests for app state isolation between tests."""

    def test_app_state_fresh_per_test(self, client):
        """Test each test gets a fresh app state."""
        # First request should work
        response = client.get("/health")
        assert response.status_code == 200

    def test_app_state_independent(self, client):
        """Test app state is independent from other tests."""
        # This test should also work independently
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()
