#!/usr/bin/env python3
# test_auth_service.py - Unit tests for AuthService
import pytest
from unittest.mock import Mock, AsyncMock
from app.services.auth_service import AuthService

@pytest.mark.asyncio
async def test_auth_service_password_hashing():
    """Test AuthService password hashing functionality"""
    auth_service = AuthService()

    # Test password hashing
    password = "test_password_123"
    hashed = await auth_service.get_password_hash(password)

    assert hashed is not None
    assert len(hashed) > 10  # bcrypt hash should be substantial
    assert "$2b$" in hashed  # bcrypt identifier

    # Test password verification
    is_valid = await auth_service.verify_password(password, hashed)
    assert is_valid is True

    # Test wrong password
    is_invalid = await auth_service.verify_password("wrong_password", hashed)
    assert is_invalid is False

@pytest.mark.asyncio
async def test_auth_service_user_authentication():
    """Test AuthService user authentication with mocked SQLite"""
    from unittest.mock import patch, MagicMock

    auth_service = AuthService()

    # Create mock user data
    test_email = "test@example.com"
    test_password = "test123"
    password_hash = await auth_service.get_password_hash(test_password)

    # Mock SQLite connection and cursor
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Mock fetchone to return user data
    mock_cursor.fetchone.return_value = (
        1,  # user_id
        test_email,  # email
        password_hash,  # password_hash
        "BUYER",  # user_type
        1,  # is_active
        "Test",  # nombre
        "User"  # apellido
    )

    # Patch sqlite3.connect to return our mock connection
    with patch('sqlite3.connect', return_value=mock_conn):
        # Test authenticate_user with valid credentials
        user = await auth_service.authenticate_user(
            db=None,  # Not used in current implementation
            email=test_email,
            password=test_password
        )

        assert user is not None
        assert user.email == test_email
        assert user.is_active == 1

        # Verify the SQL query was called
        mock_cursor.execute.assert_called_once()
        mock_conn.close.assert_called_once()

@pytest.mark.asyncio
async def test_auth_service_user_not_found():
    """Test AuthService when user doesn't exist"""
    from unittest.mock import patch, MagicMock

    auth_service = AuthService()

    # Mock SQLite connection and cursor
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Mock fetchone to return None (user not found)
    mock_cursor.fetchone.return_value = None

    # Patch sqlite3.connect to return our mock connection
    with patch('sqlite3.connect', return_value=mock_conn):
        # Test authenticate_user with non-existent user
        user = await auth_service.authenticate_user(
            db=None,  # Not used in current implementation
            email="nonexistent@example.com",
            password="password123"
        )

        assert user is None

        # Verify the SQL query was called
        mock_cursor.execute.assert_called_once()
        mock_conn.close.assert_called_once()