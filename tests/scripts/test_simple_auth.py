#!/usr/bin/env python3
"""
Simple authentication test to isolate the login issue
"""

import pytest
from app.utils.password import verify_password, hash_password
from app.core.security import create_access_token, decode_access_token
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

@pytest.mark.asyncio
async def test_simple_auth(async_db_session: AsyncSession, test_admin_user: User):
    """Test authentication with test database"""

    # Test 1: Check password verification
    print("=== PASSWORD VERIFICATION TEST ===")

    # Verify admin user exists in test DB
    assert test_admin_user is not None, "Admin user fixture should be created"

    # Test password verification with known password
    # Admin user fixture uses password "testpass123" (see conftest.py)
    password_valid = await verify_password('testpass123', test_admin_user.password_hash)
    print(f"Password for {test_admin_user.email}: {password_valid}")
    assert password_valid is True, "Password verification should succeed"

    # Test 2: Direct user lookup with SQLAlchemy
    print("\n=== DIRECT USER LOOKUP TEST ===")

    result = await async_db_session.execute(
        select(User).where(User.email == test_admin_user.email)
    )
    user = result.scalars().first()
    assert user is not None, "User should be found in database"
    print(f"User found: {user.email}, Type: {user.user_type}, Active: {user.is_active}")

    # Test password verification
    password_valid = await verify_password('testpass123', user.password_hash)
    print(f"Password valid: {password_valid}")
    assert password_valid is True, "Password should be valid"

    # Test 3: Token creation and verification
    print("\n=== TOKEN CREATION TEST ===")
    token_data = {"sub": str(user.id)}
    access_token = create_access_token(token_data)
    print(f"Created token: {access_token[:50]}...")
    assert access_token is not None, "Token should be created"

    # Verify token
    decoded = decode_access_token(access_token)
    print(f"Decoded token: {decoded}")
    assert decoded is not None, "Token should be decoded successfully"
    assert decoded.get("sub") == str(user.id), "Token subject should match user ID"

@pytest.mark.asyncio
async def test_curl_simulation(async_client, test_admin_user: User):
    """Simulate the exact curl request to identify the issue"""
    print("\n=== FASTAPI TEST CLIENT SIMULATION ===")

    # Test the login endpoint with test user credentials
    login_data = {
        "email": test_admin_user.email,
        "password": "testpass123"
    }

    response = await async_client.post("/api/v1/auth/login", json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")

    assert response.status_code == 200, f"Login should succeed, got {response.status_code}"
    response_data = response.json()

    # Verify response structure (direct data, no wrapper)
    assert "access_token" in response_data, "Response should include access_token"
    assert "refresh_token" in response_data, "Response should include refresh_token"
    assert "user" in response_data, "Response should include user data"
    assert "token_type" in response_data, "Response should include token_type"
    assert response_data["token_type"] == "bearer", "Token type should be bearer"

    # Verify user data structure
    user_data = response_data["user"]
    assert user_data["email"] == test_admin_user.email, "User email should match"
    assert user_data["user_type"] == "SUPERUSER", "User type should be SUPERUSER"

    print("✅ Login successful!")
    return response_data