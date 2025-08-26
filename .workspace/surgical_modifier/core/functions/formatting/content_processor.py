# Content Processor - Sistema de procesamiento de indentación
def detect_indentation():
    pass

def preserve_indentation():
    pass

def detect_pattern_indentation(content: str, pattern: str, occurrence_index: int = 0) -> int:
    """Detectar indentación exacta del patrón en su contexto"""
    lines = content.split(chr(10))
    occurrence_count = 0
    for line in lines:
        if pattern in line:
            if occurrence_count == occurrence_index:
                return len(line) - len(line.lstrip())
            occurrence_count += 1
    return 0

def apply_context_indentation(new_content: str, base_indentation: int) -> str:
    """Aplicar indentación del contexto al contenido nuevo"""
    if chr(10) not in new_content:
        return chr(32) * base_indentation + new_content
    lines = new_content.split(chr(10))
    indented_lines = []
    for i, line in enumerate(lines):
        if i == 0:
            indented_lines.append(chr(32) * base_indentation + line)
        else:
            indented_lines.append(line)
    return chr(10).join(indented_lines)