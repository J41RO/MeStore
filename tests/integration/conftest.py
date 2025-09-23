#!/usr/bin/env python3
"""
Integration Test Configuration with Enhanced Database Isolation
==============================================================

This module provides specialized configuration for integration tests with
enhanced database isolation to prevent ResourceClosedError and ensure
proper cross-system testing.

Features:
1. Enhanced async session management
2. Proper FastAPI dependency injection
3. User fixtures with proper token generation
4. Cross-system authentication validation
5. Transaction isolation and cleanup

Author: Integration Testing Specialist
Date: 2025-09-23
"""

import os
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# Set testing environment
os.environ["TESTING"] = "1"
os.environ["DISABLE_SEARCH_SERVICE"] = "1"
os.environ["DISABLE_CHROMA_SERVICE"] = "1"

from app.main import app
from app.models.user import User, UserType
from app.core.security import create_access_token, get_password_hash
from app.core.types import generate_uuid

# Import enhanced database isolation
from tests.integration.database_isolation_enhanced import enhanced_async_session, session_manager


@pytest.fixture(scope="function")
async def integration_async_client(
    enhanced_async_session: AsyncSession
) -> AsyncGenerator[AsyncClient, None]:
    """
    Async client fixture for integration tests with enhanced session management.

    This fixture:
    - Uses enhanced async session with proper isolation
    - Configures FastAPI dependency injection
    - Provides clean client for each test
    - Ensures proper cleanup to prevent ResourceClosedError

    Args:
        enhanced_async_session: Enhanced session with proper isolation

    Yields:
        AsyncClient: Configured client for integration tests
    """
    # Headers for realistic requests
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Integration-Test/1.0",
        "Content-Type": "application/json"
    }

    # Create async client with proper transport
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers=headers,
        timeout=30.0
    ) as client:
        yield client


@pytest.fixture(scope="function")
async def integration_superuser(
    enhanced_async_session: AsyncSession
) -> User:
    """
    Create a superuser for integration tests with enhanced session management.

    This fixture creates a superuser with all required fields for
    proper JWT token generation and cross-system authentication.

    Args:
        enhanced_async_session: Enhanced session for database operations

    Returns:
        User: Superuser with proper configuration for integration tests
    """
    superuser = User(
        id=generate_uuid(),
        email="integration.superuser@mestore.com",
        password_hash=await get_password_hash("SuperSecure123!"),
        nombre="Integration",
        apellido="Superuser",
        user_type=UserType.SUPERUSER,
        is_active=True,
        is_verified=True,
        documento="12345678",  # Required field
        telefono="3001234567"  # Required field
    )

    enhanced_async_session.add(superuser)
    await enhanced_async_session.commit()
    await enhanced_async_session.refresh(superuser)

    return superuser


@pytest.fixture(scope="function")
async def integration_vendor(
    enhanced_async_session: AsyncSession
) -> User:
    """
    Create a vendor user for integration tests.

    Args:
        enhanced_async_session: Enhanced session for database operations

    Returns:
        User: Vendor user configured for integration tests
    """
    vendor = User(
        id=generate_uuid(),
        email="integration.vendor@mestore.com",
        password_hash=await get_password_hash("VendorSecure123!"),
        nombre="Integration",
        apellido="Vendor",
        user_type=UserType.VENDOR,
        is_active=True,
        is_verified=True,
        documento="87654321",
        telefono="3009876543"
    )

    enhanced_async_session.add(vendor)
    await enhanced_async_session.commit()
    await enhanced_async_session.refresh(vendor)

    return vendor


@pytest.fixture(scope="function")
async def integration_buyer(
    enhanced_async_session: AsyncSession
) -> User:
    """
    Create a buyer user for integration tests.

    Args:
        enhanced_async_session: Enhanced session for database operations

    Returns:
        User: Buyer user configured for integration tests
    """
    buyer = User(
        id=generate_uuid(),
        email="integration.buyer@mestore.com",
        password_hash=await get_password_hash("BuyerSecure123!"),
        nombre="Integration",
        apellido="Buyer",
        user_type=UserType.BUYER,
        is_active=True,
        is_verified=True,
        documento="11223344",
        telefono="3005566778"
    )

    enhanced_async_session.add(buyer)
    await enhanced_async_session.commit()
    await enhanced_async_session.refresh(buyer)

    return buyer


