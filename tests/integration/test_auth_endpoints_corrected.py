"""
Tests de integración corregidos para endpoints de autenticación JWT.
Usa dependency_overrides y monkey patching correctamente.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from app.main import app
from app.core.auth import get_auth_service
from app.core.redis import get_redis_service


class TestAuthEndpointsCorrected:
    """Tests corregidos para endpoints de autenticación JWT"""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Setup mocks para cada test"""
        # Limpiar overrides
        app.dependency_overrides.clear()
        
        self.mock_user = MagicMock()
        self.mock_user.id = "550e8400-e29b-41d4-a716-446655440000"
        self.mock_user.email = "test@example.com"

        self.valid_login_data = {
            "email": "test@example.com",
            "password": "password123"
        }

        self.mock_access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIn0.mock_access_token"
        self.mock_refresh_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIn0.mock_refresh_token"
        
        yield
        
        # Cleanup
        app.dependency_overrides.clear()

    def test_refresh_token_valid_corrected(self, setup_mocks):
        """Test refresh token válido - CORREGIDO con dependency overrides"""
        
        # Mock AuthService con funciones async correctas
        mock_auth_service = AsyncMock()
        
        async def mock_create_access_token(user_id):
            return self.mock_access_token
            
        async def mock_create_refresh_token(user_id):
            return self.mock_refresh_token
            
        mock_auth_service.create_access_token = mock_create_access_token
        mock_auth_service.create_refresh_token = mock_create_refresh_token

        # Mock RedisService
        mock_redis_service = AsyncMock()
        mock_redis_service.get.return_value = self.mock_refresh_token  # Token found
        mock_redis_service.set_with_ttl.return_value = True

        # Mock decode_refresh_token function
        def mock_decode_refresh_token(token: str):
            if token == self.mock_refresh_token:
                return {"sub": self.mock_user.id, "type": "refresh"}
            return None

        # Override dependencies
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        app.dependency_overrides[get_redis_service] = lambda: mock_redis_service

        # Monkey patch decode_refresh_token
        import app.api.v1.endpoints.auth as auth_module
        original_decode = auth_module.decode_refresh_token
        auth_module.decode_refresh_token = mock_decode_refresh_token

        try:
            # Ejecutar request
            client = TestClient(app)
            refresh_data = {"refresh_token": self.mock_refresh_token}
            response = client.post("/api/v1/auth/refresh-token", json=refresh_data)

            # Verificaciones
            assert response.status_code == 200

            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"
            assert data["expires_in"] == 3600
            assert data["access_token"] == self.mock_access_token
            assert data["refresh_token"] == self.mock_refresh_token

            print("✅ TEST REFRESH TOKEN VALID CORRECTED: PASSED")

        finally:
            # Restore original function
            auth_module.decode_refresh_token = original_decode

    def test_refresh_token_invalid_corrected(self, setup_mocks):
        """Test refresh token inválido - CORREGIDO"""
        
        # Mock decode_refresh_token - token inválido
        def mock_decode_refresh_token(token: str):
            return None  # Token inválido

        # Monkey patch
        import app.api.v1.endpoints.auth as auth_module
        original_decode = auth_module.decode_refresh_token
        auth_module.decode_refresh_token = mock_decode_refresh_token

        try:
            # Ejecutar request con token inválido
            client = TestClient(app)
            invalid_data = {"refresh_token": "invalid_token"}
            response = client.post("/api/v1/auth/refresh-token", json=invalid_data)

            # Verificaciones
            assert response.status_code == 401

            data = response.json()
            assert "detail" in data
            assert "inválido o expirado" in data["detail"]

            print("✅ TEST REFRESH TOKEN INVALID CORRECTED: PASSED")

        finally:
            # Restore original function
            auth_module.decode_refresh_token = original_decode
