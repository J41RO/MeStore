"""
Intelligent Block Parser - Parser inteligente para bloques de código completos.
Este módulo proporciona funcionalidades para detectar y extraer bloques completos
de código como métodos, funciones y clases usando AST.
"""
import ast
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path


class IntelligentBlockParser:
    """
    Parser inteligente que detecta métodos/funciones/clases completas.
    Utiliza AST para identificar bloques de código de manera precisa.
    """
    
    def __init__(self):
        """Inicializa el parser inteligente de bloques."""
        self.logger = logging.getLogger(__name__)
        self.parsed_cache = {}
    
    def extract_complete_block(self, file_path: str, target_name: str) -> Optional[Dict[str, Any]]:
        """
        Extrae un bloque completo (método/función/clase) por nombre.
        
        Args:
            file_path: Ruta al archivo Python
            target_name: Nombre del método/función/clase a extraer
            
        Returns:
            Dict con información del bloque o None si no se encuentra
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Cache check
            cache_key = f"{file_path}_{target_name}"
            if cache_key in self.parsed_cache:
                self.logger.debug(f"Cache hit for block: {target_name}")
                return self.parsed_cache[cache_key]
            
            tree = ast.parse(content)
            lines = content.split('\n')
            
            block_info = self._find_block_in_ast(tree, target_name, lines)
            
            if block_info:
                self.parsed_cache[cache_key] = block_info
                self.logger.info(f"Successfully extracted block: {target_name}")
            
            return block_info
            
        except Exception as e:
            self.logger.error(f"Error extracting block {target_name}: {e}")
            return None
    
    def _find_block_in_ast(self, tree: ast.AST, target_name: str, lines: List[str]) -> Optional[Dict[str, Any]]:
        """
        Busca un bloque específico en el AST.
        
        Args:
            tree: AST del código
            target_name: Nombre a buscar
            lines: Líneas del código original
            
        Returns:
            Dict con información del bloque encontrado
        """
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name == target_name:
                    start_line = node.lineno - 1  # AST usa 1-indexed
                    end_line = node.end_lineno - 1 if hasattr(node, 'end_lineno') else self._estimate_end_line(node, lines)
                    
                    return {
                        'name': node.name,
                        'type': type(node).__name__,
                        'start_line': start_line,
                        'end_line': end_line,
                        'content': '\n'.join(lines[start_line:end_line + 1]),
                        'signature': self.parse_method_signature(node, lines)
                    }
        return None
    
    def parse_method_signature(self, node: ast.AST, lines: List[str]) -> str:
        """
        Extrae la firma completa de un método/función.
        
        Args:
            node: Nodo AST del método/función
            lines: Líneas del código original
            
        Returns:
            Firma completa del método
        """
        try:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start_line = node.lineno - 1
                
                # Buscar la línea que contiene la definición completa
                signature_lines = []
                current_line = start_line
                paren_count = 0
                in_signature = False
                
                while current_line < len(lines):
                    line = lines[current_line].strip()
                    
                    if 'def ' in line or 'async def ' in line:
                        in_signature = True
                    
                    if in_signature:
                        signature_lines.append(lines[current_line])
                        paren_count += line.count('(') - line.count(')')
                        
                        if ':' in line and paren_count == 0:
                            break
                    
                    current_line += 1
                
                return ''.join(signature_lines).strip()
                
        except Exception as e:
            self.logger.error(f"Error parsing method signature: {e}")
            
        return ""
    
    def _estimate_end_line(self, node: ast.AST, lines: List[str]) -> int:
        """
        Estima la línea final de un bloque cuando end_lineno no está disponible.
        
        Args:
            node: Nodo AST
            lines: Líneas del código
            
        Returns:
            Número de línea estimado para el final del bloque
        """
        start_line = node.lineno - 1
        current_line = start_line + 1
        base_indent = len(lines[start_line]) - len(lines[start_line].lstrip())
        
        while current_line < len(lines):
            line = lines[current_line]
            if line.strip():  # Línea no vacía
                line_indent = len(line) - len(line.lstrip())
                if line_indent <= base_indent:
                    return current_line - 1
            current_line += 1
        
        return len(lines) - 1