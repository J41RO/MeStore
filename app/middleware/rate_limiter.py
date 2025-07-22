# ~/app/middleware/rate_limiter.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Rate Limiting Middleware
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: rate_limiter.py
# Ruta: ~/app/middleware/rate_limiter.py
# Autor: Jairo
# Fecha de Creación: 2025-07-21
# Última Actualización: 2025-07-21
# Versión: 1.0.0
# Propósito: Middleware para rate limiting por IP y usuario usando Redis
#            Previene abuso de endpoints con límites configurables
#
# Modificaciones:
# 2025-07-21 - Implementación inicial con doble estrategia IP/Usuario
#
# ---------------------------------------------------------------------------------------------

"""
Rate Limiting Middleware para FastAPI

Implementa limitación de requests por IP (usuarios anónimos) y por user_id (usuarios autenticados).
Usa Redis como backend para contadores con TTL y soporta exclusiones configurables.

Características:
- Límites diferenciados: autenticados vs anónimos
- Exclusión de endpoints específicos (/health, /docs, etc.)
- Headers estándar HTTP para rate limiting
- Sliding window opcional con Redis
"""

import json
import time
from typing import Optional, Set, Tuple

import redis
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware para rate limiting basado en IP y usuario.

    Aplica límites diferenciados:
    - Usuarios autenticados: por user_id extraído del JWT
    - Usuarios anónimos: por IP del cliente

    Utiliza Redis para tracking con TTL automático.
    """

    def __init__(
        self,
        app: ASGIApp,
        redis_client: redis.Redis,
        authenticated_limit: int = 100,  # requests per minute para users autenticados
        anonymous_limit: int = 30,       # requests per minute para IPs anónimas
        window_seconds: int = 60,        # ventana de tiempo en segundos
        excluded_paths: Optional[Set[str]] = None
    ) -> None:
        super().__init__(app)
        self.redis_client = redis_client
        self.authenticated_limit = authenticated_limit
        self.anonymous_limit = anonymous_limit
        self.window_seconds = window_seconds

        # Paths excluidos por defecto
        default_excluded = {
            "/health",
            "/docs", 
            "/openapi.json",
            "/redoc",
            "/favicon.ico"
        }

        self.excluded_paths = excluded_paths or default_excluded

        logger.info(
            f"Rate Limiting configurado: auth={authenticated_limit}/min, "
            f"anon={anonymous_limit}/min, window={window_seconds}s"
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        """Procesa request aplicando rate limiting si corresponde."""

        # Verificar si path está excluido
        if self._is_excluded_path(request.url.path):
            return await call_next(request)

        # Determinar estrategia de rate limiting
        rate_key, limit = await self._get_rate_key_and_limit(request)

        if not rate_key:
            # Sin rate limiting (ej: error extrayendo user_id)
            logger.warning("Rate key no disponible, permitiendo request")
            return await call_next(request)

        # Aplicar rate limiting
        current_count, remaining, reset_time = await self._check_rate_limit(
            rate_key, limit
        )

        # Verificar si excede límite
        if current_count > limit:
            logger.warning(
                f"Rate limit excedido para {rate_key}: {current_count}/{limit}"
            )
            return self._create_rate_limit_response(remaining, reset_time)

        # Procesar request normalmente
        response = await call_next(request)

        # Agregar headers informativos
        self._add_rate_limit_headers(response, current_count, limit, remaining, reset_time)

        return response

    def _is_excluded_path(self, path: str) -> bool:
        """Verifica si el path está excluido del rate limiting."""
        return path in self.excluded_paths

    async def _get_rate_key_and_limit(self, request: Request) -> Tuple[Optional[str], int]:
        """
        Determina la clave de rate limiting y límite aplicable.

        Returns:
            Tuple de (rate_key, limit) o (None, 0) si no aplica rate limiting
        """
        # Intentar extraer user_id del JWT si está autenticado
        user_id = await self._extract_user_id_from_request(request)

        if user_id:
            # Usuario autenticado: usar user_id
            rate_key = f"rate_limit:user:{user_id}"
            limit = self.authenticated_limit
            logger.debug(f"Rate limiting por usuario: {user_id}"  )
        else:
            # Usuario anónimo: usar IP
            client_ip = self._get_client_ip(request)
            if not client_ip:
                return None, 0

            rate_key = f"rate_limit:ip:{client_ip}"
            limit = self.anonymous_limit
            logger.debug(f"Rate limiting por IP: {client_ip}")

        return rate_key, limit

    async def _extract_user_id_from_request(self, request: Request) -> Optional[str]:
        """Extrae user_id del JWT si está presente y válido."""
        try:
            # Buscar header Authorization
            auth_header = request.headers.get("authorization") or request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                return None

            # Extraer token
            token = auth_header.split(" ", 1)[1]

            # Importar JWT utilities (evitar circular imports)
            from app.core.security import decode_access_token

            # Decodificar token y extraer user_id
            payload = decode_access_token(token)
            if payload and "sub" in payload:
                return str(payload["sub"])

        except Exception as e:
            logger.debug(f"Error extrayendo user_id del token: {e}")

        return None

    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Extrae IP del cliente considerando proxies."""
        # Verificar headers de proxy comunes
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Tomar primera IP (cliente original)
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()

        # Fallback a IP directa
        if hasattr(request, "client") and request.client:
            return request.client.host

        return None

    async def _check_rate_limit(
        self, 
        rate_key: str, 
        limit: int
    ) -> Tuple[int, int, int]:
        """
        Verifica y actualiza contador de rate limiting en Redis.

        Returns:
            Tuple de (current_count, remaining, reset_time)
        """
        try:
            # Usar pipeline para operaciones atómicas
            pipe = self.redis_client.pipeline()

            # Incrementar contador
            pipe.incr(rate_key)

            # Establecer TTL solo si es nueva clave
            pipe.expire(rate_key, self.window_seconds)

            # Obtener TTL actual
            pipe.ttl(rate_key)

            # Ejecutar pipeline
            results = pipe.execute()

            current_count = results[0]
            ttl = results[2]

            # Calcular valores para headers
            remaining = max(0, limit - current_count)
            reset_time = int(time.time()) + max(ttl, 0)

            return current_count, remaining, reset_time

        except redis.RedisError as e:
            logger.error(f"Error Redis en rate limiting: {e}")
            # En caso de error Redis, permitir request (fail-open)
            return 0, limit, int(time.time()) + self.window_seconds

    def _create_rate_limit_response(self, remaining: int, reset_time: int) -> JSONResponse:
        """Crea respuesta 429 Too Many Requests con headers apropiados."""
        retry_after = reset_time - int(time.time())

        response_data = {
            "error": "Too Many Requests",
            "message": "Rate limit exceeded. Please try again later.",
            "retry_after_seconds": max(retry_after, 1)
        }

        response = JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=response_data
        )

        # Headers estándar de rate limiting
        response.headers["X-RateLimit-Limit"] = str(self.authenticated_limit)  # Usar límite genérico
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        response.headers["Retry-After"] = str(max(retry_after, 1))

        return response

    def _add_rate_limit_headers(
        self, 
        response: Response, 
        current_count: int, 
        limit: int, 
        remaining: int, 
        reset_time: int
    ) -> None:
        """Agrega headers informativos de rate limiting a response exitoso."""
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        response.headers["X-RateLimit-Used"] = str(current_count)