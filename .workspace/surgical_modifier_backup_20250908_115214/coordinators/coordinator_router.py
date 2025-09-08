"""
Coordinator Router Central v1.0
Router que decide automáticamente qué coordinador usar basado en tecnología detectada
"""
from pathlib import Path
from typing import Any, Optional

class CoordinatorRouter:
    """Router central que asigna coordinadores basado en tecnología detectada"""
    
    def __init__(self):
        self.project_cache = {}
        
    def get_coordinator(self, file_path: str) -> Any:
        """
        Retorna coordinador apropiado para el archivo basado en tecnología detectada
        """
        file_extension = Path(file_path).suffix.lower()
        
        # Mapeo de extensiones a coordinadores
        if file_extension == '.py':
            return self._get_python_coordinator()
        elif file_extension == '.ts':
            return self._get_typescript_coordinator()
        elif file_extension == '.tsx':
            return self._get_typescript_react_coordinator()
        elif file_extension in ['.js', '.jsx']:
            return self._get_javascript_coordinator()
        else:
            return self._get_fallback_coordinator()
            
    def _get_python_coordinator(self):
        """Retorna coordinador Python"""
        from coordinators.create import CreateCoordinator
        return CreateCoordinator()
        
    def _get_typescript_coordinator(self):
        """Retorna coordinador TypeScript especializado para archivos .ts puros"""
        from coordinators.typescript.typescript_coordinator import TypeScriptCoordinator
        return TypeScriptCoordinator()
        
    def _get_typescript_react_coordinator(self):
        """Retorna coordinador TypeScript+React para archivos .tsx"""
        from coordinators.typescript_react import TypeScriptReactCoordinator
        return TypeScriptReactCoordinator()
        
    def _get_javascript_coordinator(self):
        """Retorna coordinador JavaScript"""
        from coordinators.create import CreateCoordinator
        return CreateCoordinator()
        
    def _get_fallback_coordinator(self):
        """Coordinador fallback para tecnologías no soportadas"""
        from coordinators.create import CreateCoordinator
        return CreateCoordinator()
