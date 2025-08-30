"""
Comby Engine - Wrapper para herramienta comby de búsqueda estructural.
Proporciona capacidades avanzadas de búsqueda y reemplazo estructural de código.
"""
import subprocess
import shutil
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from .base_engine import BaseEngine, register_engine, EngineCapability, EngineResult, EngineMatch, EngineStatus

"""
Comby Engine - Motor de búsqueda y reemplazo estructural

DESCRIPCIÓN:
Este motor proporciona capacidades avanzadas de búsqueda y reemplazo estructural
utilizando la herramienta comby. Comby entiende la estructura sintáctica de diferentes
lenguajes de programación, permitiendo patrones más precisos que regex tradicional.

CAPACIDADES:
- STRUCTURAL_SEARCH: Búsqueda basada en estructura de código, no solo texto
- AST_AWARE: Comprende la sintaxis específica del lenguaje
- LANGUAGE_SPECIFIC: Soporte optimizado para múltiples lenguajes

LENGUAJES SOPORTADOS:
Python, JavaScript, TypeScript, Java, C, C++, Go, Rust, PHP, Ruby, 
Scala, Clojure, Bash y más.

SINTAXIS COMBY:
- :[hole] - Coincide con cualquier expresión
- :[var] - Coincide con identificadores
- :[type] - Coincide con tipos
- ... - Coincide con secuencias

EJEMPLOS DE PATRONES:
- "function :[name](:[args]) { :[body] }" - Función JavaScript
- "def :[name](:[args]): :[body]" - Función Python  
- "class :[name] { :[body] }" - Clase genérica

MANEJO DE ERRORES:
- NOT_SUPPORTED: Cuando comby no está instalado
- ERROR: Errores de ejecución o sintaxis
- TIMEOUT: Operaciones que exceden 30 segundos
- NO_MATCHES: Búsqueda sin resultados

DEPENDENCIAS:
Requiere herramienta 'comby' instalada en el sistema.
Instalación: https://comby.dev/docs/get-started

EJEMPLOS DE USO:
```python
engine = CombyEngine()
result = engine.search("def :[name](:[args]):", python_code, language="python")
replacement = engine.replace("print(:[x])", "logger.info(:[x])", code, language="python")
```
"""

