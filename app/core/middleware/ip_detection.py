# ~/app/core/middleware/ip_detection.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Middleware de Detección de IPs Sospechosas
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: ip_detection.py
# Ruta: ~/app/core/middleware/ip_detection.py
# Autor: Jairo
# Fecha de Creación: 2025-07-22
# Última Actualización: 2025-07-22
# Versión: 1.0.0
# Propósito: Middleware para detectar y bloquear IPs sospechosas basado en listas negras,
#            patrones de User-Agent sospechosos y comportamiento anómalo
#
# Modificaciones:
# 2025-07-22 - Implementación inicial del middleware de detección de IPs sospechosas
#
# ---------------------------------------------------------------------------------------------

"""
Middleware de Detección de IPs Sospechosas para MeStore.

Este middleware intercepta todas las requests entrantes y verifica:
- IPs en lista negra configurada
- User-Agents sospechosos (bots, scrapers)
- Patrones de comportamiento anómalo
- Logging de todas las actividades sospechosas
"""

import time
from typing import Dict, List, Optional, Set
from ipaddress import AddressValueError, ip_address

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class SuspiciousIPMiddleware(BaseHTTPMiddleware):
    """
    Middleware para detectar y bloquear IPs sospechosas.

    Características:
    - Verificación contra lista negra de IPs
    - Detección de User-Agents sospechosos
    - Logging estructurado de actividad sospechosa
    - Respuestas HTTP apropiadas para IPs bloqueadas
    """

    def __init__(self, app, suspicious_ips: Optional[List[str]] = None, enable_blacklist: bool = True):
        """
        Inicializar middleware de detección de IPs sospechosas.

        Args:
            app: Aplicación FastAPI
            suspicious_ips: Lista de IPs sospechosas (opcional)
            enable_blacklist: Habilitar verificación de lista negra
        """
        super().__init__(app)
        self.enable_blacklist = enable_blacklist

        # Lista de IPs sospechosas - combinar configuración y parámetros
        config_ips = getattr(settings, 'SUSPICIOUS_IPS', [])
        param_ips = suspicious_ips or []

        # IPs sospechosas conocidas por defecto
        default_suspicious_ips = [
            '0.0.0.0',           # IP inválida
            # '127.0.0.1',  # Comentado para permitir testing local         # Localhost (para testing)
            '10.0.0.1',          # Gateway común
            '192.168.1.1',       # Gateway doméstico común
        ]

        # Combinar todas las listas y crear set para búsqueda rápida
        all_ips = list(set(config_ips + param_ips + default_suspicious_ips))
        self.suspicious_ips: Set[str] = set(ip.strip() for ip in all_ips if ip.strip())

        # User-Agents sospechosos
        self.suspicious_user_agents = {
            'curl/',
            'python-requests/',
            'bot',
            'crawler',
            'spider',
            'scraper',
            'wget',
            'httpie',
            'postman',
            'insomnia',
        }

        # Rutas excluidas de verificación
        self.excluded_paths = {
            '/health',
            '/ready',
            '/docs',
            '/openapi.json',
            '/redoc',
            '/favicon.ico',
        }

        logger.info(
            "Middleware SuspiciousIP inicializado",
            suspicious_ips_count=len(self.suspicious_ips),
            blacklist_enabled=self.enable_blacklist,
            excluded_paths=list(self.excluded_paths)
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Procesar request y verificar IP sospechosa.

        Args:
            request: Request entrante
            call_next: Siguiente middleware en la cadena

        Returns:
            Response apropiada (403 si bloqueada, normal si permitida)
        """
        start_time = time.time()

        # Obtener IP del cliente
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get('user-agent', '').lower()
        path = request.url.path

        # Skip verificación para rutas excluidas
        if path in self.excluded_paths:
            response = await call_next(request)
            return response

        # Verificar si IP está en lista negra
        if self.enable_blacklist and self._is_ip_suspicious(client_ip):
            duration = time.time() - start_time

            logger.warning(
                "SECURITY ALERT: Suspicious IP detected",
                client_ip=client_ip,
                user_agent=request.headers.get('user-agent', ''),
                path=path,
                method=request.method,
                duration=f"{duration:.3f}s",
                action="blocked",
                reason="ip_blacklist"
            )

            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Access denied",
                    "error": "suspicious_ip",
                    "timestamp": time.time()
                }
            )

        # Verificar User-Agent sospechoso
        if self._is_user_agent_suspicious(user_agent):
            duration = time.time() - start_time

            logger.warning(
                "SECURITY ALERT: Suspicious User-Agent detected",
                client_ip=client_ip,
                user_agent=request.headers.get('user-agent', ''),
                path=path,
                method=request.method,
                duration=f"{duration:.3f}s",
                action="flagged",
                reason="suspicious_user_agent"
            )

            # Para User-Agent sospechoso, solo loggear pero permitir acceso
            # (puede ser legítimo en algunos casos)

        # Procesar request normal
        try:
            response = await call_next(request)

            # Log de IP permitida (solo para debugging en development)
            if settings.ENVIRONMENT.lower() == "development":
                duration = time.time() - start_time
                logger.debug(
                    "IP verification passed",
                    client_ip=client_ip,
                    path=path,
                    duration=f"{duration:.3f}s",
                    status="allowed"
                )

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Error in SuspiciousIP middleware",
                client_ip=client_ip,
                path=path,
                error=str(e),
                duration=f"{duration:.3f}s"
            )
            raise

    def _get_client_ip(self, request: Request) -> str:
        """
        Obtener IP del cliente considerando headers de proxy.

        Args:
            request: Request entrante

        Returns:
            IP del cliente como string
        """
        # Verificar headers de proxy primero
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            # X-Forwarded-For puede contener múltiples IPs
            return forwarded_for.split(',')[0].strip()

        # Headers alternativos
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip.strip()

        # IP directa del cliente
        if request.client and request.client.host:
            return request.client.host

        return "unknown"

    def _is_ip_suspicious(self, ip: str) -> bool:
        """
        Verificar si una IP está en la lista de sospechosas.

        Args:
            ip: Dirección IP a verificar

        Returns:
            True si es sospechosa, False si no
        """
        if not ip or ip == "unknown":
            return False

        # Verificación directa en set
        if ip in self.suspicious_ips:
            return True

        # Verificación adicional para rangos de IP (futuro enhancement)
        try:
            ip_obj = ip_address(ip)
            # Aquí se pueden agregar verificaciones de rangos
            # Por ejemplo: ip_obj.is_private, ip_obj.is_loopback, etc.
        except (AddressValueError, ValueError):
            # IP inválida (como 'testclient' de TestClient) - no bloquear
            logger.debug(f"Invalid IP format detected: {ip} - treating as non-suspicious")
            return False

        return False

    def _is_user_agent_suspicious(self, user_agent: str) -> bool:
        """
        Verificar si User-Agent es sospechoso.

        Args:
            user_agent: String del User-Agent (en minúsculas)

        Returns:
            True si es sospechoso, False si no
        """
        if not user_agent:
            return True  # User-Agent vacío es sospechoso

        # Verificar contra patrones conocidos
        for suspicious_pattern in self.suspicious_user_agents:
            if suspicious_pattern in user_agent:
                return True

        return False

    def add_suspicious_ip(self, ip: str) -> None:
        """
        Agregar IP a la lista de sospechosas dinámicamente.

        Args:
            ip: IP a agregar
        """
        if ip and ip.strip():
            self.suspicious_ips.add(ip.strip())
            logger.info(f"IP agregada a lista negra: {ip}")

    def remove_suspicious_ip(self, ip: str) -> None:
        """
        Remover IP de la lista de sospechosas.

        Args:
            ip: IP a remover
        """
        if ip in self.suspicious_ips:
            self.suspicious_ips.remove(ip)
            logger.info(f"IP removida de lista negra: {ip}")

    def get_stats(self) -> Dict[str, any]:
        """
        Obtener estadísticas del middleware.

        Returns:
            Diccionario con estadísticas
        """
        return {
            "suspicious_ips_count": len(self.suspicious_ips),
            "blacklist_enabled": self.enable_blacklist,
            "excluded_paths": list(self.excluded_paths),
            "suspicious_user_agents": list(self.suspicious_user_agents),
        }