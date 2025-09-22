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
from app.main import app, lifespan, validate_migrations_on_startup, tags_metadata


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
        assert "Python 3.11 + FastAPI" in app.description
        assert "http://192.168.1.137:8000" in app.description
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
        """Test que el lifespan maneja correctamente el startup"""
        mock_app = Mock()

        with patch('app.main.get_service_container') as mock_container, \
             patch('app.main.validate_migrations_on_startup') as mock_migrations, \
             patch('app.main.setup_log_rotation') as mock_log_rotation, \
             patch('app.main.get_logger') as mock_logger:

            mock_logger.return_value.info = Mock()
            mock_logger.return_value.error = Mock()
            mock_container.return_value = AsyncMock()
            mock_migrations.return_value = None
            mock_log_rotation.return_value = None

            # Test startup
            async with lifespan(mock_app):
                pass

            # Verificar que se llamaron las funciones de inicialización
            # get_service_container se llama 2 veces: startup y shutdown
            assert mock_container.call_count == 2
            mock_migrations.assert_called_once()
            mock_log_rotation.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_startup_failure(self):
        """Test que el lifespan maneja correctamente errores de startup"""
        mock_app = Mock()

        with patch('app.main.get_service_container') as mock_container, \
             patch('app.main.get_logger') as mock_logger:

            mock_logger.return_value.info = Mock()
            mock_logger.return_value.error = Mock()
            mock_container.side_effect = Exception("Service container failed")

            # Test que se lanza la excepción
            with pytest.raises(Exception, match="Service container failed"):
                async with lifespan(mock_app):
                    pass

    @pytest.mark.asyncio
    async def test_lifespan_shutdown_cleanup(self):
        """Test que el lifespan hace cleanup en shutdown"""
        mock_app = Mock()
        mock_container_instance = AsyncMock()

        with patch('app.main.get_service_container') as mock_container, \
             patch('app.main.validate_migrations_on_startup'), \
             patch('app.main.setup_log_rotation'), \
             patch('app.main.get_logger') as mock_logger:

            mock_logger.return_value.info = Mock()
            mock_logger.return_value.error = Mock()
            mock_container.return_value = mock_container_instance

            async with lifespan(mock_app):
                pass

            # Verificar que se llamó cleanup en shutdown
            mock_container_instance.cleanup.assert_called_once()


class TestMigrationValidation:
    """Tests for migration validation functionality"""

    @pytest.mark.asyncio
    async def test_validate_migrations_success_production(self):
        """Test validación exitosa de migraciones en producción"""
        with patch('app.main.settings') as mock_settings, \
             patch('subprocess.run') as mock_subprocess, \
             patch('app.main.get_logger') as mock_logger:

            mock_settings.ENVIRONMENT = "production"
            mock_logger.return_value.info = Mock()
            mock_logger.return_value.error = Mock()

            # Mock successful subprocess calls
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "abc123"
            mock_subprocess.return_value = mock_result

            # No debería lanzar excepción
            await validate_migrations_on_startup()

            # Verificar que se llamó subprocess 2 veces (current y heads)
            assert mock_subprocess.call_count == 2

    @pytest.mark.asyncio
    async def test_validate_migrations_pending_production(self):
        """Test que lanza error en producción con migraciones pendientes"""
        with patch('app.main.settings') as mock_settings, \
             patch('subprocess.run') as mock_subprocess, \
             patch('app.main.get_logger') as mock_logger:

            mock_settings.ENVIRONMENT = "production"
            mock_logger.return_value.info = Mock()
            mock_logger.return_value.error = Mock()

            # Mock different revisions (pending migration)
            mock_result_current = Mock()
            mock_result_current.returncode = 0
            mock_result_current.stdout = "abc123"

            mock_result_head = Mock()
            mock_result_head.returncode = 0
            mock_result_head.stdout = "def456"  # Different revision

            mock_subprocess.side_effect = [mock_result_current, mock_result_head]

            # Debería lanzar RuntimeError en producción
            with pytest.raises(RuntimeError, match="CRÍTICO.*migraciones pendientes"):
                await validate_migrations_on_startup()

    @pytest.mark.asyncio
    async def test_validate_migrations_pending_development(self):
        """Test que solo advierte en development con migraciones pendientes"""
        with patch('app.main.settings') as mock_settings, \
             patch('subprocess.run') as mock_subprocess, \
             patch('app.main.get_logger') as mock_logger:

            mock_settings.ENVIRONMENT = "development"
            mock_logger.return_value.info = Mock()
            mock_logger.return_value.warning = Mock()

            # Mock different revisions (pending migration)
            mock_result_current = Mock()
            mock_result_current.returncode = 0
            mock_result_current.stdout = "abc123"

            mock_result_head = Mock()
            mock_result_head.returncode = 0
            mock_result_head.stdout = "def456"  # Different revision

            mock_subprocess.side_effect = [mock_result_current, mock_result_head]

            # No debería lanzar excepción en development
            await validate_migrations_on_startup()

            # Debería loggear warning
            mock_logger.return_value.warning.assert_called()

    @pytest.mark.asyncio
    async def test_validate_migrations_subprocess_timeout(self):
        """Test manejo de timeout en validación de migraciones"""
        with patch('app.main.settings') as mock_settings, \
             patch('subprocess.run') as mock_subprocess, \
             patch('app.main.get_logger') as mock_logger:

            mock_settings.ENVIRONMENT = "production"
            mock_logger.return_value.error = Mock()

            # Mock subprocess timeout
            mock_subprocess.side_effect = subprocess.TimeoutExpired("alembic", 30)

            # Debería lanzar RuntimeError en producción
            with pytest.raises(RuntimeError, match="Timeout validando migraciones"):
                await validate_migrations_on_startup()

    @pytest.mark.asyncio
    async def test_validate_migrations_subprocess_error(self):
        """Test manejo de error en comando subprocess"""
        with patch('app.main.settings') as mock_settings, \
             patch('subprocess.run') as mock_subprocess, \
             patch('app.main.get_logger') as mock_logger:

            mock_settings.ENVIRONMENT = "production"
            mock_logger.return_value.error = Mock()

            # Mock subprocess error
            mock_result = Mock()
            mock_result.returncode = 1  # Error code
            mock_subprocess.return_value = mock_result

            # Debería lanzar RuntimeError en producción
            with pytest.raises(RuntimeError, match="No se puede validar migraciones"):
                await validate_migrations_on_startup()


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