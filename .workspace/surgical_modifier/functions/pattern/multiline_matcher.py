import re
from typing import List, Dict, Any, Optional, Tuple
from .base_matcher import BaseMatcher

class MultilineMatcher(BaseMatcher):
    """Matcher para patrones que span múltiples líneas con context awareness"""
    
    def __init__(self):
        self._context_cache = {}  # Cache contextos procesados
        self._block_cache = {}    # Cache bloques detectados
        super().__init__()
    
    # Métodos estándar requeridos por BaseMatcher
    def find(self, text: str, pattern: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Implementación estándar del método find()"""
        flags = kwargs.get('flags', re.MULTILINE | re.DOTALL)
        result = self.find_multiline_pattern(pattern, text, flags)
        if result.get('success') and result.get('matches'):
            first_match = result['matches'][0]
            return self._normalize_result(
                first_match['match'],  # Usar 'match' no 'text'
                first_match['start_pos'],  # Usar 'start_pos' no 'start'
                first_match['end_pos'],    # Usar 'end_pos' no 'end'
                list(first_match.get('groups', []))
            )
        return None
    
    def match(self, text: str, pattern: str, **kwargs) -> bool:
        """Implementación estándar del método match()"""
        flags = kwargs.get('flags', re.MULTILINE | re.DOTALL)
        result = self.find_multiline_pattern(pattern, text, flags)
        return result.get('success', False) and len(result.get('matches', [])) > 0
    
    def find_all(self, text: str, pattern: str, **kwargs) -> List[Dict[str, Any]]:
        """Implementación estándar del método find_all()"""
        flags = kwargs.get('flags', re.MULTILINE | re.DOTALL)
        result = self.find_multiline_pattern(pattern, text, flags)
        if result.get('success') and result.get('matches'):
            return [
                self._normalize_result(
                    match['match'],     # Usar 'match' no 'text'
                    match['start_pos'], # Usar 'start_pos' no 'start'
                    match['end_pos'],   # Usar 'end_pos' no 'end'
                    list(match.get('groups', []))
                )
                for match in result['matches']
            ]
        return []
    
    def find_multiline_pattern(self, pattern: str, text: str, 
                            flags: int = re.MULTILINE | re.DOTALL) -> Dict[str, Any]:
        """Encontrar patrón que puede span múltiples líneas"""
        if not pattern:
            return {'success': False, 'error': 'Empty pattern'}
        
        try:
            compiled_pattern = re.compile(pattern, flags)
            matches = []
            
            for match in compiled_pattern.finditer(text):
                # Calcular líneas afectadas
                before_match = text[:match.start()]
                lines_before = before_match.count('\n')
                matched_text = match.group()
                lines_in_match = matched_text.count('\n') + 1
                
                match_info = {
                    'match': matched_text,
                    'start_pos': match.start(),
                    'end_pos': match.end(),
                    'start_line': lines_before + 1,
                    'end_line': lines_before + lines_in_match,
                    'lines_spanned': lines_in_match,
                    'groups': match.groups(),
                    'groupdict': match.groupdict()
                }
                matches.append(match_info)
            
            return {
                'success': True,
                'pattern': pattern,
                'matches': matches,
                'count': len(matches),
                'flags_used': flags
            }
        
        except re.error as e:
            return {'success': False, 'error': f'Regex error: {e}'}
        except Exception as e:
            return {'success': False, 'error': f'Multiline match error: {e}'}
    
    def find_block_patterns(self, text: str, block_type: str = 'function') -> Dict[str, Any]:
        """Encontrar bloques específicos (function, class, try-except, etc.)"""
        patterns = {
            'function': r'def\s+(\w+)\s*\([^)]*\)\s*:\s*(?:\n(?:\s{4,}.*|\s*\n))*',
            'class': r'class\s+(\w+)(?:\([^)]*\))?\s*:\s*(?:\n(?:\s{4,}.*|\s*\n))*',
            'method': r'def\s+(\w+)\s*\(self[^)]*\)\s*:\s*(?:\n(?:\s{4,}.*|\s*\n))*',
            'try_except': r'try\s*:\s*\n(?:\s{4,}.*\n)*\s*except[^:]*:\s*\n(?:\s{4,}.*\n)*',
            'if_block': r'if\s+[^:]+:\s*\n(?:\s{4,}.*\n)*',
            'docstring': r'"""[^"]*(?:"[^"]*)*"""'
        }
        
        if block_type not in patterns:
            return {'success': False, 'error': f'Unknown block type: {block_type}'}
        
        pattern = patterns[block_type]
        return self.find_multiline_pattern(pattern, text)
    
    def get_line_context(self, text: str, line_number: int, 
                        context_lines: int = 3) -> Dict[str, Any]:
        """Obtener contexto alrededor de una línea específica"""
        if line_number < 1:
            return {'success': False, 'error': 'Line number must be >= 1'}
        
        try:
            lines = text.split('\n')
            if line_number > len(lines):
                return {'success': False, 'error': 'Line number exceeds text length'}
            
            # Calculate context boundaries
            start_line = max(1, line_number - context_lines)
            end_line = min(len(lines), line_number + context_lines)
            
            context_info = {
                'success': True,
                'target_line': line_number,
                'target_content': lines[line_number - 1],
                'context_start': start_line,
                'context_end': end_line,
                'context_lines': [],
                'total_lines': len(lines)
            }
            
            for i in range(start_line - 1, end_line):
                context_info['context_lines'].append({
                    'line_number': i + 1,
                    'content': lines[i],
                    'is_target': (i + 1) == line_number
                })
            
            return context_info
        
        except Exception as e:
            return {'success': False, 'error': f'Context error: {e}'}

    def analyze_indentation_structure(self, text: str) -> Dict[str, Any]:
        """Analizar estructura de indentación del texto"""
        try:
            lines = text.split('\n')
            structure = []
            blocks = []
            
            for i, line in enumerate(lines, 1):
                line_info = {
                    'line_number': i,
                    'content': line,
                    'stripped': line.strip(),
                    'indent_level': len(line) - len(line.lstrip()) if line.strip() else 0,
                    'is_empty': not line.strip()
                }
                structure.append(line_info)
            
            # Agrupar líneas consecutivas por nivel de indentación
            current_block = []
            current_indent = None
            
            for line_info in structure:
                if not line_info['is_empty']:  # Solo procesar líneas no vacías
                    line_indent = line_info['indent_level']
                    
                    # Si es un nuevo nivel de indentación, cerrar bloque anterior
                    if current_indent is not None and line_indent != current_indent:
                        if current_block:
                            blocks.append({
                                'start_line': current_block[0]['line_number'],
                                'end_line': current_block[-1]['line_number'],
                                'indent_level': current_indent,
                                'lines': current_block.copy()
                            })
                        current_block = []
                    
                    current_block.append(line_info)
                    current_indent = line_indent
            
            # Agregar último bloque
            if current_block and current_indent is not None:
                blocks.append({
                    'start_line': current_block[0]['line_number'],
                    'end_line': current_block[-1]['line_number'],
                    'indent_level': current_indent,
                    'lines': current_block
                })
            
            return {
                'success': True,
                'line_structure': structure,
                'blocks': blocks,
                'total_lines': len(lines),
                'total_blocks': len(blocks),
                'max_indent_level': max((line['indent_level'] for line in structure if not line['is_empty']), default=0)
            }
        
        except Exception as e:
            return {'success': False, 'error': f'Indentation analysis error: {e}'}
    def find_code_blocks_by_indent(self, text: str, target_indent: int = 0) -> Dict[str, Any]:
        """Encontrar bloques de código por nivel de indentación"""
        structure = self.analyze_indentation_structure(text)
        if not structure['success']:
            return structure
        
        try:
            matching_blocks = []
            for block in structure['blocks']:
                if block['indent_level'] == target_indent:
                    # Extract actual text content
                    block_lines = [line['content'] for line in block['lines']]
                    block_text = '\n'.join(block_lines)
                    
                    matching_blocks.append({
                        'start_line': block['start_line'],
                        'end_line': block['end_line'],
                        'indent_level': block['indent_level'],
                        'content': block_text,
                        'line_count': len(block['lines'])
                    })
            
            return {
                'success': True,
                'target_indent': target_indent,
                'matching_blocks': matching_blocks,
                'count': len(matching_blocks)
            }
        
        except Exception as e:
            return {'success': False, 'error': f'Indent block search error: {e}'}

    def extract_nested_structures(self, text: str) -> Dict[str, Any]:
        """Extraer estructuras anidadas (funciones dentro de clases, etc.)"""
        try:
            # Find all major structures
            functions = self.find_block_patterns(text, 'function')
            classes = self.find_block_patterns(text, 'class')
            methods = self.find_block_patterns(text, 'method')
            
            nested_info = {
                'success': True,
                'functions': functions.get('matches', []) if functions['success'] else [],
                'classes': classes.get('matches', []) if classes['success'] else [],
                'methods': methods.get('matches', []) if methods['success'] else [],
                'nesting_relationships': []
            }
            
            # Analyze nesting relationships - LÓGICA MEJORADA
            for class_match in nested_info['classes']:
                class_start = class_match['start_line']
                class_end = class_match['end_line']
                
                # Find methods within this class
                nested_methods = []
                for method_match in nested_info['methods']:
                    method_start = method_match['start_line']
                    # Método debe estar después del inicio de la clase y antes del final
                    if class_start < method_start <= (class_start + 20):  # Buscar en rango razonable
                        nested_methods.append(method_match)
                
                # También buscar functions que podrían ser métodos
                for func_match in nested_info['functions']:
                    func_start = func_match['start_line']
                    if class_start < func_start <= (class_start + 20):
                        nested_methods.append(func_match)
                
                # Si encontramos métodos anidados, crear relación
                if nested_methods:
                    nested_info['nesting_relationships'].append({
                        'parent_type': 'class',
                        'parent_match': class_match,
                        'nested_items': nested_methods
                    })
            
            return nested_info
        
        except Exception as e:
            return {'success': False, 'error': f'Nested structure error: {e}'}
    def find_patterns_with_context(self, patterns: List[str], text: str, 
                                  context_lines: int = 2) -> Dict[str, Any]:
        """Encontrar patrones múltiples con contexto preservado"""
        if not patterns:
            return {'success': False, 'error': 'No patterns provided'}
        
        try:
            results = {}
            lines = text.split('\n')
            
            for pattern in patterns:
                pattern_matches = []
                compiled_pattern = re.compile(pattern, re.MULTILINE)
                
                # Find all matches for this pattern
                for match in compiled_pattern.finditer(text):
                    # Calculate line position
                    before_match = text[:match.start()]
                    line_number = before_match.count('\n') + 1
                    
                    # Get context
                    context = self.get_line_context(text, line_number, context_lines)
                    
                    if context['success']:
                        match_with_context = {
                            'match': match.group(),
                            'line_number': line_number,
                            'start_pos': match.start(),
                            'end_pos': match.end(),
                            'context': context['context_lines'],
                            'groups': match.groups(),
                            'groupdict': match.groupdict()
                        }
                        pattern_matches.append(match_with_context)
                
                results[pattern] = {
                    'pattern': pattern,
                    'matches': pattern_matches,
                    'count': len(pattern_matches)
                }
            
            # Combine all matches and sort by line number
            all_matches = []
            for pattern_result in results.values():
                for match in pattern_result['matches']:
                    match['pattern'] = pattern_result['pattern']
                    all_matches.append(match)
            
            all_matches.sort(key=lambda x: x['line_number'])
            
            return {
                'success': True,
                'patterns': patterns,
                'individual_results': results,
                'all_matches_sorted': all_matches,
                'total_matches': len(all_matches)
            }
        
        except Exception as e:
            return {'success': False, 'error': f'Contextual search error: {e}'}

    def find_multiline_between_markers(self, start_marker: str, end_marker: str, 
                                      text: str, include_markers: bool = True) -> Dict[str, Any]:
        """Encontrar contenido entre marcadores multiline"""
        if not start_marker or not end_marker:
            return {'success': False, 'error': 'Empty markers'}
        
        try:
            # Escape markers for regex
            start_escaped = re.escape(start_marker)
            end_escaped = re.escape(end_marker)
            
            if include_markers:
                pattern = f'{start_escaped}(.*?){end_escaped}'
            else:
                pattern = f'{start_escaped}(.*?){end_escaped}'
            
            compiled_pattern = re.compile(pattern, re.MULTILINE | re.DOTALL)
            matches = []
            
            for match in compiled_pattern.finditer(text):
                # Calculate line positions
                before_match = text[:match.start()]
                start_line = before_match.count('\n') + 1
                
                matched_content = match.group(1) if not include_markers else match.group()
                content_lines = matched_content.count('\n') + 1
                
                match_info = {
                    'content': matched_content,
                    'full_match': match.group(),
                    'start_line': start_line,
                    'end_line': start_line + content_lines - 1,
                    'start_pos': match.start(),
                    'end_pos': match.end(),
                    'lines_spanned': content_lines,
                    'start_marker': start_marker,
                    'end_marker': end_marker,
                    'includes_markers': include_markers
                }
                matches.append(match_info)
            
            return {
                'success': True,
                'start_marker': start_marker,
                'end_marker': end_marker,
                'matches': matches,
                'count': len(matches)
            }
        
        except Exception as e:
            return {'success': False, 'error': f'Between markers error: {e}'}

    def replace_multiline_blocks(self, text: str, pattern: str, replacement: str, 
                               preserve_indentation: bool = True) -> Dict[str, Any]:
        """Reemplazar bloques multiline preservando indentación"""
        try:
            compiled_pattern = re.compile(pattern, re.MULTILINE | re.DOTALL)
            matches = list(compiled_pattern.finditer(text))
            
            if not matches:
                return {
                    'success': True,
                    'original_text': text,
                    'new_text': text,
                    'replacements_made': 0,
                    'preserve_indentation': preserve_indentation
                }
            
            new_text = text
            offset = 0
            replacements_made = 0
            
            for match in matches:
                if preserve_indentation:
                    # Detect indentation of first line of match
                    before_match = text[:match.start()]
                    last_newline = before_match.rfind('\n')
                    if last_newline != -1:
                        line_start = last_newline + 1
                        line_content = text[line_start:match.start()]
                        indentation = len(line_content) - len(line_content.lstrip())
                        
                        # Apply indentation to each line of replacement
                        replacement_lines = replacement.split('\n')
                        indented_lines = [' ' * indentation + line if i > 0 and line.strip() else line 
                                        for i, line in enumerate(replacement_lines)]
                        indented_replacement = '\n'.join(indented_lines)
                    else:
                        indented_replacement = replacement
                else:
                    indented_replacement = replacement
                
                # Perform replacement with offset adjustment
                start_pos = match.start() + offset
                end_pos = match.end() + offset
                new_text = new_text[:start_pos] + indented_replacement + new_text[end_pos:]
                
                # Update offset for next replacements
                offset += len(indented_replacement) - (match.end() - match.start())
                replacements_made += 1
            
            return {
                'success': True,
                'original_text': text,
                'new_text': new_text,
                'pattern': pattern,
                'replacement': replacement,
                'replacements_made': replacements_made,
                'preserve_indentation': preserve_indentation
            }
        
        except Exception as e:
            return {'success': False, 'error': f'Multiline replacement error: {e}'}
