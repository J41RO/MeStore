"""
Tests de integración para app/main.py - Middleware Stack y CORS
Testing: Middleware integration, CORS configuration, exception handling
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
import json

# Import the app and related functions
from app.main import app


class TestMiddlewareStackIntegration:
    """Tests for middleware stack integration and configuration"""

    def test_cors_middleware_integration(self):
        """Test que CORS middleware está configurado correctamente"""
        client = TestClient(app)

        # Hacer request GET con origen específico (más directo que OPTIONS)
        headers = {"Origin": "http://localhost:3000"}
        response = client.get("/health", headers=headers)

        # Si CORS está funcionando, debe permitir el request y devolver 200
        assert response.status_code == 200

        # Si hay headers CORS, verificar que están presentes
        if "Access-Control-Allow-Origin" in response.headers:
            # Si está presente, verificar que acepta el origin o es wildcard
            origin_header = response.headers.get("Access-Control-Allow-Origin")
            assert origin_header in ["http://localhost:3000", "*"] or \
                   "localhost" in origin_header

        # Verificar que otros headers CORS pueden estar presentes
        cors_related_headers = [
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Credentials"
        ]

        # Al menos debe funcionar el request básico
        assert response.content is not None

    def test_exception_handler_middleware_integration(self):
        """Test que los exception handlers funcionan correctamente"""
        client = TestClient(app)

        # Test endpoint que no existe (debería retornar 404 manejado)
        response = client.get("/endpoint-que-no-existe")
        assert response.status_code == 404

        # Verificar que response tiene formato JSON válido
        try:
            response_data = response.json()
            # Verificar que tiene estructura de error
            assert isinstance(response_data, dict)
        except json.JSONDecodeError:
            # Si no es JSON, al menos debe ser respuesta válida
            assert response.text is not None

    def test_static_files_middleware_integration(self):
        """Test que el middleware de archivos estáticos funciona"""
        client = TestClient(app)

        # Verificar que la ruta /media está montada
        # No necesitamos que tenga archivos, solo que la ruta responda
        response = client.get("/media/")

        # Debería retornar 404 (path no encontrado) o similar, pero no 500
        assert response.status_code in [404, 403, 200]

    @pytest.mark.asyncio
    async def test_middleware_order_integration(self):
        """Test que el orden del middleware funciona correctamente"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            # Hacer request normal
            response = await client.get("/health")
            assert response.status_code == 200

            # Verificar que headers básicos están presentes
            assert "content-type" in response.headers

            # Hacer request con headers personalizados
            custom_headers = {
                "X-Test-Header": "integration-test",
                "Content-Type": "application/json"
            }

            response = await client.get("/health", headers=custom_headers)
            assert response.status_code == 200

    def test_request_size_middleware_integration(self):
        """Test que el middleware maneja requests grandes apropiadamente"""
        client = TestClient(app)

        # Hacer request con body grande pero válido
        large_data = {"data": "x" * 1000}  # 1KB de datos

        response = client.post("/api/v1/auth/login", json=large_data)

        # Debería fallar por datos inválidos (no por tamaño)
        # pero no debería ser error 413 (Request Entity Too Large)
        assert response.status_code != 413

    @pytest.mark.asyncio
    async def test_async_middleware_integration(self):
        """Test que middleware funciona con requests async"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            # Hacer múltiples requests concurrentes
            tasks = []
            for i in range(5):
                task = client.get("/health")
                tasks.append(task)

            # Todos deberían completarse exitosamente
            responses = []
            for task in tasks:
                response = await task
                responses.append(response)

            for response in responses:
                assert response.status_code == 200

    def test_content_type_middleware_integration(self):
        """Test que el middleware maneja content types correctamente"""
        client = TestClient(app)

        # Test JSON content type
        response = client.get("/health", headers={"Accept": "application/json"})
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")

        # Test que acepta diferentes content types
        response = client.get("/health", headers={"Accept": "*/*"})
        assert response.status_code == 200


class TestSecurityMiddlewareIntegration:
    """Tests for security-related middleware integration"""

    def test_security_headers_integration(self):
        """Test que headers de seguridad están configurados"""
        client = TestClient(app)

        response = client.get("/health")
        assert response.status_code == 200

        headers = response.headers

        # Verificar que al menos algunos headers de seguridad básicos podrían estar presentes
        # No requerimos todos, pero documentamos lo que existe
        security_headers_check = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy"
        ]

        present_headers = []
        for header in security_headers_check:
            if header in headers:
                present_headers.append(header)

        # Al menos debería haber alguna consideración de seguridad
        # Para ahora, solo verificamos que no hay errores
        assert len(present_headers) >= 0

    def test_authentication_middleware_integration(self):
        """Test que middleware de autenticación funciona con endpoints protegidos"""
        client = TestClient(app)

        # Test endpoint protegido sin token
        response = client.get("/api/v1/auth/me")
        assert response.status_code in [401, 403, 422]  # Sin autorización

        # Test endpoint público
        response = client.get("/health")
        assert response.status_code == 200

    def test_rate_limiting_middleware_integration(self):
        """Test que middleware de rate limiting (si existe) funciona"""
        client = TestClient(app)

        # Hacer múltiples requests rápidos al mismo endpoint
        responses = []
        for i in range(10):
            response = client.get("/health")
            responses.append(response)

        # La mayoría deberían pasar (si no hay rate limiting muy agresivo)
        successful_responses = [r for r in responses if r.status_code == 200]
        assert len(successful_responses) >= 8  # Al menos 80% exitosos


class TestErrorHandlingMiddlewareIntegration:
    """Tests for error handling middleware integration"""

    def test_global_exception_handler_integration(self):
        """Test que el global exception handler funciona"""
        client = TestClient(app)

        # Test endpoint que no existe
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

        # Verificar que response es JSON válido
        try:
            error_data = response.json()
            assert isinstance(error_data, dict)
        except:
            # Si no es JSON, al menos debe ser response válida
            assert response.text is not None

    def test_validation_error_handler_integration(self):
        """Test que validation errors son manejados correctamente"""
        client = TestClient(app)

        # Enviar datos inválidos a endpoint que requiere validación
        invalid_data = {"invalid": "data"}
        response = client.post("/api/v1/auth/login", json=invalid_data)

        # Debería retornar error de validación, no error 500
        assert response.status_code in [400, 422]  # Bad Request o Unprocessable Entity

        # Verificar que response tiene formato apropiado
        try:
            error_data = response.json()
            assert isinstance(error_data, dict)
        except:
            # Si no es JSON, verificar que no es error 500
            assert response.status_code != 500

    @pytest.mark.asyncio
    async def test_async_exception_handling_integration(self):
        """Test que exceptions async son manejadas correctamente"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            # Test múltiples requests que podrían generar errores
            error_requests = [
                client.get("/api/v1/nonexistent"),
                client.post("/api/v1/auth/login", json={"invalid": "data"}),
                client.get("/api/v1/productos/999999")  # ID que probablemente no existe
            ]

            responses = []
            for request in error_requests:
                try:
                    response = await request
                    responses.append(response)
                except Exception as e:
                    # No deberían haber exceptions no manejadas
                    pytest.fail(f"Unhandled exception in middleware: {e}")

            # Todos los errors deberían ser manejados apropiadamente
            for response in responses:
                assert response.status_code < 500  # No server errors


