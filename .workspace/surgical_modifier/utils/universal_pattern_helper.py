"""
Universal Pattern Helper - Funciones universales para patrones de código.

Este módulo proporciona funciones universales para manejar patrones de búsqueda,
reemplazo y migración exacta de código, compatible con el sistema BaseOperation.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path


class UniversalPatternHelper:
    """
   Helper universal para manejo de patrones de código.
   
   Proporciona funciones para detección, migración y validación de patrones
   de código de manera universal y compatible con BaseOperation.
    """
   
    def __init__(self):
       """Inicializa el helper universal de patrones."""
       self.logger = logging.getLogger(__name__)
       self.pattern_cache = {}
       self.migration_history = []

    def _get_sqlalchemy_patterns(self) -> Dict[str, str]:
        """
        Retorna patrones regex específicos para SQLAlchemy.

        Returns:
            Dict[str, str]: Diccionario con patrones SQLAlchemy organizados por tipo
        """
        return {
            'Column': r'(\w+)\s*=\s*db\.Column\((.*?)\)',
            'relationship': r'(\w+)\s*=\s*db\.relationship\([\'"](.*?)[\'"].*?\)',
            'ForeignKey': r'db\.ForeignKey\([\'"](.*?)[\'"].*?\)',
            'Table': r'(\w+)\s*=\s*Table\([\'"](.*?)[\'"].*?\)'
        }

    def _get_pytest_patterns(self) -> Dict[str, str]:
        """
        Retorna patrones regex específicos para pytest.

        Returns:
            Dict[str, str]: Diccionario con patrones pytest organizados por tipo
        """
        return {
            'test_functions': r'def\s+(test_\w+)\s*\(',
            'fixtures': r'@pytest\.fixture\s*(?:\([^)]*\))?\s*def\s+(\w+)',
            'decorators': r'@pytest\.(mark\.\w+|parametrize|fixture)',
            'assertions': r'assert\s+([^#]+)',
            'markers': r'@pytest\.mark\.(\w+)',
            'parametrize': r'@pytest\.parametrize\s*\(\s*["\'](.*?)["\']\s*,\s*(.*?)\)'
        }
   
    def detect_code_patterns(self, content: str) -> Dict[str, List[str]]:
       """
       Detecta patrones de código comunes en el contenido.
       
       Args:
           content: Contenido de código a analizar
           
       Returns:
           Diccionario con patrones encontrados por categoría
       """
       try:
           patterns = {
               'functions': [],
               'classes': [],
               'imports': [],
               'variables': []
           }
           
           # Detectar funciones
           func_pattern = r'def\s+(\w+)\s*\('
           patterns['functions'] = re.findall(func_pattern, content)
           
           # Detectar clases
           class_pattern = r'class\s+(\w+).*:'
           patterns['classes'] = re.findall(class_pattern, content)
           
           # Detectar imports
           import_pattern = r'(?:from\s+\S+\s+)?import\s+([^\n]+)'
           patterns['imports'] = re.findall(import_pattern, content)
           
           return patterns
           
       except Exception as e:
           self.logger.error(f"Error detectando patrones: {e}")
           return {}

    def detect_sqlalchemy_patterns(self, content: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detecta patrones SQLAlchemy en código Python.

        Args:
            content (str): Código Python a analizar

        Returns:
            Dict[str, List[Dict[str, Any]]]: Patrones SQLAlchemy encontrados por tipo
        """
        try:
            patterns = self._get_sqlalchemy_patterns()
            results = {}

            for pattern_type, regex_pattern in patterns.items():
                matches = self.find_regex_patterns(content, regex_pattern)
                if matches:
                    results[pattern_type] = matches
                    self.logger.info(f"Detectados {len(matches)} patrones {pattern_type}")

            return results
        except Exception as e:
            self.logger.error(f"Error detectando patrones SQLAlchemy: {e}")
            return {}

    def detect_pytest_patterns(self, content: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detecta patrones pytest en código Python.

        Args:
            content (str): Código Python a analizar

        Returns:
            Dict[str, List[Dict[str, Any]]]: Patrones pytest encontrados por tipo
        """
        try:
            patterns = self._get_pytest_patterns()
            results = {}

            for pattern_type, regex_pattern in patterns.items():
                matches = self.find_regex_patterns(content, regex_pattern)
                if matches:
                    results[pattern_type] = matches
                    self.logger.info(f"Detectados {len(matches)} patrones pytest {pattern_type}")

            return results
        except Exception as e:
            self.logger.error(f"Error detectando patrones pytest: {e}")
            return {}
        
    def migrate_sqlalchemy_patterns(self, old_content: str, new_patterns: dict) -> Optional[str]:
        """
        Migra patrones SQLAlchemy específicos manteniendo estructura y relaciones.
        
        Args:
            old_content (str): Código original con patrones SQLAlchemy
            new_patterns (dict): Diccionario con migraciones específicas por tipo
                                Formato: {'Column': {'old': 'pattern', 'new': 'replacement'}}
        
        Returns:
            Optional[str]: Código migrado o None si hay error
        """
        try:
            migrated_content = old_content
            migration_applied = False
            
            # Obtener patrones SQLAlchemy disponibles
            sqlalchemy_patterns = self._get_sqlalchemy_patterns()
            
            # Procesar cada tipo de patrón solicitado
            for pattern_type, migration_rules in new_patterns.items():
                if pattern_type not in sqlalchemy_patterns:
                    self.logger.warning(f"Tipo de patrón SQLAlchemy no soportado: {pattern_type}")
                    continue
                
                # Aplicar migración usando migrate_exact_pattern para cada regla
                if isinstance(migration_rules, dict) and 'old' in migration_rules and 'new' in migration_rules:
                    old_pattern = migration_rules['old']
                    new_pattern = migration_rules['new']
                    
                    # Usar migrate_exact_pattern interno
                    result = self.migrate_exact_pattern(old_pattern, new_pattern, migrated_content)
                    if result and result != migrated_content:
                        migrated_content = result
                        migration_applied = True
                        self.logger.info(f"Migración SQLAlchemy {pattern_type}: {old_pattern} → {new_pattern}")
            
            # Validar migración si se aplicaron cambios
            if migration_applied:
                if self.validate_migration(old_content, migrated_content):
                    # Registrar en historial
                    self.migration_history.append({
                        'type': 'sqlalchemy_patterns',
                        'patterns': new_patterns,
                        'success': True,
                        'original_length': len(old_content),
                        'migrated_length': len(migrated_content)
                    })
                    return migrated_content
                else:
                    self.logger.error("Validación de migración SQLAlchemy falló")
                    return None
            
            return migrated_content
            
        except Exception as e:
            self.logger.error(f"Error migrando patrones SQLAlchemy: {e}")
            return None
    
    def migrate_pytest_patterns(self, old_content: str, new_patterns: dict) -> Optional[str]:
        """
        Migra patrones pytest específicos manteniendo estructura y funcionalidad.
        
        Args:
            old_content (str): Código original con patrones pytest
            new_patterns (dict): Diccionario con migraciones específicas por tipo
                                Formato: {'assertions': {'old': 'self.assertEqual', 'new': 'assert'}}
        
        Returns:
            Optional[str]: Código migrado o None si hay error
        """
        try:
            migrated_content = old_content
            migration_applied = False
            
            # Obtener patrones pytest disponibles
            pytest_patterns = self._get_pytest_patterns()
            
            # Procesar cada tipo de patrón solicitado
            for pattern_type, migration_rules in new_patterns.items():
                if pattern_type not in pytest_patterns:
                    self.logger.warning(f"Tipo de patrón pytest no soportado: {pattern_type}")
                    continue
                
                # Aplicar migración usando migrate_exact_pattern para cada regla
                if isinstance(migration_rules, dict) and 'old' in migration_rules and 'new' in migration_rules:
                    old_pattern = migration_rules['old']
                    new_pattern = migration_rules['new']
                    
                    # Usar migrate_exact_pattern interno
                    result = self.migrate_exact_pattern(old_pattern, new_pattern, migrated_content)
                    if result and result != migrated_content:
                        migrated_content = result
                        migration_applied = True
                        self.logger.info(f"Migración pytest {pattern_type}: {old_pattern} → {new_pattern}")
            
            # Validar migración si se aplicaron cambios
            if migration_applied:
                if self.validate_migration(old_content, migrated_content):
                    # Registrar en historial
                    self.migration_history.append({
                        'type': 'pytest_patterns',
                        'patterns': new_patterns,
                        'success': True,
                        'original_length': len(old_content),
                        'migrated_length': len(migrated_content)
                    })
                    return migrated_content
                else:
                    self.logger.error("Validación de migración pytest falló")
                    return None
            
            return migrated_content
            
        except Exception as e:
            self.logger.error(f"Error migrando patrones pytest: {e}")
            return None
    
    def find_exact_matches(self, content: str, pattern: str) -> List[Tuple[int, str]]:
       """
       Encuentra coincidencias exactas del patrón en el contenido.
       
       Args:
           content: Contenido donde buscar
           pattern: Patrón a buscar (texto exacto)
           
       Returns:
           Lista de tuplas (línea, contenido_línea) con coincidencias
       """
       try:
           matches = []
           lines = content.split('\n')
           
           for i, line in enumerate(lines):
               if pattern in line:
                   matches.append((i + 1, line.strip()))
           
           return matches
           
       except Exception as e:
           self.logger.error(f"Error en búsqueda exacta: {e}")
           return []

    def find_regex_patterns(self, content: str, regex_pattern: str) -> List[Dict[str, Any]]:
       """
       Busca patrones usando expresiones regulares.
       
       Args:
           content: Contenido donde buscar
           regex_pattern: Patrón de expresión regular
           
       Returns:
           Lista de diccionarios con información de coincidencias
       """
       try:
           matches = []
           compiled_pattern = re.compile(regex_pattern)
           
           for match in compiled_pattern.finditer(content):
               match_info = {
                   'text': match.group(),
                   'start': match.start(),
                   'end': match.end(),
                   'groups': match.groups()
               }
               matches.append(match_info)
           
           return matches
           
       except Exception as e:
           self.logger.error(f"Error en búsqueda regex: {e}")
           return []

    def validate_pattern_syntax(self, pattern: str, pattern_type: str = 'regex') -> bool:
       """
       Valida la sintaxis de un patrón.
       
       Args:
           pattern: Patrón a validar
           pattern_type: Tipo de patrón ('regex' o 'exact')
           
       Returns:
           True si el patrón es válido, False en caso contrario
       """
       try:
           if pattern_type == 'regex':
               re.compile(pattern)
           return True
           
       except re.error:
           return False
       except Exception as e:
           self.logger.error(f"Error validando patrón: {e}")
           return False

    def migrate_exact_pattern(self, old_pattern: str, new_pattern: str, content: str) -> Optional[str]:
       """
       Migra un patrón exacto a otro manteniendo el formato.
       
       Args:
           old_pattern: Patrón original a reemplazar
           new_pattern: Nuevo patrón de reemplazo
           content: Contenido donde realizar la migración
           
       Returns:
           Contenido modificado o None si falla
       """
       try:
           if old_pattern not in content:
               self.logger.warning(f"Patrón '{old_pattern}' no encontrado")
               return content
               
           # Preservar el formato original
           migrated_content = content.replace(old_pattern, new_pattern)
           
           # Registrar migración
           self.migration_history.append({
               'old': old_pattern,
               'new': new_pattern,
               'timestamp': str(Path(__file__).stat().st_mtime)
           })
           
           return migrated_content
           
       except Exception as e:
           self.logger.error(f"Error en migración: {e}")
           return None

    def preserve_formatting(self, original_line: str, new_content: str) -> str:
       """
       Preserva el formato (indentación, espacios) del original.
       
       Args:
           original_line: Línea original con formato
           new_content: Nuevo contenido a formatear
           
       Returns:
           Nuevo contenido con formato preservado
       """
       try:
           # Extraer indentación
           indent_match = re.match(r'^(\s*)', original_line)
           indent = indent_match.group(1) if indent_match else ''
           
           # Aplicar indentación al nuevo contenido
           return indent + new_content.strip()
           
       except Exception as e:
           self.logger.error(f"Error preservando formato: {e}")
           return new_content

    def validate_migration(self, original: str, migrated: str) -> bool:
       """
       Valida que la migración fue exitosa.
       
       Args:
           original: Contenido original
           migrated: Contenido migrado
           
       Returns:
           True si la migración es válida
       """
       try:
           # Verificar que hay cambios
           if original == migrated:
               return False
               
           # Verificar integridad básica
           original_lines = len(original.split('\n'))
           migrated_lines = len(migrated.split('\n'))
           
           # Permitir diferencia mínima en líneas
           return abs(original_lines - migrated_lines) <= 2
           
       except Exception as e:
           self.logger.error(f"Error validando migración: {e}")
           return False

    def rollback_migration(self, content: str, steps: int = 1) -> str:
       """
       Revierte migraciones previas.
       
       Args:
           content: Contenido actual
           steps: Número de pasos a revertir
           
       Returns:
           Contenido con migraciones revertidas
       """
       try:
           if not self.migration_history:
               return content
               
           rollback_content = content
           
           # Revertir los últimos 'steps' cambios
           for _ in range(min(steps, len(self.migration_history))):
               last_migration = self.migration_history.pop()
               rollback_content = rollback_content.replace(
                   last_migration['new'], 
                   last_migration['old']
               )
           
           return rollback_content
           
       except Exception as e:
           self.logger.error(f"Error en rollback: {e}")
           return content

    def get_operation_compatible_patterns(self) -> Dict[str, Any]:
       """
       Obtiene patrones compatibles con el sistema BaseOperation.
       
       Returns:
           Diccionario con configuraciones compatibles
       """
       try:
           return {
               'supported_operations': ['detect', 'migrate', 'validate', 'rollback', 'detect_sqlalchemy', 'migrate_sqlalchemy', 'detect_pytest', 'migrate_pytest'],
               'pattern_types': ['exact', 'regex', 'code_patterns'],
               'migration_modes': ['exact', 'preserve_format', 'with_validation'],
               'cache_enabled': bool(self.pattern_cache),
               'history_length': len(self.migration_history)
           }
       except Exception as e:
           self.logger.error(f"Error obteniendo patrones compatibles: {e}")
           return {}