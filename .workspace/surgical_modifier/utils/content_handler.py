#!/usr/bin/env python3
"""
Content Handler v5.4 - Lógica reestructurada
REGLA: Solo procesar escapes para FORMATEO, nunca para código fuente
"""

import re
import os
import tempfile
from typing import Tuple, Optional, Dict, List, Any
from enum import Enum
from dataclasses import dataclass

class ContentType(Enum):
    """Enum for content types"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GENERIC = "generic"
    MARKUP = "markup"
    CONFIG = "config"
    BASH = "bash"

@dataclass
class ContentValidationResult:
    """Result of content validation"""
    is_valid: bool = True
    errors: List[str] = None
    warnings: List[str] = None
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.suggestions is None:
            self.suggestions = []

class ContentHandler:
    """Manejo inteligente de contenido con lógica reestructurada"""
    
    def __init__(self, content: str, file_path: str = "", operation: str = ""):
        self.original_content = content
        self.file_path = file_path
        self.operation = operation
        self.content_type = self._detect_content_type()
        self.is_code_content = self._is_code_content()
        self.handling_strategy = self._determine_strategy()
    
    def _detect_content_type(self) -> str:
        """Detectar tipo de contenido"""
        if self.file_path:
            ext = os.path.splitext(self.file_path)[1].lower()
            type_mapping = {
                '.py': 'python', '.js': 'javascript', '.jsx': 'javascript',
                '.ts': 'typescript', '.tsx': 'typescript', '.java': 'java',
                '.cpp': 'cpp', '.c': 'c', '.cs': 'csharp', '.php': 'php',
                '.rb': 'ruby', '.go': 'go', '.rs': 'rust', '.swift': 'swift',
                '.kt': 'kotlin', '.html': 'markup', '.css': 'stylesheet',
                '.json': 'config', '.yaml': 'config', '.sql': 'database',
                '.sh': 'bash', '.md': 'markdown'
            }
            return type_mapping.get(ext, 'generic')
        return 'generic'
    
    def _is_code_content(self) -> bool:
        """Determinar si el contenido es código fuente"""
        # Es código si tiene extensión de programación
        code_types = ['python', 'javascript', 'typescript', 'java', 'cpp', 'c', 'csharp', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin']
        if self.content_type in code_types:
            return True
        
        # O si el contenido parece código
        code_indicators = ['def ', 'function ', 'class ', 'public class', 'import ', 'from ', 'const ', 'let ', 'var ', '#include']
        return any(indicator in self.original_content for indicator in code_indicators)
    
    def _determine_strategy(self) -> str:
        """Determinar estrategia basada en tipo de contenido"""
        if self.is_code_content:
            print(f"ℹ️ CÓDIGO FUENTE detectado ({self.content_type}) - preservando sintaxis")
            return 'preserve_code'
        else:
            print(f"ℹ️ CONTENIDO DE TEXTO detectado - procesando escapes para formateo")
            return 'process_formatting'
    
    def get_safe_content(self) -> Tuple[str, Optional[str]]:
        """Obtener contenido seguro con lógica clara"""
        
        if self.handling_strategy == 'preserve_code':
            # CÓDIGO FUENTE: No tocar NADA - preservar tal como está
            print("ℹ️ Preservando código fuente sin modificaciones")
            return self.original_content, None
        
        elif self.handling_strategy == 'process_formatting':
            # TEXTO/FORMATEO: Sí procesar escapes para formateo
            print("ℹ️ Procesando escapes para formateo de texto")
            formatted_content = self._process_formatting_escapes()
            return formatted_content, None
        
        else:
            # Fallback: preservar original
            return self.original_content, None
    
    def _process_formatting_escapes(self) -> str:
        """Procesar escapes SOLO para formateo de texto (no código)"""
        content = self.original_content
        
        # SOLO para texto plano o documentación
        # Convertir escapes de formateo
        content = content.replace('\\n', '\n')    # Saltos de línea
        content = content.replace('\\t', '\t')    # Tabs
        content = content.replace('\\r', '\r')    # Retorno de carro
        
        # NO tocar comillas porque esto es texto, no código
        print("ℹ️ Escapes de formateo procesados (\\n → salto de línea, \\t → tab)")
        return content

# ============================================================================
# COMPATIBILIDAD CON SISTEMA EXISTENTE
# ============================================================================

content_handler = ContentHandler("", "", "")

def create_content_handler(content: str, file_path: str = "", operation: str = "") -> ContentHandler:
    """Factory function para crear ContentHandler"""
    return ContentHandler(content, file_path, operation)

def process_content_safely(content: str, file_path: str = "", operation: str = "") -> tuple:
    """Procesar contenido de forma segura"""
    handler = ContentHandler(content, file_path, operation)
    return handler.get_safe_content()
