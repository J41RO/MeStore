#!/usr/bin/env python3
"""
Pattern matching functions for indentation detection
Extracted from replace.py for modular architecture
"""

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

def apply_context_indentation(replacement: str, base_indentation: int) -> str:
    """Aplicar indentación del contexto al contenido de reemplazo"""
    if '\n' not in replacement:
        return replacement
    lines = replacement.split('\n')
    indented_lines = []
    for i, line in enumerate(lines):
        if i == 0:
            indented_lines.append(line)
        else:
            if line.strip():
                indented_lines.append(' ' * base_indentation + line.lstrip())
            else:
                indented_lines.append(line)
    return '\n'.join(indented_lines)
