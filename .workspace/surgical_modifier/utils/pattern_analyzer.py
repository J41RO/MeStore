#!/usr/bin/env python3
"""
Pattern Analyzer - Herramienta para encontrar patrones únicos
"""
from typing import Dict, Any, List

def analyze_pattern_safety(file_path: str, pattern: str) -> Dict[str, Any]:
    """Analizar qué tan seguro es usar un patrón"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        occurrences = []
        
        for i, line in enumerate(lines, 1):
            if pattern in line:
                occurrences.append({
                    'line_number': i,
                    'content': line.strip(),
                    'context_before': lines[i-2].strip() if i >= 2 else "",
                    'context_after': lines[i].strip() if i < len(lines) else ""
                })
        
        # Determinar nivel de riesgo
        risk_level = 'SAFE' if len(occurrences) == 1 else 'HIGH_RISK'
        if len(occurrences) > 5:
            risk_level = 'EXTREMELY_DANGEROUS'
        
        return {
            'pattern': pattern,
            'total_occurrences': len(occurrences),
            'risk_level': risk_level,
            'occurrences': occurrences,
            'recommendation': get_pattern_recommendation(len(occurrences))
        }
        
    except Exception as e:
        return {'error': str(e)}

def get_pattern_recommendation(occurrence_count: int) -> str:
    """Obtener recomendación basada en número de ocurrencias"""
    if occurrence_count == 1:
        return "SAFE: Pattern is unique, proceed with confidence"
    elif occurrence_count <= 3:
        return "CAUTION: Use --occurrence flag to specify which one"
    elif occurrence_count <= 10:
        return "HIGH RISK: Use specific context or find unique pattern"
    else:
        return "EXTREMELY DANGEROUS: Find a unique pattern instead"

def suggest_unique_alternatives(file_path: str, target_line_number: int) -> List[str]:
    """Sugerir patrones únicos para línea específica"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if target_line_number > len(lines):
            return []
        
        target_line = lines[target_line_number - 1].strip()
        suggestions = []
        
        # Buscar elementos únicos en la línea
        import re
        
        # Clases CSS específicas
        css_classes = re.findall(r'className=["\']([^"\']*)["\']', target_line)
        for cls in css_classes:
            if len(cls) > 8:  # Solo clases suficientemente específicas
                suggestions.append(f'className="{cls}"')
        
        # Texto contenido único
        text_matches = re.findall(r'>([^<]{15,})<', target_line)
        for text in text_matches:
            suggestions.append(text.strip())
        
        # Atributos únicos
        attrs = re.findall(r'(\w+)=["\']([^"\']{10,})["\']', target_line)
        for attr, value in attrs:
            if attr not in ['className', 'class']:
                suggestions.append(f'{attr}="{value}"')
        
        return suggestions[:5]
        
    except Exception as e:
        return [f"Error: {e}"]
