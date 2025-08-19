"""
🚀 CodeCraft Ultimate v6.0 - Analizador de Código
"""

import ast
import os
from typing import Dict, List, Any
from ..core.exceptions import AnalysisError


class CodeAnalyzer:
    """Analizador principal de código"""
    
    def __init__(self):
        self.supported_extensions = {
            '.py': self._analyze_python,
            '.js': self._analyze_javascript, 
            '.ts': self._analyze_typescript,
            '.jsx': self._analyze_javascript,
            '.tsx': self._analyze_typescript
        }
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analizar un archivo específico"""
        
        if not os.path.exists(file_path):
            raise AnalysisError(f"File not found: {file_path}")
        
        extension = os.path.splitext(file_path)[1].lower()
        
        if extension not in self.supported_extensions:
            return self._analyze_generic(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analyzer = self.supported_extensions[extension]
            return analyzer(content, file_path)
            
        except Exception as e:
            raise AnalysisError(f"Analysis failed for {file_path}: {e}")
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analizar proyecto completo"""
        
        results = {
            'files_analyzed': 0,
            'total_lines': 0,
            'total_functions': 0,
            'total_classes': 0,
            'languages': set(),
            'files': []
        }
        
        for root, dirs, files in os.walk(project_path):
            # Skip common build directories
            dirs[:] = [d for d in dirs if d not in {
                'node_modules', '.git', '__pycache__', 'build', 'dist'
            }]
            
            for file in files:
                if self._is_code_file(file):
                    file_path = os.path.join(root, file)
                    try:
                        file_analysis = self.analyze_file(file_path)
                        results['files'].append(file_analysis)
                        results['files_analyzed'] += 1
                        results['total_lines'] += file_analysis.get('lines_of_code', 0)
                        results['total_functions'] += file_analysis.get('functions', 0)
                        results['total_classes'] += file_analysis.get('classes', 0)
                        results['languages'].add(file_analysis.get('language', 'unknown'))
                    except AnalysisError:
                        continue
        
        results['languages'] = list(results['languages'])
        return results
    
    def _analyze_python(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analizar código Python"""
        
        try:
            tree = ast.parse(content)
            
            functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
            classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
            imports = len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))])
            
            lines = content.splitlines()
            loc = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            
            complexity = self._calculate_complexity(tree)
            
            return {
                'file_path': file_path,
                'language': 'python',
                'lines_of_code': loc,
                'functions': functions,
                'classes': classes,
                'imports': imports,
                'complexity': complexity,
                'syntax_valid': True
            }
            
        except SyntaxError as e:
            return {
                'file_path': file_path,
                'language': 'python', 
                'syntax_valid': False,
                'syntax_error': str(e)
            }
    
    def _analyze_javascript(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analizar código JavaScript"""
        
        lines = content.splitlines()
        loc = len([line for line in lines if line.strip() and not line.strip().startswith('//')])
        
        # Conteo básico con regex
        import re
        functions = len(re.findall(r'function\s+\w+|=>\s*{|\w+\s*:\s*function', content))
        classes = len(re.findall(r'class\s+\w+', content))
        imports = len(re.findall(r'import\s+.*from|require\s*\(', content))
        
        return {
            'file_path': file_path,
            'language': 'javascript',
            'lines_of_code': loc,
            'functions': functions,
            'classes': classes,
            'imports': imports,
            'complexity': self._estimate_js_complexity(content),
            'syntax_valid': True  # Simplificado
        }
    
    def _analyze_typescript(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analizar código TypeScript"""
        
        # Basado en JavaScript con características adicionales
        result = self._analyze_javascript(content, file_path)
        result['language'] = 'typescript'
        
        # Agregar análisis específico de TypeScript
        import re
        interfaces = len(re.findall(r'interface\s+\w+', content))
        types = len(re.findall(r'type\s+\w+', content))
        
        result['interfaces'] = interfaces
        result['types'] = types
        
        return result
    
    def _analyze_generic(self, file_path: str) -> Dict[str, Any]:
        """Análisis genérico para archivos no soportados"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.splitlines()
            loc = len([line for line in lines if line.strip()])
            
            return {
                'file_path': file_path,
                'language': 'unknown',
                'lines_of_code': loc,
                'functions': 0,
                'classes': 0,
                'imports': 0,
                'complexity': 1,
                'syntax_valid': True
            }
            
        except Exception:
            return {
                'file_path': file_path,
                'language': 'unknown',
                'analysis_failed': True
            }
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calcular complejidad ciclomática"""
        
        complexity = 1  # Complejidad base
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, (ast.Try, ast.ExceptHandler)):
                complexity += 1
        
        return complexity
    
    def _estimate_js_complexity(self, content: str) -> int:
        """Estimar complejidad de JavaScript"""
        
        complexity_keywords = ['if', 'else', 'while', 'for', 'switch', 'case', 'catch', '&&', '||']
        complexity = 1
        
        for keyword in complexity_keywords:
            complexity += content.count(keyword)
        
        return complexity
    
    def _is_code_file(self, filename: str) -> bool:
        """Verificar si es archivo de código"""
        
        code_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala'
        }
        
        return any(filename.endswith(ext) for ext in code_extensions)