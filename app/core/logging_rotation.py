"""
Configuración avanzada de logging con rotación por ambiente.

Este módulo extiende el sistema de logging estructurado existente 
agregando rotación automática de archivos y configuración específica
por ambiente (development, staging, production).

Características:
- Rotación por tamaño (RotatingFileHandler)
- Rotación por tiempo (TimedRotatingFileHandler)
- Configuración dinámica según ENVIRONMENT
- Handlers diferenciados por ambiente
- Preservación del sistema structlog existente
"""

import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Dict, List, Optional

import structlog
from loguru import logger as loguru_logger

from app.core.config import settings


class LogRotationManager:
    """
    Gestor de rotación de logs con configuración por ambiente.
    
    Maneja la configuración automática de handlers de archivo con rotación
    basada en el entorno de ejecución actual.
    """
    
    def __init__(self):
        """Inicializa el gestor con configuración del entorno actual."""
        self.environment = settings.ENVIRONMENT.lower()
        self.log_dir = Path(settings.LOG_DIR)
        self.log_file_prefix = settings.LOG_FILE_PREFIX
        
        # Crear directorio de logs si no existe
        self.log_dir.mkdir(exist_ok=True)
        
        # Configuración de niveles por ambiente
        self._level_config = {
            "development": logging.DEBUG,
            "staging": logging.INFO,
            "production": logging.WARNING,
            "testing": logging.WARNING
        }
        
        # Configuración de handlers por ambiente
        self._handler_config = {
            "development": ["console", "file"],
            "staging": ["file"],
            "production": ["file"],
            "testing": ["file"]
        }
    
    def get_log_level(self) -> int:
        """
        Obtiene el nivel de log apropiado para el ambiente actual.
        
        Returns:
            int: Nivel de logging según ambiente
        """
        return self._level_config.get(self.environment, logging.INFO)
    
    def get_log_file_path(self) -> Path:
        """
        Genera la ruta del archivo de log para el ambiente actual.
        
        Returns:
            Path: Ruta completa al archivo de log
        """
        filename = f"{self.log_file_prefix}-{self.environment}.log"
        return self.log_dir / filename
    
    def create_rotating_file_handler(self) -> RotatingFileHandler:
        """
        Crea un handler de rotación por tamaño.
        
        Returns:
            RotatingFileHandler: Handler configurado para rotación por tamaño
        """
        log_file = self.get_log_file_path()
        
        # Convertir tamaño desde string (ej: "10MB" -> bytes)
        size_str = settings.LOG_ROTATION_SIZE.upper()
        if size_str.endswith("MB"):
            max_bytes = int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith("KB"):
            max_bytes = int(size_str[:-2]) * 1024
        elif size_str.endswith("GB"):
            max_bytes = int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            max_bytes = int(size_str)  # Asumir bytes si no hay sufijo
        
        handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=settings.LOG_ROTATION_COUNT,
            encoding="utf-8"
        )
        
        return handler
    
    def create_timed_rotating_handler(self) -> TimedRotatingFileHandler:
        """
        Crea un handler de rotación por tiempo.
        
        Returns:
            TimedRotatingFileHandler: Handler configurado para rotación temporal
        """
        log_file = self.get_log_file_path()
        
        handler = TimedRotatingFileHandler(
            filename=log_file,
            when=settings.LOG_ROTATION_TIME,
            interval=settings.LOG_ROTATION_INTERVAL,
            backupCount=settings.LOG_ROTATION_COUNT,
            encoding="utf-8"
        )
        
        # Formato de sufijo para archivos rotados
        handler.suffix = "%Y-%m-%d_%H-%M-%S"
        
        return handler
    
    def should_use_console(self) -> bool:
        """
        Determina si debe usar output de consola según el ambiente.
        
        Returns:
            bool: True si debe mostrar logs en consola
        """
        return "console" in self._handler_config.get(self.environment, [])
    
    def get_formatter(self, for_file: bool = False) -> logging.Formatter:
        """
        Crea un formatter apropiado según el destino.
        
        Args:
            for_file: True para archivos, False para consola
            
        Returns:
            logging.Formatter: Formatter configurado
        """
        if for_file:
            # Formato estructurado para archivos
            fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        else:
            # Formato más legible para consola en desarrollo
            fmt = "%(asctime)s [%(levelname)s] %(message)s"
        
        return logging.Formatter(
            fmt=fmt,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    def configure_python_logging(self) -> None:
        """
        Configura el sistema de logging estándar de Python con rotación.
        
        Esta función integra la rotación con el logging tradicional
        para bibliotecas que no usan structlog.
        """
        # Obtener logger raíz
        root_logger = logging.getLogger()
        
        # Limpiar handlers existentes para evitar duplicación
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Configurar nivel
        log_level = self.get_log_level()
        root_logger.setLevel(log_level)
        
        # Agregar handler de archivo con rotación por tamaño
        file_handler = self.create_rotating_file_handler()
        file_handler.setLevel(log_level)
        file_handler.setFormatter(self.get_formatter(for_file=True))
        root_logger.addHandler(file_handler)
        
        # Agregar handler de consola si corresponde
        if self.should_use_console():
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(self.get_formatter(for_file=False))
            root_logger.addHandler(console_handler)
    
    def configure_structlog_rotation(self) -> None:
        """
        Configura structlog para usar los handlers con rotación.
        
        Integra el sistema de rotación con structlog manteniendo
        el formato estructurado existente.
        """
        # Configurar primero el logging estándar
        self.configure_python_logging()
        
        # Configurar structlog para usar los handlers configurados
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.dev.set_exc_info,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.dev.ConsoleRenderer() if self.should_use_console() 
                else structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.make_filtering_bound_logger(self.get_log_level()),
            logger_factory=structlog.WriteLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    
    def get_environment_info(self) -> Dict[str, any]:
        """
        Obtiene información sobre la configuración actual.
        
        Returns:
            Dict: Información de configuración para debugging
        """
        return {
            "environment": self.environment,
            "log_level": logging.getLevelName(self.get_log_level()),
            "log_file": str(self.get_log_file_path()),
            "console_enabled": self.should_use_console(),
            "rotation_size": settings.LOG_ROTATION_SIZE,
            "rotation_count": settings.LOG_ROTATION_COUNT,
            "rotation_time": settings.LOG_ROTATION_TIME,
            "handlers": self._handler_config.get(self.environment, [])
        }


# Instancia global del gestor
log_rotation_manager = LogRotationManager()


def setup_log_rotation() -> LogRotationManager:
    """
    Configura el sistema completo de rotación de logs.
    
    Esta función debe llamarse al inicio de la aplicación
    para configurar todos los handlers de logging con rotación.
    
    Returns:
        LogRotationManager: Instancia configurada del gestor
    """
    # Configurar structlog con rotación
    log_rotation_manager.configure_structlog_rotation()
    
    # Log de confirmación
    logger = structlog.get_logger("logging_rotation")
    config_info = log_rotation_manager.get_environment_info()
    
    logger.info(
        "Sistema de rotación de logs configurado",
        **config_info
    )
    
    return log_rotation_manager


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Obtiene un logger structlog configurado con rotación.
    
    Args:
        name: Nombre del logger (generalmente __name__)
        
    Returns:
        structlog.BoundLogger: Logger configurado
    """
    return structlog.get_logger(name)


# Funciones de conveniencia para diferentes niveles
def log_info(message: str, **kwargs) -> None:
    """Log nivel INFO con contexto adicional."""
    logger = get_logger("app")
    logger.info(message, **kwargs)


def log_warning(message: str, **kwargs) -> None:
    """Log nivel WARNING con contexto adicional."""
    logger = get_logger("app")
    logger.warning(message, **kwargs)


def log_error(message: str, **kwargs) -> None:
    """Log nivel ERROR con contexto adicional."""
    logger = get_logger("app")
    logger.error(message, **kwargs)


def log_debug(message: str, **kwargs) -> None:
    """Log nivel DEBUG con contexto adicional."""
    logger = get_logger("app")
    logger.debug(message, **kwargs)
