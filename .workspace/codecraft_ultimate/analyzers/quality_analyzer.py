"""
🚀 CodeCraft Ultimate v6.0 - Analizador de Calidad de Código
"""

import ast
import os
import re
from typing import Dict, List, Any
from ..core.exceptions import AnalysisError


class QualityAnalyzer:
    """Analizador de calidad del código"""
    
    def __init__(self):
        self.quality_metrics = {
            'naming_conventions': {
                'python': {
                    'function_pattern': r'^[a-z_][a-z0-9_]*$',
                    'class_pattern': r'^[A-Z][a-zA-Z0-9]*$',
                    'constant_pattern': r'^[A-Z][A-Z0-9_]*$'
                },
                'javascript': {
                    'function_pattern': r'^[a-z][a-zA-Z0-9]*$',
                    'class_pattern': r'^[A-Z][a-zA-Z0-9]*$',
                    'constant_pattern': r'^[A-Z][A-Z0-9_]*$'
                }
            },
            'code_smells': {
                'long_method': 50,
                'long_class': 300,
                'too_many_parameters': 5,
                'deep_nesting': 4
            }
        }
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analizar calidad de un archivo"""
        
        if not os.path.exists(file_path):
            raise AnalysisError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            extension = os.path.splitext(file_path)[1].lower()
            language = self._detect_language(extension)
            
            quality_issues = self._analyze_quality(content, language)
            metrics = self._calculate_quality_metrics(content, language)
            
            return {
                'file_path': file_path,
                'language': language,
                'quality_score': self._calculate_quality_score(quality_issues, metrics),
                'quality_issues': len(quality_issues),
                'issues': quality_issues,
                'metrics': metrics,
                'maintainability_index': self._calculate_maintainability_index(metrics)
            }
            
        except Exception as e:
            raise AnalysisError(f"Quality analysis failed for {file_path}: {e}")
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analizar calidad del proyecto completo"""
        
        results = {
            'total_files': 0,
            'total_quality_issues': 0,
            'average_quality_score': 0,
            'maintainability_rating': 'A',
            'files': []
        }
        
        total_score = 0
        
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in {
                'node_modules', '.git', '__pycache__', 'build', 'dist'
            }]
            
            for file in files:
                if self._is_quality_analyzable(file):
                    file_path = os.path.join(root, file)
                    try:
                        file_result = self.analyze_file(file_path)
                        results['files'].append(file_result)
                        results['total_files'] += 1
                        results['total_quality_issues'] += file_result['quality_issues']
                        total_score += file_result['quality_score']
                        
                    except AnalysisError:
                        continue
        
        if results['total_files'] > 0:
            results['average_quality_score'] = int(total_score / results['total_files'])
            results['maintainability_rating'] = self._get_maintainability_rating(
                results['average_quality_score']
            )
        
        return results
    
    def _analyze_quality(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Analizar aspectos de calidad del código"""
        
        issues = []
        
        if language == 'python':
            issues.extend(self._analyze_python_quality(content))
        elif language == 'javascript':
            issues.extend(self._analyze_js_quality(content))
        
        # Análisis general
        issues.extend(self._analyze_general_quality(content, language))
        
        return issues
    
    def _analyze_python_quality(self, content: str) -> List[Dict[str, Any]]:
        """Análisis específico de calidad para Python"""
        
        issues = []
        
        try:
            tree = ast.parse(content)
            
            # Verificar convenciones de nomenclatura
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not re.match(self.quality_metrics['naming_conventions']['python']['function_pattern'], 
                                   node.name):
                        issues.append({
                            'type': 'naming_convention',
                            'line': node.lineno,
                            'code': f'def {node.name}(',
                            'severity': 'warning',
                            'description': f'Function name "{node.name}" does not follow Python naming convention',
                            'recommendation': 'Use snake_case for function names'
                        })
                    
                    # Verificar parámetros excesivos
                    param_count = len(node.args.args)
                    if param_count > self.quality_metrics['code_smells']['too_many_parameters']:
                        issues.append({
                            'type': 'too_many_parameters',
                            'line': node.lineno,
                            'code': f'def {node.name}(...) # {param_count} parameters',
                            'severity': 'warning',
                            'description': f'Function has too many parameters ({param_count})',
                            'recommendation': 'Consider using a configuration object or breaking into smaller functions'
                        })
                    
                    # Verificar longitud de método
                    method_length = node.end_lineno - node.lineno + 1
                    if method_length > self.quality_metrics['code_smells']['long_method']:
                        issues.append({
                            'type': 'long_method',
                            'line': node.lineno,
                            'code': f'def {node.name}(...) # {method_length} lines',
                            'severity': 'info',
                            'description': f'Method is too long ({method_length} lines)',
                            'recommendation': 'Break into smaller, focused methods'
                        })
                
                elif isinstance(node, ast.ClassDef):
                    # Verificar nomenclatura de clase
                    if not re.match(self.quality_metrics['naming_conventions']['python']['class_pattern'], 
                                   node.name):
                        issues.append({
                            'type': 'naming_convention',
                            'line': node.lineno,
                            'code': f'class {node.name}:',
                            'severity': 'warning',
                            'description': f'Class name "{node.name}" does not follow Python naming convention',
                            'recommendation': 'Use PascalCase for class names'
                        })
            
            # Verificar anidamiento profundo
            max_nesting = self._calculate_max_nesting(tree)
            if max_nesting > self.quality_metrics['code_smells']['deep_nesting']:
                issues.append({
                    'type': 'deep_nesting',
                    'line': 0,
                    'code': f'Maximum nesting depth: {max_nesting}',
                    'severity': 'warning',
                    'description': f'Code has deep nesting ({max_nesting} levels)',
                    'recommendation': 'Consider extracting nested logic into separate functions'
                })
            
        except SyntaxError:
            issues.append({
                'type': 'syntax_error',
                'line': 0,
                'code': 'Syntax error in file',
                'severity': 'critical',
                'description': 'File contains syntax errors',
                'recommendation': 'Fix syntax errors before quality analysis'
            })
        
        return issues
    
    def _analyze_js_quality(self, content: str) -> List[Dict[str, Any]]:
        """Análisis específico de calidad para JavaScript"""
        
        issues = []
        
        # Verificar uso de var
        var_declarations = re.findall(r'\bvar\s+\w+', content)
        if var_declarations:
            issues.append({
                'type': 'deprecated_var',
                'line': 0,
                'code': f'Found {len(var_declarations)} var declarations',
                'severity': 'info',
                'description': 'Use of deprecated var keyword',
                'recommendation': 'Use let or const instead of var'
            })
        
        # Verificar funciones anónimas sin nombre
        anonymous_functions = re.findall(r'function\s*\(', content)
        if len(anonymous_functions) > 5:
            issues.append({
                'type': 'excessive_anonymous_functions',
                'line': 0,
                'code': f'Found {len(anonymous_functions)} anonymous functions',
                'severity': 'info',
                'description': 'Excessive use of anonymous functions',
                'recommendation': 'Consider using named functions for better debugging'
            })
        
        return issues
    
    def _analyze_general_quality(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Análisis general de calidad"""
        
        issues = []
        lines = content.splitlines()
        
        # Verificar líneas muy largas
        max_line_length = 100
        for line_num, line in enumerate(lines, 1):
            if len(line) > max_line_length:
                issues.append({
                    'type': 'long_line',
                    'line': line_num,
                    'code': line[:50] + '...',
                    'severity': 'info',
                    'description': f'Line too long ({len(line)} characters)',
                    'recommendation': f'Keep lines under {max_line_length} characters'
                })
        
        # Verificar líneas en blanco excesivas
        consecutive_empty = 0
        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                consecutive_empty += 1
            else:
                if consecutive_empty > 3:
                    issues.append({
                        'type': 'excessive_blank_lines',
                        'line': line_num - consecutive_empty,
                        'code': f'{consecutive_empty} consecutive blank lines',
                        'severity': 'info',
                        'description': 'Too many consecutive blank lines',
                        'recommendation': 'Limit consecutive blank lines to 2-3'
                    })
                consecutive_empty = 0
        
        # Verificar comentarios TODO/FIXME
        todo_comments = []
        for line_num, line in enumerate(lines, 1):
            if re.search(r'(TODO|FIXME|XXX|HACK)', line, re.IGNORECASE):
                todo_comments.append(line_num)
        
        if len(todo_comments) > 10:
            issues.append({
                'type': 'excessive_todos',
                'line': 0,
                'code': f'Found {len(todo_comments)} TODO comments',
                'severity': 'info',
                'description': 'Many unresolved TODO comments',
                'recommendation': 'Address TODO comments or create proper issues'
            })
        
        return issues
    
    def _calculate_quality_metrics(self, content: str, language: str) -> Dict[str, Any]:
        """Calcular métricas de calidad"""
        
        lines = content.splitlines()
        
        metrics = {
            'total_lines': len(lines),
            'code_lines': len([line for line in lines if line.strip()]),
            'comment_lines': 0,
            'blank_lines': len([line for line in lines if not line.strip()]),
            'average_line_length': 0,
            'comment_ratio': 0
        }
        
        # Contar comentarios
        comment_patterns = {
            'python': r'^\s*#',
            'javascript': r'^\s*//',
        }
        
        if language in comment_patterns:
            pattern = comment_patterns[language]
            metrics['comment_lines'] = len([
                line for line in lines if re.match(pattern, line)
            ])
        
        # Calcular longitud promedio de línea
        if metrics['code_lines'] > 0:
            total_length = sum(len(line) for line in lines if line.strip())
            metrics['average_line_length'] = total_length / metrics['code_lines']
        
        # Calcular ratio de comentarios
        if metrics['code_lines'] > 0:
            metrics['comment_ratio'] = metrics['comment_lines'] / metrics['code_lines'] * 100
        
        return metrics
    
    def _calculate_quality_score(self, issues: List[Dict], metrics: Dict) -> int:
        """Calcular puntuación de calidad (0-100)"""
        
        base_score = 100
        
        # Penalizar por issues
        for issue in issues:
            if issue['severity'] == 'critical':
                base_score -= 25
            elif issue['severity'] == 'warning':
                base_score -= 10
            else:
                base_score -= 3
        
        # Bonificar por buenas métricas
        comment_ratio = metrics.get('comment_ratio', 0)
        if comment_ratio > 10:  # Buen ratio de comentarios
            base_score += 5
        
        avg_line_length = metrics.get('average_line_length', 0)
        if 50 <= avg_line_length <= 80:  # Longitud de línea óptima
            base_score += 3
        
        return max(0, min(100, int(base_score)))
    
    def _calculate_maintainability_index(self, metrics: Dict) -> float:
        """Calcular índice de mantenibilidad"""
        
        # Fórmula simplificada basada en métricas
        loc = metrics.get('code_lines', 1)
        comment_ratio = metrics.get('comment_ratio', 0)
        
        # Índice base
        mi = 171 - 5.2 * (loc / 100) - 0.23 * (loc / 10) + 16.2 * (comment_ratio / 10)
        
        return max(0, min(100, mi))
    
    def _calculate_max_nesting(self, tree: ast.AST) -> int:
        """Calcular nivel máximo de anidamiento"""
        
        def get_nesting_depth(node, current_depth=0):
            max_depth = current_depth
            
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                    child_depth = get_nesting_depth(child, current_depth + 1)
                    max_depth = max(max_depth, child_depth)
                else:
                    child_depth = get_nesting_depth(child, current_depth)
                    max_depth = max(max_depth, child_depth)
            
            return max_depth
        
        return get_nesting_depth(tree)
    
    def _get_maintainability_rating(self, score: int) -> str:
        """Obtener rating de mantenibilidad"""
        
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _detect_language(self, extension: str) -> str:
        """Detectar lenguaje por extensión"""
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'javascript',
            '.tsx': 'javascript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c'
        }
        
        return language_map.get(extension, 'unknown')
    
    def _is_quality_analyzable(self, filename: str) -> bool:
        """Verificar si el archivo puede ser analizado"""
        
        analyzable_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', 
            '.java', '.cpp', '.c', '.cs', '.php'
        }
        
        return any(filename.endswith(ext) for ext in analyzable_extensions)