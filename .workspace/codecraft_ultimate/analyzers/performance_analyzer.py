"""
🚀 CodeCraft Ultimate v6.0 - Analizador de Performance
"""

import ast
import os
import re
from typing import Dict, List, Any
from ..core.exceptions import AnalysisError


class PerformanceAnalyzer:
    """Analizador de rendimiento del código"""
    
    def __init__(self):
        self.performance_patterns = {
            'python': {
                'inefficient_loops': [
                    r'for.*in.*range\(len\(',
                    r'while.*len\(',
                ],
                'string_concatenation': [
                    r'\+\s*["\'].*["\']',
                    r'["\'].*["\']s*\+',
                ],
                'repeated_computations': [
                    r'for.*in.*:.*\n.*for.*in.*:',
                ],
                'memory_leaks': [
                    r'global\s+\w+\s*=',
                    r'del\s+(?!self\.|cls\.)',
                ]
            },
            'javascript': {
                'dom_queries': [
                    r'document\.getElementById.*for.*{',
                    r'querySelector.*for.*{',
                ],
                'inefficient_loops': [
                    r'for.*length.*\+\+',
                ],
                'memory_leaks': [
                    r'setInterval.*(?!clearInterval)',
                    r'addEventListener.*(?!removeEventListener)',
                ]
            }
        }
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analizar rendimiento de un archivo"""
        
        if not os.path.exists(file_path):
            raise AnalysisError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            extension = os.path.splitext(file_path)[1].lower()
            language = self._detect_language(extension)
            
            issues = self._analyze_content(content, language, file_path)
            metrics = self._calculate_metrics(content, language)
            
            return {
                'file_path': file_path,
                'language': language,
                'performance_issues': len(issues),
                'issues': issues,
                'metrics': metrics,
                'performance_score': self._calculate_score(issues, metrics)
            }
            
        except Exception as e:
            raise AnalysisError(f"Performance analysis failed for {file_path}: {e}")
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analizar rendimiento del proyecto completo"""
        
        results = {
            'total_files': 0,
            'total_issues': 0,
            'critical_issues': 0,
            'warning_issues': 0,
            'info_issues': 0,
            'files': []
        }
        
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in {
                'node_modules', '.git', '__pycache__', 'build', 'dist'
            }]
            
            for file in files:
                if self._is_analyzable_file(file):
                    file_path = os.path.join(root, file)
                    try:
                        file_result = self.analyze_file(file_path)
                        results['files'].append(file_result)
                        results['total_files'] += 1
                        
                        for issue in file_result['issues']:
                            results['total_issues'] += 1
                            if issue['severity'] == 'critical':
                                results['critical_issues'] += 1
                            elif issue['severity'] == 'warning':
                                results['warning_issues'] += 1
                            else:
                                results['info_issues'] += 1
                                
                    except AnalysisError:
                        continue
        
        results['project_performance_score'] = self._calculate_project_score(results)
        return results
    
    def _analyze_content(self, content: str, language: str, file_path: str) -> List[Dict[str, Any]]:
        """Analizar contenido por patrones de rendimiento"""
        
        issues = []
        
        if language == 'python':
            issues.extend(self._analyze_python_performance(content))
        elif language == 'javascript':
            issues.extend(self._analyze_js_performance(content))
        
        # Análisis general de patrones
        if language in self.performance_patterns:
            patterns = self.performance_patterns[language]
            lines = content.splitlines()
            
            for issue_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line):
                            issue = {
                                'type': issue_type,
                                'line': line_num,
                                'code': line.strip(),
                                'severity': self._get_issue_severity(issue_type),
                                'description': self._get_issue_description(issue_type),
                                'recommendation': self._get_issue_fix(issue_type)
                            }
                            issues.append(issue)
        
        return issues
    
    def _analyze_python_performance(self, content: str) -> List[Dict[str, Any]]:
        """Análisis específico de Python"""
        
        issues = []
        
        try:
            tree = ast.parse(content)
            
            # Buscar bucles anidados
            nested_loops = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.For, ast.While)):
                    for child in ast.walk(node):
                        if child != node and isinstance(child, (ast.For, ast.While)):
                            nested_loops += 1
            
            if nested_loops > 2:
                issues.append({
                    'type': 'nested_loops',
                    'line': 0,
                    'code': f'Found {nested_loops} nested loops',
                    'severity': 'warning',
                    'description': 'Multiple nested loops detected',
                    'recommendation': 'Consider optimizing algorithm complexity'
                })
            
            # Buscar funciones largas
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno + 1
                    if func_lines > 50:
                        issues.append({
                            'type': 'large_function',
                            'line': node.lineno,
                            'code': f'Function {node.name} has {func_lines} lines',
                            'severity': 'info',
                            'description': 'Function is too large',
                            'recommendation': 'Consider breaking into smaller functions'
                        })
        
        except SyntaxError:
            pass
        
        return issues
    
    def _analyze_js_performance(self, content: str) -> List[Dict[str, Any]]:
        """Análisis específico de JavaScript"""
        
        issues = []
        
        # Buscar acceso repetido al DOM
        dom_access_count = len(re.findall(r'document\.(getElementById|querySelector)', content))
        if dom_access_count > 10:
            issues.append({
                'type': 'excessive_dom_access',
                'line': 0,
                'code': f'{dom_access_count} DOM queries found',
                'severity': 'warning',
                'description': 'Excessive DOM queries detected',
                'recommendation': 'Cache DOM elements or use virtual DOM'
            })
        
        # Buscar uso de var en bucles
        var_in_loops = re.findall(r'for.*var\s+\w+', content)
        if var_in_loops:
            issues.append({
                'type': 'var_in_loop',
                'line': 0,
                'code': 'var used in loop',
                'severity': 'info',
                'description': 'Variable declared with var in loop',
                'recommendation': 'Use let or const instead of var'
            })
        
        return issues
    
    def _calculate_metrics(self, content: str, language: str) -> Dict[str, Any]:
        """Calcular métricas de rendimiento"""
        
        lines = content.splitlines()
        
        metrics = {
            'lines_of_code': len([line for line in lines if line.strip()]),
            'function_count': 0,
            'complexity_score': 1,
            'maintainability_index': 0
        }
        
        if language == 'python':
            try:
                tree = ast.parse(content)
                metrics['function_count'] = len([
                    node for node in ast.walk(tree) 
                    if isinstance(node, ast.FunctionDef)
                ])
                
                # Calcular complejidad ciclomática simplificada
                complexity = 1
                for node in ast.walk(tree):
                    if isinstance(node, (ast.If, ast.While, ast.For)):
                        complexity += 1
                
                metrics['complexity_score'] = complexity
                
            except SyntaxError:
                pass
        
        elif language == 'javascript':
            # Conteo básico para JavaScript
            metrics['function_count'] = len(re.findall(r'function\s+\w+|=>\s*{', content))
            
            # Complejidad estimada
            complexity_keywords = ['if', 'else', 'while', 'for', 'switch']
            complexity = 1
            for keyword in complexity_keywords:
                complexity += content.count(keyword)
            
            metrics['complexity_score'] = complexity
        
        # Índice de mantenibilidad (simplificado)
        loc = metrics['lines_of_code']
        complexity = metrics['complexity_score']
        
        if loc > 0:
            metrics['maintainability_index'] = max(0, 100 - (complexity * 2) - (loc * 0.1))
        else:
            metrics['maintainability_index'] = 100
        
        return metrics
    
    def _calculate_score(self, issues: List[Dict], metrics: Dict) -> int:
        """Calcular puntuación de rendimiento"""
        
        base_score = 100
        
        # Penalizar por issues
        for issue in issues:
            if issue['severity'] == 'critical':
                base_score -= 20
            elif issue['severity'] == 'warning':
                base_score -= 10
            else:
                base_score -= 5
        
        # Ajustar por complejidad
        complexity = metrics.get('complexity_score', 1)
        if complexity > 10:
            base_score -= (complexity - 10) * 2
        
        # Ajustar por tamaño
        loc = metrics.get('lines_of_code', 0)
        if loc > 500:
            base_score -= (loc - 500) * 0.01
        
        return max(0, int(base_score))
    
    def _calculate_project_score(self, results: Dict) -> int:
        """Calcular puntuación del proyecto"""
        
        if results['total_files'] == 0:
            return 100
        
        total_penalty = (
            results['critical_issues'] * 20 +
            results['warning_issues'] * 10 +
            results['info_issues'] * 5
        )
        
        avg_penalty = total_penalty / results['total_files']
        score = max(0, 100 - avg_penalty)
        
        return int(score)
    
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
    
    def _get_issue_severity(self, issue_type: str) -> str:
        """Obtener severidad del issue"""
        
        severity_map = {
            'nested_loops': 'warning',
            'inefficient_loops': 'warning',
            'string_concatenation': 'info',
            'memory_leaks': 'critical',
            'dom_queries': 'warning',
            'large_function': 'info'
        }
        
        return severity_map.get(issue_type, 'info')
    
    def _get_issue_description(self, issue_type: str) -> str:
        """Obtener descripción del issue"""
        
        descriptions = {
            'nested_loops': 'Nested loops may cause performance issues',
            'inefficient_loops': 'Loop implementation is not optimal',
            'string_concatenation': 'String concatenation in loop is inefficient',
            'memory_leaks': 'Potential memory leak detected',
            'dom_queries': 'Excessive DOM queries impact performance',
            'large_function': 'Function is too large and complex'
        }
        
        return descriptions.get(issue_type, 'Performance issue detected')
    
    def _get_issue_fix(self, issue_type: str) -> str:
        """Obtener recomendación de corrección"""
        
        fixes = {
            'nested_loops': 'Consider using more efficient algorithms',
            'inefficient_loops': 'Use enumerate() or iterators instead',
            'string_concatenation': 'Use join() or f-strings for string building',
            'memory_leaks': 'Ensure proper cleanup of resources',
            'dom_queries': 'Cache DOM references or use event delegation',
            'large_function': 'Break function into smaller, focused functions'
        }
        
        return fixes.get(issue_type, 'Review and optimize code')
    
    def _is_analyzable_file(self, filename: str) -> bool:
        """Verificar si el archivo puede ser analizado"""
        
        analyzable_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', 
            '.java', '.cpp', '.c', '.cs', '.php'
        }
        
        return any(filename.endswith(ext) for ext in analyzable_extensions)