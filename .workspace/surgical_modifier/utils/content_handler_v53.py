#!/usr/bin/env python3
"""
Content Handler v5.3 - Adaptado de la versión monolítica exitosa
Manejo inteligente de contenido con correcciones v5.3
"""

import re
import os
import tempfile
from typing import Tuple, Optional

class ContentHandler:
    """Manejo inteligente de contenido con correcciones v5.3"""
    
    def __init__(self, content: str, file_path: str = "", operation: str = ""):
        self.original_content = content
        self.file_path = file_path
        self.operation = operation
        self.content_type = self._detect_content_type()
        self.is_problematic = self._detect_problematic_content()
        self.handling_strategy = self._determine_strategy()
    
    def _detect_content_type(self) -> str:
        """Detectar tipo de contenido basado en archivo y contenido"""
        
        # Detección por extensión de archivo
        if self.file_path:
            ext = os.path.splitext(self.file_path)[1].lower()
            type_mapping = {
                '.py': 'python',
                '.js': 'javascript', '.jsx': 'javascript',
                '.ts': 'typescript', '.tsx': 'typescript',
                '.java': 'java',
                '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp',
                '.c': 'c',
                '.cs': 'csharp',
                '.php': 'php',
                '.rb': 'ruby',
                '.go': 'go',
                '.rs': 'rust',
                '.swift': 'swift',
                '.kt': 'kotlin',
                '.scala': 'scala',
                '.sh': 'bash', '.bash': 'bash',
                '.html': 'markup', '.xml': 'markup',
                '.css': 'stylesheet', '.scss': 'stylesheet',
                '.json': 'config', '.yaml': 'config', '.yml': 'config',
                '.sql': 'database'
            }
            
            if ext in type_mapping:
                return type_mapping[ext]
        
        # Detección por contenido (universal)
        content_lower = self.original_content.lower()
        
        # Indicadores por lenguaje
        if any(indicator in content_lower for indicator in ['def ', 'class ', 'import ', 'from ', '__name__']):
            return 'python'
        elif any(indicator in content_lower for indicator in ['function ', 'const ', 'let ', 'var ', '=>', 'console.log']):
            return 'javascript'
        elif any(indicator in content_lower for indicator in ['interface ', 'type ', 'export ', 'import ']):
            return 'typescript'
        elif any(indicator in content_lower for indicator in ['public class', 'public static', 'import java']):
            return 'java'
        elif any(indicator in content_lower for indicator in ['#include', 'namespace ', 'std::']):
            return 'cpp'
        elif any(indicator in content_lower for indicator in ['using system', 'public class', 'namespace ']):
            return 'csharp'
        elif any(indicator in content_lower for indicator in ['#!/bin/bash', 'echo ', 'if [', '${', 'then', 'fi']):
            return 'bash'
        else:
            return 'generic'
    
    def _detect_problematic_content(self) -> bool:
        """Detectar si el contenido es problemático para bash (universal)"""
        
        # Para lenguajes de programación modernos, ser más permisivo
        if self.content_type in ['python', 'javascript', 'typescript', 'java', 'cpp', 'csharp']:
            problematic_indicators = [
                # Solo contenido extremadamente complejo
                len(self.original_content.split('\n')) > 20,
                len(self.original_content) > 3000,
                
                # Backticks con comandos bash reales
                '`' in self.original_content and any(cmd in self.original_content for cmd in ['ls', 'cat', 'grep', 'find']),
                
                # Variables bash complejas
                '${' in self.original_content and 'bash' in self.original_content.lower(),
            ]
        else:
            # Para otros tipos, usar detección más estricta
            problematic_indicators = [
                len(self.original_content.split('\n')) > 8,
                '"' in self.original_content and "'" in self.original_content,
                '`' in self.original_content,
                '$' in self.original_content and '{' in self.original_content,
                self.original_content.count('"') % 2 != 0,
                self.original_content.count("'") % 2 != 0,
                '\\' in self.original_content,
                len(self.original_content) > 1000,
            ]
        
        return any(problematic_indicators)
    
    def _determine_strategy(self) -> str:
        """Determinar estrategia de manejo inteligente universal"""
        
        # NUEVA LÓGICA v5.3: Más inteligente para contenido universal
        if self.content_type in ['python', 'javascript', 'typescript', 'java', 'cpp', 'csharp']:
            print(f"ℹ️ Modo RAW v5.3 activado para contenido {self.content_type}")
            return 'raw_mode_v3'
        
        if not self.is_problematic:
            return 'direct'
        elif len(self.original_content.split('\n')) > 20:
            return 'temp_file'
        elif '`' in self.original_content and any(cmd in self.original_content for cmd in ['ls', 'cat', 'grep']):
            return 'temp_file'
        elif '"' in self.original_content or "'" in self.original_content:
            return 'smart_escape_v3'
        else:
            return 'escape_special_v3'
    
    def get_safe_content(self) -> Tuple[str, Optional[str]]:
        """Obtener contenido seguro con mejoras v5.3"""
        
        if self.handling_strategy == 'raw_mode_v3':
            # NUEVO v5.3: Modo RAW universal mejorado
            processed_content = self._process_multiline_content_v3()
            print("ℹ️ Usando modo RAW v5.3 - procesamiento universal mejorado")
            return processed_content, None
        
        elif self.handling_strategy == 'direct':
            return self.original_content, None
        
        elif self.handling_strategy == 'temp_file':
            temp_file = self._create_temp_file()
            return f'@TEMP_FILE:{temp_file}', temp_file
        
        elif self.handling_strategy == 'smart_escape_v3':
            escaped = self._smart_escape_v3()
            return escaped, None
        
        elif self.handling_strategy == 'escape_special_v3':
            escaped = self._escape_special_v3()
            return escaped, None
        
        else:
            # Fallback mejorado
            temp_file = self._create_temp_file()
            return f'@TEMP_FILE:{temp_file}', temp_file
    
    def _process_multiline_content_v3(self) -> str:
        """NUEVO v5.3: Procesar contenido multi-línea universal"""
        content = self.original_content
        
        # Si el contenido contiene \n literal, convertirlos a saltos de línea reales
        if '\\n' in content:
            # Solo convertir \n que no están ya escapados
            content = re.sub(r'(?<!\\)\\n', '\n', content)
            print("ℹ️ Convertidos \\n literales a saltos de línea reales")
        
        # Procesamiento adicional para diferentes tipos de contenido
        if self.content_type == 'python':
            # Preservar indentación Python
            content = self._preserve_python_indentation(content)
        elif self.content_type in ['javascript', 'typescript']:
            # Preservar estructura de bloques JavaScript/TypeScript
            content = self._preserve_js_structure(content)
        
        return content
    
    def _preserve_python_indentation(self, content: str) -> str:
        """Preservar indentación Python"""
        lines = content.split('\n')
        preserved_lines = []
        
        for line in lines:
            # Preservar indentación existente
            if line.strip():
                preserved_lines.append(line)
            else:
                preserved_lines.append('')
        
        return '\n'.join(preserved_lines)
    
    def _preserve_js_structure(self, content: str) -> str:
        """Preservar estructura JavaScript/TypeScript"""
        # Manejar template literals y arrow functions
        content = re.sub(r'`([^`]*)`', r'`\1`', content)  # Preservar template literals
        return content
    
    def _smart_escape_v3(self) -> str:
        """NUEVO v5.3: Escape inteligente universal mejorado"""
        content = self.original_content
        
        # Escape universal más inteligente
        if self.content_type in ['python', 'javascript', 'typescript', 'java', 'cpp', 'csharp']:
            # Solo escapar caracteres críticos para bash
            bash_critical = ['!', '$`', '$(', '&&', '||']
            for chars in bash_critical:
                if chars in content:
                    # Usar temp file para casos realmente problemáticos
                    return f'@TEMP_FILE:{self._create_temp_file()}'
            
            # Para casos simples, escape mínimo
            content = content.replace('"', '\\"')
        else:
            # Para otros tipos, escape más completo pero inteligente
            content = content.replace('\\', '\\\\')  # Escapar backslashes primero
            content = content.replace('"', '\\"')    # Escapar comillas dobles
            if "'" in content and '"' in content:
                content = content.replace("'", "\\'")
        
        return content
    
    def _escape_special_v3(self) -> str:
        """NUEVO v5.3: Escape de caracteres especiales universal"""
        content = self.original_content
        
        # Solo escapar caracteres realmente problemáticos universalmente
        critical_chars = ['$`', '$(', '!', '&&', '||']
        
        for chars in critical_chars:
            if chars in content:
                # Para casos críticos, usar temp file
                return f'@TEMP_FILE:{self._create_temp_file()}'
        
        # Para otros casos, escape selectivo universal
        safe_chars = ['`']  # Solo backticks simples
        for char in safe_chars:
            if char in content:
                content = content.replace(char, f'\\{char}')
        
        return content
    
    def _create_temp_file(self) -> str:
        """Crear archivo temporal con el contenido"""
        processed_content = self._process_multiline_content_v3()
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tmp', encoding='utf-8') as f:
            f.write(processed_content)
            return f.name
