# Pattern Matcher - Sistema de búsqueda de patrones
def find_unique_pattern():
    pass

def find_pattern_with_occurrence(content: str, pattern: str, occurrence: int = 0, use_regex: bool = False) -> tuple:
    """
    Encuentra un patrón específico por número de ocurrencia con información contextual.
    
    Args:
        content: Contenido donde buscar
        pattern: Patrón a buscar
        occurrence: Índice de ocurrencia (0-based)
        use_regex: Si usar expresiones regulares
    
    Returns:
        tuple: (found, line_number, position, context_before, context_after)
    """
    import re
    
    if use_regex:
        matches = list(re.finditer(pattern, content))
        if occurrence >= len(matches):
            return (False, -1, -1, '', '')
        match = matches[occurrence]
        position = match.start()
    else:
        parts = content.split(pattern)
        if occurrence >= len(parts) - 1:
            return (False, -1, -1, '', '')
        position = len(pattern.join(parts[:occurrence+1])) - len(pattern)
    
    lines = content[:position].split(chr(10))
    line_number = len(lines) - 1
    
    context_lines = content.split(chr(10))
    context_before = chr(10).join(context_lines[max(0, line_number-2):line_number])
    context_after = chr(10).join(context_lines[line_number+1:min(len(context_lines), line_number+3)])
    
    return (True, line_number, position, context_before, context_after)

def analyze_pattern_safety(content: str, pattern: str, operation_type: str = 'insert') -> dict:
    """
    Analiza la seguridad de aplicar una operación en un patrón específico.
    
    Args:
        content: Contenido donde se aplicará la operación
        pattern: Patrón objetivo
        operation_type: Tipo de operación ('insert', 'replace', 'delete')
    
    Returns:
        dict: {'safe': bool, 'warnings': list, 'occurrences': int, 'recommendations': list}
    """
    warnings = []
    recommendations = []
    
    # Contar ocurrencias del patrón
    occurrences = content.count(pattern)
    
    # Verificar unicidad
    if occurrences == 0:
        warnings.append('Pattern not found in content')
        return {'safe': False, 'warnings': warnings, 'occurrences': 0, 'recommendations': ['Verify pattern exists']}
    
    if occurrences > 1:
        warnings.append(f'Pattern appears {occurrences} times - may affect multiple locations')
        recommendations.append('Consider using occurrence-specific search or more unique pattern')
    
    # Análisis contextual
    lines = content.split(chr(10))
    pattern_lines = [i for i, line in enumerate(lines) if pattern in line]
    
    # Verificar si está en strings o comentarios (análisis básico)
    for line_num in pattern_lines:
        line = lines[line_num]
        if line.strip().startswith('#') or line.strip().startswith('//'):
            warnings.append(f'Pattern found in comment at line {line_num + 1}')
        if pattern in line and (chr(34) in line or chr(39) in line):
            warnings.append(f'Pattern may be inside string literal at line {line_num + 1}')
    
    # Determinar seguridad general
    is_safe = len(warnings) == 0 or (occurrences == 1 and len([w for w in warnings if 'comment' not in w and 'string' not in w]) == 0)
    
    if is_safe:
        recommendations.append('Pattern appears safe for operation')
    else:
        recommendations.append('Review warnings before proceeding')
    
    return {
        'safe': is_safe,
        'warnings': warnings,
        'occurrences': occurrences,
        'recommendations': recommendations
    }
