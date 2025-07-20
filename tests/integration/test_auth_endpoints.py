"""
Tests de integración para endpoints protegidos con autenticación
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

from app.main import app
from app.core.auth import auth_service

client = TestClient(app)


class TestAuthenticatedEndpoints:
    """Tests para endpoints que requieren autenticación"""
    
    def test_protected_endpoint_without_token(self):
        """Test endpoint protegido sin token - debe devolver 403"""
        response = client.get("/marketplace/protected")
        assert response.status_code == 403
    
    def test_protected_endpoint_with_invalid_token(self):
        """Test endpoint protegido con token inválido"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/marketplace/protected", headers=headers)
        assert response.status_code == 401
    
    def test_sellers_only_endpoint_with_buyer_token_simple(self):
        """Test endpoint vendedores con token válido pero tipo incorrecto"""
        # Este test funciona sin mock Redis porque usa override_dependency
        from app.core.auth import get_current_user
        from fastapi import Depends
        
        def mock_get_current_user():
            return {
                "user_id": "buyer_123",
                "username": "buyer", 
                "user_type": "COMPRADOR"
            }
        
        # Override dependency
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = client.get("/marketplace/sellers-only")
            assert response.status_code == 403
            data = response.json()
            assert "Access denied" in data["detail"]
        finally:
            # Cleanup override
            app.dependency_overrides.clear()
    
    def test_sellers_only_endpoint_with_seller_token_simple(self):
        """Test endpoint vendedores con token de vendedor"""
        from app.core.auth import get_current_user
        
        def mock_get_current_user():
            return {
                "user_id": "seller_123",
                "username": "seller",
                "user_type": "VENDEDOR"
            }
        
        # Override dependency
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = client.get("/marketplace/sellers-only")
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Welcome seller!"
            assert data["user"]["user_type"] == "VENDEDOR"
            assert "features" in data
        finally:
            # Cleanup override
            app.dependency_overrides.clear()


class TestAuthEndpointsBasic:
    """Tests básicos sin mocking complejo"""
    
    def test_all_marketplace_endpoints_exist(self):
        """Verificar que todos los endpoints existen"""
        # Test endpoint base
        response = client.get("/marketplace/")
        assert response.status_code == 200
        assert response.json()["module"] == "marketplace"
        
        # Test health endpoint
        response = client.get("/marketplace/health")
        assert response.status_code == 200
        assert response.json()["module"] == "marketplace"
    
    def test_protected_endpoints_require_auth(self):
        """Verificar que endpoints protegidos requieren autenticación"""
        protected_endpoints = [
            "/marketplace/protected",
            "/marketplace/sellers-only"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code in [401, 403], f"Endpoint {endpoint} should require auth"
    
    def test_auth_service_functionality(self):
        """Test directo del AuthService"""
        # Test crear token
        token_data = {"sub": "test", "username": "test", "user_type": "COMPRADOR"}
        token = auth_service.create_access_token(token_data)
        assert len(token) > 50
        
        # Test verificar token
        payload = auth_service.verify_token(token)
        assert payload["sub"] == "test"
        assert payload["user_type"] == "COMPRADOR"
        
        # Test password hashing
        password = "test123"
        hashed = auth_service.get_password_hash(password)
        assert len(hashed) > 50
        assert auth_service.verify_password(password, hashed)
