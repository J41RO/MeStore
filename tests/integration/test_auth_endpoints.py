"""
Tests de integración para endpoints de autenticación JWT - VERSIÓN CORREGIDA.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from app.main import app
from app.core.auth import get_auth_service
from app.core.redis import get_redis_service

# Cliente de prueba FastAPI
client = TestClient(app)


class TestAuthEndpoints:
    """Tests para endpoints de autenticación JWT"""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Setup mocks para cada test"""
        app.dependency_overrides.clear()
        
        self.mock_user = MagicMock()
        self.mock_user.id = "550e8400-e29b-41d4-a716-446655440000"
        self.mock_user.email = "test@example.com"

        self.mock_access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.mock_access_token"
        self.mock_refresh_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.mock_refresh_token"

        yield
        app.dependency_overrides.clear()

    def test_refresh_token_valid(self, setup_mocks):
        """Test refresh token válido - CORREGIDO"""
        
        # Mock AuthService
        mock_auth_service = AsyncMock()
        
        async def mock_create_access_token(user_id):
            return "new_access_token"
            
        async def mock_create_refresh_token(user_id):
            return "new_refresh_token"
            
        mock_auth_service.create_access_token = mock_create_access_token
        mock_auth_service.create_refresh_token = mock_create_refresh_token

        # Mock RedisService
        mock_redis_service = AsyncMock()
        mock_redis_service.get.return_value = self.mock_refresh_token
        mock_redis_service.set_with_ttl.return_value = True

        # Mock decode function
        def mock_decode_refresh_token(token: str):
            if token == self.mock_refresh_token:
                return {"sub": self.mock_user.id, "type": "refresh"}
            return None

        # Override dependencies
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        app.dependency_overrides[get_redis_service] = lambda: mock_redis_service

        import app.api.v1.endpoints.auth as auth_module
        original_decode = auth_module.decode_refresh_token
        auth_module.decode_refresh_token = mock_decode_refresh_token

        try:
            refresh_data = {"refresh_token": self.mock_refresh_token}
            response = client.post("/api/v1/auth/refresh-token", json=refresh_data)

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["access_token"] == "new_access_token"

        finally:
            auth_module.decode_refresh_token = original_decode

    def test_login_endpoint_exists(self, setup_mocks):
        """Test que endpoint login existe y responde"""
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        # Debe responder (aunque sea 401 sin usuario válido)
        assert response.status_code in [200, 401, 422]
