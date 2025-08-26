"""Coordinador de ejemplo."""

from surgical_modifier.base_coordinator import BaseCoordinator
from typing import Dict, Any


class ExampleCoordinator(BaseCoordinator):
    """Coordinador de ejemplo para testing."""
    
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Ejecutar operación ejemplo."""
        return {
            "status": "success", 
            "coordinator": "ExampleCoordinator"
        }
    
    def validate_inputs(self, *args, **kwargs) -> bool:
        """Validar inputs."""
        return True
