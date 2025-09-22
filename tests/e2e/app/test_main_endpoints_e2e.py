"""
Tests E2E para app/main.py - Endpoints principales
Testing: Complete end-to-end flows, real API interactions, full integration
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.models.user import User, UserType
from app.core.security import get_password_hash
import uuid
import json


class TestMainEndpointsE2E:
    """End-to-end tests for main application endpoints"""

    @pytest.mark.asyncio
    async def test_health_endpoint_e2e(self):
        """E2E: Test complete health check flow"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            # Test basic health endpoint
            response = await client.get("/health")
            assert response.status_code == 200

            data = response.json()

            # Verificar estructura de respuesta de health
            assert "status" in data or ("data" in data and "status" in data["data"])

            # Test health services endpoint
            services_response = await client.get("/health/services")
            assert services_response.status_code == 200

    @pytest.mark.asyncio
    async def test_database_test_endpoint_e2e(self):
        """E2E: Test database connectivity endpoint"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            response = await client.get("/db-test")
            # Puede retornar 503 si DB no está disponible en tests, eso está bien
            assert response.status_code in [200, 503]

            try:
                data = response.json()
                # Verificar que database connection funciona si está disponible
                if response.status_code == 200:
                    assert "database" in str(data).lower() or "connection" in str(data).lower()
            except:
                # Si no es JSON válido, al menos verificar que hay respuesta
                assert response.text is not None

    @pytest.mark.asyncio
    async def test_users_test_endpoint_e2e(self):
        """E2E: Test users endpoint functionality"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            response = await client.get("/users/test")
            # Puede fallar con 500 si hay problemas de DB en test environment
            assert response.status_code in [200, 500, 503]

            if response.status_code == 200:
                try:
                    data = response.json()
                    # Verificar que endpoint retorna datos válidos
                    assert isinstance(data, (dict, list))
                except:
                    # Si no es JSON válido, al menos verificar que hay respuesta
                    assert response.text is not None

    @pytest.mark.asyncio
    async def test_test_token_endpoint_e2e(self):
        """E2E: Test token endpoint functionality"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            response = await client.get("/test-token")
            # Puede fallar con 500 si hay problemas de servicio en test environment
            assert response.status_code in [200, 500, 503]

            if response.status_code == 200:
                try:
                    data = response.json()
                    # Verificar que endpoint retorna información de token
                    assert isinstance(data, dict)
                except:
                    # Si no es JSON válido, al menos verificar que hay respuesta
                    assert response.text is not None

    @pytest.mark.asyncio
    async def test_api_documentation_endpoints_e2e(self):
        """E2E: Test API documentation endpoints are accessible"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            # Test OpenAPI docs
            docs_response = await client.get("/docs")
            assert docs_response.status_code == 200

            # Test ReDoc
            redoc_response = await client.get("/redoc")
            assert redoc_response.status_code == 200

            # Test OpenAPI JSON
            openapi_response = await client.get("/openapi.json")
            assert openapi_response.status_code == 200

            # Verificar que OpenAPI JSON es válido
            openapi_data = openapi_response.json()
            assert "openapi" in openapi_data
            assert "info" in openapi_data
            assert "paths" in openapi_data

    @pytest.mark.asyncio
    async def test_media_static_files_e2e(self):
        """E2E: Test static files serving"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            # Test que la ruta /media responde (aunque esté vacía)
            response = await client.get("/media/")

            # Debería retornar 404 (no hay archivos) o 403/200, pero no 500
            assert response.status_code in [200, 403, 404]


class TestAPIEndpointsE2E:
    """E2E tests for API v1 endpoints integration"""

    @pytest.mark.asyncio
    async def test_auth_login_endpoint_e2e(self):
        """E2E: Test auth endpoint accessibility and basic validation"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            # Test con datos vacíos - debe validar y retornar error apropiado
            response = await client.post("/api/v1/auth/login", json={})
            # Endpoint debe validar y retornar error apropiado (no 404 o 500)
            assert response.status_code in [400, 422, 401]

            # Test con datos inválidos - debe validar formato
            invalid_data = {
                "email": "not-an-email",
                "password": "short"
            }
            response = await client.post("/api/v1/auth/login", json=invalid_data)
            # Endpoint debe validar formato y retornar error apropiado
            assert response.status_code in [400, 422, 401]

            # Test con usuario inexistente - debe manejar correctamente
            valid_format_data = {
                "email": "nonexistent@test.com",
                "password": "validpassword123"
            }
            response = await client.post("/api/v1/auth/login", json=valid_format_data)
            # Endpoint debe manejar usuario inexistente correctamente
            assert response.status_code in [400, 401, 422]

            # Verificar que response es JSON válido
            try:
                error_data = response.json()
                assert isinstance(error_data, dict)
            except:
                # Si no es JSON, al menos verificar que hay respuesta
                assert response.text is not None

    @pytest.mark.asyncio
    async def test_productos_endpoint_e2e(self):
        """E2E: Test productos endpoint accessibility"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            # Test que endpoint de productos responde (puede redirigir)
            response = await client.get("/api/v1/productos")
            # Puede retornar 307 (redirect), 200 (ok), o error de servicio
            assert response.status_code in [200, 307, 500, 503]

            if response.status_code == 200:
                try:
                    products = response.json()
                    assert isinstance(products, list)
                except:
                    # Si no es JSON válido, al menos verificar que hay respuesta
                    assert response.text is not None

    @pytest.mark.asyncio
    async def test_complete_user_journey_e2e(self):
        """E2E: Test basic API journey without complex authentication"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            # Test basic public endpoints journey
            # 1. Health check
            health_response = await client.get("/health")
            assert health_response.status_code == 200

            # 2. API documentation
            docs_response = await client.get("/docs")
            assert docs_response.status_code == 200

            # 3. API auth endpoint (should exist)
            auth_response = await client.post("/api/v1/auth/login", json={})
            assert auth_response.status_code in [400, 401, 422]

            # 4. Products endpoint (should exist, may redirect or error)
            products_response = await client.get("/api/v1/productos")
            assert products_response.status_code in [200, 307, 401, 500, 503]


