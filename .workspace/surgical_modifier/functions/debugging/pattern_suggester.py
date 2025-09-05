class PatternSuggester:
    """Sugiere alternativas para patrones que no coinciden"""
    
    def __init__(self):
        pass
    
    def suggest_alternatives(self, pattern: str, content: str) -> list:
        """Detecta problemas comunes y sugiere alternativas"""
        suggestions = []
        
        # Detección básica de case sensitivity
        if pattern.lower() in content.lower():
            if pattern not in content:
                suggestions.append(f"Try case-insensitive: '{pattern.lower()}' or '{pattern.upper()}'")
        
        # Detección de whitespace issues
        pattern_no_spaces = pattern.replace(' ', '')
        if pattern_no_spaces in content.replace(' ', ''):
            suggestions.append(f"Check whitespace: pattern may have spacing differences")
        
        # Fuzzy matching básico para patrones similares
        lines = content.split('\n')
        for line in lines:
            if len(pattern) > 3:  # Solo para patrones no triviales
                # Buscar coincidencias parciales
                for word in line.split():
                    if len(word) > 3 and abs(len(word) - len(pattern)) <= 2:
                        if pattern.lower()[:3] == word.lower()[:3]:
                            suggestions.append(f"Similar word found: '{word}'")
        
        return suggestions[:3]  # Máximo 3 sugerencias
