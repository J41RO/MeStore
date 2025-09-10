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
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.auth import AuthService, get_current_user, auth_service
from app.core.security import create_access_token, decode_access_token


@pytest.mark.asyncio  
class TestGetCurrentUser:
    """Tests completos para dependency get_current_user"""

    async def test_get_current_user_valid_token_with_email(self):
        """Test get_current_user con token válido incluyendo email"""
        jwt_token = auth_service.create_access_token("00000000-0000-0000-0000-000000000001")
        mock_credentials = AsyncMock()
        mock_credentials.credentials = jwt_token

        class MockUser:
            def __init__(self):
                self.id = "00000000-0000-0000-0000-000000000001"
                self.email = "test@example.com"
                self.nombre = "Test User"
        
        mock_user = MockUser()
        
        # Patch la base de datos directamente en lugar de toda la función
        with patch('app.database.AsyncSessionLocal') as mock_session_class:
            # Setup del context manager - async context manager real
            mock_session = AsyncMock()
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__ = AsyncMock(return_value=mock_session)
            mock_context_manager.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_context_manager
            
            # Setup del resultado de la consulta - usar MagicMock para evitar coroutines innecesarias
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_session.execute = AsyncMock(return_value=mock_result)

            result = await get_current_user(mock_credentials)
            assert result.id == "00000000-0000-0000-0000-000000000001"
            assert result.email == "test@example.com"
            assert hasattr(result, 'id')

    async def test_get_current_user_valid_token_with_data(self):
        """Test get_current_user usando función security directamente"""
        token_data = {"sub": "00000000-0000-0000-0000-000000000002", "email": "test2@example.com"}
        jwt_token = create_access_token(token_data)
        mock_credentials = AsyncMock()
        mock_credentials.credentials = jwt_token

        class MockUser:
            def __init__(self):
                self.id = "00000000-0000-0000-0000-000000000002"
                self.email = "test2@example.com"
                self.nombre = "Test User 2"
        
        mock_user = MockUser()
        
        # Patch la base de datos directamente en lugar de toda la función
        with patch('app.database.AsyncSessionLocal') as mock_session_class:
            # Setup del context manager - async context manager real
            mock_session = AsyncMock()
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__ = AsyncMock(return_value=mock_session)
            mock_context_manager.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_context_manager
            
            # Setup del resultado de la consulta - usar MagicMock para evitar coroutines innecesarias
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_session.execute = AsyncMock(return_value=mock_result)

            result = await get_current_user(mock_credentials)
            assert result.id == "00000000-0000-0000-0000-000000000002"
            assert result.email == "test2@example.com"
            assert hasattr(result, 'id')

    async def test_get_current_user_invalid_token_malformed(self):
        """Test con token completamente malformado"""
        mock_credentials = AsyncMock()
        mock_credentials.credentials = "invalid.token.format"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials)

        assert exc_info.value.status_code == 401

    async def test_get_current_user_invalid_token_expired(self):
        """Test con token expirado o inválido"""
        mock_credentials = AsyncMock()
        mock_credentials.credentials = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZXhwIjoxNjI2MjYyNDAwfQ.invalid"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials)

        assert exc_info.value.status_code == 401

    async def test_get_current_user_user_not_found(self):
        """Test cuando el usuario del token no existe en la base de datos"""
        jwt_token = auth_service.create_access_token("00000000-0000-0000-0000-000000000099")
        mock_credentials = AsyncMock()
        mock_credentials.credentials = jwt_token

        # Patch la base de datos para simular que el usuario no existe
        with patch('app.database.AsyncSessionLocal') as mock_session_class:
            # Setup del context manager - async context manager real
            mock_session = AsyncMock()
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__ = AsyncMock(return_value=mock_session)
            mock_context_manager.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_context_manager
            
            # Setup del resultado de la consulta - usuario no encontrado
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None  # Usuario no encontrado
            mock_session.execute = AsyncMock(return_value=mock_result)

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials)

            assert exc_info.value.status_code == 401
            assert "Usuario no encontrado" in str(exc_info.value.detail)

    async def test_get_current_user_missing_sub_claim(self):
        """Test con token que no tiene claim 'sub'"""
        # Crear token sin 'sub'
        token_data = {"email": "test@example.com", "name": "Test"}
        jwt_token = create_access_token(token_data)

        mock_credentials = AsyncMock()
        mock_credentials.credentials = jwt_token

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Token inválido"

    async def test_get_current_user_database_error(self):
        """Test cuando hay error de base de datos"""
        jwt_token = auth_service.create_access_token("00000000-0000-0000-0000-000000000003")
        mock_credentials = AsyncMock()
        mock_credentials.credentials = jwt_token

        # Patch la base de datos para simular un error de conexión
        with patch('app.database.AsyncSessionLocal') as mock_session_class:
            # Setup del context manager - async context manager real
            mock_session = AsyncMock()
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__ = AsyncMock(return_value=mock_session)
            mock_context_manager.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_context_manager
            
            # Simular error de base de datos al ejecutar la consulta
            mock_session.execute = AsyncMock(side_effect=Exception("Database connection error"))

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials)

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Token inválido"


@pytest.mark.asyncio
class TestAuthServiceTokenGeneration:
    """Tests para generación de tokens del AuthService"""

    async def test_create_access_token_valid_user_id(self):
        """Test creación de token con user_id válido"""
        user_id = "user123"
        token = auth_service.create_access_token(user_id)
        
        # Verificar que es string y no vacío
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decodificar y verificar claims
        payload = decode_access_token(token)
        assert payload["sub"] == user_id

    async def test_create_access_token_with_additional_data(self):
        """Test creación de token con datos adicionales"""
        token_data = {
            "sub": "user456",
            "email": "test@example.com",
            "role": "user"
        }
        
        token = create_access_token(token_data)
        
        # Decodificar y verificar todos los claims
        payload = decode_access_token(token)
        assert payload["sub"] == "user456"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "user"

    async def test_decode_access_token_valid(self):
        """Test decodificación de token válido"""
        original_data = {"sub": "user789", "admin": True}
        token = create_access_token(original_data)
        
        decoded_data = decode_access_token(token)
        
        assert decoded_data["sub"] == "user789"
        assert decoded_data["admin"] == True

    async def test_decode_access_token_invalid(self):
        """Test decodificación de token inválido"""
        invalid_token = "invalid.jwt.token"
        
        # decode_access_token retorna None cuando el token es inválido (no lanza excepción)
        result = decode_access_token(invalid_token)
        assert result is None