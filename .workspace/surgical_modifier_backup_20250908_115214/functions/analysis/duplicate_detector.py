from typing import Dict, List, Optional, Set, Tuple, Any
from pathlib import Path
import re
import ast
import logging
from dataclasses import dataclass

from .types import StructuralIssue

@dataclass
class DuplicateMatch:
    """Representa una duplicación encontrada"""
    name: str
    type: str  # 'interface', 'function', 'class', 'variable'
    locations: List[Tuple[int, str]]  # [(line_number, definition)]
    severity: str

class DuplicateDetector:
    """
    Detector especializado en duplicaciones de código.
    
    Detecta:
    - Interfaces duplicadas en TypeScript/JavaScript
    - Funciones duplicadas en cualquier lenguaje
    - Clases duplicadas
    - Variables/constantes duplicadas
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Patrones regex para diferentes tipos de duplicaciones
        self.interface_pattern = re.compile(
            r'interface\s+(\w+)\s*\{',
            re.IGNORECASE | re.MULTILINE
        )
        
        self.function_pattern = re.compile(
            r'(?:function\s+(\w+)|(\w+)\s*:\s*(?:function|\(.*?\)\s*=>)|(\w+)\s*\([^)]*\)\s*\{)',
            re.IGNORECASE | re.MULTILINE
        )
        
        self.class_pattern = re.compile(
            r'class\s+(\w+)',
            re.IGNORECASE | re.MULTILINE
        )
        
        # Patrones para Python
        self.python_function_pattern = re.compile(
            r'def\s+(\w+)\s*\(',
            re.MULTILINE
        )
        
        self.python_class_pattern = re.compile(
            r'class\s+(\w+)',
            re.MULTILINE  
        )
    
    def find_duplicate_interfaces(self, file_path: str, content: Optional[str] = None) -> List[StructuralIssue]:
        """
        Detecta interfaces duplicadas en archivos TypeScript/JavaScript.
        
        Args:
            file_path: Ruta del archivo
            content: Contenido del archivo (opcional)
            
        Returns:
            Lista de problemas de interfaces duplicadas
        """
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                return [StructuralIssue(
                    type='file_read_error',
                    severity='error',
                    file_path=file_path,
                    line_number=None,
                    message=f'Error leyendo archivo: {str(e)}',
                    details={'error': str(e)}
                )]
        
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in ['.ts', '.tsx', '.js', '.jsx']:
            return []
        
        issues = []
        
        try:
            # Encontrar todas las interfaces
            interfaces = {}
            lines = content.split('\n')
            
            # Buscar TODAS las interfaces en TODO el contenido
            for match in self.interface_pattern.finditer(content):
                # Calcular número de línea para la posición del match
                line_num = content[:match.start()].count('\n') + 1
                line = content.split('\n')[line_num-1] if line_num <= len(lines) else match.group(0)
                if match:
                    interface_name = match.group(1)
                    
                    if interface_name in interfaces:
                        # Interface duplicada encontrada
                        interfaces[interface_name].append((line_num, line.strip()))
                    else:
                        interfaces[interface_name] = [(line_num, line.strip())]
            
            # Reportar duplicados
            for interface_name, locations in interfaces.items():
                if len(locations) > 1:
                    issues.append(StructuralIssue(
                        type='duplicate_interface',
                        severity='warning',
                        file_path=file_path,
                        line_number=locations[0][0],
                        message=f'Interface duplicada: {interface_name} (aparece {len(locations)} veces)',
                        details={
                            'interface_name': interface_name,
                            'locations': locations,
                            'count': len(locations)
                        }
                    ))
                    
                    self.logger.warning(f'Interface duplicada {interface_name} en {file_path}: líneas {[loc[0] for loc in locations]}')
        
        except Exception as e:
            issues.append(StructuralIssue(
                type='interface_detection_error',
                severity='warning',
                file_path=file_path,
                line_number=None,
                message=f'Error detectando interfaces: {str(e)}',
                details={'error': str(e)}
            ))
        
        return issues
    
    def find_duplicate_functions(self, file_path: str, content: Optional[str] = None) -> List[StructuralIssue]:
        """
        Detecta funciones duplicadas en cualquier lenguaje soportado.
        
        Args:
            file_path: Ruta del archivo
            content: Contenido del archivo (opcional)
            
        Returns:
            Lista de problemas de funciones duplicadas
        """
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                return [StructuralIssue(
                    type='file_read_error', 
                    severity='error',
                    file_path=file_path,
                    line_number=None,
                    message=f'Error leyendo archivo: {str(e)}',
                    details={'error': str(e)}
                )]
        
        file_ext = Path(file_path).suffix.lower()
        issues = []
        
        try:
            if file_ext == '.py':
                issues.extend(self._find_python_function_duplicates(file_path, content))
            elif file_ext in ['.js', '.jsx', '.ts', '.tsx']:
                issues.extend(self._find_js_function_duplicates(file_path, content))
        
        except Exception as e:
            issues.append(StructuralIssue(
                type='function_detection_error',
                severity='warning', 
                file_path=file_path,
                line_number=None,
                message=f'Error detectando funciones: {str(e)}',
                details={'error': str(e)}
            ))
        
        return issues
    
    def _find_python_function_duplicates(self, file_path: str, content: str) -> List[StructuralIssue]:
        """Detecta funciones duplicadas en Python"""
        issues = []
        functions = {}
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            match = self.python_function_pattern.search(line)
            if match:
                func_name = match.group(1)
                
                # Ignorar métodos especiales de Python
                if func_name.startswith('__') and func_name.endswith('__'):
                    continue
                
                if func_name in functions:
                    functions[func_name].append((line_num, line.strip()))
                else:
                    functions[func_name] = [(line_num, line.strip())]
        
        # Reportar duplicados
        for func_name, locations in functions.items():
            if len(locations) > 1:
                issues.append(StructuralIssue(
                    type='duplicate_function',
                    severity='warning',
                    file_path=file_path,
                    line_number=locations[0][0],
                    message=f'Función duplicada: {func_name} (aparece {len(locations)} veces)',
                    details={
                        'function_name': func_name,
                        'locations': locations,
                        'count': len(locations),
                        'language': 'python'
                    }
                ))
        
        return issues
    
    def _find_js_function_duplicates(self, file_path: str, content: str) -> List[StructuralIssue]:
        """Detecta funciones duplicadas en JavaScript/TypeScript"""
        issues = []
        functions = {}
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Buscar diferentes patrones de funciones JS/TS
            
            # function nombre()
            func_match = re.search(r'function\s+(\w+)\s*\(', line)
            # const nombre = function() or arrow functions
            arrow_match = re.search(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:function|\([^)]*\)\s*=>)', line)
            # nombre: function() en objetos
            method_match = re.search(r'(\w+)\s*:\s*function\s*\(', line)
            
            func_name = None
            if func_match:
                func_name = func_match.group(1)
            elif arrow_match:
                func_name = arrow_match.group(1)  
            elif method_match:
                func_name = method_match.group(1)
            
            if func_name:
                if func_name in functions:
                    functions[func_name].append((line_num, line.strip()))
                else:
                    functions[func_name] = [(line_num, line.strip())]
        
        # Reportar duplicados
        for func_name, locations in functions.items():
            if len(locations) > 1:
                issues.append(StructuralIssue(
                    type='duplicate_function',
                    severity='warning',
                    file_path=file_path,
                    line_number=locations[0][0],
                    message=f'Función duplicada: {func_name} (aparece {len(locations)} veces)',
                    details={
                        'function_name': func_name,
                        'locations': locations,
                        'count': len(locations),
                        'language': 'javascript'
                    }
                ))
        
        return issues
    
    def find_duplicate_classes(self, file_path: str, content: Optional[str] = None) -> List[StructuralIssue]:
        """
        Detecta clases duplicadas en cualquier lenguaje soportado.
        
        Args:
            file_path: Ruta del archivo
            content: Contenido del archivo (opcional)
            
        Returns:
            Lista de problemas de clases duplicadas
        """
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                return [StructuralIssue(
                    type='file_read_error',
                    severity='error',
                    file_path=file_path,
                    line_number=None,
                    message=f'Error leyendo archivo: {str(e)}',
                    details={'error': str(e)}
                )]
        
        issues = []
        classes = {}
        lines = content.split('\n')
        
        try:
            for line_num, line in enumerate(lines, 1):
                match = self.class_pattern.search(line)
                if match:
                    class_name = match.group(1)
                    
                    if class_name in classes:
                        classes[class_name].append((line_num, line.strip()))
                    else:
                        classes[class_name] = [(line_num, line.strip())]
            
            # Reportar duplicados
            for class_name, locations in classes.items():
                if len(locations) > 1:
                    issues.append(StructuralIssue(
                        type='duplicate_class',
                        severity='warning',
                        file_path=file_path,
                        line_number=locations[0][0],
                        message=f'Clase duplicada: {class_name} (aparece {len(locations)} veces)',
                        details={
                            'class_name': class_name,
                            'locations': locations,
                            'count': len(locations)
                        }
                    ))
        
        except Exception as e:
            issues.append(StructuralIssue(
                type='class_detection_error',
                severity='warning',
                file_path=file_path,
                line_number=None,
                message=f'Error detectando clases: {str(e)}',
                details={'error': str(e)}
            ))
        
        return issues
    
    def detect_all_duplicates(self, file_path: str, content: Optional[str] = None) -> List[StructuralIssue]:
        """
        Detecta todos los tipos de duplicaciones en un archivo.
        
        Args:
            file_path: Ruta del archivo
            content: Contenido del archivo (opcional)
            
        Returns:
            Lista consolidada de todos los problemas de duplicación
        """
        all_issues = []
        
        try:
            # Detectar interfaces duplicadas
            all_issues.extend(self.find_duplicate_interfaces(file_path, content))
            
            # Detectar funciones duplicadas
            all_issues.extend(self.find_duplicate_functions(file_path, content))
            
            # Detectar clases duplicadas  
            all_issues.extend(self.find_duplicate_classes(file_path, content))
            
            self.logger.info(f'Detección de duplicados completada para {file_path}: {len(all_issues)} problemas encontrados')
        
        except Exception as e:
            all_issues.append(StructuralIssue(
                type='duplicate_detection_error',
                severity='error',
                file_path=file_path,
                line_number=None,
                message=f'Error general en detección de duplicados: {str(e)}',
                details={'error': str(e)}
            ))
        
        return all_issues
    
    def get_duplicate_summary(self, issues: List[StructuralIssue]) -> Dict[str, Any]:
        """
        Genera un resumen de los duplicados encontrados.
        
        Args:
            issues: Lista de problemas de duplicación
            
        Returns:
            Diccionario con estadísticas de duplicación
        """
        summary = {
            'total_duplicates': len(issues),
            'by_type': {},
            'by_severity': {},
            'files_affected': set()
        }
        
        for issue in issues:
            # Contar por tipo
            issue_type = issue.type
            summary['by_type'][issue_type] = summary['by_type'].get(issue_type, 0) + 1
            
            # Contar por severidad
            severity = issue.severity
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
            
            # Archivos afectados
            summary['files_affected'].add(issue.file_path)
        
        summary['files_affected'] = len(summary['files_affected'])
        
        return summary
