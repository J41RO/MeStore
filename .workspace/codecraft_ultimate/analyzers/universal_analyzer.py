"""
🚀 CodeCraft Ultimate v6.0 - Universal Analyzer  
Advanced multi-language code analysis
"""

import os
import ast
import re
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass


@dataclass
class ComplexityMetrics:
    """Code complexity metrics"""
    cyclomatic_complexity: int
    cognitive_complexity: int
    lines_of_code: int
    functions: int
    classes: int
    complexity_score: float


@dataclass
class DependencyInfo:
    """Dependency information"""
    name: str
    type: str  # 'import', 'require', 'include', etc.
    source: Optional[str] = None
    line_number: Optional[int] = None


class UniversalAnalyzer:
    """Universal code analyzer supporting multiple languages"""
    
    def __init__(self):
        self.language_parsers = {
            'python': self._analyze_python,
            'javascript': self._analyze_javascript,
            'typescript': self._analyze_typescript,
            'java': self._analyze_java,
            'cpp': self._analyze_cpp,
            'csharp': self._analyze_csharp
        }
    
    def detect_file_type(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        
        type_mapping = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript', 
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala'
        }
        
        return type_mapping.get(ext, 'unknown')
    
    def analyze_complexity(self, content: str, file_path: str = '') -> ComplexityMetrics:
        """Analyze code complexity universally"""
        file_type = self.detect_file_type(file_path) if file_path else 'unknown'
        
        if file_type in self.language_parsers:
            return self.language_parsers[file_type](content)
        else:
            return self._analyze_generic(content)
    
    def extract_dependencies(self, content: str, file_path: str = '') -> List[DependencyInfo]:
        """Extract dependencies from code"""
        file_type = self.detect_file_type(file_path) if file_path else 'unknown'
        dependencies = []
        
        if file_type == 'python':
            dependencies.extend(self._extract_python_imports(content))
        elif file_type in ['javascript', 'typescript']:
            dependencies.extend(self._extract_js_imports(content))
        elif file_type == 'java':
            dependencies.extend(self._extract_java_imports(content))
        elif file_type in ['cpp', 'c']:
            dependencies.extend(self._extract_cpp_includes(content))
        elif file_type == 'csharp':
            dependencies.extend(self._extract_csharp_usings(content))
        
        return dependencies
    
    def _analyze_python(self, content: str) -> ComplexityMetrics:
        """Analyze Python code complexity"""
        try:
            tree = ast.parse(content)
            
            # Count functions and classes
            functions = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
            classes = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            
            # Calculate cyclomatic complexity
            cyclomatic = self._calculate_python_cyclomatic_complexity(tree)
            
            # Calculate cognitive complexity (simplified)
            cognitive = self._calculate_python_cognitive_complexity(tree)
            
            # Lines of code (excluding empty and comment lines)
            loc = len([line for line in content.split('\n') 
                      if line.strip() and not line.strip().startswith('#')])
            
            complexity_score = (cyclomatic * 0.4 + cognitive * 0.6) / max(loc, 1) * 100
            
            return ComplexityMetrics(
                cyclomatic_complexity=cyclomatic,
                cognitive_complexity=cognitive,
                lines_of_code=loc,
                functions=functions,
                classes=classes,
                complexity_score=complexity_score
            )
        
        except SyntaxError:
            return ComplexityMetrics(0, 0, 0, 0, 0, 0.0)
    
    def _analyze_javascript(self, content: str) -> ComplexityMetrics:
        """Analyze JavaScript code complexity"""
        # Simplified JavaScript analysis using regex patterns
        lines = content.split('\n')
        loc = len([line for line in lines 
                  if line.strip() and not line.strip().startswith('//') 
                  and not line.strip().startswith('/*')])
        
        # Count functions
        function_patterns = [
            r'function\s+\w+',
            r'\w+\s*:\s*function',
            r'const\s+\w+\s*=\s*\([^)]*\)\s*=>',
            r'let\s+\w+\s*=\s*\([^)]*\)\s*=>',
            r'var\s+\w+\s*=\s*\([^)]*\)\s*=>'
        ]
        
        functions = 0
        for pattern in function_patterns:
            functions += len(re.findall(pattern, content))
        
        # Count classes
        classes = len(re.findall(r'class\s+\w+', content))
        
        # Estimate cyclomatic complexity
        complexity_keywords = ['if', 'else', 'while', 'for', 'switch', 'case', 'catch', '&&', '||', '?']
        cyclomatic = 1  # Base complexity
        for keyword in complexity_keywords:
            cyclomatic += len(re.findall(r'\b' + keyword + r'\b', content))
        
        cognitive = int(cyclomatic * 1.2)  # Rough estimate
        complexity_score = cyclomatic / max(loc, 1) * 100
        
        return ComplexityMetrics(
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            lines_of_code=loc,
            functions=functions,
            classes=classes,
            complexity_score=complexity_score
        )
    
    def _analyze_typescript(self, content: str) -> ComplexityMetrics:
        """Analyze TypeScript code complexity"""
        # TypeScript analysis similar to JavaScript but with additional patterns
        js_metrics = self._analyze_javascript(content)
        
        # Add TypeScript-specific patterns
        interfaces = len(re.findall(r'interface\s+\w+', content))
        types = len(re.findall(r'type\s+\w+', content))
        
        # Adjust complexity for TypeScript features
        js_metrics.complexity_score *= 0.95  # TypeScript tends to be more structured
        
        return js_metrics
    
    def _analyze_java(self, content: str) -> ComplexityMetrics:
        """Analyze Java code complexity"""
        lines = content.split('\n')
        loc = len([line for line in lines 
                  if line.strip() and not line.strip().startswith('//')])
        
        # Count methods and classes
        methods = len(re.findall(r'(public|private|protected)?\s*(static\s+)?\w+\s+\w+\s*\([^)]*\)', content))
        classes = len(re.findall(r'(public\s+)?(abstract\s+)?class\s+\w+', content))
        
        # Estimate complexity
        complexity_keywords = ['if', 'else', 'while', 'for', 'switch', 'case', 'catch', '&&', '||']
        cyclomatic = 1
        for keyword in complexity_keywords:
            cyclomatic += len(re.findall(r'\b' + keyword + r'\b', content))
        
        cognitive = int(cyclomatic * 1.3)
        complexity_score = cyclomatic / max(loc, 1) * 100
        
        return ComplexityMetrics(
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            lines_of_code=loc,
            functions=methods,
            classes=classes,
            complexity_score=complexity_score
        )
    
    def _analyze_cpp(self, content: str) -> ComplexityMetrics:
        """Analyze C++ code complexity"""
        lines = content.split('\n')
        loc = len([line for line in lines 
                  if line.strip() and not line.strip().startswith('//')])
        
        # Count functions and classes
        functions = len(re.findall(r'\w+\s+\w+\s*\([^)]*\)\s*{', content))
        classes = len(re.findall(r'class\s+\w+', content))
        
        # Estimate complexity
        complexity_keywords = ['if', 'else', 'while', 'for', 'switch', 'case', 'catch', '&&', '||']
        cyclomatic = 1
        for keyword in complexity_keywords:
            cyclomatic += len(re.findall(r'\b' + keyword + r'\b', content))
        
        cognitive = int(cyclomatic * 1.4)  # C++ can be more complex
        complexity_score = cyclomatic / max(loc, 1) * 100
        
        return ComplexityMetrics(
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            lines_of_code=loc,
            functions=functions,
            classes=classes,
            complexity_score=complexity_score
        )
    
    def _analyze_csharp(self, content: str) -> ComplexityMetrics:
        """Analyze C# code complexity"""
        lines = content.split('\n')
        loc = len([line for line in lines 
                  if line.strip() and not line.strip().startswith('//')])
        
        # Count methods and classes
        methods = len(re.findall(r'(public|private|protected)?\s*(static\s+)?\w+\s+\w+\s*\([^)]*\)', content))
        classes = len(re.findall(r'(public\s+)?(abstract\s+)?class\s+\w+', content))
        
        # Estimate complexity
        complexity_keywords = ['if', 'else', 'while', 'for', 'switch', 'case', 'catch', '&&', '||']
        cyclomatic = 1
        for keyword in complexity_keywords:
            cyclomatic += len(re.findall(r'\b' + keyword + r'\b', content))
        
        cognitive = int(cyclomatic * 1.25)
        complexity_score = cyclomatic / max(loc, 1) * 100
        
        return ComplexityMetrics(
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            lines_of_code=loc,
            functions=methods,
            classes=classes,
            complexity_score=complexity_score
        )
    
    def _analyze_generic(self, content: str) -> ComplexityMetrics:
        """Generic analysis for unknown file types"""
        lines = content.split('\n')
        loc = len([line for line in lines if line.strip()])
        
        # Very basic complexity estimation
        complexity_indicators = ['{', '}', 'if', 'for', 'while']
        complexity = sum(content.count(indicator) for indicator in complexity_indicators)
        
        return ComplexityMetrics(
            cyclomatic_complexity=max(complexity, 1),
            cognitive_complexity=max(complexity, 1),
            lines_of_code=loc,
            functions=0,
            classes=0,
            complexity_score=complexity / max(loc, 1) * 100
        )
    
    def _calculate_python_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity for Python AST"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            # Decision points that increase complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, (ast.Try, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.Lambda):
                complexity += 1
        
        return complexity
    
    def _calculate_python_cognitive_complexity(self, tree: ast.AST) -> int:
        """Calculate cognitive complexity for Python AST"""
        cognitive = 0
        
        def visit_node(node, level=0):
            nonlocal cognitive
            
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                cognitive += 1 + level
            elif isinstance(node, ast.BoolOp):
                cognitive += len(node.values) - 1
            elif isinstance(node, (ast.Try, ast.ExceptHandler)):
                cognitive += 1 + level
            elif isinstance(node, ast.Lambda):
                cognitive += 1 + level
            
            # Increase nesting for compound statements
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.Try, ast.With, ast.AsyncWith)):
                level += 1
            
            for child in ast.iter_child_nodes(node):
                visit_node(child, level)
        
        visit_node(tree)
        return cognitive
    
    def _extract_python_imports(self, content: str) -> List[DependencyInfo]:
        """Extract Python import statements"""
        dependencies = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(DependencyInfo(
                            name=alias.name,
                            type='import',
                            line_number=node.lineno
                        ))
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        dependencies.append(DependencyInfo(
                            name=alias.name,
                            type='from_import',
                            source=module,
                            line_number=node.lineno
                        ))
        
        except SyntaxError:
            # Fallback to regex if AST parsing fails
            import_patterns = [
                r'import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)',
                r'from\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s+import\s+([a-zA-Z_][a-zA-Z0-9_,\s]*)'
            ]
            
            for i, line in enumerate(content.split('\n'), 1):
                for pattern in import_patterns:
                    matches = re.findall(pattern, line)
                    for match in matches:
                        if isinstance(match, tuple):
                            dependencies.append(DependencyInfo(
                                name=match[1].strip(),
                                type='from_import',
                                source=match[0],
                                line_number=i
                            ))
                        else:
                            dependencies.append(DependencyInfo(
                                name=match,
                                type='import',
                                line_number=i
                            ))
        
        return dependencies
    
    def _extract_js_imports(self, content: str) -> List[DependencyInfo]:
        """Extract JavaScript/TypeScript import statements"""
        dependencies = []
        
        # ES6 imports
        import_patterns = [
            r'import\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+{\s*([^}]+)\s*}\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+\*\s+as\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'const\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*require\([\'"]([^\'"]+)[\'"]\)',
            r'require\([\'"]([^\'"]+)[\'"]\)'
        ]
        
        for i, line in enumerate(content.split('\n'), 1):
            for pattern in import_patterns:
                matches = re.findall(pattern, line.strip())
                for match in matches:
                    if isinstance(match, tuple) and len(match) >= 2:
                        dependencies.append(DependencyInfo(
                            name=match[0],
                            type='import',
                            source=match[1],
                            line_number=i
                        ))
                    elif isinstance(match, str):
                        dependencies.append(DependencyInfo(
                            name=match,
                            type='require',
                            line_number=i
                        ))
        
        return dependencies
    
    def _extract_java_imports(self, content: str) -> List[DependencyInfo]:
        """Extract Java import statements"""
        dependencies = []
        
        import_pattern = r'import\s+(static\s+)?([a-zA-Z_][a-zA-Z0-9_\.]*(?:\.\*)?);'
        
        for i, line in enumerate(content.split('\n'), 1):
            matches = re.findall(import_pattern, line.strip())
            for match in matches:
                is_static = match[0].strip() == 'static'
                import_name = match[1]
                
                dependencies.append(DependencyInfo(
                    name=import_name,
                    type='static_import' if is_static else 'import',
                    line_number=i
                ))
        
        return dependencies
    
    def _extract_cpp_includes(self, content: str) -> List[DependencyInfo]:
        """Extract C/C++ include statements"""
        dependencies = []
        
        include_patterns = [
            r'#include\s*<([^>]+)>',  # System headers
            r'#include\s*"([^"]+)"'   # Local headers
        ]
        
        for i, line in enumerate(content.split('\n'), 1):
            for pattern in include_patterns:
                matches = re.findall(pattern, line.strip())
                for match in matches:
                    include_type = 'system_include' if '<' in line else 'local_include'
                    dependencies.append(DependencyInfo(
                        name=match,
                        type=include_type,
                        line_number=i
                    ))
        
        return dependencies
    
    def _extract_csharp_usings(self, content: str) -> List[DependencyInfo]:
        """Extract C# using statements"""
        dependencies = []
        
        using_pattern = r'using\s+([a-zA-Z_][a-zA-Z0-9_\.]*);'
        
        for i, line in enumerate(content.split('\n'), 1):
            matches = re.findall(using_pattern, line.strip())
            for match in matches:
                dependencies.append(DependencyInfo(
                    name=match,
                    type='using',
                    line_number=i
                ))
        
        return dependencies
    
    def analyze_security_issues(self, content: str, file_path: str = '') -> List[Dict[str, Any]]:
        """Analyze potential security issues"""
        file_type = self.detect_file_type(file_path) if file_path else 'unknown'
        issues = []
        
        if file_type == 'python':
            issues.extend(self._analyze_python_security(content))
        elif file_type in ['javascript', 'typescript']:
            issues.extend(self._analyze_js_security(content))
        
        return issues
    
    def _analyze_python_security(self, content: str) -> List[Dict[str, Any]]:
        """Analyze Python security issues"""
        issues = []
        
        # Common Python security anti-patterns
        security_patterns = [
            (r'eval\s*\(', 'high', 'Use of eval() function - potential code injection'),
            (r'exec\s*\(', 'high', 'Use of exec() function - potential code injection'),
            (r'__import__\s*\(', 'medium', 'Dynamic imports may be dangerous'),
            (r'subprocess\.call.*shell\s*=\s*True', 'high', 'Shell injection vulnerability'),
            (r'os\.system\s*\(', 'high', 'Command injection vulnerability'),
            (r'pickle\.loads\s*\(', 'high', 'Unsafe deserialization'),
            (r'yaml\.load\s*\([^,]*\)', 'medium', 'Unsafe YAML loading'),
            (r'password\s*=\s*[\'"][^\'"]+[\'"]', 'medium', 'Hardcoded password'),
            (r'secret\s*=\s*[\'"][^\'"]+[\'"]', 'medium', 'Hardcoded secret'),
            (r'api[_-]?key\s*=\s*[\'"][^\'"]+[\'"]', 'medium', 'Hardcoded API key')
        ]
        
        for i, line in enumerate(content.split('\n'), 1):
            for pattern, severity, description in security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'line': i,
                        'severity': severity,
                        'description': description,
                        'code': line.strip()
                    })
        
        return issues
    
    def _analyze_js_security(self, content: str) -> List[Dict[str, Any]]:
        """Analyze JavaScript security issues"""
        issues = []
        
        # Common JavaScript security anti-patterns
        security_patterns = [
            (r'eval\s*\(', 'high', 'Use of eval() - potential code injection'),
            (r'innerHTML\s*=', 'medium', 'DOM XSS vulnerability with innerHTML'),
            (r'document\.write\s*\(', 'medium', 'Potential XSS with document.write'),
            (r'\.html\s*\([^)]*\+', 'medium', 'Potential XSS with dynamic HTML'),
            (r'window\.location\s*=.*\+', 'medium', 'Potential open redirect'),
            (r'localStorage\.setItem.*password', 'medium', 'Storing password in localStorage'),
            (r'console\.log.*password', 'low', 'Logging sensitive information'),
            (r'Math\.random\s*\(\)', 'low', 'Weak random number generation'),
            (r'http://', 'low', 'Insecure HTTP protocol')
        ]
        
        for i, line in enumerate(content.split('\n'), 1):
            for pattern, severity, description in security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'line': i,
                        'severity': severity,
                        'description': description,
                        'code': line.strip()
                    })
        
        return issues