import re
from typing import List, Optional, Tuple


class FuzzyMatcher:
    """
    Clase para realizar fuzzy matching de patrones multilínea.
    Permite matching flexible que ignore diferencias menores de espaciado.
    """
    
    def normalize_whitespace(self, text: str) -> str:
        """
        Estandariza espacios y saltos de línea.
        
        Args:
            text: Texto a normalizar
            
        Returns:
            Texto con espaciado normalizado
        """
        # Normalizar espacios múltiples a uno solo
        text = re.sub(r'[ \t]+', ' ', text)
        # Normalizar saltos de línea múltiples
        text = re.sub(r'\n+', '\n', text)
        # Remover espacios al inicio/final de líneas
        text = '\n'.join(line.strip() for line in text.split('\n'))
        return text.strip()
    
    def fuzzy_match(self, target: str, line: str, flexible: bool = False) -> bool:
        """
        Compara target con línea usando matching exacto o flexible.
        
        Args:
            target: Patrón a buscar
            line: Línea donde buscar
            flexible: Si True, usa normalización para matching flexible
            
        Returns:
            True si hay match, False caso contrario
        """
        if not flexible:
            # Comportamiento tradicional: matching exacto
            return target in line
        
        # Matching flexible con normalización
        normalized_target = self.normalize_whitespace(target)
        normalized_line = self.normalize_whitespace(line)
        
        return normalized_target in normalized_line
    
    def find_target_line(self, lines: List[str], target: str, flexible: bool = False) -> Optional[int]:
        """
        Encuentra la línea que contiene el patrón target.
        
        Args:
            lines: Lista de líneas donde buscar
            target: Patrón a encontrar
            flexible: Si True, usa matching flexible
            
        Returns:
            Índice de la línea encontrada o None si no se encuentra
        """
        for i, line in enumerate(lines):
            if self.fuzzy_match(target, line, flexible):
                return i
        return None
