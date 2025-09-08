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
            return self._get_react_coordinator()
        elif file_extension == '.jsx':
            return self._get_react_coordinator()
        elif file_extension == '.js':
            return self._get_javascript_coordinator()
        else:
            return self._get_fallback_coordinator()
            
    def _get_python_coordinator(self):
        """Retorna coordinador Python"""
        from coordinators.create import CreateCoordinator
        return CreateCoordinator()


    def _find_project_root(self, file_path: str) -> str:
        """
        Encuentra la raíz del proyecto buscando archivos indicadores
        Busca hacia arriba desde el archivo hasta encontrar:
        - package.json (proyectos Node.js/React)
        - pyproject.toml o setup.py (proyectos Python)
        - .git (repositorio Git)
        - requirements.txt (proyectos Python)
        """
        current_path = Path(file_path).resolve().parent
        
        # Archivos/directorios que indican raíz de proyecto
        project_indicators = [
            'package.json',
            'pyproject.toml', 
            'setup.py',
            '.git',
            'requirements.txt',
            'Pipfile',
            'poetry.lock',
            'yarn.lock',
            'package-lock.json'
        ]
        
        # Buscar hacia arriba hasta encontrar un indicador
        while current_path != current_path.parent:
            for indicator in project_indicators:
                if (current_path / indicator).exists():
                    return str(current_path)
            current_path = current_path.parent
        
        # Si no encuentra nada, retornar directorio del archivo
        return str(Path(file_path).resolve().parent)


    def _detect_file_technology(self, file_path: str, project_root: str) -> str:
        """
        Detecta la tecnología del archivo basado en extensión y contenido
        Analiza tanto la extensión como el contenido para una detección más precisa
        """
        file_path_obj = Path(file_path)
        extension = file_path_obj.suffix.lower()
        
        # Mapeo básico por extensión
        extension_mapping = {
            '.py': 'python',
            '.js': 'javascript', 
            '.jsx': 'react',
            '.ts': 'typescript',
            '.tsx': 'react-typescript',
            '.vue': 'vue',
            '.php': 'php',
            '.rb': 'ruby',
            '.java': 'java',
            '.cs': 'csharp',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin'
        }
        
        # Detección básica por extensión
        if extension in extension_mapping:
            base_tech = extension_mapping[extension]
            
            # Análisis de contenido para casos especiales
            if extension in ['.js', '.jsx'] and file_path_obj.exists():
                try:
                    with open(file_path_obj, 'r', encoding='utf-8') as f:
                        content = f.read(1000)  # Leer primeros 1000 caracteres
                        
                    # Detectar React en archivos .js
                    if 'import React' in content or 'from \'react\'' in content or 'from "react"' in content:
                        return 'react'
                    # Detectar Vue en archivos .js
                    elif 'Vue' in content or '@vue' in content:
                        return 'vue'
                        
                except (IOError, UnicodeDecodeError):
                    pass
                    
            return base_tech
        
        # Fallback para archivos sin extensión conocida
        return 'generic'
        
    def _get_typescript_coordinator(self):
        """Retorna coordinador TypeScript especializado para archivos .ts puros"""
        from coordinators.typescript.typescript_coordinator import TypeScriptCoordinator
        return TypeScriptCoordinator()
        
    def _get_react_coordinator(self):
        """Retorna coordinador React especializado para archivos .tsx y .jsx"""
        from coordinators.react.react_coordinator import ReactCoordinator
        return ReactCoordinator()
        
    def _get_javascript_coordinator(self):
        """Retorna coordinador JavaScript"""
        from coordinators.create import CreateCoordinator
        return CreateCoordinator()
        
    def _get_fallback_coordinator(self):
        """Coordinador fallback para tecnologías no soportadas"""
        from coordinators.create import CreateCoordinator
        return CreateCoordinator()