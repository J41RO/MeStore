"""
Módulo de logging estructurado usando structlog.

Este módulo configura logging estructurado con:
- Formato legible y coloreado para desarrollo
- Formato JSON para producción
- Metadata automática (timestamp, nivel, módulo)
- Integración con FastAPI
"""

import logging
import sys
from typing import Any, Dict

import structlog
from structlog.typing import FilteringBoundLogger

from app.core.config import settings


def configure_logging() -> FilteringBoundLogger:
    """
    Configura structlog según el entorno (desarrollo/producción).
    
    Returns:
        Logger configurado listo para usar
    """
    # Configurar el logging estándar de Python
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )
    
    # Configuración base de structlog
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if settings.ENVIRONMENT.lower() == "development":
        # Formato legible para desarrollo
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        # Formato JSON para producción
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()


def get_logger(name: str = None) -> FilteringBoundLogger:
    """
    Obtiene un logger configurado con nombre específico.
    
    Args:
        name: Nombre del logger (por defecto usa el módulo llamador)
    
    Returns:
        Logger listo para usar
    """
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'unknown')
    
    return structlog.get_logger(name)


def log_startup_info() -> None:
    """Log información de arranque de la aplicación."""
    logger = get_logger("app.startup")
    logger.info(
        "MeStore API iniciando",
        environment=settings.ENVIRONMENT,
        debug=settings.DEBUG,
        database_url=settings.DATABASE_URL.split('@')[0] + '@***',  # Ocultar credenciales
        redis_url=settings.REDIS_URL.split('@')[0] + '@***' if '@' in settings.REDIS_URL else settings.REDIS_URL,
        version="0.2.6"
    )


def log_shutdown_info() -> None:
    """Log información de apagado de la aplicación."""
    logger = get_logger("app.shutdown")
    logger.info("MeStore API finalizando correctamente")


def log_request_info(
    method: str,
    url: str,
    status_code: int,
    duration_ms: float,
    user_id: str = None,
    **extra_context: Any
) -> None:
    """
    Log información de request HTTP.
    
    Args:
        method: Método HTTP (GET, POST, etc.)
        url: URL del request
        status_code: Código de respuesta HTTP
        duration_ms: Duración en milisegundos
        user_id: ID del usuario (opcional)
        **extra_context: Contexto adicional
    """
    logger = get_logger("app.requests")
    
    log_data = {
        "method": method,
        "url": url,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
        **extra_context
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if status_code >= 500:
        logger.error("Request completed with server error", **log_data)
    elif status_code >= 400:
        logger.warning("Request completed with client error", **log_data)
    else:
        logger.info("Request completed successfully", **log_data)


def log_error(
    error: Exception,
    context: Dict[str, Any] = None,
    logger_name: str = "app.error"
) -> None:
    """
    Log un error con contexto estructurado.
    
    Args:
        error: Excepción a loggear
        context: Contexto adicional
        logger_name: Nombre del logger
    """
    logger = get_logger(logger_name)
    
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    
    if context:
        log_data.update(context)
    
    logger.error("Error occurred", **log_data, exc_info=error)


# Configurar logging al importar el módulo
configure_logging()

# Logger por defecto para uso general
logger = get_logger("app")