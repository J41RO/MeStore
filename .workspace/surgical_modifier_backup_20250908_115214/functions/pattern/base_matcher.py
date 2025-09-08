"""
Base Matcher Interface - Interface común para todos los pattern matchers
Proporciona métodos estándar que todos los matchers deben implementar
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Union, Dict
import re


class BaseMatcher(ABC):
    """
    Interface abstracta base para todos los pattern matchers.
    
    Define métodos estándar que garantizan compatibilidad y combinabilidad:
    - find(): Encuentra primera coincidencia
    - match(): Verifica si hay coincidencia
    - find_all(): Encuentra todas las coincidencias
    """
    
    def __init__(self, engine_type: Optional[str] = None):
        """
        Inicializa el matcher base con soporte opcional para engine awareness.
        
        Args:
            engine_type: Tipo de engine ('native', 'ast', 'comby', etc.) - OPCIONAL para retrocompatibilidad
        """
        self._debug = False
        self._case_sensitive = True
        # Nueva funcionalidad engine-aware
        self._engine_type = engine_type
        self._engine_capabilities = []
        self._pattern_cache = {}
        
    @abstractmethod
    def find(self, text: str, pattern: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Encuentra la primera coincidencia del patrón en el texto.
        
        Args:
            text: Texto donde buscar
            pattern: Patrón a buscar
            **kwargs: Argumentos específicos del matcher
            
        Returns:
            Dict con información de la coincidencia o None si no encuentra
            Formato estándar: {'match': str, 'start': int, 'end': int, 'groups': list}
        """
        pass
    
    @abstractmethod
    def match(self, text: str, pattern: str, **kwargs) -> bool:
        """
        Verifica si el patrón coincide en el texto.
        
        Args:
            text: Texto donde verificar
            pattern: Patrón a verificar
            **kwargs: Argumentos específicos del matcher
            
        Returns:
            True si encuentra coincidencia, False caso contrario
        """
        pass
    
    @abstractmethod
    def find_all(self, text: str, pattern: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Encuentra todas las coincidencias del patrón en el texto.
        
        Args:
            text: Texto donde buscar
            pattern: Patrón a buscar
            **kwargs: Argumentos específicos del matcher
            
        Returns:
            Lista de dicts con información de coincidencias
            Formato estándar: [{'match': str, 'start': int, 'end': int, 'groups': list}, ...]
        """
        pass
    
    # Métodos de configuración comunes
    def set_debug(self, debug: bool) -> None:
        """Activa/desactiva modo debug."""
        self._debug = debug
        
    def set_case_sensitive(self, case_sensitive: bool) -> None:
        """Configura sensibilidad a mayúsculas/minúsculas."""
        self._case_sensitive = case_sensitive
    
    def _normalize_result(self, match_obj: Any, start: int, end: int, groups: List[str] = None) -> Dict[str, Any]:
        """
        Normaliza resultado a formato estándar.
        
        Args:
            match_obj: Objeto de coincidencia (puede ser str o match object)
            start: Posición de inicio
            end: Posición de fin
            groups: Grupos capturados (opcional)
            
        Returns:
            Dict normalizado con formato estándar
        """
        if groups is None:
            groups = []
            
        if hasattr(match_obj, 'group'):
            # Es un match object de regex
            match_text = match_obj.group(0)
            if hasattr(match_obj, 'groups'):
                groups = list(match_obj.groups())
        else:
            # Es un string simple
            match_text = str(match_obj)
            
        return {
            'match': match_text,
            'start': start,
            'end': end,
            'groups': groups
        }
    
    def _debug_print(self, message: str) -> None:
        """Imprime mensaje solo si debug está activado."""
        if self._debug:
            print(f"[DEBUG {self.__class__.__name__}] {message}")

        # ==================== NUEVOS MÉTODOS ENGINE-AWARE v2.0 ====================
        
    def set_engine_context(self, engine_type: str, capabilities: List[str]) -> None:
        """
        Configura el contexto del engine para optimizaciones específicas.
        
        Args:
            engine_type: Identificador del engine ('native', 'ast', 'comby', etc.)
            capabilities: Lista de capabilities que soporta el engine
        """
        self._engine_type = engine_type
        self._engine_capabilities = capabilities
        # Limpiar cache cuando cambia engine
        self._pattern_cache.clear()

    def get_engine_optimized_pattern(self, pattern: str) -> str:
        """
        Retorna versión optimizada del pattern para el engine actual.
        
        Args:
            pattern: Pattern original a optimizar
            
        Returns:
            Pattern optimizado para el engine actual, o pattern original si no hay optimización
        """
        if not self._engine_type:
            return pattern
            
        cache_key = f"{self._engine_type}:{pattern}"
        if cache_key in self._pattern_cache:
            return self._pattern_cache[cache_key]
            
        optimized = self._optimize_pattern_for_engine(pattern)
        self._pattern_cache[cache_key] = optimized
        return optimized

    def _optimize_pattern_for_engine(self, pattern: str) -> str:
        """
        Método protegido para optimizar pattern según engine actual.
        Subclases deben implementar optimizaciones específicas.
        Base class retorna pattern sin modificar.
        """
        return pattern

    @property
    def engine_type(self) -> Optional[str]:
        """Retorna el tipo de engine configurado"""
        return self._engine_type

    @property 
    def engine_capabilities(self) -> List[str]:
        """Retorna las capabilities del engine actual"""
        return self._engine_capabilities.copy()

    def has_engine_capability(self, capability: str) -> bool:
        """
        Verifica si el engine actual soporta una capability específica.
        
        Args:
            capability: Capability a verificar
            
        Returns:
            True si el engine soporta la capability, False en caso contrario
        """
        return capability in self._engine_capabilities


class MatcherCombiner:
    """
    Clase helper para combinar múltiples matchers de forma eficiente.
    Permite usar varios matchers en secuencia o en paralelo.
    """
    
    def __init__(self, matchers: List[BaseMatcher]):
        """
        Inicializa el combinador con lista de matchers.
        
        Args:
            matchers: Lista de instancias de BaseMatcher
        """
        self.matchers = matchers
        
    def find_any(self, text: str, patterns: List[str], **kwargs) -> Optional[Dict[str, Any]]:
        """
        Busca cualquier patrón usando cualquier matcher.
        Retorna la primera coincidencia encontrada.
        """
        for i, pattern in enumerate(patterns):
            for j, matcher in enumerate(self.matchers):
                result = matcher.find(text, pattern, **kwargs)
                if result:
                    result['matcher_index'] = j
                    result['pattern_index'] = i
                    return result
        return None
        
    def find_all_combined(self, text: str, patterns: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Busca todos los patrones usando todos los matchers.
        Retorna todas las coincidencias encontradas.
        """
        results = []
        for i, pattern in enumerate(patterns):
            for j, matcher in enumerate(self.matchers):
                matches = matcher.find_all(text, pattern, **kwargs)
                for match in matches:
                    match['matcher_index'] = j
                    match['pattern_index'] = i
                    results.append(match)
        
        # Ordenar por posición en el texto
        results.sort(key=lambda x: x['start'])
        return results
        
    def match_any(self, text: str, patterns: List[str], **kwargs) -> bool:
        """
        Verifica si cualquier patrón coincide usando cualquier matcher.
        """
        for pattern in patterns:
            for matcher in self.matchers:
                if matcher.match(text, pattern, **kwargs):
                    return True
        return False