"""
Tests para módulo de autenticación
"""

import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch

from app.core.auth import AuthService, get_current_user, auth_service


class TestAuthService:
    """Tests para AuthService"""

    def test_verify_password(self):
        """Test verificación de contraseña"""
        password = "test123"
        hashed = auth_service.get_password_hash(password)

        assert auth_service.verify_password(password, hashed)
        assert not auth_service.verify_password("wrong", hashed)

    def test_create_access_token(self):
        """Test creación de token JWT"""
        data = {"sub": "user123", "username": "testuser"}
        token = auth_service.create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens son largos

    def test_verify_token_valid(self):
        """Test verificación de token válido"""
        data = {"sub": "user123", "username": "testuser"}
        token = auth_service.create_access_token(data)

        payload = auth_service.verify_token(token)
        assert payload["sub"] == "user123"
        assert payload["username"] == "testuser"

    def test_verify_token_invalid(self):
        """Test verificación de token inválido"""
        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_token("invalid_token")

        assert exc_info.value.status_code == 401


@pytest.mark.asyncio
class TestGetCurrentUser:
    """Tests para dependency get_current_user"""

    async def test_get_current_user_valid_token(self):
        """Test obtener usuario con token válido"""
        # Mock credentials
        mock_credentials = AsyncMock()
        mock_credentials.credentials = auth_service.create_access_token({
            "sub": "user123",
            "username": "testuser",
            "user_type": "COMPRADOR"
        })

        # Mock Redis
        mock_redis = AsyncMock()
        mock_redis.get.return_value = b"session_data"

        # Test
        user = await get_current_user(mock_credentials, mock_redis)

        assert user["user_id"] == "user123"
        assert user["username"] == "testuser"
        assert user["user_type"] == "COMPRADOR"

    async def test_get_current_user_expired_session(self):
        """Test con sesión expirada en Redis"""
        # Mock credentials
        mock_credentials = AsyncMock()
        mock_credentials.credentials = auth_service.create_access_token({
            "sub": "user123",
            "username": "testuser"
        })

        # Mock Redis - sesión no existe
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None

        # Test
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials, mock_redis)

        assert exc_info.value.status_code == 401
        assert "Session expired" in str(exc_info.value.detail)
