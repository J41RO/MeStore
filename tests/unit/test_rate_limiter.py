# ~/tests/unit/test_rate_limiter.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Rate Limiter Tests
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_rate_limiter.py
# Ruta: ~/tests/unit/test_rate_limiter.py
# Autor: Jairo
# Fecha de Creación: 2025-07-21
# Última Actualización: 2025-07-21
# Versión: 1.0.0
# Propósito: Tests unitarios para Rate Limiting Middleware
#            Verificar límites por IP, usuario, headers y exclusiones
#
# Modificaciones:
# 2025-07-21 - Tests completos con mocks Redis y JWT
#
# ---------------------------------------------------------------------------------------------

"""
Tests unitarios para Rate Limiting Middleware.

Verifica:
- Rate limiting por IP (usuarios anónimos)
- Rate limiting por user_id (usuarios autenticados)
- Headers HTTP correctos
- Exclusión de paths específicos
- Manejo de errores Redis
"""

import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.testclient import TestClient

from app.middleware.rate_limiter import RateLimitMiddleware


@pytest.fixture
def mock_redis():
    """Mock Redis client para tests."""
    redis_mock = MagicMock()

    # Configurar pipeline mock
    pipeline_mock = MagicMock()
    pipeline_mock.execute.return_value = [1, True, 60]  # count, set_result, ttl
    redis_mock.pipeline.return_value = pipeline_mock

    return redis_mock


@pytest.fixture
def app_with_rate_limiting(mock_redis):
    """App FastAPI con RateLimitMiddleware configurado."""
    app = FastAPI()

    # Agregar middleware
    app.add_middleware(
        RateLimitMiddleware,
        redis_client=mock_redis,
        authenticated_limit=5,  # Límite bajo para tests
        anonymous_limit=3,      # Límite bajo para tests
        window_seconds=60
    )

    # Endpoint de prueba
    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}

    # Endpoint excluido
    @app.get("/health")
    async def health_endpoint():
        return {"status": "ok"}

    return app


@pytest.fixture
def client(app_with_rate_limiting):
    """Test client para la app."""
    return TestClient(app_with_rate_limiting)


