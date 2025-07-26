"""
Tests unitarios para las dependencias de autenticación.

Tests para app/api/v1/deps/auth.py:
- get_current_user con diferentes escenarios
- oauth2_scheme configuración
- Manejo de errores de autenticación
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.api.v1.deps.auth import get_current_user, oauth2_scheme
from app.schemas.user import UserRead


class TestOAuth2Scheme:
    """Tests para la configuración de OAuth2PasswordBearer"""

    def test_oauth2_scheme_configuration(self):
        """Test que oauth2_scheme está configurado correctamente"""
        assert isinstance(oauth2_scheme, OAuth2PasswordBearer)
        # OAuth2PasswordBearer no expone tokenUrl como atributo público


class TestGetCurrentUser:
    """Tests para la dependencia get_current_user"""

    @pytest.fixture
    def mock_redis_sessions(self):
        """Mock del cliente Redis para sesiones"""
        mock_redis = AsyncMock()
        return mock_redis

    @pytest.fixture
    def valid_token_payload(self):
        """Payload válido de JWT token"""
        return {
            "sub": "123",
            "email": "usuario@test.com",
            "nombre": "Usuario",
            "apellido": "Test",
            "user_type": "COMPRADOR",
            "is_active": True,
            "is_verified": False,
            "last_login": None
        }

    @pytest.mark.asyncio
    async def test_get_current_user_token_valido(
        self, 
        mock_redis_sessions, 
        valid_token_payload
    ):
        """Test: Token válido debe retornar UserRead"""

        # Arrange
        token = "valid.jwt.token"
        mock_redis_sessions.get.return_value = b"session_data"  # Sesión activa

        with patch("app.api.v1.deps.auth.auth_service") as mock_auth_service:
            mock_auth_service.verify_token.return_value = valid_token_payload

            # Act
            result = await get_current_user(token, mock_redis_sessions)

            # Assert
            assert isinstance(result, UserRead)
            assert result.id == 123
            assert result.email == "usuario@test.com"
            assert result.nombre == "Usuario"
            assert result.apellido == "Test"
            assert result.user_type.value == "COMPRADOR"  # Comparar valor del enum
            assert result.is_active is True

            # Verificar que se llamaron los métodos correctos
            mock_auth_service.verify_token.assert_called_once_with(token)
            mock_redis_sessions.get.assert_called_once_with("session:123")

    @pytest.mark.asyncio
    async def test_get_current_user_token_invalido(self, mock_redis_sessions):
        """Test: Token inválido debe lanzar HTTP 401"""

        # Arrange
        token = "invalid.jwt.token"

        with patch("app.api.v1.deps.auth.auth_service") as mock_auth_service:
            # auth_service.verify_token lanza HTTPException cuando token es inválido
            mock_auth_service.verify_token.side_effect = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token, mock_redis_sessions)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid or expired token" in str(exc_info.value.detail)

            # Verificar que se intentó verificar el token
            mock_auth_service.verify_token.assert_called_once_with(token)
            # Redis no debería ser consultado si el token es inválido
            mock_redis_sessions.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_current_user_sesion_expirada(
        self, 
        mock_redis_sessions, 
        valid_token_payload
    ):
        """Test: Sesión expirada en Redis debe lanzar HTTP 401"""

        # Arrange
        token = "valid.jwt.token"
        mock_redis_sessions.get.return_value = None  # Sesión no existe

        with patch("app.api.v1.deps.auth.auth_service") as mock_auth_service:
            mock_auth_service.verify_token.return_value = valid_token_payload

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token, mock_redis_sessions)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Sesión expirada" in str(exc_info.value.detail)
            assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

            # Verificar llamadas
            mock_auth_service.verify_token.assert_called_once_with(token)
            mock_redis_sessions.get.assert_called_once_with("session:123")

    @pytest.mark.asyncio
    async def test_get_current_user_payload_sin_user_id(self, mock_redis_sessions):
        """Test: Payload sin user_id debe lanzar HTTP 401"""

        # Arrange
        token = "token.without.userid"
        invalid_payload = {
            "email": "test@test.com",
            # sub (user_id) faltante
        }

        with patch("app.api.v1.deps.auth.auth_service") as mock_auth_service:
            mock_auth_service.verify_token.return_value = invalid_payload

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token, mock_redis_sessions)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Token payload inválido" in str(exc_info.value.detail)
            assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    @pytest.mark.asyncio
    async def test_get_current_user_excepcion_general(self, mock_redis_sessions):
        """Test: Excepción general debe convertirse en HTTP 401"""

        # Arrange
        token = "token.causing.exception"

        with patch("app.api.v1.deps.auth.auth_service") as mock_auth_service:
            # Simular excepción inesperada (no HTTPException)
            mock_auth_service.verify_token.side_effect = ValueError("Database connection error")

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token, mock_redis_sessions)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "No se pudo validar las credenciales" in str(exc_info.value.detail)
            assert "Database connection error" in str(exc_info.value.detail)
            assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


class TestGetCurrentActiveUser:
    """Tests para la dependencia get_current_active_user"""

    @pytest.mark.asyncio
    async def test_get_current_active_user_usuario_activo(self):
        """Test: Usuario activo debe retornarse sin problemas"""

        # Arrange
        active_user = UserRead(
            id=123,
            email="activo@test.com",
            nombre="Usuario",
            apellido="Activo",
            user_type="COMPRADOR",
            is_active=True,
            is_verified=False,
            last_login=None
        )

        # Importar la función
        from app.api.v1.deps.auth import get_current_active_user

        # Act
        result = await get_current_active_user(active_user)

        # Assert
        assert result == active_user
        assert result.is_active is True

    @pytest.mark.asyncio 
    async def test_get_current_active_user_usuario_inactivo(self):
        """Test: Usuario inactivo debe lanzar HTTP 400"""

        # Arrange
        inactive_user = UserRead(
            id=456,
            email="inactivo@test.com",
            nombre="Usuario",
            apellido="Inactivo",
            user_type="VENDEDOR",
            is_active=False,
            is_verified=False,
            last_login=None
        )

        # Importar la función
        from app.api.v1.deps.auth import get_current_active_user

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(inactive_user)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Usuario inactivo" in str(exc_info.value.detail)