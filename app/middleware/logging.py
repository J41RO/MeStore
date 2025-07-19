"""
~/app/middleware/logging.py
-------------------------------------------------------------------------------------
MeStore - Middleware de Logging para Requests FastAPI (VERSIÓN CORREGIDA)
Copyright (c) 2025 Jairo. Todos los derechos reservados.
Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
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
        
        # Detectar usuario autenticado
        user_info = self._get_user_info(request)
        if user_info:
            log_context["authenticated_user"] = user_info
        
        # Log de request iniciado
        logger.bind(**log_context).info(
            "HTTP request started",
            event="request_started"
        )
        
        try:
            # Procesar request a través de la cadena
            response = await call_next(request)
            
            # Calcular tiempo de procesamiento
            process_time = time.monotonic() - start_time
            duration_ms = round(process_time * 1000, 2)
            
            # Contexto extendido para response
            response_context = {
                **log_context,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }
            
            # Log de request completado exitosamente
            logger.bind(**response_context).info(
                "HTTP request completed successfully",
                event="request_completed"
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
                event="request_error",
                exc_info=True
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
