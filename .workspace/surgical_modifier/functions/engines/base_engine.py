"""
Base Engine - Interface común para engines de modificación de código.
Define protocolo estándar que deben implementar todos los engines.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import re

class EngineCapability(Enum):
    """Capacidades que puede ofrecer un engine"""
    LITERAL_SEARCH = "literal_search"
    REGEX_SEARCH = "regex_search"
    STRUCTURAL_SEARCH = "structural_search"
    AST_AWARE = "ast_aware"
    MULTILINE_PATTERNS = "multiline_patterns"
    CONTEXT_AWARE = "context_aware"
    LANGUAGE_SPECIFIC = "language_specific"
    BATCH_OPERATIONS = "batch_operations"

class OperationType(Enum):
    """Tipos de operaciones soportadas"""
    SEARCH = "search"
    REPLACE = "replace"
    INSERT_BEFORE = "insert_before"
    INSERT_AFTER = "insert_after"
    DELETE = "delete"
    EXTRACT = "extract"

class EngineStatus(Enum):
    """Estados de resultado de engine"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    NOT_SUPPORTED = "not_supported"

@dataclass
class EngineMatch:
    """Representa un match encontrado por el engine"""
    content: str
    start_line: int
    end_line: int
    start_column: int
    end_column: int
    context_before: str = ""
    context_after: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass 
class EngineResult:
    """Resultado de operación de engine"""
    status: EngineStatus
    matches: List[EngineMatch]
    modified_content: Optional[str] = None
    error_message: Optional[str] = None
    operations_count: int = 0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
            
    @property
    def success(self) -> bool:
        """True si la operación fue exitosa"""
        return self.status == EngineStatus.SUCCESS
        
    @property 
    def has_matches(self) -> bool:
        """True si se encontraron matches"""
        return len(self.matches) > 0

class BaseEngine(ABC):
    """
    Clase abstracta base para todos los engines de modificación.
    Define interface común que deben implementar todos los engines.
    """
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self._capabilities = set()
        self._supported_languages = set()
    
    @property
    def capabilities(self) -> set[EngineCapability]:
        """Capacidades soportadas por este engine"""
        return self._capabilities.copy()
        
    @property
    def supported_languages(self) -> set[str]:
        """Lenguajes soportados por este engine"""
        return self._supported_languages.copy()
    
    def supports_capability(self, capability: EngineCapability) -> bool:
        """Verifica si el engine soporta una capacidad específica"""
        return capability in self._capabilities
        
    def supports_language(self, language: str) -> bool:
        """Verifica si el engine soporta un lenguaje específico"""
        return language.lower() in self._supported_languages or len(self._supported_languages) == 0
        
    def supports_operation(self, operation: OperationType) -> bool:
        """Verifica si el engine soporta un tipo de operación"""
        return hasattr(self, f'_{operation.value}')
    
    @abstractmethod
    def search(self, content: str, pattern: str, **kwargs) -> EngineResult:
        """
        Buscar patrón en contenido.
        
        Args:
            content: Contenido donde buscar
            pattern: Patrón a buscar
            **kwargs: Parámetros adicionales específicos del engine
            
        Returns:
            EngineResult con matches encontrados
        """
        pass
    
    @abstractmethod 
    def replace(self, content: str, pattern: str, replacement: str, **kwargs) -> EngineResult:
        """
        Reemplazar patrón en contenido.
        
        Args:
            content: Contenido donde reemplazar
            pattern: Patrón a reemplazar
            replacement: Texto de reemplazo
            **kwargs: Parámetros adicionales
            
        Returns:
            EngineResult con contenido modificado
        """
        pass
    
    def insert_before(self, content: str, pattern: str, insertion: str, **kwargs) -> EngineResult:
        """
        Insertar texto antes del patrón.
        Implementación por defecto usando search + manipulación.
        """
        search_result = self.search(content, pattern, **kwargs)
        if not search_result.has_matches:
            return EngineResult(
                status=EngineStatus.FAILURE,
                matches=[],
                error_message=f"Pattern '{pattern}' not found"
            )
            
        # Implementación base - engines específicos pueden sobrescribir
        lines = content.split('\n')
        modified_lines = lines.copy()
        
        for match in reversed(search_result.matches):  # Reverse para preservar line numbers
            modified_lines.insert(match.start_line - 1, insertion)
            
        return EngineResult(
            status=EngineStatus.SUCCESS,
            matches=search_result.matches,
            modified_content='\n'.join(modified_lines),
            operations_count=len(search_result.matches)
        )
    
    def insert_after(self, content: str, pattern: str, insertion: str, **kwargs) -> EngineResult:
        """
        Insertar texto después del patrón.
        Implementación por defecto usando search + manipulación.
        """
        search_result = self.search(content, pattern, **kwargs)
        if not search_result.has_matches:
            return EngineResult(
                status=EngineStatus.FAILURE, 
                matches=[],
                error_message=f"Pattern '{pattern}' not found"
            )
            
        lines = content.split('\n')
        modified_lines = lines.copy()
        
        for match in reversed(search_result.matches):
            modified_lines.insert(match.end_line, insertion)
            
        return EngineResult(
            status=EngineStatus.SUCCESS,
            matches=search_result.matches, 
            modified_content='\n'.join(modified_lines),
            operations_count=len(search_result.matches)
        )
    
    def delete(self, content: str, pattern: str, **kwargs) -> EngineResult:
        """
        Eliminar patrón del contenido.
        Implementación por defecto usando replace con string vacío.
        """
        return self.replace(content, pattern, "", **kwargs)
    
    def __str__(self) -> str:
        return f"{self.name} v{self.version}"
        
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.name}, {self.version})>"

class EngineRegistry:
    """Registry para engines disponibles en el sistema"""
    
    _engines: Dict[str, type[BaseEngine]] = {}
    _instances: Dict[str, BaseEngine] = {}
    
    @classmethod
    def register(cls, engine_class: type[BaseEngine], name: Optional[str] = None) -> None:
        """Registrar un engine en el sistema"""
        engine_name = name or getattr(engine_class, 'DEFAULT_NAME', engine_class.__name__)
        cls._engines[engine_name.lower()] = engine_class
    
    @classmethod
    def get_engine(cls, name: str, **kwargs) -> BaseEngine:
        """Obtener instancia de engine por nombre"""
        name_lower = name.lower()
        
        # Usar instancia cached si existe y no hay kwargs
        if not kwargs and name_lower in cls._instances:
            return cls._instances[name_lower]
            
        if name_lower not in cls._engines:
            available = ', '.join(cls._engines.keys())
            raise ValueError(f"Engine '{name}' not found. Available: {available}")
            
        engine_class = cls._engines[name_lower]
        instance = engine_class(**kwargs)
        
        # Cache instancia si no hay kwargs personalizados
        if not kwargs:
            cls._instances[name_lower] = instance
            
        return instance
    
    @classmethod
    def list_engines(cls) -> List[str]:
        """Listar engines registrados"""
        return list(cls._engines.keys())
    
    @classmethod
    def clear_cache(cls) -> None:
        """Limpiar cache de instancias"""
        cls._instances.clear()

def register_engine(name: Optional[str] = None):
    """Decorator para registrar engines automáticamente"""
    def decorator(engine_class: type[BaseEngine]) -> type[BaseEngine]:
        EngineRegistry.register(engine_class, name)
        return engine_class
    return decorator