"""
Tests robustos para módulo de autenticación basados en análisis completo.

Incluye tests para:
- get_current_user dependency (casos válidos e inválidos)
- Manejo de errores y excepciones HTTPException
- Validación de estructura de tokens JWT
- Casos edge y valores límite
"""
import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch
from app.core.auth import AuthService, get_current_user, auth_service
from app.core.security import create_access_token, decode_access_token


@pytest.mark.asyncio  
class TestGetCurrentUser:
    """Tests completos para dependency get_current_user"""

    async def test_get_current_user_valid_token_with_email(self):
        """Test get_current_user con token válido incluyendo email"""
        # Usar AuthService que maneja la conversión user_id -> dict internamente
        jwt_token = auth_service.create_access_token("user123")

        # Mock HTTPAuthorizationCredentials
        mock_credentials = AsyncMock()
        mock_credentials.credentials = jwt_token

        # Ejecutar función
        result = await get_current_user(mock_credentials)

        # Verificaciones robustas
        assert result["user_id"] == "user123"
        assert isinstance(result, dict)
        assert "user_id" in result

    async def test_get_current_user_valid_token_with_data(self):
        """Test get_current_user usando función security directamente"""
        # Usar función directa de security con dict completo
        token_data = {
            "sub": "user456", 
            "email": "test@example.com"
        }
        jwt_token = create_access_token(token_data)

        mock_credentials = AsyncMock()
        mock_credentials.credentials = jwt_token

        result = await get_current_user(mock_credentials)

        assert result["user_id"] == "user456"
        assert result["email"] == "test@example.com"
        assert isinstance(result, dict)

    async def test_get_current_user_invalid_token_malformed(self):
        """Test con token completamente malformado"""
        mock_credentials = AsyncMock()
        mock_credentials.credentials = "invalid.token.format"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials)

        assert exc_info.value.status_code == 401
        assert "Token inválido" in exc_info.value.detail
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    async def test_get_current_user_token_without_sub(self):
        """Test con token válido pero sin campo sub requerido"""
        token_data = {
            "email": "test@example.com",
            "exp": 9999999999  # Fecha futura válida
        }
        jwt_token = create_access_token(token_data)

        mock_credentials = AsyncMock()
        mock_credentials.credentials = jwt_token

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials)

        assert exc_info.value.status_code == 401
        assert "Token inválido" in exc_info.value.detail

    async def test_get_current_user_empty_token(self):
        """Test con token vacío"""
        mock_credentials = AsyncMock()
        mock_credentials.credentials = ""

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials)

        assert exc_info.value.status_code == 401

    @patch("app.core.auth.decode_access_token")
    async def test_get_current_user_decode_exception(self, mock_decode):
        """Test cuando decode_access_token lanza excepción"""
        mock_decode.side_effect = Exception("JWT decode error")

        mock_credentials = AsyncMock()
        mock_credentials.credentials = "any_token"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials)

        assert exc_info.value.status_code == 401
        assert "Token inválido" in exc_info.value.detail
