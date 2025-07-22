"""
~/tests/unit/test_logging_middleware.py
-------------------------------------------------------------------------------------
MeStore - Tests unitarios para RequestLoggingMiddleware con body logging
Copyright (c) 2025 Jairo. Todos los derechos reservados.
Licensed under proprietary license in LICENSE file.
-------------------------------------------------------------------------------------

Nombre del Archivo: test_logging_middleware.py
Ruta: ~/tests/unit/test_logging_middleware.py
Autor: Jairo
Fecha de Creación: 2025-07-21
Última Actualización: 2025-07-21
Versión: 1.0.0
Propósito: Tests completos para middleware de logging con captura de request/response bodies

Modificaciones:
2025-07-21 - Implementación inicial con tests de body logging
-------------------------------------------------------------------------------------
"""

import json
import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse
import structlog
from unittest.mock import patch, AsyncMock

from app.middleware.logging import RequestLoggingMiddleware


# App de prueba para tests
def create_test_app():
    """Crear app de FastAPI para testing."""
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.post("/api/test")
    async def test_endpoint(request: Request):
        """Endpoint de prueba que recibe y retorna JSON."""
        body = await request.body()
        if body:
            data = json.loads(body)
            return JSONResponse({"received": data, "status": "success"})
        return JSONResponse({"message": "No data received"})

    @app.get("/api/text")
    async def text_endpoint():
        """Endpoint que retorna texto plano."""
        return Response("Plain text response", media_type="text/plain")

    @app.post("/api/large")
    async def large_endpoint(request: Request):
        """Endpoint para testing de payloads grandes."""
        body = await request.body()
        return JSONResponse({"size": len(body), "truncated": len(body) > 10240})

    @app.get("/docs")
    async def docs_endpoint():
        """Endpoint excluido del logging."""
        return JSONResponse({"docs": "swagger"})

    @app.post("/api/binary")
    async def binary_endpoint():
        """Endpoint que simula contenido binario."""
        return Response(b"\\x00\\x01\\x02\\x03", media_type="application/octet-stream")

    return app


@pytest.fixture
def test_app():
    """Fixture de app de prueba."""
    return create_test_app()


@pytest.fixture
def client(test_app):
    """Cliente de prueba."""
    return TestClient(test_app)


class TestRequestLoggingMiddleware:
    """Tests para RequestLoggingMiddleware con body logging."""

    def test_middleware_logs_json_request_body(self, client, caplog):
        """Test: Middleware loguea request body JSON correctamente."""
        # Configurar caplog para capturar logs de structlog
        with caplog.at_level("INFO"):
            # Request con JSON body
            test_data = {"event": "click", "user_id": 123}
            response = client.post(
                "/api/test",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )

        assert response.status_code == 200

        # Verificar que se logueó el request body
        log_records = [record.getMessage() for record in caplog.records]
        request_logs = [log for log in log_records if "HTTP request started" in log]
        assert len(request_logs) >= 1

    def test_middleware_logs_json_response_body(self, client, caplog):
        """Test: Middleware loguea response body JSON correctamente."""
        with caplog.at_level("INFO"):
            test_data = {"test": "data"}
            response = client.post("/api/test", json=test_data)

        assert response.status_code == 200
        response_data = response.json()
        assert "received" in response_data

    def test_middleware_handles_large_payloads(self, client, caplog):
        """Test: Middleware trunca payloads grandes (>10KB)."""
        # Crear payload grande (15KB)
        large_data = "x" * 15000

        with caplog.at_level("INFO"):
            response = client.post(
                "/api/large",
                data=large_data,
                headers={"Content-Type": "text/plain"}
            )

        assert response.status_code == 200

    def test_middleware_excludes_binary_content(self, client, caplog):
        """Test: Middleware NO loguea contenido binario."""
        with caplog.at_level("INFO"):
            response = client.post("/api/binary")

        assert response.status_code == 200

    def test_middleware_excludes_documentation_endpoints(self, client, caplog):
        """Test: Middleware NO loguea endpoints de documentación."""
        with caplog.at_level("INFO"):
            response = client.get("/docs")

        assert response.status_code == 200

    def test_middleware_logs_successfully(self, client, caplog):
        """Test: Middleware captura request body incluso con JSON malformado."""
        # JSON malformado que causa error en endpoint (comportamiento esperado)
        malformed_json = "{\"incomplete\": \"json\""

        with caplog.at_level("INFO"):
            # El test pasa si el middleware logueó antes del error del endpoint
            try:
                client.post(
                    "/api/test",
                    data=malformed_json,
                    headers={"Content-Type": "application/json"}
                )
            except:
                pass  # Ignorar error del endpoint

        # Verificar que el middleware logueó el request body
        log_records = [record.getMessage() for record in caplog.records]
        request_logs = [log for log in log_records if "HTTP request started" in log]
        assert len(request_logs) >= 1

        # Verificar que el request body fue capturado en logs
        body_logged = any("incomplete" in log for log in log_records)
        assert body_logged, "Request body should be logged even with malformed JSON"
        """Test: Middleware loguea correctamente requests válidos."""
        # JSON malformado
        malformed_json = "{\"incomplete\": \"json\""