"""
Content Validator - Validador especializado de contenido antes de insertar.
Este módulo proporciona validación de sintaxis y consistencia antes de
realizar operaciones de inserción en el código.
"""
import ast
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from textwrap import dedent


class PreInsertionValidator:
    """
    Validador que verifica contenido antes de operaciones de inserción.
    Valida sintaxis, indentación y compatibilidad con el contexto objetivo.
    """
    
    def __init__(self):
        """Inicializa el validador de pre-inserción."""
        self.logger = logging.getLogger(__name__)
        self.validation_cache = {}
    
    def validate_syntax_compatibility(self, content: str, target_context: str) -> Tuple[bool, List[str]]:
        """
        Valida que el contenido sea sintácticamente compatible con el contexto objetivo.
        
        Args:
            content: Contenido a validar
            target_context: Contexto donde se insertará ('class_method', 'function', 'module', etc.)
            
        Returns:
            Tupla (es_válido, lista_de_problemas)
        """
        try:
            issues = []
            
            # Cache check
            cache_key = f"syntax_{hash(content)}_{target_context}"
            if cache_key in self.validation_cache:
                self.logger.debug(f"Cache hit for syntax validation")
                return self.validation_cache[cache_key]
            
            # Validar sintaxis básica de Python
            if not self._validate_python_syntax(content):
                issues.append("Invalid Python syntax detected")
            
            # Validar compatibilidad con contexto
            context_issues = self._validate_context_compatibility(content, target_context)
            issues.extend(context_issues)
            
            # Validar estructura de indentación
            indent_issues = self._validate_indentation_structure(content)
            issues.extend(indent_issues)
            
            is_valid = len(issues) == 0
            result = (is_valid, issues)
            
            # Almacenar en cache
            self.validation_cache[cache_key] = result
            
            if is_valid:
                self.logger.info(f"Content validation passed for context: {target_context}")
            else:
                self.logger.warning(f"Content validation failed: {len(issues)} issues found")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in syntax validation: {e}")
            return (False, [f"Validation error: {str(e)}"])
    
    def validate_indentation_consistency(self, content: str, target_indent: int = 4) -> Tuple[bool, List[str]]:
        """
        Valida la consistencia de indentación del contenido.
        
        Args:
            content: Contenido a validar
            target_indent: Nivel de indentación esperado
            
        Returns:
            Tupla (es_válido, lista_de_problemas)
        """
        try:
            issues = []
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                if line.strip():  # Ignorar líneas vacías
                    indent_level = len(line) - len(line.lstrip())
                    
                    # Verificar que la indentación sea múltiplo del target
                    if indent_level % target_indent != 0:
                        issues.append(f"Line {i}: Indentation not multiple of {target_indent}")
                    
                    # Verificar que use espacios, no tabs
                    if '\t' in line[:indent_level]:
                        issues.append(f"Line {i}: Found tabs instead of spaces")
            
            is_valid = len(issues) == 0
            
            if is_valid:
                self.logger.debug(f"Indentation validation passed")
            else:
                self.logger.warning(f"Indentation issues found: {len(issues)}")
            
            return (is_valid, issues)
            
        except Exception as e:
            self.logger.error(f"Error in indentation validation: {e}")
            return (False, [f"Indentation validation error: {str(e)}"])
    
    def _validate_python_syntax(self, content: str) -> bool:
        """
        Valida que el contenido tenga sintaxis Python válida.
        
        Args:
            content: Contenido a validar
            
        Returns:
            True si la sintaxis es válida
        """
        try:
            # Intentar parsear como fragmento de código
            ast.parse(dedent(content))
            return True
        except SyntaxError:
            # Intentar como expresión
            try:
                ast.parse(dedent(content), mode='eval')
                return True
            except SyntaxError:
                return False
        except Exception:
            return False
    
    def _validate_context_compatibility(self, content: str, target_context: str) -> List[str]:
        """
        Valida que el contenido sea compatible con el contexto objetivo.
        
        Args:
            content: Contenido a validar
            target_context: Contexto objetivo
            
        Returns:
            Lista de problemas de compatibilidad
        """
        issues = []
        
        if target_context == 'class_method':
            if not content.strip().startswith('def '):
                if 'def ' not in content:
                    issues.append("Content doesn't appear to be a method definition")
        
        elif target_context == 'function':
            if content.strip().startswith('class '):
                issues.append("Class definition not appropriate for function context")
        
        elif target_context == 'class_body':
            # Verificar que el contenido sea apropiado para dentro de una clase
            if content.strip().startswith('import '):
                issues.append("Import statements should be at module level")
        
        return issues
    
    def _validate_indentation_structure(self, content: str) -> List[str]:
        """
        Valida la estructura general de indentación.
        
        Args:
            content: Contenido a validar
            
        Returns:
            Lista de problemas de estructura
        """
        issues = []
        lines = content.split('\n')
        indent_stack = []
        
        for i, line in enumerate(lines, 1):
            if line.strip():
                current_indent = len(line) - len(line.lstrip())
                
                # Verificar saltos de indentación válidos
                if indent_stack:
                    if current_indent > indent_stack[-1]:
                        # Aumento de indentación
                        indent_stack.append(current_indent)
                    elif current_indent < indent_stack[-1]:
                        # Disminución de indentación
                        while indent_stack and current_indent < indent_stack[-1]:
                            indent_stack.pop()
                        if not indent_stack or current_indent != indent_stack[-1]:
                            if current_indent not in indent_stack:
                                issues.append(f"Line {i}: Invalid indentation level")
                else:
                    indent_stack.append(current_indent)
        
        return issues