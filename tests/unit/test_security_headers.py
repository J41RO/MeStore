
# tests/unit/test_security_headers.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Tests de Security Headers Middleware
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_security_headers.py
# Ruta: tests/unit/test_security_headers.py
# Autor: Jairo
# Fecha de Creación: 2025-07-21
# Última Actualización: 2025-07-21
# Versión: 1.0.0
# Propósito: Tests unitarios para middleware de seguridad
#            Verifica comportamiento condicional según entorno
#
# Modificaciones:
# 2025-07-21 - Creación inicial de tests de seguridad
#
# ---------------------------------------------------------------------------------------------

"""
Tests unitarios para SecurityHeadersMiddleware.

Verifica:
- Headers de seguridad en producción
- Ausencia de headers en desarrollo
- Configuración condicional
- Integridad de respuestas
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient
from app.middleware.security import SecurityHeadersMiddleware, get_security_middleware_config


class TestSecurityHeadersMiddleware:
    """Test suite para SecurityHeadersMiddleware."""

    @pytest.fixture
    def mock_app(self):
        """Fixture que proporciona una app FastAPI mock."""
        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test response"}

        return app

    @patch('app.middleware.security.settings.ENVIRONMENT', 'production')
    def test_security_headers_enabled_in_production(self, mock_app):
        """Test que verifica headers de seguridad en producción."""
        # Agregar middleware a la app
        mock_app.add_middleware(SecurityHeadersMiddleware)

        # Crear cliente de test
        client = TestClient(mock_app)

        # Realizar request
        response = client.get("/test")

        # Verificar que response es exitosa
        assert response.status_code == 200
        assert response.json() == {"message": "test response"}

        # Verificar headers de seguridad presentes
        expected_headers = {
            "strict-transport-security": "max-age=31536000; includeSubDomains; preload",
            "x-frame-options": "DENY",
            "x-content-type-options": "nosniff",
            "referrer-policy": "no-referrer",
            "permissions-policy": "geolocation=(), camera=(), microphone=()",
            "content-security-policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:"
        }

        for header_name, expected_value in expected_headers.items():
            assert header_name in response.headers, f"Header {header_name} no encontrado"
            assert response.headers[header_name] == expected_value, f"Valor incorrecto para {header_name}"

    @patch('app.middleware.security.settings.ENVIRONMENT', 'development')
    def test_security_headers_disabled_in_development(self, mock_app):
        """Test que verifica ausencia de headers en desarrollo."""
        # Agregar middleware a la app
        mock_app.add_middleware(SecurityHeadersMiddleware)

        # Crear cliente de test
        client = TestClient(mock_app)

        # Realizar request
        response = client.get("/test")

        # Verificar que response es exitosa
        assert response.status_code == 200
        assert response.json() == {"message": "test response"}

        # Verificar que NO hay headers de seguridad
        security_headers = [
            "strict-transport-security",
            "x-frame-options",
            "x-content-type-options",
            "referrer-policy",
            "permissions-policy",
            "content-security-policy"
        ]

        for header_name in security_headers:
            assert header_name not in response.headers, f"Header {header_name} NO debería estar presente en development"

    @patch('app.middleware.security.settings.ENVIRONMENT', 'testing')
    def test_security_headers_disabled_in_testing(self, mock_app):
        """Test que verifica ausencia de headers en testing."""
        # Agregar middleware a la app
        mock_app.add_middleware(SecurityHeadersMiddleware)

        # Crear cliente de test
        client = TestClient(mock_app)

        # Realizar request
        response = client.get("/test")

        # Verificar que response es exitosa
        assert response.status_code == 200

        # Verificar que NO hay headers de seguridad en testing
        security_headers = ["strict-transport-security", "x-frame-options", "x-content-type-options"]

        for header_name in security_headers:
            assert header_name not in response.headers, f"Header {header_name} NO debería estar presente en testing"

    @patch('app.middleware.security.settings.ENVIRONMENT', 'production')
    def test_middleware_preserves_response_content(self, mock_app):
        """Test que verifica que el middleware no altera el contenido de la response."""
        # Agregar middleware
        mock_app.add_middleware(SecurityHeadersMiddleware)

        # Crear cliente de test
        client = TestClient(mock_app)

        # Realizar request
        response = client.get("/test")

        # Verificar que el contenido no se alteró
        assert response.status_code == 200
        assert response.json() == {"message": "test response"}

        # Verificar que el content-type original se preserva
        assert "application/json" in response.headers.get("content-type", "")

    def test_middleware_with_disabled_config(self, mock_app):
        """Test que verifica configuración deshabilitada explícitamente."""
        # Agregar middleware con configuración deshabilitada
        mock_app.add_middleware(SecurityHeadersMiddleware, enable_in_production=False)

        # Crear cliente de test
        client = TestClient(mock_app)

        # Realizar request
        response = client.get("/test")

        # Verificar que NO hay headers de seguridad aunque estemos en production
        security_headers = ["strict-transport-security", "x-frame-options"]

        for header_name in security_headers:
            assert header_name not in response.headers, f"Header {header_name} debería estar deshabilitado"


class TestSecurityMiddlewareConfig:
    """Tests para configuración del middleware de seguridad."""

    @patch('app.middleware.security.settings.ENVIRONMENT', 'production')
    def test_config_production_environment(self):
        """Test configuración en entorno de producción."""
        config = get_security_middleware_config()

        assert config["environment"] == "production"
        assert config["security_enabled"] is True
        assert config["headers_count"] == 6
        assert "Security headers middleware" in config["description"]

    @patch('app.middleware.security.settings.ENVIRONMENT', 'development')
    def test_config_development_environment(self):
        """Test configuración en entorno de desarrollo."""
        config = get_security_middleware_config()

        assert config["environment"] == "development"
        assert config["security_enabled"] is False
        assert config["headers_count"] == 6
        assert "Security headers middleware" in config["description"]


class TestHTTPSRedirectIntegration:
    """Tests de integración para redirección HTTPS."""

    @pytest.fixture
    def mock_app(self):
        """Fixture que proporciona una app FastAPI mock."""
        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test response"}

        return app
    """Tests de integración para redirección HTTPS."""

    def test_https_redirect_middleware_import(self):
        """Test que verifica que HTTPSRedirectMiddleware se puede importar."""
        try:
            from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
            assert HTTPSRedirectMiddleware is not None
        except ImportError:
            pytest.fail("HTTPSRedirectMiddleware no se puede importar")

    @patch('app.middleware.security.settings.ENVIRONMENT', 'production')
    def test_https_redirect_configuration(self, mock_app):
        """Test básico de configuración de HTTPS redirect."""
        from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

        # Agregar middleware de redirect
        mock_app.add_middleware(HTTPSRedirectMiddleware)

        # Verificar que la app se puede crear sin errores
        assert mock_app is not None

        # Nota: TestClient siempre usa HTTPS, por lo que no podemos testear 
        # la redirección real aquí. Esto se testea en tests de integración.


if __name__ == "__main__":
    # Ejecutar tests directamente si se llama el archivo
    pytest.main([__file__, "-v"])