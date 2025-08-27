"""
Position Calculator - Cálculo de posiciones exactas para inserción de código.
Integra con IndentationDetector para posicionamiento preciso.
"""

from typing import Union, List, Tuple, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass
import re
from .indentation_detector import IndentationDetector


class PositionType(Enum):
    """Tipos de posición para inserción."""
    BEFORE = "before"
    AFTER = "after" 
    INSIDE = "inside"


@dataclass
class InsertionPosition:
    """Estructura de datos para representar una posición de inserción."""
    line_number: int
    column: int
    position_type: PositionType
    indentation_level: int
    context_info: Dict[str, Any]
    is_safe: bool = True


class PositionCalculator:
    """
    Calculadora de posiciones exactas para inserción de código.
    Integra con IndentationDetector para manejo preciso de indentación.
    """
    
    def __init__(self):
        """Inicializar calculator con IndentationDetector."""
        self.indentation_detector = IndentationDetector()
        self._cache: Dict[str, Any] = {}
    
    def calculate_line_position(self, content: str, line_index: int) -> InsertionPosition:
        """
        Calcular posición en línea específica.
        
        Args:
            content: Contenido del archivo
            line_index: Índice de línea (0-based)
            
        Returns:
            InsertionPosition con datos de posición
        """
        lines = content.split('\n')
        
        if line_index < 0 or line_index >= len(lines):
            return InsertionPosition(
                line_number=line_index,
                column=0,
                position_type=PositionType.AFTER,
                indentation_level=0,
                context_info={'error': 'Line index out of range'},
                is_safe=False
            )
        
        line = lines[line_index]
        indentation_info = self.indentation_detector.analyze_line(line)
        
        return InsertionPosition(
            line_number=line_index,
            column=len(line.rstrip()),
            position_type=PositionType.AFTER,
            indentation_level=indentation_info.level,
            context_info={
                'line_content': line.strip(),
                'indentation_char': indentation_info.type.value if hasattr(indentation_info.type, 'value') else str(indentation_info.type),
                'is_empty': not line.strip()
            },
            is_safe=True
        )
    
    def find_insertion_point(self, content: str, target_pattern: str) -> Optional[InsertionPosition]:
        """
        Encontrar punto exacto de inserción basado en patrón.
        
        Args:
            content: Contenido del archivo
            target_pattern: Patrón a buscar
            
        Returns:
            InsertionPosition si encuentra el patrón, None si no
        """
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if target_pattern in line:
                indentation_info = self.indentation_detector.analyze_line(line)
                
                return InsertionPosition(
                    line_number=i,
                    column=len(line.rstrip()),
                    position_type=PositionType.AFTER,
                    indentation_level=indentation_info.level,
                    context_info={
                        'matched_line': line.strip(),
                        'pattern': target_pattern,
                        'full_line': line
                    },
                    is_safe=True
                )
        
        return None
    
    def calculate_before_position(self, content: str, target_pattern: str, 
                                new_content: str) -> Optional[InsertionPosition]:
        """
        Calcular posición antes de elemento específico.
        
        Args:
            content: Contenido del archivo
            target_pattern: Patrón objetivo
            new_content: Contenido a insertar
            
        Returns:
            InsertionPosition para inserción antes del patrón
        """
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if target_pattern in line:
                # Calcular indentación apropiada usando context_lines
                context_lines = lines[max(0, i-2):i+3]
                suggested_indent_str = self.indentation_detector.suggest_indentation(
                    context_lines, new_content
                )
                suggested_indent = len(suggested_indent_str)
                
                return InsertionPosition(
                    line_number=i,
                    column=0,
                    position_type=PositionType.BEFORE,
                    indentation_level=suggested_indent,
                    context_info={
                        'target_line': line.strip(),
                        'suggested_indentation': suggested_indent,
                        'indentation_string': suggested_indent_str
                    },
                    is_safe=True
                )
        
        return None
    
    def calculate_after_position(self, content: str, target_pattern: str, 
                            new_content: str) -> Optional[InsertionPosition]:
        """
        Calcular posición después de elemento específico.
        
        Args:
            content: Contenido del archivo
            target_pattern: Patrón objetivo
            new_content: Contenido a insertar
            
        Returns:
            InsertionPosition para inserción después del patrón
        """
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if target_pattern in line:
                # Calcular posición después considerando indentación
                context_lines = lines[max(0, i-1):i+4]
                suggested_indent_str = self.indentation_detector.suggest_indentation(
                    context_lines, new_content
                )
                suggested_indent = len(suggested_indent_str)
                
                return InsertionPosition(
                    line_number=i + 1,
                    column=0,
                    position_type=PositionType.AFTER,
                    indentation_level=suggested_indent,
                    context_info={
                        'target_line': line.strip(),
                        'insertion_line': i + 1,
                        'suggested_indentation': suggested_indent,
                        'indentation_string': suggested_indent_str
                    },
                    is_safe=True
                )
        
        return None
    
    def calculate_inside_block(self, content: str, target_pattern: str, 
                                new_content: str) -> Optional[InsertionPosition]:
        """
        Calcular posición dentro de un bloque (class, def, if, etc.).
        
        Args:
            content: Contenido del archivo
            target_pattern: Patrón que define el bloque
            new_content: Contenido a insertar
            
        Returns:
            InsertionPosition para inserción dentro del bloque
        """
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if target_pattern in line:
                # Encontrar la línea siguiente no vacía para determinar indentación del bloque
                insertion_line = i + 1
                
                # Usar context_lines para calcular indentación apropiada
                context_lines = lines[max(0, i):i+5]
                suggested_indent_str = self.indentation_detector.suggest_indentation(
                    context_lines, new_content
                )
                suggested_indent = len(suggested_indent_str)
                
                return InsertionPosition(
                    line_number=insertion_line,
                    column=0,
                    position_type=PositionType.INSIDE,
                    indentation_level=suggested_indent,
                    context_info={
                        'block_start': line.strip(),
                        'block_type': self._detect_block_type(line),
                        'calculated_indent': suggested_indent,
                        'indentation_string': suggested_indent_str
                    },
                    is_safe=True
                )
        
        return None
    
    def handle_nested_structures(self, content: str, target_pattern: str, 
                            depth: int = 0) -> List[InsertionPosition]:
        """
        Manejar estructuras anidadas y encontrar múltiples posiciones.
        
        Args:
            content: Contenido del archivo
            target_pattern: Patrón a buscar
            depth: Profundidad de anidamiento a considerar
            
        Returns:
            Lista de InsertionPosition encontradas
        """
        positions = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if target_pattern in line:
                indentation_info = self.indentation_detector.analyze_line(line)
                
                # Solo incluir si la profundidad coincide
                if depth == 0 or indentation_info.level == depth:
                    position = InsertionPosition(
                        line_number=i,
                        column=len(line.rstrip()),
                        position_type=PositionType.AFTER,
                        indentation_level=indentation_info.level,
                        context_info={
                            'nesting_depth': indentation_info.level,
                            'matched_content': line.strip(),
                            'position_index': len(positions)
                        },
                        is_safe=True
                    )
                    positions.append(position)
        
        return positions
    
    def detect_block_boundaries(self, content: str, start_line: int) -> Tuple[int, int]:
        """
        Detectar límites de un bloque de código.
        
        Args:
            content: Contenido del archivo
            start_line: Línea donde inicia el bloque
            
        Returns:
            Tupla (línea_inicio, línea_fin) del bloque
        """
        lines = content.split('\n')
        
        if start_line >= len(lines):
            return (start_line, start_line)
        
        start_indent = self.indentation_detector.analyze_line(lines[start_line]).level
        end_line = start_line
        
        # Buscar el final del bloque
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            
            # Línea vacía, continuar
            if not line.strip():
                continue
            
            current_indent = self.indentation_detector.analyze_line(line).level
            
            # Si la indentación es menor o igual, terminó el bloque
            if current_indent <= start_indent:
                break
            
            end_line = i
        
        return (start_line, end_line)
    
    def analyze_context(self, content: str, position: int) -> Dict[str, Any]:
        """
        Analizar contexto alrededor de una posición específica.
        
        Args:
            content: Contenido del archivo
            position: Línea a analizar
            
        Returns:
            Diccionario con información contextual
        """
        lines = content.split('\n')
        
        if position < 0 or position >= len(lines):
            return {'error': 'Position out of range'}
        
        # Analizar líneas circundantes
        context_range = 3
        start_line = max(0, position - context_range)
        end_line = min(len(lines), position + context_range + 1)
        
        context_lines = lines[start_line:end_line]
        current_line = lines[position]
        
        return {
            'current_line': current_line,
            'current_line_number': position,
            'indentation_level': self.indentation_detector.analyze_line(current_line).level,
            'block_type': self._detect_block_type(current_line),
            'context_lines': context_lines,
            'is_inside_function': self._is_inside_function(lines, position),
            'is_inside_class': self._is_inside_class(lines, position)
        }
    
    def _detect_block_type(self, line: str) -> str:
        """Detectar tipo de bloque basado en la línea."""
        line = line.strip()
        
        if line.startswith('class '):
            return 'class'
        elif line.startswith('def '):
            return 'function'
        elif line.startswith('if '):
            return 'if'
        elif line.startswith('for '):
            return 'for'
        elif line.startswith('while '):
            return 'while'
        elif line.startswith('try:'):
            return 'try'
        elif line.startswith('except'):
            return 'except'
        elif line.startswith('with '):
            return 'with'
        else:
            return 'unknown'
    
    def _is_inside_function(self, lines: List[str], position: int) -> bool:
        """Verificar si la posición está dentro de una función."""
        for i in range(position, -1, -1):
            line = lines[i].strip()
            if line.startswith('def '):
                return True
            elif line.startswith('class ') and not line.endswith(':'):
                return False
        return False
    
    def _is_inside_class(self, lines: List[str], position: int) -> bool:
        """Verificar si la posición está dentro de una clase."""
        for i in range(position, -1, -1):
            line = lines[i].strip()
            if line.startswith('class '):
                return True
        return False
    
    def find_pattern_positions(self, content: str, pattern: str) -> List[InsertionPosition]:
        """
        Encontrar posiciones usando patrones regex.
        
        Args:
            content: Contenido del archivo
            pattern: Patrón regex a buscar
            
        Returns:
            Lista de InsertionPosition que coinciden con el patrón
        """
        import re
        positions = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            matches = re.finditer(pattern, line)
            for match in matches:
                indentation_info = self.indentation_detector.analyze_line(line)
                
                position = InsertionPosition(
                    line_number=i,
                    column=match.end(),
                    position_type=PositionType.AFTER,
                    indentation_level=indentation_info.level,
                    context_info={
                        'matched_text': match.group(),
                        'match_start': match.start(),
                        'match_end': match.end(),
                        'full_line': line,
                        'pattern': pattern
                    },
                    is_safe=True
                )
                positions.append(position)
        
        return positions
    
    def calculate_relative_position(self, content: str, anchor_pattern: str, 
                                offset_lines: int = 0, offset_type: str = 'after') -> Optional[InsertionPosition]:
        """
        Calcular posición relativa a un patrón ancla.
        
        Args:
            content: Contenido del archivo
            anchor_pattern: Patrón de referencia
            offset_lines: Número de líneas de desplazamiento
            offset_type: Tipo de desplazamiento ('before', 'after')
            
        Returns:
            InsertionPosition relativa al ancla
        """
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if anchor_pattern in line:
                if offset_type == 'before':
                    target_line = max(0, i - offset_lines)
                else:  # after
                    target_line = min(len(lines), i + offset_lines + 1)
                
                # Calcular indentación apropiada para la línea objetivo
                if target_line < len(lines):
                    context_lines = lines[max(0, target_line-2):target_line+3]
                    suggested_indent_str = self.indentation_detector.suggest_indentation(
                        context_lines, ""
                    )
                    suggested_indent = len(suggested_indent_str)
                else:
                    suggested_indent = 0
                    suggested_indent_str = ""
                
                return InsertionPosition(
                    line_number=target_line,
                    column=0,
                    position_type=PositionType.AFTER if offset_type == 'after' else PositionType.BEFORE,
                    indentation_level=suggested_indent,
                    context_info={
                        'anchor_line': line.strip(),
                        'anchor_line_number': i,
                        'offset_lines': offset_lines,
                        'offset_type': offset_type,
                        'indentation_string': suggested_indent_str
                    },
                    is_safe=True
                )
        
        return None
    
    def handle_multiple_matches(self, content: str, pattern: str, 
                            selection_strategy: str = 'first') -> Optional[InsertionPosition]:
        """
        Manejar múltiples coincidencias de un patrón.
        
        Args:
            content: Contenido del archivo
            pattern: Patrón a buscar
            selection_strategy: Estrategia de selección ('first', 'last', 'all')
            
        Returns:
            InsertionPosition según la estrategia seleccionada
        """
        positions = self.find_pattern_positions(content, pattern)
        
        if not positions:
            return None
        
        if selection_strategy == 'first':
            return positions[0]
        elif selection_strategy == 'last':
            return positions[-1]
        elif selection_strategy == 'all':
            # Para 'all', devolver información agregada
            return InsertionPosition(
                line_number=-1,  # Indicador especial para múltiples
                column=0,
                position_type=PositionType.AFTER,
                indentation_level=0,
                context_info={
                    'strategy': 'all',
                    'total_matches': len(positions),
                    'positions': positions,
                    'pattern': pattern
                },
                is_safe=True
            )
        
        return positions[0]  # Default a first
    
    def validate_insertion_safety(self, content: str, position: InsertionPosition, 
                                new_content: str) -> bool:
        """
        Validar que una inserción es segura y no romperá la sintaxis.
        
        Args:
            content: Contenido original
            position: Posición propuesta para inserción
            new_content: Contenido a insertar
            
        Returns:
            True si la inserción es segura
        """
        lines = content.split('\n')
        
        # Validaciones básicas
        if position.line_number < 0 or position.line_number > len(lines):
            return False
        
        # Validar indentación consistente
        if position.line_number < len(lines):
            current_line = lines[position.line_number]
            if current_line.strip():  # Solo validar si la línea no está vacía
                current_indent = self.indentation_detector.get_indentation_level(current_line)
                if abs(current_indent - position.indentation_level) > 8:  # Diferencia muy grande
                    return False
        
        # Validar que el contenido nuevo tiene indentación apropiada
        new_lines = new_content.split('\n')
        for new_line in new_lines:
            if new_line.strip():  # Solo líneas con contenido
                new_line_indent = self.indentation_detector.get_indentation_level(new_line)
                if new_line_indent == 0 and position.indentation_level > 0:
                    # Contenido sin indentación en posición indentada
                    return False
        
        # Validaciones específicas por tipo de bloque
        if position.line_number < len(lines):
            context = self.analyze_context(content, position.line_number)
            block_type = context.get('block_type', 'unknown')
            
            # Validar coherencia con el tipo de bloque
            if block_type == 'class' and 'def ' not in new_content and 'class ' not in new_content:
                # En clase, probablemente debería ser método o clase anidada
                pass  # Permitir por ahora
            
            if block_type == 'function' and new_content.startswith('def '):
                # Definición de función dentro de función (anidada)
                if position.indentation_level <= context.get('indentation_level', 0):
                    return False  # Debería estar más indentada
        
        return True
    
    def _cache_key(self, content: str, operation: str, *args) -> str:
        """Generar clave de cache para operaciones."""
        import hashlib
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        args_str = "_".join(str(arg) for arg in args)
        return f"{operation}_{content_hash}_{args_str}"
    
    def _get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Obtener resultado desde cache."""
        return self._cache.get(cache_key)
    
    def _cache_result(self, cache_key: str, result: Any) -> None:
        """Guardar resultado en cache."""
        # Limitar cache a 1000 entradas
        if len(self._cache) > 1000:
            # Eliminar las 100 entradas más antiguas
            oldest_keys = list(self._cache.keys())[:100]
            for key in oldest_keys:
                del self._cache[key]
        
        self._cache[cache_key] = result
    
    def calculate_after_position_optimized(self, content: str, target_pattern: str, 
                                        new_content: str) -> Optional[InsertionPosition]:
        """
        Versión optimizada con cache para archivos grandes.
        """
        cache_key = self._cache_key(content, "after_position", target_pattern, new_content)
        cached_result = self._get_cached_result(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        result = self.calculate_after_position(content, target_pattern, new_content)
        self._cache_result(cache_key, result)
        
        return result
    
    def handle_encoding_variants(self, content: Union[str, bytes], 
                                encoding: str = 'utf-8') -> str:
        """
        Manejar archivos con diferentes encodings.
        
        Args:
            content: Contenido como string o bytes
            encoding: Encoding a usar
            
        Returns:
            Contenido como string
        """
        if isinstance(content, bytes):
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                # Intentar con encodings comunes
                encodings_to_try = ['utf-8', 'latin1', 'cp1252', 'ascii']
                for enc in encodings_to_try:
                    try:
                        return content.decode(enc)
                    except UnicodeDecodeError:
                        continue
                # Si nada funciona, usar errors='ignore'
                return content.decode('utf-8', errors='ignore')
        
        return content
    
    def validate_position(self, content: str, position: InsertionPosition) -> bool:
        """
        Validar que una posición calculada es válida.
        
        Args:
            content: Contenido original
            position: Posición a validar
            
        Returns:
            True si la posición es válida
        """
        lines = content.split('\n')
        
        # Validaciones básicas
        if position.line_number < 0 or position.line_number > len(lines):
            return False
        
        if position.column < 0:
            return False
        
        if position.line_number < len(lines):
            line_length = len(lines[position.line_number])
            if position.column > line_length:
                return False
        
        # Validar indentación razonable
        if position.indentation_level < 0 or position.indentation_level > 100:
            return False
        
        return position.is_safe
    
    def handle_empty_file(self, new_content: str) -> InsertionPosition:
        """
        Manejar caso especial de archivo vacío.
        
        Args:
            new_content: Contenido a insertar
            
        Returns:
            InsertionPosition para archivo vacío
        """
        return InsertionPosition(
            line_number=0,
            column=0,
            position_type=PositionType.AFTER,
            indentation_level=0,
            context_info={
                'file_state': 'empty',
                'new_content_lines': len(new_content.split('\n'))
            },
            is_safe=True
        )
    
    def handle_large_files(self, content: str, target_pattern: str, 
                        sample_size: int = 500) -> Optional[InsertionPosition]:
        """
        Manejar archivos grandes con sampling.
        
        Args:
            content: Contenido del archivo
            target_pattern: Patrón a buscar
            sample_size: Número de líneas para sample
            
        Returns:
            InsertionPosition si encuentra el patrón
        """
        lines = content.split('\n')
        
        if len(lines) <= sample_size * 2:
            # Archivo no tan grande, usar método normal
            return self.find_insertion_point(content, target_pattern)
        
        # Sampling: primeras N líneas, últimas N líneas, y muestra del medio
        sample_lines = []
        sample_mapping = {}  # Mapear índices de sample a índices reales
        
        # Primeras líneas
        for i in range(min(sample_size, len(lines))):
            sample_lines.append(lines[i])
            sample_mapping[len(sample_lines) - 1] = i
        
        # Últimas líneas
        start_idx = max(sample_size, len(lines) - sample_size)
        for i in range(start_idx, len(lines)):
            sample_lines.append(lines[i])
            sample_mapping[len(sample_lines) - 1] = i
        
        # Buscar en el sample
        sample_content = '\n'.join(sample_lines)
        sample_position = self.find_insertion_point(sample_content, target_pattern)
        
        if sample_position:
            # Mapear de vuelta al archivo original
            real_line_number = sample_mapping.get(sample_position.line_number)
            if real_line_number is not None:
                return InsertionPosition(
                    line_number=real_line_number,
                    column=sample_position.column,
                    position_type=sample_position.position_type,
                    indentation_level=sample_position.indentation_level,
                    context_info={
                        **sample_position.context_info,
                        'sampled_from_large_file': True,
                        'original_file_lines': len(lines)
                    },
                    is_safe=sample_position.is_safe
                )
        
        return None
    
    def performance_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de performance.
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            'cache_entries': len(self._cache),
            'cache_size_bytes': sum(len(str(v)) for v in self._cache.values()),
            'methods_available': len([m for m in dir(self) if not m.startswith('_')])
        }
    
    