@pytest.fixture(scope="function")
def integration_superuser_token(integration_superuser: User) -> str:
    """
    Generate a valid JWT token for the integration superuser.

    This token includes all fields expected by the auth system
    and is properly formatted for cross-system authentication.

    Args:
        integration_superuser: Superuser to create token for

    Returns:
        str: Valid JWT access token
    """
    token_data = {
        "sub": str(integration_superuser.id),
        "user_id": str(integration_superuser.id),
        "email": integration_superuser.email,
        "nombre": integration_superuser.nombre,
        "apellido": integration_superuser.apellido,
        "user_type": integration_superuser.user_type.value,
        "is_active": integration_superuser.is_active,
        "is_verified": integration_superuser.is_verified,
        "documento": integration_superuser.documento,
        "telefono": integration_superuser.telefono,
    }

    return create_access_token(data=token_data)


@pytest.fixture(scope="function")
def integration_vendor_token(integration_vendor: User) -> str:
    """
    Generate a valid JWT token for the integration vendor.

    Args:
        integration_vendor: Vendor to create token for

    Returns:
        str: Valid JWT access token
    """
    token_data = {
        "sub": str(integration_vendor.id),
        "user_id": str(integration_vendor.id),
        "email": integration_vendor.email,
        "nombre": integration_vendor.nombre,
        "apellido": integration_vendor.apellido,
        "user_type": integration_vendor.user_type.value,
        "is_active": integration_vendor.is_active,
        "is_verified": integration_vendor.is_verified,
        "documento": integration_vendor.documento,
        "telefono": integration_vendor.telefono,
    }

    return create_access_token(data=token_data)


@pytest.fixture(scope="function")
def integration_buyer_token(integration_buyer: User) -> str:
    """
    Generate a valid JWT token for the integration buyer.

    Args:
        integration_buyer: Buyer to create token for

    Returns:
        str: Valid JWT access token
    """
    token_data = {
        "sub": str(integration_buyer.id),
        "user_id": str(integration_buyer.id),
        "email": integration_buyer.email,
        "nombre": integration_buyer.nombre,
        "apellido": integration_buyer.apellido,
        "user_type": integration_buyer.user_type.value,
        "is_active": integration_buyer.is_active,
        "is_verified": integration_buyer.is_verified,
        "documento": integration_buyer.documento,
        "telefono": integration_buyer.telefono,
    }

    return create_access_token(data=token_data)


@pytest.fixture(scope="function")
def integration_superuser_headers(integration_superuser_token: str) -> dict:
    """
    Generate authentication headers for the integration superuser.

    Args:
        integration_superuser_token: JWT token for superuser

    Returns:
        dict: Headers with Authorization bearer token
    """
    return {
        "Authorization": f"Bearer {integration_superuser_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="function")
def integration_vendor_headers(integration_vendor_token: str) -> dict:
    """
    Generate authentication headers for the integration vendor.

    Args:
        integration_vendor_token: JWT token for vendor

    Returns:
        dict: Headers with Authorization bearer token
    """
    return {
        "Authorization": f"Bearer {integration_vendor_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="function")
def integration_buyer_headers(integration_buyer_token: str) -> dict:
    """
    Generate authentication headers for the integration buyer.

    Args:
        integration_buyer_token: JWT token for buyer

    Returns:
        dict: Headers with Authorization bearer token
    """
    return {
        "Authorization": f"Bearer {integration_buyer_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="function", autouse=True)
async def cleanup_integration_test():
    """
    Auto-cleanup fixture for integration tests.

    This fixture ensures proper cleanup after each integration test
    to prevent ResourceClosedError and maintain test isolation.
    """
    # Setup - nothing needed
    yield

    # Cleanup - ensure session manager is clean
    try:
        await session_manager.cleanup_all_sessions()
        session_manager.clear_dependency_overrides()
    except Exception as e:
        # Log cleanup errors but don't fail the test
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Integration test cleanup warning: {e}")


# Aliases for backward compatibility with existing test imports
async_session = enhanced_async_session
async_client = integration_async_client
test_admin_user = integration_superuser
test_vendor_user = integration_vendor
test_buyer_user = integration_buyer