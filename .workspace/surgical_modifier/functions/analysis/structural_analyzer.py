from typing import Dict, List, Optional, Any, Set
from pathlib import Path
import logging
from dataclasses import dataclass

from ..engines.ast_engine import AstEngine
from ..engines.base_engine import BaseEngine
from .types import StructuralIssue, AnalysisResult

class StructuralAnalyzer:
    """
    Coordinador central para análisis estructural preventivo.
    
    Detecta problemas estructurales ANTES de realizar modificaciones:
    - Interfaces/funciones duplicadas
    - Referencias circulares
    - Sintaxis rota
    - Dependencias problemáticas
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ast_engine = AstEngine()
        # BaseEngine es abstracta - se usará a través de AstEngine
        self._detectors = {}
        
    def analyze_before_modification(
        self, 
        file_path: str, 
        content: Optional[str] = None,
        analysis_types: Optional[List[str]] = None
    ) -> AnalysisResult:
        """
        Punto de entrada principal para análisis preventivo.
        
        Args:
            file_path: Ruta del archivo a analizar
            content: Contenido del archivo (opcional, se lee si no se proporciona)
            analysis_types: Tipos de análisis a realizar (['duplicates', 'circular', 'syntax'])
            
        Returns:
            AnalysisResult con todos los problemas detectados
        """
        import time
        start_time = time.time()
        
        try:
            self.logger.info(f'Iniciando análisis estructural preventivo: {file_path}')
            
            # Análisis por defecto si no se especifica
            if analysis_types is None:
                analysis_types = ['duplicates', 'syntax']
            
            # Leer contenido si no se proporciona
            if content is None:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception as e:
                    return AnalysisResult(
                        has_issues=True,
                        issues=[StructuralIssue(
                            type='file_read_error',
                            severity='error', 
                            file_path=file_path,
                            line_number=None,
                            message=f'Error leyendo archivo: {str(e)}',
                            details={'error': str(e)}
                        )],
                        analysis_time=time.time() - start_time,
                        files_analyzed=0
                    )
            
            # Realizar análisis estructural
            issues = self.detect_structural_issues(file_path, content, analysis_types)
            
            analysis_time = time.time() - start_time
            
            result = AnalysisResult(
                has_issues=len(issues) > 0,
                issues=issues,
                analysis_time=analysis_time,
                files_analyzed=1
            )
            
            self.logger.info(f'Análisis completado: {len(issues)} problemas detectados en {analysis_time:.3f}s')
            return result
            
        except Exception as e:
            self.logger.error(f'Error en análisis estructural: {str(e)}')
            return AnalysisResult(
                has_issues=True,
                issues=[StructuralIssue(
                    type='analysis_error',
                    severity='error',
                    file_path=file_path, 
                    line_number=None,
                    message=f'Error en análisis: {str(e)}',
                    details={'error': str(e)}
                )],
                analysis_time=time.time() - start_time,
                files_analyzed=0
            )
    
    def detect_structural_issues(
        self, 
        file_path: str, 
        content: str, 
        analysis_types: List[str]
    ) -> List[StructuralIssue]:
        """
        Orquestador principal de detección de problemas estructurales.
        
        Args:
            file_path: Ruta del archivo
            content: Contenido del archivo
            analysis_types: Tipos de análisis a realizar
            
        Returns:
            Lista de problemas estructurales detectados
        """
        issues = []
        
        try:
            # Análisis de sintaxis básica usando AST Engine
            if 'syntax' in analysis_types:
                syntax_issues = self._analyze_syntax_with_ast(file_path, content)
                issues.extend(syntax_issues)
            
            # Análisis de duplicados usando DuplicateDetector
            if 'duplicates' in analysis_types:
                from .duplicate_detector import DuplicateDetector
                detector = DuplicateDetector()
                duplicate_issues = detector.detect_all_duplicates(file_path, content)
                issues.extend(duplicate_issues)
            
            # Análisis de referencias circulares usando CircularDetector
            if 'circular' in analysis_types:
                from .circular_detector import CircularDetector
                detector = CircularDetector()
                circular_issues = detector.detect_circular_references(file_path, content)
                issues.extend(circular_issues)
                
        except Exception as e:
            self.logger.error(f'Error en detección estructural: {str(e)}')
            issues.append(StructuralIssue(
                type='detection_error',
                severity='error',
                file_path=file_path,
                line_number=None, 
                message=f'Error en detección: {str(e)}',
                details={'error': str(e)}
            ))
        
        return issues
    
    def _analyze_syntax_with_ast(self, file_path: str, content: str) -> List[StructuralIssue]:
        """Análisis de sintaxis usando AST Engine"""
        issues = []
        
        try:
            # Determinar tipo de archivo
            file_ext = Path(file_path).suffix.lower()
            
            # Para archivos Python, usar ast nativo
            if file_ext == '.py':
                issues.extend(self._analyze_python_syntax(file_path, content))
            
            # Para archivos JS/TS, usar AST Engine
            elif file_ext in ['.js', '.jsx', '.ts', '.tsx']:
                issues.extend(self._analyze_js_syntax(file_path, content))
            
        except Exception as e:
            issues.append(StructuralIssue(
                type='syntax_analysis_error',
                severity='warning',
                file_path=file_path,
                line_number=None,
                message=f'Error analizando sintaxis: {str(e)}',
                details={'error': str(e)}
            ))
        
        return issues
    
    def _analyze_python_syntax(self, file_path: str, content: str) -> List[StructuralIssue]:
        """Análisis de sintaxis Python"""
        issues = []
        
        try:
            import ast
            ast.parse(content)
            self.logger.debug(f'Sintaxis Python OK: {file_path}')
        except SyntaxError as e:
            issues.append(StructuralIssue(
                type='python_syntax_error',
                severity='error',
                file_path=file_path,
                line_number=e.lineno,
                message=f'Error de sintaxis Python: {e.msg}',
                details={
                    'offset': e.offset,
                    'text': e.text,
                    'filename': e.filename
                }
            ))
        except Exception as e:
            issues.append(StructuralIssue(
                type='python_parse_error', 
                severity='warning',
                file_path=file_path,
                line_number=None,
                message=f'Error parseando Python: {str(e)}',
                details={'error': str(e)}
            ))
        
        return issues
    
    def _analyze_js_syntax(self, file_path: str, content: str) -> List[StructuralIssue]:
        """Análisis de sintaxis JavaScript/TypeScript usando AST Engine"""
        issues = []
        
        try:
            # Usar AST Engine para análisis JS/TS
            if hasattr(self.ast_engine, 'parse_javascript'):
                result = self.ast_engine.parse_javascript(content)
                if not result.get('success', False):
                    issues.append(StructuralIssue(
                        type='js_syntax_error',
                        severity='error',
                        file_path=file_path,
                        line_number=result.get('line'),
                        message=f'Error de sintaxis JS/TS: {result.get("error", "Error desconocido")}',
                        details=result
                    ))
                else:
                    self.logger.debug(f'Sintaxis JS/TS OK: {file_path}')
            else:
                self.logger.warning('AST Engine no tiene soporte para JavaScript')
                
        except Exception as e:
            issues.append(StructuralIssue(
                type='js_analysis_error',
                severity='warning',
                file_path=file_path,
                line_number=None,
                message=f'Error analizando JS/TS: {str(e)}',
                details={'error': str(e)}
            ))
        
        return issues
    
    def register_detector(self, name: str, detector_class):
        """Registra un detector personalizado"""
        self._detectors[name] = detector_class
        self.logger.info(f'Detector registrado: {name}')
    
    def get_supported_analysis_types(self) -> List[str]:
        """Retorna tipos de análisis soportados"""
        base_types = ['syntax', 'duplicates', 'circular']
        custom_types = list(self._detectors.keys())
        return base_types + custom_types