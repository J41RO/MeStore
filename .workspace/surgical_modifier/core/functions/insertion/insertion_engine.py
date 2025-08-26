# Insertion Engine - Lógica consolidada de inserción
"""
Módulo consolidado para manejo de inserción de contenido.
Extrae lógica común de operadores before.py y after.py.
"""

import re
from typing import Dict, List, Tuple, Optional


def detect_pattern_indentation(content: str, pattern: str, occurrence_index: int = 0) -> int:
    """Detectar indentación exacta del patrón en su contexto"""
    lines = content.split('\n')
    occurrence_count = 0
    for line in lines:
        if pattern in line:
            if occurrence_count == occurrence_index:
                return len(line) - len(line.lstrip())
            occurrence_count += 1
    return 0


def apply_context_indentation(new_content: str, base_indentation: int) -> str:
    """Aplicar indentación del contexto al contenido nuevo"""
    if '\n' not in new_content:
        return ' ' * base_indentation + new_content

    lines = new_content.split('\n')
    indented_lines = []
    for i, line in enumerate(lines):
        if i == 0:
            indented_lines.append(' ' * base_indentation + line)
        else:
            indented_lines.append(line)
    return '\n'.join(indented_lines)


def line_matches_pattern(line: str, pattern: str, regex_mode: bool, case_sensitive: bool) -> bool:
    """Verificar si una línea coincide con el patrón"""
    if regex_mode:
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            return bool(re.search(pattern, line, flags))
        except re.error:
            return False
    else:
        if case_sensitive:
            return pattern in line
        else:
            return pattern.lower() in line.lower()


def handle_insertion(
    content: str,
    pattern: str,
    insertion: str,
    position: str,  # 'before' or 'after'
    regex_mode: bool = False,
    case_sensitive: bool = True,
    first_match_only: bool = False,
    preserve_indentation: bool = True
) -> Dict:
    """
    Función consolidada para manejar inserción antes o después de patrones.

    Args:
        content: Contenido original del archivo
        pattern: Patrón a buscar
        insertion: Contenido a insertar
        position: 'before' o 'after'
        regex_mode: Usar matching con regex
        case_sensitive: Matching sensible a mayúsculas
        first_match_only: Solo primera coincidencia
        preserve_indentation: Preservar indentación

    Returns:
        Dict con resultado de la operación
    """
    try:
        lines = content.splitlines(keepends=True)
        new_lines = []
        insertions_made = 0
        insertion_positions = []

        for i, line in enumerate(lines):
            if line_matches_pattern(line, pattern, regex_mode, case_sensitive):
                # Detectar indentación si está habilitado
                indentation = 0
                if preserve_indentation:
                    indentation = len(line) - len(line.lstrip())

                # Aplicar indentación al contenido a insertar
                indented_insertion = insertion
                if preserve_indentation and indentation > 0:
                    indented_insertion = apply_context_indentation(insertion, indentation)

                # Insertar antes o después según posición
                if position == 'before':
                    new_lines.append(indented_insertion + '\n')
                    new_lines.append(line)
                else:  # after
                    new_lines.append(line)
                    new_lines.append(indented_insertion + '\n')

                insertions_made += 1
                insertion_positions.append(i + 1)  # línea basada en 1

                # Si solo primera coincidencia, parar
                if first_match_only:
                    new_lines.extend(lines[i+1:])
                    break
            else:
                new_lines.append(line)

        if insertions_made == 0:
            return {
                'success': False,
                'message': f'Pattern "{pattern}" not found in content',
                'details': {
                    'insertions_made': 0,
                    'positions': []
                }
            }

        return {
            'success': True,
            'content': ''.join(new_lines),
            'message': f'Successfully inserted content {position} {insertions_made} occurrence(s)',
            'details': {
                'insertions_made': insertions_made,
                'positions': insertion_positions,
                'preserve_indentation': preserve_indentation
            }
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'Error during insertion: {str(e)}',
            'details': {'error': str(e)}
        }