class TestRateLimitMiddleware:
    """Tests para RateLimitMiddleware."""

    def test_excluded_paths_no_rate_limiting(self, client, mock_redis):
        """Paths excluidos no deben aplicar rate limiting."""
        # Request a path excluido
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        # Redis no debe ser consultado
        mock_redis.pipeline.assert_not_called()

    def test_anonymous_rate_limiting_by_ip(self, client, mock_redis):
        """Usuarios anónimos deben usar rate limiting por IP."""
        # Configurar Redis mock
        pipeline_mock = mock_redis.pipeline.return_value
        pipeline_mock.execute.return_value = [2, True, 58]  # 2 requests, 58s TTL

        # Request sin autenticación
        response = client.get("/test")

        assert response.status_code == 200

        # Verificar headers de rate limiting
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Used" in response.headers

        # Verificar que se usó IP para rate limiting
        pipeline_mock.incr.assert_called_once()
        call_args = pipeline_mock.incr.call_args[0][0]
        assert call_args.startswith("rate_limit:ip:")

    @patch('app.core.security.decode_access_token')
    def test_authenticated_rate_limiting_by_user(self, mock_decode, client, mock_redis):
        """Usuarios autenticados deben usar rate limiting por user_id."""
        # Mock JWT decode
        mock_decode.return_value = {"sub": "user123"}

        # Configurar Redis mock
        pipeline_mock = mock_redis.pipeline.return_value
        pipeline_mock.execute.return_value = [1, True, 60]

        # Request con token JWT
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/test", headers=headers)

        assert response.status_code == 200

        # Verificar que se usó user_id para rate limiting
        pipeline_mock.incr.assert_called_once()
        call_args = pipeline_mock.incr.call_args[0][0]
        assert call_args == "rate_limit:user:user123"

    def test_rate_limit_exceeded_anonymous(self, client, mock_redis):
        """Exceder límite anónimo debe retornar 429."""
        # Configurar Redis mock para simular límite excedido
        pipeline_mock = mock_redis.pipeline.return_value
        pipeline_mock.execute.return_value = [4, True, 45]  # 4 > límite de 3

        # Request sin autenticación
        response = client.get("/test")

        assert response.status_code == 429

        response_data = response.json()
        assert response_data["error"] == "Too Many Requests"
        assert "retry_after_seconds" in response_data

        # Verificar headers
        assert "Retry-After" in response.headers
        assert "X-RateLimit-Remaining" in response.headers

    @patch('app.core.security.decode_access_token')
    def test_rate_limit_exceeded_authenticated(self, mock_decode, client, mock_redis):
        """Exceder límite autenticado debe retornar 429."""
        # Mock JWT decode
        mock_decode.return_value = {"sub": "user456"}

        # Configurar Redis mock para simular límite excedido
        pipeline_mock = mock_redis.pipeline.return_value
        pipeline_mock.execute.return_value = [6, True, 30]  # 6 > límite de 5

        # Request con token JWT
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/test", headers=headers)

        assert response.status_code == 429

        # Verificar que usó user_id en rate limiting
        pipeline_mock.incr.assert_called_once()
        call_args = pipeline_mock.incr.call_args[0][0]
        assert call_args == "rate_limit:user:user456"

    def test_invalid_jwt_falls_back_to_ip(self, client, mock_redis):
        """JWT inválido debe usar fallback a IP."""
        # Configurar Redis mock
        pipeline_mock = mock_redis.pipeline.return_value
        pipeline_mock.execute.return_value = [1, True, 60]

        # Request con token inválido
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/test")

        assert response.status_code == 200

        # Debe usar IP como fallback
        pipeline_mock.incr.assert_called_once()
        call_args = pipeline_mock.incr.call_args[0][0]
        assert call_args.startswith("rate_limit:ip:")

    def test_redis_error_allows_request(self, client, mock_redis):
        """Error Redis debe permitir request (fail-open)."""
        # Configurar Redis para generar error
        import redis
        mock_redis.pipeline.side_effect = redis.RedisError("Redis connection error")

        # Request debe proceder normalmente
        response = client.get("/test")

        assert response.status_code == 200
        assert response.json() == {"message": "success"}

    def test_rate_limit_headers_format(self, client, mock_redis):
        """Headers de rate limiting deben tener formato correcto."""
        # Configurar Redis mock
        pipeline_mock = mock_redis.pipeline.return_value
        pipeline_mock.execute.return_value = [2, True, 45]

        response = client.get("/test")

        assert response.status_code == 200

        # Verificar formato de headers
        assert int(response.headers["X-RateLimit-Limit"]) == 3  # Límite anónimo
        assert int(response.headers["X-RateLimit-Remaining"]) == 1  # 3 - 2
        assert int(response.headers["X-RateLimit-Used"]) == 2
        assert "X-RateLimit-Reset" in response.headers

    def test_x_forwarded_for_ip_extraction(self, client, mock_redis):
        """Debe extraer IP de header X-Forwarded-For si está presente."""
        # Configurar Redis mock
        pipeline_mock = mock_redis.pipeline.return_value
        pipeline_mock.execute.return_value = [1, True, 60]

        # Request con header X-Forwarded-For
        headers = {"X-Forwarded-For": "192.168.1.100, 10.0.0.1"}
        response = client.get("/test", headers=headers)

        assert response.status_code == 200

        # Debe usar primera IP del header
        pipeline_mock.incr.assert_called_once()
        call_args = pipeline_mock.incr.call_args[0][0]
        assert "192.168.1.100" in call_args


@pytest.mark.asyncio
class TestRateLimitMiddlewareAsync:
    """Tests asíncronos adicionales."""

    @patch('app.core.security.decode_access_token')
    async def test_concurrent_requests_same_user(self, mock_decode, mock_redis):
        """Requests concurrentes del mismo usuario deben incrementar contador."""
        mock_decode.return_value = {"sub": "user789"}

        # Configurar Redis mock para múltiples requests
        pipeline_mock = mock_redis.pipeline.return_value
        pipeline_mock.execute.side_effect = [
            [1, True, 60],  # Primera request
            [2, True, 59],  # Segunda request
            [3, True, 58],  # Tercera request
        ]

        # Simular múltiples requests
        app = FastAPI()
        middleware = RateLimitMiddleware(
            app=app,
            redis_client=mock_redis,
            authenticated_limit=5,
            anonymous_limit=3
        )

        # Mock request con JWT
        request = MagicMock()
        request.url.path = "/test"
        request.headers.get.return_value = "Bearer valid_token"

        # Mock call_next
        async def mock_call_next(req):
            return JSONResponse({"message": "success"})

        # Ejecutar múltiples requests
        for i in range(3):
            response = await middleware.dispatch(request, mock_call_next)
            assert response.status_code == 200

        # Verificar que Redis fue llamado 3 veces
        assert pipeline_mock.incr.call_count == 3