"""
IndentationDetector - Detector y analizador de patrones de indentación.

Detecta y analiza patrones de indentación en código para inserción inteligente,
manteniendo consistencia con el archivo existente.
"""

from typing import Dict, List, Optional, Tuple, Union
import re
from enum import Enum
from dataclasses import dataclass


class IndentationType(Enum):
    """Tipos de indentación soportados."""
    SPACES = "spaces"
    TABS = "tabs"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass
class IndentationInfo:
    """Información de indentación de una línea."""
    type: IndentationType
    size: int
    level: int
    raw_indent: str


@dataclass
class FileIndentationStats:
    """Estadísticas de indentación de un archivo completo."""
    dominant_type: IndentationType
    dominant_size: int
    lines_analyzed: int
    spaces_count: int
    tabs_count: int
    mixed_lines: int
    consistency_score: float


class IndentationDetector:
    """
    Detector de patrones de indentación para inserción inteligente de código.
    
    Esta clase analiza patrones de indentación en código fuente para:
    - Detectar tipo de indentación (espacios vs tabs)
    - Determinar tamaño de indentación (2, 4, 8 espacios)
    - Analizar consistencia en archivos
    - Sugerir indentación apropiada para nuevas líneas
    """
    
    def __init__(self):
        """Inicializa el detector con configuración por defecto."""
        self._common_sizes = [2, 4, 8]
        self._cache = {}
        self._logging_enabled = False
        self._log_entries = []
        
    def analyze_line(self, line: str) -> IndentationInfo:
        """
        Analiza la indentación de una línea individual.
        
        Args:
            line: Línea de código a analizar
            
        Returns:
            IndentationInfo con información detallada de la indentación
        """
        if not line.strip():  # Línea vacía
            return IndentationInfo(
                type=IndentationType.UNKNOWN,
                size=0,
                level=0,
                raw_indent=""
            )
        
        # Extraer indentación inicial
        indent_match = re.match(r'^(\s*)', line)
        raw_indent = indent_match.group(1) if indent_match else ""
        
        if not raw_indent:  # Sin indentación
            return IndentationInfo(
                type=IndentationType.SPACES,
                size=0,
                level=0,
                raw_indent=""
            )
        
        # Detectar tipo
        has_spaces = ' ' in raw_indent
        has_tabs = '\t' in raw_indent
        
        if has_spaces and has_tabs:
            indent_type = IndentationType.MIXED
            size = len(raw_indent)  # Tamaño bruto para mixto
            level = 1  # Nivel aproximado
        elif has_tabs:
            indent_type = IndentationType.TABS
            size = 1  # Un tab = una unidad
            level = len(raw_indent)
        else:  # Solo espacios
            indent_type = IndentationType.SPACES
            size = self._detect_space_size(raw_indent)
            level = len(raw_indent) // size if size > 0 else 0
        
        return IndentationInfo(
            type=indent_type,
            size=size,
            level=level,
            raw_indent=raw_indent
        )
    
    def _detect_space_size(self, indent_str: str) -> int:
        """
        Detecta el tamaño de indentación basado en espacios.
        
        Args:
            indent_str: String de indentación con solo espacios
            
        Returns:
            Tamaño estimado de indentación (2, 4, 8)
        """
        space_count = len(indent_str)
        
        if space_count == 0:
            return 4  # Default
        
        # Probar tamaños estándar en orden de preferencia
        for size in [4, 2, 8]:  # Preferir 4 espacios primero
            if space_count % size == 0:
                return size
        
        # Si no es divisible por ningún tamaño estándar, usar el total como tamaño
        return space_count
    
    def detect_indentation_type(self, lines: List[str]) -> IndentationType:
        """
        Detecta el tipo dominante de indentación en múltiples líneas.
        
        Args:
            lines: Lista de líneas a analizar
            
        Returns:
            Tipo de indentación dominante
        """
        spaces_count = 0
        tabs_count = 0
        mixed_count = 0
        
        for line in lines:
            if not line.strip():  # Ignorar líneas vacías
                continue
                
            info = self.analyze_line(line)
            if info.type == IndentationType.SPACES:
                spaces_count += 1
            elif info.type == IndentationType.TABS:
                tabs_count += 1
            elif info.type == IndentationType.MIXED:
                mixed_count += 1
        
        total = spaces_count + tabs_count + mixed_count
        if total == 0:
            return IndentationType.UNKNOWN
        
        if mixed_count > 0:
            return IndentationType.MIXED
        elif spaces_count >= tabs_count:
            return IndentationType.SPACES
        else:
            return IndentationType.TABS
    
    def detect_indentation_size(self, lines: List[str]) -> int:
        """
        Detecta el tamaño dominante de indentación.
        
        Args:
            lines: Lista de líneas a analizar
            
        Returns:
            Tamaño de indentación más común
        """
        size_counts = {}
        
        for line in lines:
            if not line.strip():
                continue
                
            info = self.analyze_line(line)
            if info.type == IndentationType.SPACES and info.size > 0:
                size_counts[info.size] = size_counts.get(info.size, 0) + 1
        
        if not size_counts:
            return 4  # Default
            
        # Retornar el tamaño más común
        return max(size_counts.items(), key=lambda x: x[1])[0]
    
    def get_indentation_level(self, line: str) -> int:
        """
        Obtiene el nivel de indentación de una línea.
        
        Args:
            line: Línea a analizar
            
        Returns:
            Nivel de indentación (0, 1, 2, etc.)
        """
        return self.analyze_line(line).level
    
    def analyze_file(self, content: str) -> FileIndentationStats:
        """
        Analiza las estadísticas de indentación de un archivo completo.
        
        Args:
            content: Contenido completo del archivo
            
        Returns:
            FileIndentationStats con estadísticas detalladas
        """
        lines = content.split('\n')
        spaces_count = 0
        tabs_count = 0
        mixed_lines = 0
        total_analyzed = 0
        
        # Contador de tamaños de indentación
        size_counts = {}
        
        for line in lines:
            if not line.strip():  # Ignorar líneas vacías
                continue
                
            total_analyzed += 1
            info = self.analyze_line(line)
            
            if info.type == IndentationType.SPACES:
                spaces_count += 1
                if info.size > 0:
                    size_counts[info.size] = size_counts.get(info.size, 0) + 1
            elif info.type == IndentationType.TABS:
                tabs_count += 1
            elif info.type == IndentationType.MIXED:
                mixed_lines += 1
        
        # Determinar tipo dominante
        if mixed_lines > 0:
            dominant_type = IndentationType.MIXED
        elif spaces_count >= tabs_count:
            dominant_type = IndentationType.SPACES
        elif tabs_count > 0:
            dominant_type = IndentationType.TABS
        else:
            dominant_type = IndentationType.UNKNOWN
        
        # Determinar tamaño dominante
        dominant_size = 4  # Default
        if size_counts:
            dominant_size = max(size_counts.items(), key=lambda x: x[1])[0]
        
        # Calcular score de consistencia
        if total_analyzed == 0:
            consistency_score = 1.0
        else:
            consistent_lines = max(spaces_count, tabs_count)
            consistency_score = consistent_lines / total_analyzed
        
        return FileIndentationStats(
            dominant_type=dominant_type,
            dominant_size=dominant_size,
            lines_analyzed=total_analyzed,
            spaces_count=spaces_count,
            tabs_count=tabs_count,
            mixed_lines=mixed_lines,
            consistency_score=consistency_score
        )
    
    def detect_dominant_pattern(self, content: str) -> Tuple[IndentationType, int]:
        """
        Detecta el patrón dominante de indentación en un archivo.
        
        Args:
            content: Contenido del archivo
            
        Returns:
            Tupla con (tipo_dominante, tamaño_dominante)
        """
        stats = self.analyze_file(content)
        return stats.dominant_type, stats.dominant_size
    
    def get_statistics(self, content: str) -> Dict[str, Union[str, int, float]]:
        """
        Obtiene estadísticas detalladas de indentación.
        
        Args:
            content: Contenido del archivo
            
        Returns:
            Diccionario con estadísticas completas
        """
        stats = self.analyze_file(content)
        
        return {
            'type': stats.dominant_type.value,
            'size': stats.dominant_size,
            'lines_analyzed': stats.lines_analyzed,
            'spaces_lines': stats.spaces_count,
            'tabs_lines': stats.tabs_count,
            'mixed_lines': stats.mixed_lines,
            'consistency': round(stats.consistency_score * 100, 2)
        }
    
    def validate_consistency(self, content: str, threshold: float = 0.8) -> bool:
        """
        Valida si el archivo tiene consistencia en la indentación.
        
        Args:
            content: Contenido del archivo
            threshold: Umbral mínimo de consistencia (0.0-1.0)
            
        Returns:
            True si la consistencia supera el umbral
        """
        stats = self.analyze_file(content)
        return stats.consistency_score >= threshold
    
    def suggest_indentation(self, context_lines: List[str], new_line_content: str = "") -> str:
        """
        Sugiere la indentación apropiada para una nueva línea basada en el contexto.
        
        Args:
            context_lines: Líneas de contexto previas
            new_line_content: Contenido de la nueva línea (opcional)
            
        Returns:
            String con la indentación sugerida
        """
        if not context_lines:
            return ""
        
        # Analizar cada línea para detectar el patrón real de indentación
        indent_sizes = []
        line_levels = []
        
        for line in context_lines:
            if line.strip():  # Solo líneas con contenido
                info = self.analyze_line(line)
                if info.level > 0:  # Solo líneas con indentación
                    actual_spaces = len(info.raw_indent)
                    calculated_size = actual_spaces // info.level if info.level > 0 else 4
                    indent_sizes.append(calculated_size)
                    line_levels.append((info.level, actual_spaces))
        
        # Determinar el tamaño de indentación más común en el contexto
        if indent_sizes:
            # Usar el tamaño más común
            size_counts = {}
            for size in indent_sizes:
                size_counts[size] = size_counts.get(size, 0) + 1
            detected_size = max(size_counts.items(), key=lambda x: x[1])[0]
        else:
            detected_size = 4  # Default
        
        # Obtener la última línea con contenido
        last_meaningful_line = None
        for line in reversed(context_lines):
            if line.strip():
                last_meaningful_line = line
                break
        
        if not last_meaningful_line:
            return ""
        
        last_info = self.analyze_line(last_meaningful_line)
        suggested_level = last_info.level
        
        # Determinar si necesita incrementar nivel
        if self._should_increase_indentation(last_meaningful_line):
            suggested_level += 1
        elif self._should_decrease_indentation(new_line_content):
            suggested_level = max(0, suggested_level - 1)
        
        # Generar indentación usando el tamaño detectado
        return ' ' * (suggested_level * detected_size)
    
    def _should_increase_indentation(self, line: str) -> bool:
        """
        Determina si una línea indica que la siguiente debe tener más indentación.
        
        Args:
            line: Línea a analizar
            
        Returns:
            True si la siguiente línea debe tener más indentación
        """
        stripped_line = line.strip()
        
        # Patrones que típicamente requieren más indentación
        increase_patterns = [
            r':\s*$',  # Líneas que terminan con ':'
            r'{\s*$',  # Líneas que terminan con '{'
            r'\(\s*$',  # Líneas que terminan con '('
            r'\[\s*$',  # Líneas que terminan con '['
        ]
        
        for pattern in increase_patterns:
            if re.search(pattern, stripped_line):
                return True
        
        # Palabras clave que requieren más indentación
        keywords = ['if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 
                   'with', 'def', 'class', 'async def']
        
        for keyword in keywords:
            if re.match(rf'\s*{keyword}\b', line):
                return True
        
        return False
    
    def _should_decrease_indentation(self, line_content: str) -> bool:
        """
        Determina si el contenido de la línea indica que debe tener menos indentación.
        
        Args:
            line_content: Contenido de la línea nueva
            
        Returns:
            True si debe tener menos indentación
        """
        stripped_content = line_content.strip()
        
        # Palabras clave que reducen indentación
        decrease_keywords = ['else', 'elif', 'except', 'finally', 'case', 'default']
        
        for keyword in decrease_keywords:
            if stripped_content.startswith(keyword):
                return True
        
        # Caracteres de cierre
        if stripped_content.startswith(('}', ')', ']')):
            return True
        
        return False
    
    def calculate_insert_position(self, lines: List[str], target_line: int) -> Tuple[int, str]:
        """
        Calcula la posición correcta y la indentación para insertar una nueva línea.
        
        Args:
            lines: Lista de líneas del archivo
            target_line: Línea objetivo donde insertar
            
        Returns:
            Tupla con (posición_ajustada, indentación_sugerida)
        """
        if target_line < 0 or target_line >= len(lines):
            target_line = len(lines)
        
        # Obtener contexto alrededor de la línea objetivo
        context_start = max(0, target_line - 5)
        context_end = min(len(lines), target_line + 1)
        context_lines = lines[context_start:context_end]
        
        # Sugerir indentación basada en contexto
        suggested_indent = self.suggest_indentation(context_lines)
        
        return target_line, suggested_indent
    
    def match_context_indentation(self, context_lines: List[str], block_type: str = "general") -> str:
        """
        Coincide la indentación con el contexto específico.
        
        Args:
            context_lines: Líneas de contexto
            block_type: Tipo de bloque (function, class, if, etc.)
            
        Returns:
            Indentación que coincide con el contexto
        """
        if not context_lines:
            return ""
        
        # Buscar patrones específicos según el tipo de bloque
        if block_type == "function":
            return self._match_function_context(context_lines)
        elif block_type == "class":
            return self._match_class_context(context_lines)
        else:
            return self.suggest_indentation(context_lines)
    
    def _match_function_context(self, context_lines: List[str]) -> str:
        """Coincide indentación para contexto de función."""
        # Buscar definición de función más cercana
        for line in reversed(context_lines):
            if re.match(r'\s*def\s+', line):
                func_info = self.analyze_line(line)
                # El cuerpo de la función tiene un nivel más
                stats = self.analyze_file('\n'.join(context_lines))
                if stats.dominant_type == IndentationType.TABS:
                    return '\t' * (func_info.level + 1)
                else:
                    return ' ' * ((func_info.level + 1) * stats.dominant_size)
        
        return self.suggest_indentation(context_lines)
    
    def _match_class_context(self, context_lines: List[str]) -> str:
        """Coincide indentación para contexto de clase."""
        # Buscar definición de clase más cercana
        for line in reversed(context_lines):
            if re.match(r'\s*class\s+', line):
                class_info = self.analyze_line(line)
                stats = self.analyze_file('\n'.join(context_lines))
                if stats.dominant_type == IndentationType.TABS:
                    return '\t' * (class_info.level + 1)
                else:
                    return ' ' * ((class_info.level + 1) * stats.dominant_size)
        
        return self.suggest_indentation(context_lines)
    
    def handle_special_cases(self, context_lines: List[str], new_content: str) -> str:
        """
        Maneja casos especiales de indentación (decoradores, docstrings, etc.).
        
        Args:
            context_lines: Líneas de contexto
            new_content: Contenido de la nueva línea
            
        Returns:
            Indentación ajustada para casos especiales
        """
        stripped_content = new_content.strip()
        
        # Decoradores
        if stripped_content.startswith('@'):
            return self._handle_decorator(context_lines)
        
        # Docstrings
        if stripped_content.startswith(('"""', "'''")):
            return self._handle_docstring(context_lines)
        
        # Comentarios
        if stripped_content.startswith('#'):
            return self._handle_comment(context_lines)
        
        return self.suggest_indentation(context_lines, new_content)
    
    def _handle_decorator(self, context_lines: List[str]) -> str:
        """Maneja indentación para decoradores."""
        # Los decoradores van al mismo nivel que la función/clase que decoran
        # Buscar la función/clase más cercana con indentación
        for line in reversed(context_lines):  # Buscar desde atrás
            if re.match(r'\s*def\s+', line):  # Solo funciones
                return self.analyze_line(line).raw_indent
        
        # Si no encuentra función, buscar clase
        for line in reversed(context_lines):
            if re.match(r'\s*class\s+', line):
                return self.analyze_line(line).raw_indent
        
        # Si no encuentra nada, usar sugerencia normal
        return self.suggest_indentation(context_lines)
    
    def _handle_docstring(self, context_lines: List[str]) -> str:
        """Maneja indentación para docstrings."""
        # Los docstrings van un nivel más adentro que la función/clase
        for line in reversed(context_lines):
            if re.match(r'\s*(def|class)\s+', line):
                info = self.analyze_line(line)
                stats = self.analyze_file('\n'.join(context_lines))
                if stats.dominant_type == IndentationType.TABS:
                    return '\t' * (info.level + 1)
                else:
                    return ' ' * ((info.level + 1) * stats.dominant_size)
        
        return self.suggest_indentation(context_lines)
    
    def _handle_comment(self, context_lines: List[str]) -> str:
        """Maneja indentación para comentarios."""
        # Los comentarios siguen la indentación del contexto actual
        return self.suggest_indentation(context_lines)
    
    def analyze_mixed_indentation(self, content: str) -> Dict[str, any]:
        """
        Analiza archivos con indentación mixta y propone solución.
        
        Args:
            content: Contenido del archivo con indentación mixta
            
        Returns:
            Diccionario con análisis detallado y recomendación
        """
        lines = content.split('\n')
        mixed_lines = []
        spaces_lines = []
        tabs_lines = []
        
        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue
                
            info = self.analyze_line(line)
            if info.type == IndentationType.MIXED:
                mixed_lines.append({
                    'line_number': line_num,
                    'content': line,
                    'raw_indent': info.raw_indent
                })
            elif info.type == IndentationType.SPACES:
                spaces_lines.append(line_num)
            elif info.type == IndentationType.TABS:
                tabs_lines.append(line_num)
        
        # Determinar recomendación basada en mayoría
        recommendation = "spaces" if len(spaces_lines) >= len(tabs_lines) else "tabs"
        
        return {
            'has_mixed': len(mixed_lines) > 0,
            'mixed_lines': mixed_lines,
            'spaces_lines_count': len(spaces_lines),
            'tabs_lines_count': len(tabs_lines),
            'recommendation': recommendation,
            'total_problematic': len(mixed_lines)
        }
    
    def optimize_for_large_files(self, content: str, sample_size: int = 100) -> FileIndentationStats:
        """
        Optimiza el análisis para archivos grandes usando muestreo.
        
        Args:
            content: Contenido del archivo
            sample_size: Número de líneas a muestrar
            
        Returns:
            FileIndentationStats estimadas basadas en muestra
        """
        lines = content.split('\n')
        meaningful_lines = [line for line in lines if line.strip()]
        
        if len(meaningful_lines) <= sample_size:
            return self.analyze_file(content)
        
        # Muestreo estratificado: inicio, medio, fin
        third = len(meaningful_lines) // 3
        sample_lines = []
        
        # Muestra del inicio
        sample_lines.extend(meaningful_lines[:sample_size//3])
        # Muestra del medio
        mid_start = third
        sample_lines.extend(meaningful_lines[mid_start:mid_start + sample_size//3])
        # Muestra del fin
        sample_lines.extend(meaningful_lines[-sample_size//3:])
        
        # Analizar muestra
        sample_content = '\n'.join(sample_lines)
        stats = self.analyze_file(sample_content)
        
        # Ajustar estadísticas para archivo completo
        stats.lines_analyzed = len(meaningful_lines)
        
        return stats
    
    def detect_language_specific_patterns(self, content: str, file_extension: str = ".py") -> Dict[str, any]:
        """
        Detecta patrones específicos del lenguaje de programación.
        
        Args:
            content: Contenido del archivo
            file_extension: Extensión del archivo
            
        Returns:
            Diccionario con patrones específicos del lenguaje
        """
        patterns = {}
        
        if file_extension.lower() == ".py":
            patterns = self._analyze_python_patterns(content)
        elif file_extension.lower() in [".js", ".jsx", ".ts", ".tsx"]:
            patterns = self._analyze_javascript_patterns(content)
        elif file_extension.lower() in [".java", ".c", ".cpp", ".cs"]:
            patterns = self._analyze_brace_language_patterns(content)
        
        return patterns
    
    def _analyze_python_patterns(self, content: str) -> Dict[str, any]:
        """Analiza patrones específicos de Python."""
        lines = content.split('\n')
        
        decorators = []
        docstrings = []
        comprehensions = []
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if stripped.startswith('@'):
                decorators.append(line_num)
            elif stripped.startswith(('"""', "'''")):
                docstrings.append(line_num)
            elif '[' in stripped and 'for' in stripped and 'in' in stripped:
                comprehensions.append(line_num)
        
        return {
            'decorators': decorators,
            'docstrings': docstrings,
            'comprehensions': comprehensions,
            'language': 'python'
        }
    
    def _analyze_javascript_patterns(self, content: str) -> Dict[str, any]:
        """Analiza patrones específicos de JavaScript/TypeScript."""
        lines = content.split('\n')
        
        arrow_functions = []
        jsx_elements = []
        ternary_operators = []
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if '=>' in stripped:
                arrow_functions.append(line_num)
            elif '<' in stripped and '>' in stripped and not stripped.startswith('//'):
                jsx_elements.append(line_num)
            elif '?' in stripped and ':' in stripped:
                ternary_operators.append(line_num)
        
        return {
            'arrow_functions': arrow_functions,
            'jsx_elements': jsx_elements,
            'ternary_operators': ternary_operators,
            'language': 'javascript'
        }
    
    def _analyze_brace_language_patterns(self, content: str) -> Dict[str, any]:
        """Analiza patrones de lenguajes con llaves."""
        lines = content.split('\n')
        
        opening_braces = []
        closing_braces = []
        switch_statements = []
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if stripped.endswith('{'):
                opening_braces.append(line_num)
            elif stripped.startswith('}'):
                closing_braces.append(line_num)
            elif stripped.startswith('switch') or stripped.startswith('case'):
                switch_statements.append(line_num)
        
        return {
            'opening_braces': opening_braces,
            'closing_braces': closing_braces,
            'switch_statements': switch_statements,
            'language': 'brace_based'
        }
    
    def cache_results(self, cache_key: str, result: any) -> None:
        """
        Almacena resultados en cache para optimización.
        
        Args:
            cache_key: Clave única para el cache
            result: Resultado a almacenar
        """
        if len(self._cache) > 100:  # Limpiar cache si crece mucho
            self._cache.clear()
        
        self._cache[cache_key] = result
    
    def get_cached_result(self, cache_key: str) -> any:
        """
        Recupera resultado del cache.
        
        Args:
            cache_key: Clave del cache
            
        Returns:
            Resultado almacenado o None si no existe
        """
        return self._cache.get(cache_key)
    
    def enable_logging(self, enable: bool = True) -> None:
        """
        Habilita o deshabilita logging de análisis.
        
        Args:
            enable: True para habilitar logging
        """
        self._logging_enabled = enable
        if not hasattr(self, '_log_entries'):
            self._log_entries = []
    
    def log_analysis(self, operation: str, details: str) -> None:
        """
        Registra operación de análisis en log.
        
        Args:
            operation: Tipo de operación
            details: Detalles de la operación
        """
        if hasattr(self, '_logging_enabled') and self._logging_enabled:
            import datetime
            self._log_entries.append({
                'timestamp': datetime.datetime.now().isoformat(),
                'operation': operation,
                'details': details
            })
    
    def get_analysis_log(self) -> List[Dict]:
        """
        Obtiene el log de análisis.
        
        Returns:
            Lista con entradas del log
        """
        return getattr(self, '_log_entries', [])
    