@register_engine("comby")
class CombyEngine(BaseEngine):
    """
    Engine que encapsula la herramienta comby para búsqueda y reemplazo estructural.
    
    Comby es una herramienta que permite realizar búsquedas y reemplazos estructurales
    en código, entendiendo la sintaxis específica de cada lenguaje de programación.
    """
    
    def __init__(self, name: str = "comby", version: str = "1.0.0"):
        super().__init__(name, version)
        # Definir capacidades del motor comby
        self._capabilities = {
            EngineCapability.STRUCTURAL_SEARCH,
            EngineCapability.AST_AWARE,
            EngineCapability.LANGUAGE_SPECIFIC
        }
        # Soporta múltiples lenguajes específicos
        self._supported_languages = {
            'python', 'javascript', 'java', 'c', 'cpp', 'go', 'rust',
            'typescript', 'php', 'ruby', 'scala', 'clojure', 'bash'
        }
        # Verificar si comby está disponible
        self._comby_available = self._check_comby_availability()
        
    def _check_comby_availability(self) -> bool:
        """
        Verifica si la herramienta comby está instalada y disponible.
        
        Returns:
            bool: True si comby está disponible, False en caso contrario
        """
        return shutil.which("comby") is not None
        
    def _search_impl(self, pattern: str, content: str, **kwargs) -> EngineResult:
        """
        Realiza búsqueda estructural usando comby.
        
        Args:
            pattern: Patrón de búsqueda en sintaxis comby
            content: Contenido donde buscar
            **kwargs: Argumentos adicionales (language, etc.)
            
        Returns:
            EngineResult: Resultado de la búsqueda con matches encontrados
        """
        if not self._comby_available:
            return EngineResult(
                matches=[],
                status=EngineStatus.NOT_SUPPORTED,
                error_message="Comby no está instalado en el sistema"
            )
            
        try:
            # Preparar comando comby
            cmd = ["comby", pattern, "", "-stdin", "-json-lines"]
            
            # Agregar lenguaje si se especifica
            if "language" in kwargs:
                cmd.extend(["-matcher", kwargs["language"]])
                
            # Ejecutar comby con subprocess
            result = subprocess.run(
                cmd,
                input=content,
                text=True,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return EngineResult(
                    matches=[],
                    status=EngineStatus.ERROR,
                    error_message=f"Comby error: {result.stderr}"
                )
                
            # Parsear output JSON de comby
            matches = []
            if result.stdout.strip():
                import json
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            match_data = json.loads(line)
                            match = EngineMatch(
                                text=match_data.get('matched', ''),
                                start_pos=match_data.get('range', {}).get('start', {}).get('offset', 0),
                                end_pos=match_data.get('range', {}).get('end', {}).get('offset', 0),
                                line_number=match_data.get('range', {}).get('start', {}).get('line', 1),
                                metadata={
                                    'environment': match_data.get('environment', {}),
                                    'file': match_data.get('uri', '')
                                }
                            )
                            matches.append(match)
                        except json.JSONDecodeError:
                            continue
                            
            return EngineResult(
                matches=matches,
                status=EngineStatus.SUCCESS if matches else EngineStatus.NO_MATCHES,
                modified_content=None
            )
            
        except subprocess.TimeoutExpired:
            return EngineResult(
                matches=[],
                status=EngineStatus.ERROR,
                error_message="Comby search timeout (30s)"
            )
        except Exception as e:
            return EngineResult(
                matches=[],
                status=EngineStatus.ERROR,
                error_message=f"Error ejecutando comby: {str(e)}"
            )
        
    def _replace_impl(self, pattern: str, replacement: str, content: str, **kwargs) -> EngineResult:
        """
        Realiza reemplazo estructural usando comby.
        
        Args:
            pattern: Patrón a buscar en sintaxis comby
            replacement: Texto de reemplazo
            content: Contenido donde realizar el reemplazo
            **kwargs: Argumentos adicionales (language, etc.)
            
        Returns:
            EngineResult: Resultado del reemplazo con contenido modificado
        """
        if not self._comby_available:
            return EngineResult(
                matches=[],
                status=EngineStatus.NOT_SUPPORTED,
                error_message="Comby no está instalado en el sistema"
            )
            
        try:
            # Crear backup antes de operación destructiva
            file_path = kwargs.get('file_path', 'unknown_file')
            if file_path != 'unknown_file':
                self._create_backup_before_operation(file_path, 'replace')
                
            # Preparar comando comby para reemplazo
            cmd = ["comby", pattern, replacement, "-stdin", "-json-lines"]
            
            # Agregar lenguaje si se especifica
            if "language" in kwargs:
                cmd.extend(["-matcher", kwargs["language"]])
                
            # Ejecutar comby con subprocess
            result = subprocess.run(
                cmd,
                input=content,
                text=True,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return EngineResult(
                    matches=[],
                    status=EngineStatus.ERROR,
                    error_message=f"Comby replace error: {result.stderr}"
                )
                
            # Parsear output y obtener contenido modificado
            matches = []
            modified_content = content  # Por defecto, contenido original
            
            if result.stdout.strip():
                import json
                lines = result.stdout.strip().split('\n')
                
                # La primera línea contiene el contenido modificado (sin -json-lines)
                # Vamos a ejecutar sin -json-lines para obtener solo contenido
                cmd_content = ["comby", pattern, replacement, "-stdin"]
                if "language" in kwargs:
                    cmd_content.extend(["-matcher", kwargs["language"]])
                    
                content_result = subprocess.run(
                    cmd_content,
                    input=content,
                    text=True,
                    capture_output=True,
                    timeout=30
                )
                
                if content_result.returncode == 0:
                    modified_content = content_result.stdout
                    
                    # Crear matches para mostrar cambios
                    if modified_content != content:
                        matches.append(EngineMatch(
                            text=pattern,
                            start_pos=0,
                            end_pos=len(content),
                            line_number=1,
                            metadata={
                                'operation': 'replace',
                                'pattern': pattern,
                                'replacement': replacement,
                                'backup_created': file_path != 'unknown_file'
                            }
                        ))
                        
            return EngineResult(
                matches=matches,
                status=EngineStatus.SUCCESS if matches else EngineStatus.NO_MATCHES,
                modified_content=modified_content,
                metadata={
                    'engine': self.name,
                    'backup_created': file_path != 'unknown_file'
                }
            )
            
        except subprocess.TimeoutExpired:
            return EngineResult(
                matches=[],
                status=EngineStatus.ERROR,
                error_message="Comby replace timeout (30s)"
            )
        except Exception as e:
            return EngineResult(
                matches=[],
                status=EngineStatus.ERROR,
                error_message=f"Error ejecutando comby replace: {str(e)}"
            )