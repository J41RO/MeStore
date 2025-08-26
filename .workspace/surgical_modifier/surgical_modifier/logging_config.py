"""Configuración de logging centralizado."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from .config import DEFAULT_CONFIG, PROJECT_ROOT


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    verbose: bool = False
) -> logging.Logger:
    """Configurar sistema de logging centralizado.
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        log_file: Archivo opcional para guardar logs
        verbose: Activar logging detallado
        
    Returns:
        Logger configurado
    """
    # Determinar nivel de logging
    if verbose:
        level = logging.DEBUG
    else:
        level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configurar logger principal
    logger = logging.getLogger("surgical_modifier")
    logger.setLevel(level)
    
    # Limpiar handlers existentes
    logger.handlers.clear()
    
    # Formatter para mensajes
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo (opcional)
    if log_file:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)  # Archivo siempre DEBUG
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"No se pudo configurar logging a archivo: {e}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Obtener logger específico para un módulo."""
    return logging.getLogger(f"surgical_modifier.{name}")


# Logger por defecto del sistema
DEFAULT_LOGGER = setup_logging(
    log_level=DEFAULT_CONFIG["log_level"],
    verbose=DEFAULT_CONFIG["verbose"]
)
