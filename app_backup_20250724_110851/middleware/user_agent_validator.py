"""
User-Agent Validator Middleware para MeStore.

Este middleware bloquea requests con User-Agent vacíos o sospechosos (bots/crawlers)
mientras permite navegadores legítimos y excluye rutas críticas del sistema.
"""

import re
from typing import Set
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core.logger import get_logger

logger = get_logger(__name__)


class UserAgentValidatorMiddleware(BaseHTTPMiddleware):
    """
    Middleware para validar User-Agent headers y bloquear bots maliciosos.

    Bloquea requests con User-Agent:
    - Vacío o None
    - Patrones conocidos de bots/crawlers/scripts automatizados
    - Tools de desarrollo como curl, wget, etc.

    Excluye de validación:
    - /health, /ready, /docs, /openapi.json
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

        # Rutas excluidas de validación User-Agent
        self.excluded_paths: Set[str] = {
            "/health",
            "/ready", 
            "/docs",
            "/openapi.json",
            "/redoc"
        }

        # Patrones de User-Agent sospechosos (case-insensitive)
        self.suspicious_patterns = [
            r"curl/.*",
            r"python-requests/.*",
            r"go-http-client/.*", 
            r"scrapy/.*",
            r"wget/.*",
            r"http-client/.*",
            r".*bot.*",
            r".*crawler.*",
            r".*spider.*",
            r".*scraper.*",
            r"postman.*",
            r"insomnia.*",
            r"node-fetch.*",
            r"python.*",
            r"java.*",
            r"rust.*",
            r"^$",  # Empty string
        ]

        # Compilar patterns para performance
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.suspicious_patterns
        ]

    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """
        Verifica si un User-Agent es sospechoso.

        Args:
            user_agent: Header User-Agent del request

        Returns:
            True si es sospechoso, False si es legítimo
        """
        if not user_agent or user_agent.strip() == "":
            return True

        # Verificar contra patrones compilados
        for pattern in self.compiled_patterns:
            if pattern.match(user_agent.strip()):
                return True

        return False

    def _should_validate_path(self, path: str) -> bool:
        """
        Determina si una ruta debe ser validada.

        Args:
            path: Ruta del request

        Returns:
            True si debe validarse, False si está excluida
        """
        return path not in self.excluded_paths

    async def dispatch(self, request: Request, call_next):
        """
        Procesa el request y valida User-Agent si es necesario.

        Args:
            request: Request FastAPI
            call_next: Siguiente middleware en la cadena

        Returns:
            Response apropiada (403 si bloqueado, response normal si permitido)
        """
        path = request.url.path

        # Obtener información del cliente
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "")

        # Verificar si la ruta debe ser validada
        if not self._should_validate_path(path):
            # Log del bypass para rutas excluidas
            logger.info(
                "User-Agent validation bypassed for excluded path",
                extra={
                    "client_ip": client_ip,
                    "path": path,
                    "user_agent": user_agent,
                    "action": "bypass",
                    "reason": "excluded_path"
                }
            )
            return await call_next(request)

        # Verificar User-Agent sospechoso
        if self._is_suspicious_user_agent(user_agent):
            # Log del bloqueo
            logger.warning(
                "Suspicious User-Agent blocked",
                extra={
                    "client_ip": client_ip,
                    "path": path, 
                    "method": request.method,
                    "user_agent": user_agent,
                    "action": "blocked",
                    "reason": "suspicious_user_agent"
                }
            )

            # Retornar respuesta 403
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Forbidden",
                    "message": "User-Agent no permitido",
                    "code": "INVALID_USER_AGENT"
                }
            )

        # User-Agent válido - continuar con el request
        logger.debug(
            "Valid User-Agent allowed",
            extra={
                "client_ip": client_ip,
                "path": path,
                "user_agent": user_agent,
                "action": "allowed"
            }
        )

        return await call_next(request)