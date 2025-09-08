from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import re
import difflib


class ContextExtractor:
    """Extractor de contexto para información detallada de errores"""
    
    def __init__(self, max_context_lines: int = 5):
        self.max_context_lines = max_context_lines
    
    def extract_surrounding_lines(self, file_path: str, line_number: int,
                                context_lines: int = None) -> Dict[str, Any]:
        """Extraer líneas antes y después de una línea específica"""
        if context_lines is None:
            context_lines = self.max_context_lines
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            start = max(0, line_number - context_lines - 1)
            end = min(total_lines, line_number + context_lines)
            
            context = {
                'target_line_number': line_number,
                'target_line': lines[line_number - 1].strip() if line_number <= total_lines else None,
                'before_lines': [
                    {'number': i + 1, 'content': lines[i].strip()} 
                    for i in range(start, line_number - 1)
                ],
                'after_lines': [
                    {'number': i + 1, 'content': lines[i].strip()} 
                    for i in range(line_number, end)
                ],
                'total_lines': total_lines
            }
            
            return context
            
        except Exception as e:
            return {'error': f'Failed to extract context: {str(e)}'}
    
    def extract_pattern_context(self, file_path: str, pattern: str, 
                              is_regex: bool = False) -> Dict[str, Any]:
        """Extraer contexto específico donde se intentó encontrar un patrón"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            context = {
                'pattern_searched': pattern,
                'is_regex': is_regex,
                'file_info': {
                    'total_lines': len(lines),
                    'total_chars': len(content),
                    'file_size_bytes': Path(file_path).stat().st_size
                },
                'sample_content': {
                    'first_lines': lines[:3],
                    'last_lines': lines[-3:] if len(lines) > 3 else [],
                    'random_middle': lines[len(lines)//2:len(lines)//2+2] if len(lines) > 5 else []
                },
                'potential_matches': []
            }
            
            # Buscar coincidencias similares
            if not is_regex:
                similar_lines = []
                pattern_lower = pattern.lower()
                for i, line in enumerate(lines):
                    if pattern_lower in line.lower():
                        similar_lines.append({
                            'line_number': i + 1,
                            'content': line.strip(),
                            'match_type': 'case_insensitive'
                        })
                    elif pattern in line:
                        similar_lines.append({
                            'line_number': i + 1,
                            'content': line.strip(),
                            'match_type': 'exact'
                        })
                
                context['potential_matches'] = similar_lines[:5]  # Límite de 5
            
            return context
            
        except Exception as e:
            return {'error': f'Failed to extract pattern context: {str(e)}'}
    
    def suggest_alternatives(self, file_path: str, pattern: str, 
                           threshold: float = 0.6) -> List[Dict[str, Any]]:
        """Sugerir patrones alternativos basados en contenido del archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            suggestions = []
            
            # Buscar líneas similares usando difflib
            all_text_pieces = []
            for line in lines:
                words = line.split()
                all_text_pieces.extend(words)
                if line.strip():
                    all_text_pieces.append(line.strip())
            
            # Obtener coincidencias similares
            close_matches = difflib.get_close_matches(
                pattern, all_text_pieces, n=5, cutoff=threshold
            )
            
            for match in close_matches:
                # Encontrar en qué línea aparece
                for i, line in enumerate(lines):
                    if match in line:
                        suggestions.append({
                            'suggested_pattern': match,
                            'line_number': i + 1,
                            'line_content': line.strip(),
                            'similarity_score': difflib.SequenceMatcher(None, pattern, match).ratio()
                        })
                        break
            
            # Sugerencias de casos comunes
            common_suggestions = []
            if pattern.islower():
                common_suggestions.append({
                    'suggested_pattern': pattern.title(),
                    'reason': 'Try with title case',
                    'example': f'Original: "{pattern}" -> Suggested: "{pattern.title()}"'
                })
            
            if pattern.isupper():
                common_suggestions.append({
                    'suggested_pattern': pattern.lower(),
                    'reason': 'Try with lowercase',
                    'example': f'Original: "{pattern}" -> Suggested: "{pattern.lower()}"'
                })
            
            return {
                'similar_patterns': suggestions[:3],  # Top 3
                'common_case_suggestions': common_suggestions,
                'regex_suggestions': [
                    {
                        'pattern': f'.*{re.escape(pattern)}.*',
                        'description': 'Match lines containing the pattern'
                    },
                    {
                        'pattern': f'^.*{re.escape(pattern)}',
                        'description': 'Match lines ending with the pattern'
                    }
                ]
            }
            
        except Exception as e:
            return {'error': f'Failed to generate suggestions: {str(e)}'}
    
    def analyze_file_structure(self, file_path: str) -> Dict[str, Any]:
        """Analizar estructura del archivo para mejor debugging"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            analysis = {
                'file_info': {
                    'path': file_path,
                    'size_bytes': len(content),
                    'total_lines': len(lines),
                    'non_empty_lines': len([l for l in lines if l.strip()]),
                    'encoding': 'utf-8'
                },
                'content_analysis': {
                    'has_imports': any('import ' in line for line in lines[:20]),
                    'has_functions': any('def ' in line for line in lines),
                    'has_classes': any('class ' in line for line in lines),
                    'indentation_style': self._detect_indentation(lines),
                    'line_endings': self._detect_line_endings(content)
                },
                'structure_hints': []
            }
            
            # Generar hints basados en el análisis
            if analysis['content_analysis']['has_functions']:
                analysis['structure_hints'].append('File contains function definitions')
            if analysis['content_analysis']['has_classes']:
                analysis['structure_hints'].append('File contains class definitions')
                
            return analysis
            
        except Exception as e:
            return {'error': f'Failed to analyze file structure: {str(e)}'}
    
    def _detect_indentation(self, lines: List[str]) -> str:
        """Detectar estilo de indentación del archivo"""
        indent_counts = {'spaces': 0, 'tabs': 0}
        
        for line in lines:
            if line.startswith('    '):
                indent_counts['spaces'] += 1
            elif line.startswith('\t'):
                indent_counts['tabs'] += 1
                
        if indent_counts['spaces'] > indent_counts['tabs']:
            return 'spaces'
        elif indent_counts['tabs'] > 0:
            return 'tabs'
        else:
            return 'unknown'
    
    def _detect_line_endings(self, content: str) -> str:
        """Detectar tipo de terminaciones de línea"""
        if '\r\n' in content:
            return 'CRLF (Windows)'
        elif '\n' in content:
            return 'LF (Unix/Linux)'
        elif '\r' in content:
            return 'CR (Old Mac)'
        else:
            return 'unknown'