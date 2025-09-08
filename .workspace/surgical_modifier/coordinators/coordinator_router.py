"""
Coordinator Router Central v1.0
Router que decide automáticamente qué coordinador usar basado en tecnología detectada
"""

from pathlib import Path
from typing import Any, Optional
from functions.analysis.technology_detector import detect_project_technology

class CoordinatorRouter:
    """Router central que asigna coordinadores basado en tecnología detectada"""
    
    def __init__(self):
        self.project_cache = {}
    
    def get_coordinator(self, file_path: str) -> Any:
        """
        Retorna coordinador apropiado para el archivo basado en tecnología detectada
        
        Args:
            file_path: Ruta del archivo a procesar
            
        Returns:
            Instancia del coordinador específico para la tecnología
        """
        project_root = self._find_project_root(file_path)
        technology = self._detect_file_technology(file_path, project_root)
        
        return self._get_coordinator_for_technology(technology)
    
    def _find_project_root(self, file_path: str) -> str:
        """Encuentra la raíz del proyecto desde la ruta del archivo"""
        current_path = Path(file_path).parent.absolute()
        
        # Buscar hacia arriba hasta encontrar indicadores de proyecto
        project_indicators = ['.git', 'package.json', 'requirements.txt', 'pyproject.toml']
        
        while current_path != current_path.parent:
            for indicator in project_indicators:
                if (current_path / indicator).exists():
                    return str(current_path)
            current_path = current_path.parent
        
        # Si no encuentra, usar directorio del archivo
        return str(Path(file_path).parent)
    
    def _detect_file_technology(self, file_path: str, project_root: str) -> str:
        """Detecta tecnología específica del archivo y contexto del proyecto"""
        # Cache de detección por proyecto
        if project_root not in self.project_cache:
            self.project_cache[project_root] = detect_project_technology(project_root)
        
        project_info = self.project_cache[project_root]
        file_extension = Path(file_path).suffix.lower()
        
        # Mapeo de extensiones a tecnologías
        if file_extension == '.py':
            return 'python'
        elif file_extension == '.ts':
            return 'typescript'
        elif file_extension == '.tsx':
            # React + TypeScript
            return 'typescript_react'
        elif file_extension == '.js':
            # Verificar si hay TypeScript en el proyecto
            if 'typescript' in project_info.get('secondary', []):
                return 'javascript_typescript_project'
            return 'javascript'
        elif file_extension == '.jsx':
            # React + JavaScript
            return 'javascript_react'
        else:
            return 'unknown'
    
    def _get_coordinator_for_technology(self, technology: str) -> Any:
        """Mapea tecnología a coordinador específico"""
        coordinator_map = {
            'python': self._get_python_coordinator,
            'typescript': self._get_typescript_coordinator,
            'typescript_react': self._get_react_coordinator,
            'javascript': self._get_javascript_coordinator,
            'javascript_react': self._get_react_coordinator,
            'javascript_typescript_project': self._get_javascript_coordinator,
        }
        
        coordinator_factory = coordinator_map.get(technology, self._get_fallback_coordinator)
        return coordinator_factory()
    
    def _get_python_coordinator(self):
        """Retorna coordinador Python existente"""
        from coordinators.create import CreateCoordinator
        return CreateCoordinator()  # Usar coordinador Python existente
    
    def _get_typescript_coordinator(self):
        """Retorna coordinador TypeScript (placeholder por ahora)"""
        # TODO: Implementar en Fase 3
        from coordinators.create import CreateCoordinator
        return CreateCoordinator()  # Fallback por ahora
    
    def _get_react_coordinator(self):
        """Retorna coordinador React (placeholder por ahora)"""
        # TODO: Implementar en Fase 4
        from coordinators.create import CreateCoordinator
        return CreateCoordinator()  # Fallback por ahora
    
    def _get_javascript_coordinator(self):
        """Retorna coordinador JavaScript"""
        from coordinators.create import CreateCoordinator
        return CreateCoordinator()  # Usar coordinador existente por ahora
    
    def _get_fallback_coordinator(self):
        """Coordinador fallback para tecnologías no soportadas"""
        from coordinators.create import CreateCoordinator
        return CreateCoordinator()
