"""Clase base para todos los coordinadores."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from . import config


class BaseCoordinator(ABC):
    """Clase base que define la interfaz común para todos los coordinadores.
    
    Todos los coordinadores deben heredar de esta clase e implementar
    los métodos abstractos requeridos.
    """
    
    def __init__(self, verbose: bool = False, dry_run: bool = False):
        """Inicializar coordinador base.
        
        Args:
            verbose: Activar modo verbose
            dry_run: Activar modo simulación sin ejecutar
        """
        self.verbose = verbose
        self.dry_run = dry_run
        self.logger = self._setup_logger()
        self._validate_dependencies()
    
    def _setup_logger(self) -> logging.Logger:
        """Configurar logger para el coordinador."""
        logger = logging.getLogger(self.__class__.__name__)
        level = logging.DEBUG if self.verbose else logging.INFO
        logger.setLevel(level)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _validate_dependencies(self) -> None:
        """Validar que las dependencias necesarias están disponibles."""
        # Implementar validaciones básicas
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Ejecutar la operación principal del coordinador.
        
        Returns:
            Dict con resultado de la operación
            
        Raises:
            NotImplementedError: Si no se implementa en subclase
        """
        raise NotImplementedError("Subclases deben implementar execute()")
    
    @abstractmethod
    def validate_inputs(self, *args, **kwargs) -> bool:
        """Validar los inputs antes de ejecutar operación.
        
        Returns:
            True si inputs son válidos, False en caso contrario
        """
        raise NotImplementedError("Subclases deben implementar validate_inputs()")
    
    def get_coordinator_info(self) -> Dict[str, Any]:
        """Obtener información del coordinador."""
        return {
            "name": self.__class__.__name__,
            "verbose": self.verbose,
            "dry_run": self.dry_run,
            "version": config.DEFAULT_CONFIG.get("version", "0.1.0")
        }
    
    def log_operation(self, operation: str, details: str = "") -> None:
        """Registrar operación en log."""
        if self.verbose:
            self.logger.info(f"Operation: {operation} - {details}")
        
        if self.dry_run:
            self.logger.info(f"DRY RUN: Would execute {operation}")