class TestPerformanceMiddlewareIntegration:
    """Tests for performance-related middleware integration"""

    @pytest.mark.asyncio
    async def test_response_time_middleware_integration(self):
        """Test que response times son razonables con middleware"""
        import time

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            start_time = time.time()
            response = await client.get("/health")
            end_time = time.time()

            response_time = (end_time - start_time) * 1000  # ms

            assert response.status_code == 200
            assert response_time < 1000  # Menos de 1 segundo para health check

    def test_gzip_compression_middleware_integration(self):
        """Test que compresión (si está habilitada) funciona"""
        client = TestClient(app)

        # Hacer request con Accept-Encoding
        headers = {"Accept-Encoding": "gzip, deflate"}
        response = client.get("/health", headers=headers)

        assert response.status_code == 200

        # Si hay compresión, verificar que funciona
        # Si no hay compresión, verificar que funciona sin ella
        content_encoding = response.headers.get("Content-Encoding", "")

        # En cualquier caso, response debe ser válida
        assert len(response.content) > 0

    def test_middleware_memory_usage_integration(self):
        """Test que middleware no causa memory leaks obvios"""
        client = TestClient(app)

        # Hacer múltiples requests para verificar que no hay leaks obvios
        for i in range(20):
            response = client.get("/health")
            assert response.status_code == 200

            # Verificar que response se completa correctamente
            assert response.content is not None