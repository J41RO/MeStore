"""
Debug tests for authentication integration issues.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserType
from app.core.security import get_password_hash

pytestmark = [pytest.mark.integration, pytest.mark.api, pytest.mark.auth]


class TestAuthenticationDebug:
    """Debug authentication integration tests."""

    @pytest.mark.asyncio
    async def test_debug_test_user_creation(
        self,
        client: TestClient,
        test_buyer_user: User
    ):
        """Debug test to check if test user is properly created."""
        print(f"Test buyer user ID: {test_buyer_user.id}")
        print(f"Test buyer user email: {test_buyer_user.email}")
        print(f"Test buyer user type: {test_buyer_user.user_type}")
        print(f"Test buyer user is_active: {test_buyer_user.is_active}")
        print(f"Test buyer user password_hash: {test_buyer_user.password_hash}")

        assert test_buyer_user is not None
        assert test_buyer_user.email is not None
        assert test_buyer_user.password_hash is not None

    @pytest.mark.asyncio
    async def test_debug_login_request_format(
        self,
        client: TestClient,
        test_buyer_user: User
    ):
        """Debug test to check login request format and response."""
        login_data = {
            "email": test_buyer_user.email,
            "password": "testpass123"
        }

        print(f"Sending login request with data: {login_data}")

        response = client.post("/api/v1/auth/login", json=login_data)

        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response content: {response.text}")

        if response.status_code != 200:
            try:
                error_data = response.json()
                print(f"Error response JSON: {error_data}")
            except:
                print("Could not parse error response as JSON")

    @pytest.mark.asyncio
    async def test_debug_password_verification(
        self,
        test_buyer_user: User
    ):
        """Debug test to verify password hashing and verification."""
        from app.core.security import verify_password

        original_password = "testpass123"
        stored_hash = test_buyer_user.password_hash

        print(f"Original password: {original_password}")
        print(f"Stored hash: {stored_hash}")

        # Test password verification (await if it's async)
        is_valid = await verify_password(original_password, stored_hash)
        print(f"Password verification result: {is_valid}")

        assert is_valid, "Password verification should succeed"

    def test_debug_endpoint_routing(self, client: TestClient):
        """Debug test to check if endpoint routing works correctly."""
        # Test that the endpoint exists
        response = client.post("/api/v1/auth/login", json={})
        print(f"Empty request response status: {response.status_code}")

        # Should not be 404 (endpoint exists) and should be 422 (validation error)
        assert response.status_code != 404, "Login endpoint should exist"
        assert response.status_code == 422, "Should get validation error with empty request"

    @pytest.mark.asyncio
    async def test_debug_database_session(
        self,
        async_session: AsyncSession,
        test_buyer_user: User
    ):
        """Debug test to verify database session and user retrieval."""
        from sqlalchemy import select

        # Try to find the user in the database
        stmt = select(User).where(User.email == test_buyer_user.email)
        result = await async_session.execute(stmt)
        db_user = result.scalar_one_or_none()

        print(f"Database lookup result: {db_user}")

        if db_user:
            print(f"DB user ID: {db_user.id}")
            print(f"DB user email: {db_user.email}")
            print(f"DB user password_hash: {db_user.password_hash}")
            print(f"DB user user_type: {db_user.user_type}")
            print(f"DB user is_active: {db_user.is_active}")

        assert db_user is not None, "User should be found in database"
        assert db_user.email == test_buyer_user.email