"""
TypeScript Import Resolver
==========================
Resolución de imports con alias para TypeScript
"""

import re
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

class ImportResolver:
    """Resolver especializado para imports TypeScript con alias"""
    
    def __init__(self, tsconfig_path: Optional[str] = None):
        """Inicializar resolver con configuración TypeScript"""
        self.aliases = {}
        self.base_url = '.'
        
        if tsconfig_path and os.path.exists(tsconfig_path):
            self._load_aliases_from_tsconfig(tsconfig_path)
        else:
            # Alias comunes por defecto
            self.aliases = {
                '@': './src',
                '@components': './src/components',
                '@utils': './src/utils',
                '@types': './src/types'
            }
            
    def _extract_import_path(self, import_statement: str) -> str:
        """Extraer path del import statement"""
        
        # Patterns para diferentes tipos de import - REGEX CORREGIDOS
        patterns = [
            r"import\s+.*?from\s+['\"](.+?)['\"]",  # import x from 'path'
            r"import\s+['\"](.+?)['\"]",             # import 'path'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, import_statement)
            if match:
                return match.group(1)
                
        return ''
        
    def resolve_import_path(self, import_statement: str) -> str:
        """Resolver import con alias a ruta real"""
        
        # Extraer path del import
        import_path = self._extract_import_path(import_statement)
        if not import_path:
            return import_statement
            
        # Resolver alias
        for alias, real_path in self.aliases.items():
            if import_path.startswith(alias):
                resolved_path = import_path.replace(alias, real_path, 1)
                return import_statement.replace(import_path, resolved_path)
                
        return import_statement
        
    def get_available_aliases(self) -> Dict[str, str]:
        """Obtener alias disponibles"""
        return self.aliases.copy()



    def add_import_if_missing(self, file_content: str, import_statement: str) -> str:
        """Agregar import si no existe"""
        if import_statement.strip() not in file_content:
            return import_statement + '\n' + file_content
        return file_content
        
    def organize_imports(self, file_content: str) -> str:
        """Organizar imports TypeScript por categorías"""
        
        lines = file_content.split('\n')
        imports = []
        other_lines = []
        
        # Separar imports del resto del código
        for i, line in enumerate(lines):
            if line.strip().startswith('import '):
                imports.append(line.strip())
            else:
                other_lines.extend(lines[i:])
                break
                
        if not imports:
            return file_content
            
        # Categorizar imports
        categorized_imports = {
            'libraries': [],  # node_modules
            'aliases': [],    # @/... imports
            'relative': []    # ./... imports
        }
        
        for import_line in imports:
            import_path = self._extract_import_path(import_line)
            
            if import_path.startswith('@/') or any(import_path.startswith(alias) for alias in self.aliases.keys()):
                categorized_imports['aliases'].append(import_line)
            elif import_path.startswith('./') or import_path.startswith('../'):
                categorized_imports['relative'].append(import_line)
            else:
                categorized_imports['libraries'].append(import_line)
                
        # Reconstruir imports organizados
        organized_imports = []
        
        # Libraries primero
        if categorized_imports['libraries']:
            organized_imports.extend(sorted(categorized_imports['libraries']))
            organized_imports.append('')  # Línea vacía
            
        # Alias imports
        if categorized_imports['aliases']:
            organized_imports.extend(sorted(categorized_imports['aliases']))
            organized_imports.append('')  # Línea vacía
            
        # Relative imports al final
        if categorized_imports['relative']:
            organized_imports.extend(sorted(categorized_imports['relative']))
            organized_imports.append('')  # Línea vacía
            
        # Remover línea vacía extra al final
        while organized_imports and organized_imports[-1] == '':
            organized_imports.pop()
            
        return '\n'.join(organized_imports + other_lines)
        
    def create_import_statement(self, module_name: str, import_path: str, import_type: str = 'default') -> str:
        """Crear import statement TypeScript"""
        
        if import_type == 'default':
            return f'import {module_name} from \'{import_path}\';'
        elif import_type == 'named':
            return f'import {{ {module_name} }} from \'{import_path}\';'
        elif import_type == 'namespace':
            return f'import * as {module_name} from \'{import_path}\';'
        elif import_type == 'side_effect':
            return f'import \'{import_path}\';'
        else:
            raise ValueError(f'Unknown import type: {import_type}')
