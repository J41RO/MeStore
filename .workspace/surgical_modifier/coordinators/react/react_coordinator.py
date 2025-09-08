from pathlib import Path
from typing import Dict, Any, Optional
import logging
from coordinators.typescript_react import TypeScriptReactCoordinator

class ReactCoordinator(TypeScriptReactCoordinator):
    """
    Coordinador especializado para React (JSX + TypeScript)
    Hereda todas las capacidades de TypeScriptReactCoordinator y agrega funcionalidad React específica
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.jsx_extensions = {'.jsx', '.tsx'}
        
    def execute(self, operation: str, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta operaciones especializadas para React
        Extiende funcionalidad base con análisis JSX específico
        """
        self.logger.info(f"ReactCoordinator executing {operation} on {file_path}")
        
        # Validar que es archivo React válido
        if not self._is_react_file(file_path):
            self.logger.warning(f"File {file_path} may not be a React file")
        
        # Ejecutar operación usando capacidades heredadas de TypeScriptReactCoordinator
        result = super().execute(file_path, operation, **kwargs)
        
        # Agregar análisis React específico al resultado
        if result.get('success', False):
            result['react_analysis'] = self._analyze_react_content(file_path, result.get('content', ''))
        
        return result
    
    def _is_react_file(self, file_path: str) -> bool:
        """Verifica si el archivo es un archivo React válido"""
        path_obj = Path(file_path)
        return path_obj.suffix in self.jsx_extensions
    
    def _analyze_react_content(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analiza contenido específico de React"""
        analysis = {
            'has_jsx': '<' in content and '>' in content,
            'has_react_imports': 'react' in content.lower(),
            'has_hooks': any(hook in content for hook in ['useState', 'useEffect', 'useContext']),
            'component_type': self._detect_component_type(content)
        }
        return analysis
    
    def _detect_component_type(self, content: str) -> str:
        """Detecta tipo de componente React"""
        if 'const ' in content and '=>' in content:
            return 'functional_arrow'
        elif 'function ' in content and 'return' in content:
            return 'functional_declaration'
        elif 'class ' in content and 'extends' in content:
            return 'class_component'
        else:
            return 'unknown'
