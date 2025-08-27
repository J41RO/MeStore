"""
ContentFormatter - Formateador de contenido para inserción de código.
Integra con IndentationDetector y PositionCalculator para formateo consistente.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import textwrap
import re

from .indentation_detector import IndentationDetector, IndentationInfo
from .position_calculator import PositionCalculator, PositionType


class ContentType(Enum):
    """Tipos de contenido que puede formatear ContentFormatter."""
    CLASS = "class"
    METHOD = "method" 
    STATEMENT = "statement"
    BLOCK = "block"


@dataclass
class FormattedContent:
    """Representa contenido formateado listo para inserción."""
    content: str
    content_type: ContentType
    indentation_level: int
    line_count: int
    has_trailing_newline: bool
    
    def __str__(self) -> str:
        return self.content


class ContentFormatter:
    """
    Formateador de contenido para inserción de código.
    
    Integra con IndentationDetector para aplicar indentación apropiada
    y con PositionCalculator para formateo según tipo de posición.
    """
    
    def __init__(self):
        """Inicializa ContentFormatter con componentes de integración."""
        self.indentation_detector = IndentationDetector()
        self.position_calculator = PositionCalculator()
        
    def format_content(self, content: str, context: str, content_type: Optional[ContentType] = None) -> FormattedContent:
        """
        Formatea contenido general para inserción.
        
        Args:
            content: Contenido a formatear
            context: Contexto donde se insertará el contenido
            content_type: Tipo de contenido (se detecta automáticamente si no se especifica)
            
        Returns:
            FormattedContent con contenido formateado
        """
        # Detectar tipo de contenido si no se especifica
        if content_type is None:
            content_type = self._detect_content_type(content)
            
        # Analizar indentación del contexto
        indent_info = self.indentation_detector.analyze_file(context)
        
        # Normalizar contenido
        normalized_content = self.normalize_line_endings(content)
        normalized_content = self.remove_trailing_whitespace(normalized_content)
        
        # Aplicar indentación
        formatted_content = self.apply_indentation(normalized_content, indent_info)
        
        # Crear resultado formateado
        lines = formatted_content.split('\n')
        return FormattedContent(
            content=formatted_content,
            content_type=content_type,
            indentation_level=indent_info.dominant_size,
            line_count=len(lines),
            has_trailing_newline=formatted_content.endswith('\n')
        )
    
    def apply_indentation(self, content: str, indent_info) -> str:
        """
        Aplica indentación usando IndentationDetector.
        
        Args:
            content: Contenido a indentar
            indent_info: FileIndentationStats del contexto
            
        Returns:
            Contenido con indentación aplicada
        """
        lines = content.split('\n')
        indented_lines = []
        
        # Crear cadena de indentación basada en FileIndentationStats
        if indent_info.dominant_type.value == 'spaces':
            base_indent = ' ' * indent_info.dominant_size
        elif indent_info.dominant_type.value == 'tabs':
            base_indent = '\t'
        else:
            base_indent = '    '  # Default: 4 espacios
        
        for line in lines:
            if line.strip():  # Solo aplicar indentación a líneas no vacías
                # Calcular nivel de indentación actual de la línea
                current_indent_level = len(line) - len(line.lstrip())
                
                # Si la línea ya tiene indentación, mantenerla
                if current_indent_level > 0:
                    indented_line = base_indent + line
                else:
                    # Aplicar solo indentación base
                    indented_line = base_indent + line.lstrip()
                indented_lines.append(indented_line)
            else:
                indented_lines.append('')  # Preservar líneas vacías
                
        return '\n'.join(indented_lines)
    
    def normalize_line_endings(self, content: str) -> str:
        """
        Normaliza terminaciones de línea a \n.
        
        Args:
            content: Contenido a normalizar
            
        Returns:
            Contenido con terminaciones normalizadas
        """
        return content.replace('\r\n', '\n').replace('\r', '\n')
    
    def remove_trailing_whitespace(self, content: str) -> str:
        """
        Elimina espacios innecesarios al final de cada línea.
        
        Args:
            content: Contenido a limpiar
            
        Returns:
            Contenido sin espacios trailing
        """
        lines = content.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        return '\n'.join(cleaned_lines)
    
    def _detect_content_type(self, content: str) -> ContentType:
        """
        Detecta automáticamente el tipo de contenido.
        
        Args:
            content: Contenido a analizar
            
        Returns:
            ContentType detectado
        """
        content_stripped = content.strip()
        
        # Detectar definición de clase
        if re.match(r'^\s*class\s+\w+', content_stripped, re.MULTILINE):
            return ContentType.CLASS
            
        # Detectar definición de método/función
        if re.match(r'^\s*def\s+\w+', content_stripped, re.MULTILINE):
            return ContentType.METHOD
            
        # Detectar bloque (múltiples líneas con estructura)
        lines = content_stripped.split('\n')
        if len(lines) > 3 and any(line.strip().endswith(':') for line in lines):
            return ContentType.BLOCK
            
        # Default: statement simple
        return ContentType.STATEMENT
    
    def format_class_definition(self, content: str, context: str) -> FormattedContent:
        """
        Formatea definiciones de clase con estructura apropiada.
        
        Args:
            content: Contenido de clase a formatear
            context: Contexto donde se insertará
            
        Returns:
            FormattedContent con clase formateada
        """
        # Analizar indentación del contexto
        indent_info = self.indentation_detector.analyze_file(context)
        
        # Normalizar contenido
        normalized_content = self.normalize_line_endings(content)
        normalized_content = self.remove_trailing_whitespace(normalized_content)
        
        # Para clases, asegurar línea en blanco antes si no está al inicio
        lines = normalized_content.split('\n')
        if lines and not lines[0].strip().startswith('class'):
            # Si no es una definición directa de clase, formatear como bloque
            return self.format_block(content, context)
        
        # Aplicar indentación específica para clase
        formatted_content = self.apply_indentation(normalized_content, indent_info)
        
        # Asegurar línea en blanco al final para separación
        if not formatted_content.endswith('\n\n'):
            formatted_content = formatted_content.rstrip() + '\n\n'
        
        return FormattedContent(
            content=formatted_content,
            content_type=ContentType.CLASS,
            indentation_level=indent_info.dominant_size,
            line_count=len(formatted_content.split('\n')),
            has_trailing_newline=True
        )
    
    def format_method_definition(self, content: str, context: str) -> FormattedContent:
        """
        Formatea definiciones de método con indentación de clase.
        
        Args:
            content: Contenido de método a formatear
            context: Contexto donde se insertará
            
        Returns:
            FormattedContent con método formateado
        """
        # Analizar indentación del contexto
        indent_info = self.indentation_detector.analyze_file(context)
        
        # Normalizar contenido
        normalized_content = self.normalize_line_endings(content)
        normalized_content = self.remove_trailing_whitespace(normalized_content)
        
        # Aplicar indentación base + un nivel adicional para métodos dentro de clase
        base_indent = ' ' * indent_info.dominant_size if indent_info.dominant_type.value == 'spaces' else '\t'
        
        lines = normalized_content.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip():
                # Para métodos, aplicar indentación base (assumiendo que van dentro de clase)
                formatted_line = base_indent + line.lstrip()
                formatted_lines.append(formatted_line)
            else:
                formatted_lines.append('')
        
        formatted_content = '\n'.join(formatted_lines)
        
        # Agregar línea en blanco al final para separación entre métodos
        if not formatted_content.endswith('\n'):
            formatted_content += '\n'
        
        return FormattedContent(
            content=formatted_content,
            content_type=ContentType.METHOD,
            indentation_level=indent_info.dominant_size,
            line_count=len(formatted_lines),
            has_trailing_newline=True
        )
    
    def format_statement(self, content: str, context: str) -> FormattedContent:
        """
        Formatea declaraciones individuales.
        
        Args:
            content: Declaración a formatear
            context: Contexto donde se insertará
            
        Returns:
            FormattedContent con declaración formateada
        """
        # Para statements simples, usar formateo básico
        return self.format_content(content, context, ContentType.STATEMENT)
    
    def format_block(self, content: str, context: str) -> FormattedContent:
        """
        Formatea bloques de código completos.
        
        Args:
            content: Bloque de código a formatear
            context: Contexto donde se insertará
            
        Returns:
            FormattedContent con bloque formateado
        """
        # Analizar indentación del contexto
        indent_info = self.indentation_detector.analyze_file(context)
        
        # Normalizar contenido
        normalized_content = self.normalize_line_endings(content)
        normalized_content = self.remove_trailing_whitespace(normalized_content)
        
        # Aplicar indentación preservando estructura relativa del bloque
        lines = normalized_content.split('\n')
        formatted_lines = []
        base_indent = ' ' * indent_info.dominant_size if indent_info.dominant_type.value == 'spaces' else '\t'
        
        # Detectar indentación mínima del bloque para preservar estructura
        non_empty_lines = [line for line in lines if line.strip()]
        if non_empty_lines:
            min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
        else:
            min_indent = 0
        
        for line in lines:
            if line.strip():
                # Calcular indentación relativa
                current_indent = len(line) - len(line.lstrip())
                relative_indent = current_indent - min_indent
                
                # Aplicar indentación base + indentación relativa
                total_indent = base_indent + (' ' * relative_indent)
                formatted_line = total_indent + line.lstrip()
                formatted_lines.append(formatted_line)
            else:
                formatted_lines.append('')
        
        formatted_content = '\n'.join(formatted_lines)
        
        # Asegurar línea final para bloques
        if not formatted_content.endswith('\n'):
            formatted_content += '\n'
        
        return FormattedContent(
            content=formatted_content,
            content_type=ContentType.BLOCK,
            indentation_level=indent_info.dominant_size,
            line_count=len(formatted_lines),
            has_trailing_newline=True
        )
    
    def format_for_position(self, content: str, context: str, position_type: PositionType) -> FormattedContent:
        """
        Formatea contenido según tipo de posición específica.
        
        Args:
            content: Contenido a formatear
            context: Contexto donde se insertará
            position_type: Tipo de posición (BEFORE, AFTER, INSIDE)
            
        Returns:
            FormattedContent formateado para la posición específica
        """
        if position_type == PositionType.BEFORE:
            return self.format_before_insertion(content, context)
        elif position_type == PositionType.AFTER:
            return self.format_after_insertion(content, context)
        elif position_type == PositionType.INSIDE:
            return self.format_inside_insertion(content, context)
        else:
            # Fallback a formateo general
            return self.format_content(content, context)
    
    def format_before_insertion(self, content: str, context: str) -> FormattedContent:
        """
        Formatea contenido para inserción BEFORE.
        
        Args:
            content: Contenido a formatear
            context: Contexto donde se insertará
            
        Returns:
            FormattedContent formateado para inserción antes
        """
        # Detectar tipo de contenido
        content_type = self._detect_content_type(content)
        
        # Para BEFORE, usar indentación del nivel del contexto
        formatted = self.format_content(content, context, content_type)
        
        # Asegurar línea en blanco después para separación
        if not formatted.content.endswith('\n\n'):
            formatted.content = formatted.content.rstrip() + '\n\n'
            
        return FormattedContent(
            content=formatted.content,
            content_type=content_type,
            indentation_level=formatted.indentation_level,
            line_count=len(formatted.content.split('\n')),
            has_trailing_newline=True
        )
    
    def format_after_insertion(self, content: str, context: str) -> FormattedContent:
        """
        Formatea contenido para inserción AFTER.
        
        Args:
            content: Contenido a formatear
            context: Contexto donde se insertará
            
        Returns:
            FormattedContent formateado para inserción después
        """
        # Detectar tipo de contenido
        content_type = self._detect_content_type(content)
        
        # Para AFTER, usar indentación del nivel del contexto
        formatted = self.format_content(content, context, content_type)
        
        # Asegurar línea en blanco antes para separación
        if not formatted.content.startswith('\n'):
            formatted.content = '\n' + formatted.content
            
        return FormattedContent(
            content=formatted.content,
            content_type=content_type,
            indentation_level=formatted.indentation_level,
            line_count=len(formatted.content.split('\n')),
            has_trailing_newline=formatted.has_trailing_newline
        )
    
    def format_inside_insertion(self, content: str, context: str) -> FormattedContent:
        """
        Formatea contenido para inserción INSIDE.
        
        Args:
            content: Contenido a formatear
            context: Contexto donde se insertará
            
        Returns:
            FormattedContent formateado para inserción dentro
        """
        # Para INSIDE, necesitamos indentación adicional
        indent_info = self.indentation_detector.analyze_file(context)
        
        # Detectar tipo de contenido
        content_type = self._detect_content_type(content)
        
        # Normalizar contenido
        normalized_content = self.normalize_line_endings(content)
        normalized_content = self.remove_trailing_whitespace(normalized_content)
        
        # Aplicar indentación adicional para INSIDE (un nivel más)
        base_indent = ' ' * indent_info.dominant_size if indent_info.dominant_type.value == 'spaces' else '\t'
        additional_indent = base_indent  # Un nivel adicional para INSIDE
        
        lines = normalized_content.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip():
                # Aplicar indentación base + adicional para INSIDE
                current_indent = len(line) - len(line.lstrip())
                if current_indent > 0:
                    # Si ya tiene indentación, mantenerla + agregar base + adicional
                    formatted_line = base_indent + additional_indent + line
                else:
                    # Aplicar base + adicional
                    formatted_line = base_indent + additional_indent + line.lstrip()
                formatted_lines.append(formatted_line)
            else:
                formatted_lines.append('')
        
        formatted_content = '\n'.join(formatted_lines)
        
        return FormattedContent(
            content=formatted_content,
            content_type=content_type,
            indentation_level=indent_info.dominant_size * 2,  # Doble indentación para INSIDE
            line_count=len(formatted_lines),
            has_trailing_newline=formatted_content.endswith('\n')
        )
    
    def validate_formatted_content(self, content: str, context: str) -> bool:
        """
        Valida que el contenido formateado sea correcto.
        
        Args:
            content: Contenido formateado a validar
            context: Contexto original
            
        Returns:
            True si el contenido es válido, False en caso contrario
        """
        try:
            # Validar que el contenido no esté vacío
            if not content or not content.strip():
                return False
                
            # Validar que mantenga estructura básica de indentación
            lines = content.split('\n')
            for line in lines:
                if line.strip():  # Solo validar líneas no vacías
                    # Verificar que no tenga tabs mezclados con espacios inadecuadamente
                    if '\t' in line and ' ' * 4 in line[:len(line) - len(line.lstrip())]:
                        return False
                        
            # Validar estructura sintáctica básica para Python
            if any(keyword in content for keyword in ['class ', 'def ', 'if ', 'for ', 'while ']):
                # Verificar que las líneas con ':' tengan indentación apropiada después
                content_lines = content.split('\n')
                for i, line in enumerate(content_lines[:-1]):  # Excluir última línea
                    if line.strip().endswith(':'):
                        next_line = content_lines[i + 1] if i + 1 < len(content_lines) else ""
                        if next_line.strip():  # Si hay contenido en línea siguiente
                            current_indent = len(line) - len(line.lstrip())
                            next_indent = len(next_line) - len(next_line.lstrip())
                            if next_indent <= current_indent:  # Debe estar más indentado
                                return False
                                
            return True
            
        except Exception:
            return False
    
    def optimize_whitespace(self, content: str) -> str:
        """
        Optimiza espacios en blanco del contenido.
        
        Args:
            content: Contenido a optimizar
            
        Returns:
            Contenido con espacios optimizados
        """
        # Normalizar líneas en blanco múltiples
        lines = content.split('\n')
        optimized_lines = []
        blank_line_count = 0
        
        for line in lines:
            if line.strip():  # Línea con contenido
                # Agregar máximo 2 líneas en blanco antes de contenido
                if blank_line_count > 0:
                    optimized_lines.extend([''] * min(blank_line_count, 2))
                optimized_lines.append(line.rstrip())  # Remover espacios al final
                blank_line_count = 0
            else:  # Línea vacía
                blank_line_count += 1
                
        # Agregar líneas en blanco finales si las había
        if blank_line_count > 0:
            optimized_lines.extend([''] * min(blank_line_count, 1))
            
        return '\n'.join(optimized_lines)
    
    def preserve_code_structure(self, content: str, original_content: str) -> str:
        """
        Preserva la estructura original del código durante formateo.
        
        Args:
            content: Contenido formateado
            original_content: Contenido original
            
        Returns:
            Contenido con estructura preservada
        """
        # Detectar y preservar comentarios inline
        original_lines = original_content.split('\n')
        formatted_lines = content.split('\n')
        preserved_lines = []
        
        # Mapear líneas formateadas con originales para preservar comentarios
        for i, formatted_line in enumerate(formatted_lines):
            if i < len(original_lines):
                original_line = original_lines[i]
                # Si la línea original tiene comentario inline, preservarlo
                if '#' in original_line and formatted_line.strip():
                    comment_match = re.search(r'#.*$', original_line)
                    if comment_match:
                        comment = comment_match.group(0)
                        if comment not in formatted_line:
                            formatted_line = formatted_line.rstrip() + '  ' + comment
            preserved_lines.append(formatted_line)
            
        return '\n'.join(preserved_lines)
    
    def handle_special_characters(self, content: str) -> str:
        """
        Maneja caracteres especiales en el contenido.
        
        Args:
            content: Contenido con posibles caracteres especiales
            
        Returns:
            Contenido con caracteres especiales manejados apropiadamente
        """
        # Manejar caracteres Unicode comunes en código Python
        replacements = {
            '"': '"',  # Comillas curvas a rectas
            '"': '"',
            ''': "'",  # Apostrofes curvos a rectos
            ''': "'",
            '–': '-',  # Em dash a guión normal
            '—': '--'  # En dash a doble guión
        }
        
        handled_content = content
        for old_char, new_char in replacements.items():
            handled_content = handled_content.replace(old_char, new_char)
            
        # Normalizar espacios no estándar
        handled_content = re.sub(r'[\u00A0\u2007\u202F]', ' ', handled_content)  # Espacios no-break a espacios normales
        
        return handled_content
    