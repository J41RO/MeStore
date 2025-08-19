"""
🚀 CodeCraft Ultimate v6.0 - Core Models
Shared data models to avoid circular imports
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import json


@dataclass
class OperationResult:
    """Resultado de una operación de CodeCraft"""
    
    success: bool
    operation: str
    message: str
    data: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    next_suggestions: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        result = {
            'success': self.success,
            'operation': self.operation,
            'message': self.message
        }
        
        if self.data:
            result['data'] = self.data
        
        if self.suggestions:
            result['suggestions'] = self.suggestions
        
        if self.next_suggestions:
            result['next_suggestions'] = self.next_suggestions
        
        return result
    
    def to_json(self) -> str:
        """Convertir a JSON"""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ExecutionContext:
    """Contexto de ejecución"""
    
    project_root: str
    current_file: Optional[str] = None
    backup_enabled: bool = True
    verbose: bool = False
    output_format: str = "structured"
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'project_root': self.project_root,
            'current_file': self.current_file,
            'backup_enabled': self.backup_enabled,
            'verbose': self.verbose,
            'output_format': self.output_format,
            'session_id': self.session_id
        }


@dataclass
class CommandArgs:
    """Argumentos de comando parseados"""
    
    operation: str
    primary_args: List[str]
    options: Dict[str, str]
    flags: List[str]
    
    def __post_init__(self):
        if self.primary_args is None:
            self.primary_args = []
        if self.options is None:
            self.options = {}
        if self.flags is None:
            self.flags = []