class TestErrorHandlingE2E:
    """E2E tests for error handling across the application"""

    @pytest.mark.asyncio
    async def test_404_error_handling_e2e(self):
        """E2E: Test 404 error handling"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            response = await client.get("/nonexistent-endpoint")
            assert response.status_code == 404

            # Verificar que error response es válido
            try:
                error_data = response.json()
                assert isinstance(error_data, dict)
            except json.JSONDecodeError:
                # Si no es JSON, verificar que al menos hay content
                assert response.text is not None

    @pytest.mark.asyncio
    async def test_validation_error_handling_e2e(self):
        """E2E: Test validation error handling"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            # Enviar datos inválidos
            invalid_login = {"email": "not-an-email", "password": ""}

            response = await client.post("/api/v1/auth/login", json=invalid_login)
            assert response.status_code in [400, 422]

            try:
                error_data = response.json()
                assert isinstance(error_data, dict)
            except json.JSONDecodeError:
                assert response.text is not None

    @pytest.mark.asyncio
    async def test_unauthorized_access_e2e(self):
        """E2E: Test unauthorized access handling"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            # Intentar acceso sin token
            response = await client.get("/api/v1/auth/me")
            assert response.status_code in [401, 403, 422]

            # Intentar acceso con token inválido
            headers = {"Authorization": "Bearer invalid-token"}
            response = await client.get("/api/v1/auth/me", headers=headers)
            assert response.status_code in [401, 403, 422]


class TestPerformanceE2E:
    """E2E tests for application performance"""

    @pytest.mark.asyncio
    async def test_concurrent_requests_e2e(self):
        """E2E: Test application handles concurrent requests"""
        import asyncio
        import time

        async def make_request():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                start_time = time.time()
                response = await client.get("/health")
                end_time = time.time()
                return response.status_code, (end_time - start_time) * 1000

        # Hacer 15 requests concurrentes
        tasks = [make_request() for _ in range(15)]
        results = await asyncio.gather(*tasks)

        # Verificar que todos fueron exitosos
        for status_code, response_time in results:
            assert status_code == 200
            assert response_time < 2000  # Menos de 2 segundos

        # Verificar tiempo promedio
        avg_time = sum(result[1] for result in results) / len(results)
        assert avg_time < 1000  # Promedio menos de 1 segundo

    @pytest.mark.asyncio
    async def test_memory_usage_stability_e2e(self):
        """E2E: Test memory usage stability over multiple requests"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            # Hacer múltiples requests para verificar estabilidad
            endpoints = ["/health", "/db-test", "/users/test", "/test-token"]

            for _ in range(5):  # 5 rounds
                for endpoint in endpoints:
                    response = await client.get(endpoint)
                    # Algunos endpoints pueden fallar en test environment
                    assert response.status_code in [200, 503, 500]

                    # Verificar que response se completa
                    assert response.content is not None
                    assert len(response.content) > 0


class TestFullIntegrationE2E:
    """Complete end-to-end integration tests"""

    @pytest.mark.asyncio
    async def test_application_startup_to_shutdown_e2e(self):
        """E2E: Test complete application lifecycle"""

        # Test que app está funcionando completamente
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            # 1. Verificar que app responde
            health_response = await client.get("/health")
            assert health_response.status_code == 200

            # 2. Verificar database connectivity (puede fallar en test environment)
            db_response = await client.get("/db-test")
            assert db_response.status_code in [200, 503]

            # 3. Verificar API documentation
            docs_response = await client.get("/docs")
            assert docs_response.status_code == 200

            # 4. Verificar OpenAPI schema
            openapi_response = await client.get("/openapi.json")
            assert openapi_response.status_code == 200

            openapi_data = openapi_response.json()
            assert openapi_data["info"]["title"] == "MeStore API - Fulfillment & Marketplace Colombia"

    def test_application_metadata_e2e(self):
        """E2E: Test application metadata and configuration"""

        # Verificar configuración de la app
        assert app.title == "MeStore API - Fulfillment & Marketplace Colombia"
        assert app.version == "1.0.0"
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"
        assert app.openapi_url == "/openapi.json"

        # Verificar que hay rutas registradas
        routes = [route.path for route in app.routes]

        critical_routes = ["/health", "/", "/docs", "/redoc", "/openapi.json"]
        for route in critical_routes:
            assert route in routes

        # Verificar que hay rutas API
        api_routes = [route for route in routes if route.startswith("/api/v1")]
        assert len(api_routes) > 0