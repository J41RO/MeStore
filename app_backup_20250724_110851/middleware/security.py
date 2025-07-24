
# app/middleware/security.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Security Headers Middleware
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: security.py
# Ruta: app/middleware/security.py
# Autor: Jairo
# Fecha de Creación: 2025-07-21
# Última Actualización: 2025-07-21
# Versión: 1.0.0
# Propósito: Middleware de seguridad condicional para headers y HTTPS redirect
#            Solo se activa en entorno de producción para no interferir con desarrollo
#
# Modificaciones:
# 2025-07-21 - Creación inicial del middleware de seguridad
#
# ---------------------------------------------------------------------------------------------

"""
Middleware de seguridad para FastAPI.

Este middleware proporciona:
- Headers de seguridad estándar en producción
- Redirección HTTPS condicional
- Configuración que respeta el entorno de desarrollo
"""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware que agrega headers de seguridad estándar.

    Solo se activa cuando ENVIRONMENT='production' para no interferir
    con herramientas de desarrollo como Swagger UI.
    """

    def __init__(self, app, enable_in_production: bool = True):
        """
        Inicializa el middleware de seguridad.

        Args:
            app: Aplicación FastAPI
            enable_in_production: Si debe activarse en producción
        """
        super().__init__(app)
        self.enable_in_production = enable_in_production
        self.is_production = settings.ENVIRONMENT.lower() == "production"

        if self.is_production and self.enable_in_production:
            logger.info("🔒 SecurityHeadersMiddleware ACTIVADO para entorno de producción")
        else:
            logger.info("🔓 SecurityHeadersMiddleware DESACTIVADO para entorno de desarrollo")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Procesa la request y agrega headers de seguridad en producción.

        Args:
            request: Request HTTP entrante
            call_next: Siguiente middleware en la cadena

        Returns:
            Response con headers de seguridad agregados si corresponde
        """
        # Ejecutar el siguiente middleware/endpoint
        response = await call_next(request)

        # Solo agregar headers en producción
        if self.is_production and self.enable_in_production:
            self._add_security_headers(response, request.url.path)

            # Log para debugging en producción
            logger.debug(
                f"🔒 Security headers agregados para {request.method} {request.url.path}"
            )

        return response

    def _add_security_headers(self, response: Response, request_path: str = "") -> None:
        """
        Agrega todos los headers de seguridad estándar.

        Args:
            response: Response HTTP a modificar
        """
        # HSTS - Forzar HTTPS por 1 año
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

        # Prevenir iframe embedding (clickjacking)
        response.headers["X-Frame-Options"] = "DENY"

        # Prevenir MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Política de referrer restrictiva
        response.headers["Referrer-Policy"] = "no-referrer"

        # Deshabilitar APIs sensibles del navegador
        response.headers["Permissions-Policy"] = (
            "geolocation=(), camera=(), microphone=()"
        )

        # Content Security Policy - Protección XSS con exclusiones
        # Excluir rutas de documentación que requieren scripts inline
        # request_path ya se pasa como parámetro
        excluded_paths = ["/docs", "/redoc", "/openapi.json"]
        
        if not any(request_path.startswith(path) for path in excluded_paths):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "object-src 'none'; "
                "base-uri 'none'; "
                "frame-ancestors 'none'"
            )


def get_security_middleware_config() -> dict:
    """
    Retorna configuración del middleware de seguridad.

    Returns:
        Dict con configuración basada en el entorno actual
    """
    config = {
        "environment": settings.ENVIRONMENT,
        "security_enabled": settings.ENVIRONMENT.lower() == "production",
        "headers_count": 6,
        "description": "Security headers middleware for production environment"
    }

    logger.info(f"🔧 Security middleware config: {config}")
    return config
