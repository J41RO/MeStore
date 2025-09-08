"""
Base Engine - Interface común para engines de modificación de código.
Define protocolo estándar que deben implementar todos los engines.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import re
import time
from collections import defaultdict
from datetime import datetime
from threading import Lock
from functions.backup.manager import BackupManager

class EngineCapability(Enum):
    """Capacidades que puede ofrecer un engine"""
    # Capabilities técnicas existentes
    LITERAL_SEARCH = "literal_search"
    REGEX_SEARCH = "regex_search" 
    STRUCTURAL_SEARCH = "structural_search"
    AST_AWARE = "ast_aware"
    MULTILINE_PATTERNS = "multiline_patterns"
    CONTEXT_AWARE = "context_aware"
    LANGUAGE_SPECIFIC = "language_specific"
    BATCH_OPERATIONS = "batch_operations"
    
    # Capabilities de operación requeridas por coordinadores
    CREATE = "create"
    WRITE = "write"
    PYTHON_SUPPORT = "python_support"
    JAVASCRIPT_SUPPORT = "javascript_support"

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
class EngineMetrics:
    """Sistema de métricas individual por engine"""
    def __init__(self):
        self.operation_count = defaultdict(int)
        self.success_count = defaultdict(int)
        self.total_execution_time = defaultdict(float)
        self.response_times = defaultdict(list)
        self.error_count = defaultdict(int)
        self.last_operation_time = defaultdict(float)
        self.operation_history = []
        self._lock = Lock()
    
    def record_operation(self, operation: str, success: bool, execution_time: float, error_msg: str = None):
        """Registra una operación con sus métricas"""
        with self._lock:
            self.operation_count[operation] += 1
            if success:
                self.success_count[operation] += 1
            else:
                self.error_count[operation] += 1
            
            self.total_execution_time[operation] += execution_time
            self.response_times[operation].append(execution_time)
            self.last_operation_time[operation] = execution_time
            
            # Mantener historial limitado (últimas 1000 operaciones)
            self.operation_history.append({
                'timestamp': datetime.now(),
                'operation': operation,
                'success': success,
                'execution_time': execution_time,
                'error_msg': error_msg
            })
            if len(self.operation_history) > 1000:
                self.operation_history = self.operation_history[-1000:]
    
    def get_success_rate(self, operation: str = None) -> float:
        """Obtiene tasa de éxito para operación específica o general"""
        if operation:
            total = self.operation_count[operation]
            return (self.success_count[operation] / total) if total > 0 else 0.0
        
        total_ops = sum(self.operation_count.values())
        total_success = sum(self.success_count.values())
        return (total_success / total_ops) if total_ops > 0 else 0.0
    
    def get_avg_response_time(self, operation: str = None) -> float:
        """Obtiene tiempo de respuesta promedio"""
        if operation:
            times = self.response_times[operation]
            return sum(times) / len(times) if times else 0.0
        
        all_times = []
        for times_list in self.response_times.values():
            all_times.extend(times_list)
        return sum(all_times) / len(all_times) if all_times else 0.0
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obtiene resumen completo de performance"""
        return {
            'total_operations': sum(self.operation_count.values()),
            'success_rate': self.get_success_rate(),
            'avg_response_time': self.get_avg_response_time(),
            'operations_by_type': dict(self.operation_count),
            'success_by_type': dict(self.success_count),
            'error_by_type': dict(self.error_count),
            'last_operation_times': dict(self.last_operation_time)
        }
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

    @property
    def execution_time(self) -> float:
        """Tiempo de ejecución de la operación si está disponible"""
        return self.metadata.get('execution_time', 0.0) if self.metadata else 0.0

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
        self._metrics = EngineMetrics()  # Nuevo sistema de métricas
        self.backup_manager = BackupManager()

    def _instrument_operation(self, operation_name: str):
        """Decorator interno para instrumentar operaciones con métricas automáticas"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                success = False
                error_msg = None
                
                try:
                    result = func(*args, **kwargs)
                    success = result.success if hasattr(result, 'success') else True
                    return result
                except Exception as e:
                    error_msg = str(e)
                    raise
                finally:
                    execution_time = time.perf_counter() - start_time
                    self._metrics.record_operation(operation_name, success, execution_time, error_msg)
                    
                    # Agregar timing al resultado si existe
                    if 'result' in locals() and hasattr(result, 'metadata'):
                        result.metadata['execution_time'] = execution_time
                        result.metadata['operation_timestamp'] = datetime.now().isoformat()
            
            return wrapper
        return decorator

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
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de performance de este engine específico"""
        summary = self._metrics.get_performance_summary()
        summary.update({
            'engine_name': self.name,
            'engine_version': self.version,
            'capabilities': [cap.value for cap in self.capabilities],
            'supported_languages': list(self.supported_languages)
        })
        return summary

    def get_performance_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtiene historial de operaciones recientes"""
        return self._metrics.operation_history[-limit:]

    def reset_metrics(self):
        """Reinicia todas las métricas"""
        self._metrics = EngineMetrics()
    
    def _create_backup_before_operation(self, file_path: str, operation_type: str) -> bool:
        """
        Crea un backup antes de realizar operaciones destructivas.
        
        Args:
            file_path: Ruta del archivo a respaldar
            operation_type: Tipo de operación (replace, insert_before, insert_after)
            
        Returns:
            bool: True si el backup se creó exitosamente
        """
        try:
            if operation_type in ['replace', 'insert_before', 'insert_after']:
                snapshot_id = self.backup_manager.create_snapshot(
                                    file_path, 
                                    operation_type
                                )
                return snapshot_id is not None
            return True  # No se requiere backup para operaciones de solo lectura
        except Exception as e:
            # Si el backup falla, registrar pero no interrumpir la operación
            print(f"Warning: Backup failed for {file_path}: {e}")
            return False
    
    @abstractmethod
    def _search_impl(self, content: str, pattern: str, **kwargs) -> EngineResult:
        """
        Implementación interna de búsqueda sin instrumentación.
        Los engines heredados deben implementar este método.
        
        Args:
            content: Contenido donde buscar
            pattern: Patrón a buscar
            **kwargs: Parámetros adicionales específicos del engine

        Returns:
            EngineResult con matches encontrados
        """
        pass

    @abstractmethod
    def _replace_impl(self, content: str, pattern: str, replacement: str, **kwargs) -> EngineResult:
        """
        Implementación interna de reemplazo sin instrumentación.
        Los engines heredados deben implementar este método.
        
        Args:
            content: Contenido donde reemplazar
            pattern: Patrón a reemplazar
            replacement: Texto de reemplazo
            **kwargs: Parámetros adicionales

        Returns:
            EngineResult con contenido modificado
        """
        pass

    def search(self, content: str, pattern: str, **kwargs) -> EngineResult:
        """
        Buscar patrón en contenido con instrumentación automática de métricas.
        
        Args:
            content: Contenido donde buscar
            pattern: Patrón a buscar
            **kwargs: Parámetros adicionales específicos del engine

        Returns:
            EngineResult con matches encontrados y métricas de timing
        """
        @self._instrument_operation('search')
        def instrumented_search():
            return self._search_impl(content, pattern, **kwargs)
        
        return instrumented_search()

    def replace(self, content: str, pattern: str, replacement: str, **kwargs) -> EngineResult:
        """
        Reemplazar patrón con instrumentación automática de métricas.
        
        Args:
            content: Contenido donde reemplazar
            pattern: Patrón a reemplazar
            replacement: Texto de reemplazo
            **kwargs: Parámetros adicionales

        Returns:
            EngineResult con contenido modificado y métricas de timing
        """
        @self._instrument_operation('replace')
        def instrumented_replace():
            return self._replace_impl(content, pattern, replacement, **kwargs)
        
        return instrumented_replace()
    
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