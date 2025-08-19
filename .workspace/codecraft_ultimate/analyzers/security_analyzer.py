"""
🚀 CodeCraft Ultimate v6.0 - Analizador de Seguridad
"""

import re
import os
from typing import Dict, List, Any
from ..core.exceptions import AnalysisError


class SecurityAnalyzer:
    """Analizador de seguridad del código"""
    
    def __init__(self):
        self.vulnerability_patterns = {
            'python': {
                'sql_injection': [
                    r'execute\s*\(\s*["\'].*%.*["\']',
                    r'cursor\.execute\s*\(\s*f["\'].*{.*}.*["\']',
                    r'\.format\s*\(.*\)\s*\)',
                ],
                'xss': [
                    r'render_template_string\s*\(.*\+',
                    r'Markup\s*\(.*\+',
                ],
                'command_injection': [
                    r'os\.system\s*\(.*\+',
                    r'subprocess\.call\s*\(.*\+',
                    r'eval\s*\(',
                    r'exec\s*\(',
                ],
                'hardcoded_secrets': [
                    r'password\s*=\s*["\'][^"\']+["\']',
                    r'api_key\s*=\s*["\'][^"\']+["\']',
                    r'secret\s*=\s*["\'][^"\']+["\']',
                ]
            },
            'javascript': {
                'xss': [
                    r'innerHTML\s*=.*\+',
                    r'document\.write\s*\(.*\+',
                    r'eval\s*\(',
                ],
                'prototype_pollution': [
                    r'__proto__',
                    r'constructor\.prototype',
                ],
                'unsafe_regex': [
                    r'new\s+RegExp\s*\(.*\+',
                ]
            }
        }
    
    def scan_file(self, file_path: str, severity: str = 'medium') -> Dict[str, Any]:
        """Escanear archivo por vulnerabilidades"""
        
        if not os.path.exists(file_path):
            raise AnalysisError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            extension = os.path.splitext(file_path)[1].lower()
            language = self._detect_language(extension)
            
            vulnerabilities = self._scan_content(content, language, file_path)
            
            # Filtrar por severidad
            filtered_vulns = self._filter_by_severity(vulnerabilities, severity)
            
            return {
                'file_path': file_path,
                'language': language,
                'vulnerabilities_found': len(filtered_vulns),
                'vulnerabilities': filtered_vulns,
                'security_score': self._calculate_security_score(filtered_vulns),
                'severity_filter': severity
            }
            
        except Exception as e:
            raise AnalysisError(f"Security scan failed for {file_path}: {e}")
    
    def scan_project(self, project_path: str, severity: str = 'medium') -> Dict[str, Any]:
        """Escanear proyecto completo"""
        
        results = {
            'total_files_scanned': 0,
            'total_vulnerabilities': 0,
            'high_severity': 0,
            'medium_severity': 0,
            'low_severity': 0,
            'files': []
        }
        
        for root, dirs, files in os.walk(project_path):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in {
                'node_modules', '.git', '__pycache__', 'build', 'dist', '.venv'
            }]
            
            for file in files:
                if self._is_scannable_file(file):
                    file_path = os.path.join(root, file)
                    try:
                        file_result = self.scan_file(file_path, severity)
                        results['files'].append(file_result)
                        results['total_files_scanned'] += 1
                        
                        # Count vulnerabilities by severity
                        for vuln in file_result['vulnerabilities']:
                            results['total_vulnerabilities'] += 1
                            if vuln['severity'] == 'high':
                                results['high_severity'] += 1
                            elif vuln['severity'] == 'medium':
                                results['medium_severity'] += 1
                            else:
                                results['low_severity'] += 1
                                
                    except AnalysisError:
                        continue
        
        results['project_security_score'] = self._calculate_project_score(results)
        return results
    
    def _scan_content(self, content: str, language: str, file_path: str) -> List[Dict[str, Any]]:
        """Escanear contenido por patrones de vulnerabilidad"""
        
        vulnerabilities = []
        
        if language not in self.vulnerability_patterns:
            return vulnerabilities
        
        patterns = self.vulnerability_patterns[language]
        lines = content.splitlines()
        
        for vuln_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        vulnerability = {
                            'type': vuln_type,
                            'line': line_num,
                            'code': line.strip(),
                            'severity': self._get_vulnerability_severity(vuln_type),
                            'description': self._get_vulnerability_description(vuln_type),
                            'recommendation': self._get_vulnerability_fix(vuln_type)
                        }
                        vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    def _detect_language(self, extension: str) -> str:
        """Detectar lenguaje por extensión"""
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript', 
            '.ts': 'javascript',
            '.tsx': 'javascript',
            '.php': 'php',
            '.java': 'java',
            '.cs': 'csharp',
            '.rb': 'ruby'
        }
        
        return language_map.get(extension, 'unknown')
    
    def _get_vulnerability_severity(self, vuln_type: str) -> str:
        """Obtener severidad de vulnerabilidad"""
        
        severity_map = {
            'sql_injection': 'high',
            'command_injection': 'high',
            'xss': 'high',
            'hardcoded_secrets': 'medium',
            'prototype_pollution': 'medium',
            'unsafe_regex': 'low'
        }
        
        return severity_map.get(vuln_type, 'low')
    
    def _get_vulnerability_description(self, vuln_type: str) -> str:
        """Obtener descripción de vulnerabilidad"""
        
        descriptions = {
            'sql_injection': 'Potential SQL injection vulnerability',
            'command_injection': 'Potential command injection vulnerability',
            'xss': 'Potential cross-site scripting (XSS) vulnerability',
            'hardcoded_secrets': 'Hardcoded credentials or secrets detected',
            'prototype_pollution': 'Potential prototype pollution vulnerability',
            'unsafe_regex': 'Potentially unsafe regular expression'
        }
        
        return descriptions.get(vuln_type, 'Security issue detected')
    
    def _get_vulnerability_fix(self, vuln_type: str) -> str:
        """Obtener recomendación de corrección"""
        
        fixes = {
            'sql_injection': 'Use parameterized queries or prepared statements',
            'command_injection': 'Avoid executing user input directly, use safe APIs',
            'xss': 'Sanitize and escape user input before rendering',
            'hardcoded_secrets': 'Use environment variables or secure key management',
            'prototype_pollution': 'Validate object properties and use Object.create(null)',
            'unsafe_regex': 'Review regex pattern for ReDoS vulnerabilities'
        }
        
        return fixes.get(vuln_type, 'Review and fix security issue')
    
    def _filter_by_severity(self, vulnerabilities: List[Dict], severity: str) -> List[Dict]:
        """Filtrar vulnerabilidades por severidad"""
        
        severity_levels = {'low': 0, 'medium': 1, 'high': 2}
        min_level = severity_levels.get(severity, 1)
        
        return [
            vuln for vuln in vulnerabilities 
            if severity_levels.get(vuln['severity'], 0) >= min_level
        ]
    
    def _calculate_security_score(self, vulnerabilities: List[Dict]) -> int:
        """Calcular puntuación de seguridad (0-100)"""
        
        if not vulnerabilities:
            return 100
        
        high_count = sum(1 for v in vulnerabilities if v['severity'] == 'high')
        medium_count = sum(1 for v in vulnerabilities if v['severity'] == 'medium') 
        low_count = sum(1 for v in vulnerabilities if v['severity'] == 'low')
        
        # Penalizar más las vulnerabilidades de alta severidad
        penalty = (high_count * 20) + (medium_count * 10) + (low_count * 5)
        score = max(0, 100 - penalty)
        
        return score
    
    def _calculate_project_score(self, results: Dict) -> int:
        """Calcular puntuación de seguridad del proyecto"""
        
        if results['total_files_scanned'] == 0:
            return 100
        
        total_penalty = (
            results['high_severity'] * 20 +
            results['medium_severity'] * 10 +
            results['low_severity'] * 5
        )
        
        # Normalizar por número de archivos
        avg_penalty = total_penalty / results['total_files_scanned']
        score = max(0, 100 - avg_penalty)
        
        return int(score)
    
    def _is_scannable_file(self, filename: str) -> bool:
        """Verificar si el archivo puede ser escaneado"""
        
        scannable_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.php', 
            '.java', '.cs', '.rb', '.go', '.cpp', '.c'
        }
        
        return any(filename.endswith(ext) for ext in scannable_extensions)