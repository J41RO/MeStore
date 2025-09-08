from typing import Dict, List, Optional, Set, Tuple, Any
from pathlib import Path
import re
import logging
from collections import defaultdict, deque

from .types import StructuralIssue

class CircularDetector:
    """
    Detector especializado en referencias circulares.
    
    Detecta:
    - Imports circulares en JavaScript/TypeScript
    - Imports circulares en Python
    - Referencias circulares entre módulos
    - Dependencias circulares en general
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Patrones para diferentes tipos de imports
        self.js_import_patterns = [
            re.compile(r'import\s+(?:{[^}]+}|\w+|\*\s+as\s+\w+)\s+from\s+["\']([^"\'\n]+)["\']', re.MULTILINE),
            re.compile(r'import\s*\(["\']([^"\'\n]+)["\']\)', re.MULTILINE),
            re.compile(r'require\s*\(["\']([^"\'\n]+)["\']\)', re.MULTILINE)
        ]
        
        self.python_import_patterns = [
            re.compile(r'from\s+([\w\.]+)\s+import', re.MULTILINE),
            re.compile(r'import\s+([\w\.]+)', re.MULTILINE)
        ]
    
    def detect_circular_imports(self, directory_path: str) -> List[StructuralIssue]:
        """
        Detecta imports circulares en un directorio completo.
        
        Args:
            directory_path: Ruta del directorio a analizar
            
        Returns:
            Lista de problemas de imports circulares detectados
        """
        issues = []
        
        try:
            directory = Path(directory_path)
            if not directory.exists():
                return [StructuralIssue(
                    type='directory_not_found',
                    severity='error',
                    file_path=directory_path,
                    line_number=None,
                    message=f'Directorio no encontrado: {directory_path}',
                    details={'path': directory_path}
                )]
            
            # Construir grafo de dependencias
            dependency_graph = self._build_dependency_graph(directory)
            
            # Detectar ciclos en el grafo
            cycles = self._detect_cycles_in_graph(dependency_graph)
            
            # Convertir ciclos a StructuralIssues
            for cycle in cycles:
                issues.append(self._cycle_to_issue(cycle, dependency_graph))
            
            self.logger.info(f'Detección de imports circulares completada: {len(cycles)} ciclos encontrados')
        
        except Exception as e:
            issues.append(StructuralIssue(
                type='circular_detection_error',
                severity='error',
                file_path=directory_path,
                line_number=None,
                message=f'Error detectando imports circulares: {str(e)}',
                details={'error': str(e)}
            ))
        
        return issues
    
    def detect_circular_references(self, file_path: str, content: Optional[str] = None) -> List[StructuralIssue]:
        """
        Detecta referencias circulares en un archivo específico.
        
        Args:
            file_path: Ruta del archivo
            content: Contenido del archivo (opcional)
            
        Returns:
            Lista de problemas de referencias circulares
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
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext in ['.js', '.jsx', '.ts', '.tsx']:
                issues.extend(self._analyze_js_references(file_path, content))
            elif file_ext == '.py':
                issues.extend(self._analyze_python_references(file_path, content))
        
        except Exception as e:
            issues.append(StructuralIssue(
                type='reference_analysis_error',
                severity='warning',
                file_path=file_path,
                line_number=None,
                message=f'Error analizando referencias: {str(e)}',
                details={'error': str(e)}
            ))
        
        return issues
    
    def _build_dependency_graph(self, directory: Path) -> Dict[str, Set[str]]:
        """Construye un grafo de dependencias para el directorio"""
        graph = defaultdict(set)
        
        # Obtener todos los archivos de código
        code_files = []
        for ext in ['*.py', '*.js', '*.jsx', '*.ts', '*.tsx']:
            code_files.extend(directory.rglob(ext))
        
        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extraer dependencias del archivo
                dependencies = self._extract_dependencies(file_path, content)
                
                # Convertir rutas a relativas
                relative_path = str(file_path.relative_to(directory))
                
                for dep in dependencies:
                    # Resolver ruta de dependencia
                    resolved_dep = self._resolve_dependency_path(file_path, dep, directory)
                    if resolved_dep:
                        graph[relative_path].add(resolved_dep)
            
            except Exception as e:
                self.logger.warning(f'Error procesando {file_path}: {str(e)}')
        
        return dict(graph)
    
    def _extract_dependencies(self, file_path: Path, content: str) -> List[str]:
        """Extrae dependencias de un archivo"""
        dependencies = []
        file_ext = file_path.suffix.lower()
        
        if file_ext in ['.js', '.jsx', '.ts', '.tsx']:
            # Usar patrones JavaScript/TypeScript
            for pattern in self.js_import_patterns:
                matches = pattern.findall(content)
                dependencies.extend(matches)
        
        elif file_ext == '.py':
            # Usar patrones Python
            for pattern in self.python_import_patterns:
                matches = pattern.findall(content)
                dependencies.extend(matches)
        
        return dependencies
    
    def _resolve_dependency_path(self, file_path: Path, dependency: str, base_directory: Path) -> Optional[str]:
        """Resuelve la ruta real de una dependencia"""
        try:
            # Si es dependencia relativa
            if dependency.startswith('.'):
                # Resolver ruta relativa
                current_dir = file_path.parent
                dep_path = current_dir / dependency
                
                # Intentar diferentes extensiones
                for ext in ['.js', '.jsx', '.ts', '.tsx', '.py']:
                    potential_path = dep_path.with_suffix(ext)
                    if potential_path.exists():
                        return str(potential_path.relative_to(base_directory))
                
                # Intentar como directorio con index
                for ext in ['.js', '.jsx', '.ts', '.tsx']:
                    index_path = dep_path / f'index{ext}'
                    if index_path.exists():
                        return str(index_path.relative_to(base_directory))
            
            # Si es dependencia absoluta dentro del proyecto
            elif not dependency.startswith('@') and '/' in dependency:
                # Intentar resolver desde base del proyecto
                potential_path = base_directory / dependency
                for ext in ['.js', '.jsx', '.ts', '.tsx', '.py']:
                    if potential_path.with_suffix(ext).exists():
                        return str(potential_path.with_suffix(ext).relative_to(base_directory))
        
        except Exception:
            pass
        
        return None
    
    def _detect_cycles_in_graph(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Detecta ciclos en el grafo de dependencias usando DFS"""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str) -> bool:
            """DFS que detecta ciclos"""
            if node in rec_stack:
                # Ciclo detectado
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            # Visitar vecinos
            for neighbor in graph.get(node, set()):
                if dfs(neighbor):
                    return True
            
            rec_stack.remove(node)
            path.pop()
            return False
        
        # Ejecutar DFS desde cada nodo no visitado
        for node in graph:
            if node not in visited:
                dfs(node)
        
        return cycles
    
    def _cycle_to_issue(self, cycle: List[str], graph: Dict[str, Set[str]]) -> StructuralIssue:
        """Convierte un ciclo detectado en un StructuralIssue"""
        cycle_description = ' -> '.join(cycle)
        
        return StructuralIssue(
            type='circular_import',
            severity='warning',
            file_path=cycle[0],
            line_number=None,
            message=f'Import circular detectado: {cycle_description}',
            details={
                'cycle': cycle,
                'cycle_length': len(cycle) - 1,
                'files_involved': list(set(cycle[:-1]))  # Remover duplicado final
            }
        )
    
    def _analyze_js_references(self, file_path: str, content: str) -> List[StructuralIssue]:
        """Analiza referencias específicas de JavaScript/TypeScript"""
        issues = []
        
        # Buscar auto-referencias (archivo que se importa a sí mismo)
        lines = content.split('\n')
        file_name = Path(file_path).stem
        
        for line_num, line in enumerate(lines, 1):
            for pattern in self.js_import_patterns:
                matches = pattern.finditer(line)
                for match in matches:
                    import_path = match.group(1)
                    
                    # Verificar si es auto-referencia
                    if self._is_self_reference(file_path, import_path):
                        issues.append(StructuralIssue(
                            type='self_reference',
                            severity='error',
                            file_path=file_path,
                            line_number=line_num,
                            message=f'Auto-referencia detectada: {import_path}',
                            details={
                                'import_path': import_path,
                                'line_content': line.strip()
                            }
                        ))
        
        return issues
    
    def _analyze_python_references(self, file_path: str, content: str) -> List[StructuralIssue]:
        """Analiza referencias específicas de Python"""
        issues = []
        
        # Buscar auto-referencias en Python
        lines = content.split('\n')
        file_name = Path(file_path).stem
        
        for line_num, line in enumerate(lines, 1):
            for pattern in self.python_import_patterns:
                matches = pattern.finditer(line)
                for match in matches:
                    module_path = match.group(1)
                    
                    # Verificar si es auto-referencia
                    if file_name in module_path.split('.'):
                        issues.append(StructuralIssue(
                            type='self_reference',
                            severity='error',
                            file_path=file_path,
                            line_number=line_num,
                            message=f'Auto-referencia Python detectada: {module_path}',
                            details={
                                'module_path': module_path,
                                'line_content': line.strip()
                            }
                        ))
        
        return issues
    
    def _is_self_reference(self, file_path: str, import_path: str) -> bool:
        """Verifica si un import es una auto-referencia"""
        file_name = Path(file_path).stem
        
        # Casos de auto-referencia
        if import_path in ['.', './', f'./{file_name}']:
            return True
        
        # Verificar si el import apunta al mismo archivo
        if import_path.endswith(f'/{file_name}') or import_path == file_name:
            return True
        
        return False
    
    def analyze_project_dependencies(self, project_path: str) -> Dict[str, Any]:
        """
        Análisis completo de dependencias del proyecto.
        
        Args:
            project_path: Ruta del proyecto
            
        Returns:
            Diccionario con estadísticas y problemas encontrados
        """
        issues = self.detect_circular_imports(project_path)
        
        # Generar estadísticas
        stats = {
            'total_issues': len(issues),
            'circular_imports': len([i for i in issues if i.type == 'circular_import']),
            'self_references': len([i for i in issues if i.type == 'self_reference']),
            'files_with_issues': len(set(i.file_path for i in issues)),
            'issues': issues
        }
        
        return stats
