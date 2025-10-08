"""
Tests unitarios para app/main.py - Inicialización de FastAPI App
Testing: App creation, middleware setup, route registration
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
import subprocess

# Import the app and related functions
from app.main import app, lifespan, tags_metadata


class TestFastAPIAppInitialization:
    """Tests for FastAPI application initialization and configuration"""

    def test_app_instance_creation(self):
        """Test que la instancia de FastAPI se crea correctamente"""
        assert isinstance(app, FastAPI)
        assert app.title == "MeStore API - Fulfillment & Marketplace Colombia"
        assert app.version == "1.0.0"
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"
        assert app.openapi_url == "/openapi.json"

    def test_app_metadata_configuration(self):
        """Test que los metadatos del app están configurados correctamente"""
        assert "Enterprise-grade API for MeStore marketplace" in app.description
        assert "Production-ready architecture" in app.description
        assert "FastAPI" in app.description
        assert app.openapi_tags == tags_metadata

    def test_tags_metadata_structure(self):
        """Test que los tags metadata están bien definidos"""
        expected_tags = ["health", "embeddings", "logs", "marketplace", "agents"]
        actual_tags = [tag["name"] for tag in tags_metadata]

        for expected_tag in expected_tags:
            assert expected_tag in actual_tags

        # Verificar que cada tag tiene descripción
        for tag in tags_metadata:
            assert "name" in tag
            assert "description" in tag
            assert len(tag["description"]) > 0

    def test_app_includes_api_router(self):
        """Test que el router API está incluido con prefijo correcto"""
        # Verificar que hay rutas registradas con el prefijo /api/v1
        routes = [route.path for route in app.routes]
        api_routes = [route for route in routes if route.startswith("/api/v1")]
        assert len(api_routes) > 0

    def test_app_static_files_mount(self):
        """Test que los archivos estáticos están montados correctamente"""
        # Verificar que el mount para /media existe
        mounts = [mount for mount in app.routes if hasattr(mount, 'path') and mount.path == "/media"]
        assert len(mounts) > 0

    @pytest.mark.asyncio
    async def test_lifespan_startup_success(self):
        """Test que el lifespan maneja correctamente el startup (simplified version)"""
        mock_app = Mock()

        with patch('app.main.get_logger') as mock_logger:
            mock_logger.return_value.info = Mock()

            # Test simplified startup/shutdown cycle
            async with lifespan(mock_app):
                pass

            # Verificar que el logger fue usado
            assert mock_logger.called

    @pytest.mark.asyncio
    async def test_lifespan_startup_failure(self):
        """Test que el lifespan maneja correctamente errores de startup (simplified - no validation)"""
        mock_app = Mock()

        with patch('app.main.get_logger') as mock_logger:
            mock_logger.return_value.info = Mock()
            mock_logger.side_effect = Exception("Logger initialization failed")

            # Test que se lanza la excepción
            with pytest.raises(Exception, match="Logger initialization failed"):
                async with lifespan(mock_app):
                    pass

    @pytest.mark.asyncio
    async def test_lifespan_shutdown_cleanup(self):
        """Test que el lifespan hace cleanup en shutdown (simplified - just logs)"""
        mock_app = Mock()

        with patch('app.main.get_logger') as mock_logger:
            mock_logger.return_value.info = Mock()

            async with lifespan(mock_app):
                pass

            # Verificar que el logger fue usado
            assert mock_logger.called


class TestAppConfiguration:
    """Tests for application configuration and setup"""

    def test_app_has_exception_handlers(self):
        """Test que los exception handlers están registrados"""
        # Verificar que hay exception handlers registrados
        assert len(app.exception_handlers) > 0

        # Verificar que hay un handler para Exception
        assert Exception in app.exception_handlers or any(
            issubclass(Exception, exc_type) for exc_type in app.exception_handlers.keys()
        )

    def test_app_middleware_stack(self):
        """Test que el middleware stack está configurado"""
        # Verificar que hay middlewares configurados
        assert len(app.user_middleware) > 0 or len(app.middleware_stack) > 0

    def test_app_routes_basic_endpoints(self):
        """Test que los endpoints básicos están registrados"""
        routes = [route.path for route in app.routes]

        # Verificar endpoints básicos
        assert "/" in routes
        assert "/health" in routes
        assert "/health/services" in routes
        assert "/db-test" in routes
        assert "/users/test" in routes
        assert "/test-token" in routes