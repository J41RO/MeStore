"""
~/app/middleware/logging.py
-------------------------------------------------------------------------------------
MeStore - Middleware de Logging para Requests FastAPI (VERSIÓN CORREGIDA)
Copyright (c) 2025 Jairo. Todos los derechos reservados.
Licensed under proprietary license in LICENSE file.
-------------------------------------------------------------------------------------

Nombre del Archivo: logging.py
Ruta: ~/app/middleware/logging.py
Autor: Jairo
Fecha de Creación: 2025-07-19
Última Actualización: 2025-07-19
Versión: 2.0.0
Propósito: Middleware FUNCIONAL para registrar requests usando structlog

Modificaciones:
2025-07-19 - Implementación inicial (v1.0.0) - FALLÓ
2025-07-19 - Reescritura completa usando BaseHTTPMiddleware correctamente (v2.0.0)
-------------------------------------------------------------------------------------
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logger import get_logger

# Instancia del logger estructurado
logger = get_logger(__name__)


# Constantes para logging de bodies
MAX_BODY_SIZE = 10 * 1024  # 10KB máximo
EXCLUDED_PATHS = {"/docs", "/openapi.json", "/health", "/ready"}
JSON_CONTENT_TYPES = {"application/json", "application/ld+json"}
TEXT_CONTENT_TYPES = {"text/plain", "text/html", "text/css", "text/javascript"}


def _should_log_body(path: str, content_type: str = None) -> bool:
    """
    Determina si se debe loguear el body basado en path y content-type.

    Args:
        path: URL path del request
        content_type: Content-Type header

    Returns:
        bool: True si se debe loguear el body
    """
    # Excluir paths específicos
    if path in EXCLUDED_PATHS:
        return False

    # Si no hay content-type, no loguear
    if not content_type:
        return False

    # Normalizar content-type (remover charset, etc.)
    content_type = content_type.split(';')[0].strip().lower()

    # Permitir solo tipos seguros para logging
    allowed_types = JSON_CONTENT_TYPES | TEXT_CONTENT_TYPES
    return content_type in allowed_types


def _parse_body_safely(body_bytes: bytes, content_type: str = None) -> str | dict | None:
    """
    Parsea el body de forma segura según su content-type.

    Args:
        body_bytes: Raw bytes del body
        content_type: Content-Type header

    Returns:
        str | dict | None: Body parseado o None si no se puede parsear
    """
    if not body_bytes:
        return None

    # Limitar tamaño
    if len(body_bytes) > MAX_BODY_SIZE:
        truncated_body = body_bytes[:MAX_BODY_SIZE].decode('utf-8', errors='replace')
        return f"{truncated_body}... [truncated - original size: {len(body_bytes)} bytes]"

    try:
        body_str = body_bytes.decode('utf-8')

        # Intentar parsear como JSON si es application/json
        if content_type and 'application/json' in content_type.lower():
            try:
                import json
                return json.loads(body_str)
            except json.JSONDecodeError:
                # Si falla JSON parsing, devolver como string
                return body_str

        # Para otros tipos, devolver como string
        return body_str

    except UnicodeDecodeError:
        # Si no se puede decodificar, no loguear
        return None


async def _capture_response_body(response: Response) -> tuple[Response, str | dict | None]:
    """
    Captura el body del response sin consumir el stream.

    Args:
        response: Response de FastAPI

    Returns:
        tuple: (response_modificado, body_parseado)
    """
    # Obtener content-type del response
    content_type = response.headers.get('content-type', '')

    # Verificar si debemos loguear este response
    if not _should_log_body('', content_type):
        return response, None

    # Leer el body del response
    response_body = b''
    async for chunk in response.body_iterator:
        response_body += chunk

    # Parsear el body
    parsed_body = _parse_body_safely(response_body, content_type)

    # Crear nuevo response con el mismo contenido
    new_response = Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )

    return new_response, parsed_body


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware de logging para FastAPI usando BaseHTTPMiddleware CORRECTAMENTE.

    Este middleware registra automáticamente cada request con:
    - Método HTTP y URL completa
    - IP del cliente y User-Agent
    - Duración de procesamiento en milisegundos
    - Código de respuesta HTTP
    - Usuario autenticado (si existe)
    - Manejo completo de errores
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Método dispatch que maneja cada request/response.

        Args:
            request: Request de FastAPI
            call_next: Siguiente handler en la cadena

        Returns:
            Response: Respuesta HTTP procesada
        """
        # Marcar inicio de procesamiento
        start_time = time.monotonic()

        # Extraer información del request
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "Unknown")
        method = request.method
        url_path = str(request.url.path)
        query_string = str(request.url.query) if request.url.query else None

        # Construir contexto base para logging
        log_context = {
            "method": method,
            "path": url_path,
            "client_ip": client_ip,
            "user_agent": user_agent,
        }

        # Agregar query string si existe
        if query_string:
            log_context["query_string"] = query_string

        # Capturar request body de forma segura
        request_body = None
        content_type = request.headers.get("content-type", "")

        if _should_log_body(url_path, content_type):
            try:
                body_bytes = await request.body()
                request_body = _parse_body_safely(body_bytes, content_type)
                if request_body is not None:
                    log_context["request_body"] = request_body
            except Exception as e:
                # Si falla la captura del body, no romper el middleware
                logger.bind(**log_context).warning(
                    "Failed to capture request body",
                    error_type=type(e).__name__,
                    error_message=str(e)
                )

        # Detectar usuario autenticado
        user_info = self._get_user_info(request)
        if user_info:
            log_context["authenticated_user"] = user_info

        # Log de request iniciado
        logger.bind(**log_context).info("HTTP request started")

        try:
            # Procesar request a través de la cadena
            # Procesar request y capturar response con body
            original_response = await call_next(request)
            response, response_body = await _capture_response_body(original_response)

            # Calcular tiempo de procesamiento
            process_time = time.monotonic() - start_time
            duration_ms = round(process_time * 1000, 2)

            # Contexto extendido para response
            response_context = {
                **log_context,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "response_body": response_body,
            }

            # Log de request completado exitosamente
            logger.bind(**response_context).info(
                "HTTP request completed successfully"
            )

            # Agregar header con tiempo de procesamiento
            response.headers["X-Process-Time"] = str(duration_ms)

            return response

        except Exception as exc:
            # Calcular tiempo hasta el error
            process_time = time.monotonic() - start_time
            duration_ms = round(process_time * 1000, 2)

            # Contexto para logging de error
            error_context = {
                **log_context,
                "duration_ms": duration_ms,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
            }

            # Log detallado del error
            logger.bind(**error_context).error(
                "HTTP request failed with exception",
                exc_info=True,
            )
            # Re-lanzar excepción para que sea manejada por FastAPI
            raise

    def _get_client_ip(self, request: Request) -> str:
        """
        Obtiene la IP real del cliente, considerando proxies.

        Args:
            request: Request de FastAPI

        Returns:
            str: IP del cliente
        """
        # Verificar headers de proxy en orden de prioridad
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # X-Forwarded-For puede tener múltiples IPs separadas por coma
            return forwarded_for.split(",")[0].strip()

        # Header alternativo
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()

        # Fallback al client directo
        if request.client and request.client.host:
            return request.client.host

        return "unknown"

    def _get_user_info(self, request: Request) -> str | None:
        """
        Extrae información del usuario autenticado si está disponible.

        Args:
            request: Request de FastAPI

        Returns:
            str | None: Información del usuario o None
        """
        # Verificar request.state.user (patrón común en FastAPI)
        if hasattr(request.state, "user") and request.state.user:
            user = request.state.user

            # Extraer identificador según tipo de objeto
            if hasattr(user, "email"):
                return user.email
            elif hasattr(user, "username"):
                return user.username
            elif hasattr(user, "id"):
                return f"user_id:{user.id}"
            elif isinstance(user, (str, int)):
                return str(user)
            else:
                return repr(user)

        # Verificar header Authorization para debugging
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            # No loggear el token por seguridad, solo indicar que existe
            return "authenticated_via_bearer_token"

        return None