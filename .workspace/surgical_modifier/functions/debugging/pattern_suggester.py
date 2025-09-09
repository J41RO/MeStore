class PatternSuggester:
    """Sugiere alternativas inteligentes para patrones que no coinciden"""
    def __init__(self):
        self.fuzzy_matcher = None
        
    def _get_fuzzy_matcher(self):
        """Lazy loading del fuzzy matcher"""
        if self.fuzzy_matcher is None:
            from ..pattern.fuzzy_matcher import FuzzyMatcher
            self.fuzzy_matcher = FuzzyMatcher()
        return self.fuzzy_matcher
    
    def suggest_patterns(self, content: str, pattern: str) -> list:
        """Método principal para sugerir patrones alternativos"""
        suggestions = []
        
        # 1. Detección de propiedades de objetos JavaScript/TypeScript
        if ':' in pattern:
            suggestions.extend(self._detect_object_properties(content, pattern))
        
        # 2. Detección de estructuras similares con fuzzy matching
        suggestions.extend(self._detect_fuzzy_structures(content, pattern))
        
        # 3. Detección de diferencias de formato
        suggestions.extend(self._detect_format_differences(content, pattern))
        
        # 4. Fallback a sugerencias básicas
        suggestions.extend(self.suggest_alternatives(pattern, content))
        
        # Eliminar duplicados y limitar
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:5]
    
    def _detect_object_properties(self, content: str, pattern: str) -> list:
        """Detecta propiedades de objetos con formato diferente"""
        suggestions = []
        if ':' in pattern:
            prop_name = pattern.split(':')[0].strip()
            # Buscar la propiedad con diferentes formatos de espaciado
            import re
            property_regex = rf'{re.escape(prop_name)}\s*:\s*[^,}}\n]+'
            matches = re.findall(property_regex, content)
            for match in matches[:3]:
                if match.strip() != pattern.strip():
                    suggestions.append(f"Found property with different spacing: '{match.strip()}'")
        return suggestions
    
    def _detect_fuzzy_structures(self, content: str, pattern: str) -> list:
        """Usa fuzzy matching para detectar estructuras similares"""
        suggestions = []
        try:
            fuzzy_matcher = self._get_fuzzy_matcher()
            matches = fuzzy_matcher.find_all(content, pattern, threshold=0.6)
            for match in matches[:2]:
                start, end = match['start'], match['end']
                found_text = content[start:end+10].split('\n')[0]  # Primera línea
                suggestions.append(f"Fuzzy match found: '{found_text.strip()}'")
        except Exception:
            pass
        return suggestions
    
    def _detect_format_differences(self, content: str, pattern: str) -> list:
        """Detecta diferencias de formato comunes"""
        suggestions = []
        
        # Quotes diferentes
        if '"' in pattern and "'" in content:
            alt_pattern = pattern.replace('"', "'")
            if alt_pattern in content:
                suggestions.append(f"Try with single quotes: '{alt_pattern}'")
        elif "'" in pattern and '"' in content:
            alt_pattern = pattern.replace("'", '"')
            if alt_pattern in content:
                suggestions.append(f"Try with double quotes: '{alt_pattern}'")
        
        return suggestions
    
    def suggest_alternatives(self, pattern: str, content: str) -> list:
        """Detecta problemas comunes y sugiere alternativas (método original mejorado)"""
        suggestions = []
        
        # Detección básica de case sensitivity
        if pattern.lower() in content.lower():
            if pattern not in content:
                suggestions.append(f"Try case-insensitive: '{pattern.lower()}' or '{pattern.upper()}'")
        
        # Detección de whitespace issues mejorada
        pattern_no_spaces = pattern.replace(' ', '')
        if pattern_no_spaces in content.replace(' ', ''):
            suggestions.append(f"Check whitespace: pattern may have spacing differences")
        
        return suggestions[:3]
