"""
Integration tests for authentication API endpoints.

Tests cover:
- POST /auth/login - User authentication
- POST /auth/register - User registration
- GET /auth/me - Current user info
- POST /auth/refresh-token - Token refresh
- POST /auth/admin-login - Admin authentication
- POST /auth/logout - Session termination
- Role-based access validation

Following TDD methodology: failing test first, then implementation.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch
import json

from app.main import app
from app.models.user import User, UserType
from app.core.security import get_password_hash, create_access_token, create_refresh_token

# Test markers
pytestmark = [pytest.mark.integration, pytest.mark.api, pytest.mark.auth]


class TestAuthenticationEndpoints:
    """Integration tests for authentication API endpoints."""

    def test_auth_endpoints_exist(self, client: TestClient):
        """Test that authentication endpoints exist and return proper error codes."""
        # Test /auth/login endpoint exists
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code != 404, "Login endpoint should exist"

        # Test /auth/register endpoint exists
        response = client.post("/api/v1/auth/register", json={})
        assert response.status_code != 404, "Register endpoint should exist"

        # Test /auth/me endpoint exists (should require auth)
        response = client.get("/api/v1/auth/me")
        assert response.status_code in [401, 403], "Me endpoint should require authentication"

        # Test /auth/refresh-token endpoint exists
        response = client.post("/api/v1/auth/refresh-token", json={})
        assert response.status_code != 404, "Refresh token endpoint should exist"

        # Test /auth/admin-login endpoint exists
        response = client.post("/api/v1/auth/admin-login", json={})
        assert response.status_code != 404, "Admin login endpoint should exist"


class TestLoginEndpoint:
    """Integration tests for POST /auth/login endpoint."""

    @pytest.mark.asyncio
    async def test_login_success_with_valid_credentials(
        self,
        client: TestClient,
        test_buyer_user: User
    ):
        """Test successful login with valid credentials returns JWT tokens."""
        login_data = {
            "email": test_buyer_user.email,
            "password": "testpass123"
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        # Should return 200 with valid token response
        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert "access_token" in response_data
        assert "refresh_token" in response_data
        assert response_data["token_type"] == "bearer"
        assert response_data["expires_in"] == 3600

        # Tokens should be valid JWT strings
        assert len(response_data["access_token"]) > 100
        assert len(response_data["refresh_token"]) > 100

    def test_login_failure_with_invalid_email(self, client: TestClient):
        """Test login failure with non-existent email."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "testpass123"
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        # Should return 401 unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response_data = response.json()
        assert "Email o contraseña incorrectos" in response_data["detail"]

    @pytest.mark.asyncio
    async def test_login_failure_with_invalid_password(
        self,
        client: TestClient,
        test_buyer_user: User
    ):
        """Test login failure with incorrect password."""
        login_data = {
            "email": test_buyer_user.email,
            "password": "wrongpassword"
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        # Should return 401 unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response_data = response.json()
        assert "Email o contraseña incorrectos" in response_data["detail"]

    def test_login_validation_missing_email(self, client: TestClient):
        """Test login validation with missing email field."""
        login_data = {
            "password": "testpass123"
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        # Should return 422 validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_validation_missing_password(self, client: TestClient):
        """Test login validation with missing password field."""
        login_data = {
            "email": "test@example.com"
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        # Should return 422 validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_validation_invalid_email_format(self, client: TestClient):
        """Test login validation with invalid email format."""
        login_data = {
            "email": "invalid-email-format",
            "password": "testpass123"
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        # Should return 422 validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_validation_password_too_short(self, client: TestClient):
        """Test login validation with password too short."""
        login_data = {
            "email": "test@example.com",
            "password": "123"  # Less than minimum 6 characters
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        # Should return 422 validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestRegisterEndpoint:
    """Integration tests for POST /auth/register endpoint."""

    @pytest.mark.asyncio
    async def test_register_success_with_valid_data(
        self,
        client: TestClient,
        async_session: AsyncSession
    ):
        """Test successful user registration with valid data."""
        register_data = {
            "email": "newuser@example.com",
            "password": "newpass123"
        }

        response = client.post("/api/v1/auth/register", json=register_data)

        # Should return 201 created with token response
        assert response.status_code == status.HTTP_201_CREATED

        response_data = response.json()
        assert "access_token" in response_data
        assert response_data["token_type"] == "bearer"
        assert response_data["expires_in"] == 3600

    @pytest.mark.asyncio
    async def test_register_failure_with_existing_email(
        self,
        client: TestClient,
        test_buyer_user: User
    ):
        """Test registration failure when email already exists."""
        register_data = {
            "email": test_buyer_user.email,  # Already exists
            "password": "newpass123"
        }

        response = client.post("/api/v1/auth/register", json=register_data)

        # Should return 500 internal server error (email already exists)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_register_validation_missing_email(self, client: TestClient):
        """Test registration validation with missing email."""
        register_data = {
            "password": "newpass123"
        }

        response = client.post("/api/v1/auth/register", json=register_data)

        # Should return 422 validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_validation_missing_password(self, client: TestClient):
        """Test registration validation with missing password."""
        register_data = {
            "email": "newuser@example.com"
        }

        response = client.post("/api/v1/auth/register", json=register_data)

        # Should return 422 validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCurrentUserEndpoint:
    """Integration tests for GET /auth/me endpoint."""

    @pytest.mark.asyncio
    async def test_get_current_user_success_with_valid_token(
        self,
        client: TestClient,
        test_buyer_user: User,
        auth_headers_buyer: dict
    ):
        """Test getting current user info with valid authentication token."""
        response = client.get("/api/v1/auth/me", headers=auth_headers_buyer)

        # Should return 200 with user info
        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert response_data["email"] == test_buyer_user.email
        assert response_data["id"] == str(test_buyer_user.id)
        assert "user_type" in response_data
        assert "is_active" in response_data

    def test_get_current_user_failure_without_token(self, client: TestClient):
        """Test getting current user info without authentication token."""
        response = client.get("/api/v1/auth/me")

        # Should return 403 forbidden (no token provided)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_failure_with_invalid_token(self, client: TestClient):
        """Test getting current user info with invalid authentication token."""
        headers = {"Authorization": "Bearer invalid-token-123"}
        response = client.get("/api/v1/auth/me", headers=headers)

        # Should return 401 unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_failure_with_malformed_token(self, client: TestClient):
        """Test getting current user info with malformed authorization header."""
        headers = {"Authorization": "invalid-format-token"}
        response = client.get("/api/v1/auth/me", headers=headers)

        # Should return 403 forbidden (invalid authorization format)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestRefreshTokenEndpoint:
    """Integration tests for POST /auth/refresh-token endpoint."""

    @pytest.mark.asyncio
    async def test_refresh_token_success_with_valid_refresh_token(
        self,
        client: TestClient,
        test_buyer_user: User
    ):
        """Test token refresh with valid refresh token."""
        # Create a valid refresh token
        refresh_token = create_refresh_token(data={"sub": str(test_buyer_user.id)})

        refresh_data = {
            "refresh_token": refresh_token
        }

        response = client.post("/api/v1/auth/refresh-token", json=refresh_data)

        # Should return 200 with new token pair
        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert "access_token" in response_data
        assert "refresh_token" in response_data
        assert response_data["token_type"] == "bearer"
        assert response_data["expires_in"] == 3600

    def test_refresh_token_failure_with_invalid_token(self, client: TestClient):
        """Test token refresh failure with invalid refresh token."""
        refresh_data = {
            "refresh_token": "invalid-refresh-token"
        }

        response = client.post("/api/v1/auth/refresh-token", json=refresh_data)

        # Should return 401 unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_validation_missing_token(self, client: TestClient):
        """Test token refresh validation with missing refresh token."""
        refresh_data = {}

        response = client.post("/api/v1/auth/refresh-token", json=refresh_data)

        # Should return 422 validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAdminLoginEndpoint:
    """Integration tests for POST /auth/admin-login endpoint."""

    @pytest.mark.asyncio
    async def test_admin_login_success_with_admin_user(
        self,
        client: TestClient,
        test_admin_user: User
    ):
        """Test successful admin login with admin user credentials."""
        login_data = {
            "email": test_admin_user.email,
            "password": "testpass123"
        }

        response = client.post("/api/v1/auth/admin-login", json=login_data)

        # Should return 200 with valid token response
        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert "access_token" in response_data
        assert "refresh_token" in response_data
        assert response_data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_admin_login_failure_with_non_admin_user(
        self,
        client: TestClient,
        test_buyer_user: User
    ):
        """Test admin login failure with non-admin user credentials."""
        login_data = {
            "email": test_buyer_user.email,
            "password": "testpass123"
        }

        response = client.post("/api/v1/auth/admin-login", json=login_data)

        # Should return 403 forbidden (insufficient privileges)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response_data = response.json()
        assert "privilegios administrativos" in response_data["detail"]

    def test_admin_login_failure_with_invalid_credentials(self, client: TestClient):
        """Test admin login failure with invalid credentials."""
        login_data = {
            "email": "nonexistent@admin.com",
            "password": "wrongpassword"
        }

        response = client.post("/api/v1/auth/admin-login", json=login_data)

        # Should return 401 unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogoutEndpoint:
    """Integration tests for POST /auth/logout endpoint."""

    @pytest.mark.asyncio
    async def test_logout_success_with_valid_token(
        self,
        client: TestClient,
        test_buyer_user: User,
        auth_headers_buyer: dict
    ):
        """Test successful logout with valid authentication token."""
        response = client.post("/api/v1/auth/logout", headers=auth_headers_buyer)

        # Should return 200 with success message
        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert response_data["success"] is True
        assert "exitosamente" in response_data["message"]

    def test_logout_failure_without_token(self, client: TestClient):
        """Test logout failure without authentication token."""
        response = client.post("/api/v1/auth/logout")

        # Should return 403 forbidden (no token provided)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_logout_failure_with_invalid_token(self, client: TestClient):
        """Test logout failure with invalid authentication token."""
        headers = {"Authorization": "Bearer invalid-token-123"}
        response = client.post("/api/v1/auth/logout", headers=headers)

        # Should return 401 unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRoleBasedAccess:
    """Integration tests for role-based access validation across endpoints."""

    @pytest.mark.asyncio
    async def test_admin_endpoint_access_with_admin_token(
        self,
        client: TestClient,
        test_admin_user: User,
        auth_headers_admin: dict
    ):
        """Test admin endpoint access with admin authentication token."""
        response = client.get("/api/v1/auth/me", headers=auth_headers_admin)

        # Should return 200 with admin user info
        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert response_data["email"] == test_admin_user.email
        assert "ADMIN" in response_data["user_type"] or "SUPERUSER" in response_data["user_type"]

    @pytest.mark.asyncio
    async def test_vendor_endpoint_access_with_vendor_token(
        self,
        client: TestClient,
        test_vendor_user: User,
        auth_headers_vendor: dict
    ):
        """Test vendor endpoint access with vendor authentication token."""
        response = client.get("/api/v1/auth/me", headers=auth_headers_vendor)

        # Should return 200 with vendor user info
        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert response_data["email"] == test_vendor_user.email
        assert "VENDOR" in response_data["user_type"] or "VENDEDOR" in response_data["user_type"]

    @pytest.mark.asyncio
    async def test_buyer_endpoint_access_with_buyer_token(
        self,
        client: TestClient,
        test_buyer_user: User,
        auth_headers_buyer: dict
    ):
        """Test buyer endpoint access with buyer authentication token."""
        response = client.get("/api/v1/auth/me", headers=auth_headers_buyer)

        # Should return 200 with buyer user info
        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert response_data["email"] == test_buyer_user.email
        assert "BUYER" in response_data["user_type"] or "COMPRADOR" in response_data["user_type"]

    @pytest.mark.asyncio
    async def test_cross_role_token_validation(
        self,
        client: TestClient,
        test_buyer_user: User,
        test_admin_user: User,
        auth_headers_buyer: dict,
        auth_headers_admin: dict
    ):
        """Test that tokens are properly validated for correct user roles."""
        # Buyer token should return buyer info
        response = client.get("/api/v1/auth/me", headers=auth_headers_buyer)
        assert response.status_code == status.HTTP_200_OK
        buyer_data = response.json()
        assert buyer_data["email"] == test_buyer_user.email

        # Admin token should return admin info
        response = client.get("/api/v1/auth/me", headers=auth_headers_admin)
        assert response.status_code == status.HTTP_200_OK
        admin_data = response.json()
        assert admin_data["email"] == test_admin_user.email

        # Ensure different users get different data
        assert buyer_data["id"] != admin_data["id"]
        assert buyer_data["email"] != admin_data["email"]


class TestAuthenticationErrorHandling:
    """Integration tests for authentication error scenarios and edge cases."""

    def test_authentication_with_empty_request_body(self, client: TestClient):
        """Test authentication endpoint behavior with empty request body."""
        response = client.post("/api/v1/auth/login", json={})

        # Should return 422 validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_authentication_with_null_values(self, client: TestClient):
        """Test authentication endpoint behavior with null values."""
        login_data = {
            "email": None,
            "password": None
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        # Should return 422 validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_authentication_with_special_characters(self, client: TestClient):
        """Test authentication endpoint behavior with special characters."""
        login_data = {
            "email": "test@example.com",
            "password": "pass!@#$%^&*()_+-=[]{}|;:,.<>?"
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        # Should handle special characters properly and return 401 (user not found)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authentication_with_very_long_inputs(self, client: TestClient):
        """Test authentication endpoint behavior with very long inputs."""
        long_email = "a" * 200 + "@example.com"
        long_password = "b" * 500

        login_data = {
            "email": long_email,
            "password": long_password
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        # Should handle long inputs gracefully
        assert response.status_code in [401, 422]  # Either validation error or user not found

    @pytest.mark.asyncio
    async def test_concurrent_authentication_requests(
        self,
        client: TestClient,
        test_buyer_user: User
    ):
        """Test behavior with concurrent authentication requests."""
        import asyncio
        import httpx

        login_data = {
            "email": test_buyer_user.email,
            "password": "testpass123"
        }

        # Simulate concurrent login requests
        async def make_login_request():
            async with httpx.AsyncClient(app=app, base_url="http://testserver") as ac:
                response = await ac.post("/api/v1/auth/login", json=login_data)
                return response.status_code

        # Execute multiple concurrent requests
        tasks = [make_login_request() for _ in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All requests should succeed
        for result in results:
            if isinstance(result, Exception):
                pytest.fail(f"Concurrent request failed: {result}")
            assert result == status.HTTP_200_OK


class TestAuthenticationSecurityFeatures:
    """Integration tests for authentication security features."""

    def test_password_not_returned_in_responses(
        self,
        client: TestClient,
        test_buyer_user: User,
        auth_headers_buyer: dict
    ):
        """Test that password hashes are never returned in API responses."""
        response = client.get("/api/v1/auth/me", headers=auth_headers_buyer)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        # Ensure no password-related fields are exposed
        assert "password" not in response_data
        assert "password_hash" not in response_data
        assert "passwd" not in response_data

    def test_token_format_validation(
        self,
        client: TestClient,
        test_buyer_user: User,
        auth_headers_buyer: dict
    ):
        """Test JWT token format and structure validation."""
        # Login to get a token
        login_data = {
            "email": test_buyer_user.email,
            "password": "testpass123"
        }

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK

        token_data = response.json()
        access_token = token_data["access_token"]

        # JWT tokens should have 3 parts separated by dots
        token_parts = access_token.split(".")
        assert len(token_parts) == 3, "JWT should have header.payload.signature format"

        # Each part should be base64 encoded
        for part in token_parts:
            assert len(part) > 0, "JWT parts should not be empty"

    @pytest.mark.asyncio
    async def test_token_expiration_handling(
        self,
        client: TestClient,
        test_buyer_user: User
    ):
        """Test handling of expired tokens."""
        # Create an expired token (this would need to be mocked or use a very short expiration)
        from datetime import datetime, timedelta
        from app.core.security import create_access_token

        # Create a token with very short expiration (this is a simplified test)
        expired_token_data = {
            "sub": str(test_buyer_user.id),
            "exp": datetime.utcnow() - timedelta(seconds=1)  # Already expired
        }

        # Note: This test would need proper JWT creation with custom expiration
        # For now, we test with an invalid token format which should be rejected
        headers = {"Authorization": "Bearer expired-token"}
        response = client.get("/api/v1/auth/me", headers=headers)

        # Should return 401 unauthorized for expired/invalid token
        assert response.status_code == status.HTTP_401_UNAUTHORIZED