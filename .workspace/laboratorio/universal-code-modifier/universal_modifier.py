#!/usr/bin/env python3
"""
Universal Code Modifier
Una herramienta para modificar código de forma universal y segura.
Permite aplicar transformaciones y modificaciones a diferentes tipos de archivos de código.

Author: Laboratorio de Desarrollo
Version: 0.1.0

Sistema de Logging Avanzado:
---------------------------
- LoggerManager centralizado para configuración profesional
- Soporte para handlers múltiples: consola, archivo, rotating
- Logging contextual con información de operaciones
- Performance timing automático
- Configuración dinámica de niveles y formatos
"""

import ast
import logging
import os
import sys
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Union

# ============================================================================
# CONSTANTES Y CONFIGURACIONES GLOBALES
# ============================================================================

# Información del proyecto
PROJECT_NAME = "Universal Code Modifier"
VERSION = "0.1.3"
AUTHOR = "Laboratorio de Desarrollo"

# ============================================================================
# CONFIGURACIONES DE ARCHIVOS Y EXTENSIONES
# ============================================================================

# Extensiones de archivos soportadas por defecto
DEFAULT_SUPPORTED_EXTENSIONS = [
    ".py",  # Python
    ".js",  # JavaScript
    ".ts",  # TypeScript
    ".java",  # Java
    ".cpp",  # C++
    ".c",  # C
    ".cs",  # C#
    ".go",  # Go
    ".rs",  # Rust
    ".php",  # PHP
    ".rb",  # Ruby
    ".swift",  # Swift
    ".kt",  # Kotlin
]

# Mapeo de extensiones a lenguajes
EXTENSION_TO_LANGUAGE = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby",
    ".swift": "Swift",
    ".kt": "Kotlin",
}

# ============================================================================
# CONFIGURACIONES DE DIRECTORIO Y EXCLUSIONES
# ============================================================================

# Directorios excluidos por defecto
DEFAULT_EXCLUDED_DIRS = {
    ".git",  # Control de versiones Git
    "__pycache__",  # Cache de Python
    "node_modules",  # Dependencias de Node.js
    ".venv",  # Entorno virtual Python
    "venv",  # Entorno virtual Python alternativo
    ".idea",  # Archivos de IntelliJ IDEA
    ".vscode",  # Archivos de Visual Studio Code
    "build",  # Directorio de build
    "dist",  # Directorio de distribución
    "target",  # Directorio target (Java/Maven)
    ".next",  # Archivos de Next.js
    ".nuxt",  # Archivos de Nuxt.js
}

# ============================================================================
# CONFIGURACIONES DE ENCODING Y ARCHIVOS
# ============================================================================

# Encodings a probar para leer archivos
SUPPORTED_ENCODINGS = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]

# Encoding por defecto para nuevos archivos
DEFAULT_FILE_ENCODING = "utf-8"

# ============================================================================
# CONFIGURACIONES DE TAMAÑO Y LÍMITES
# ============================================================================

# Factores de conversión
BYTES_PER_KB = 1024
BYTES_PER_MB = 1024 * 1024
BYTES_PER_GB = 1024 * 1024 * 1024

# Tamaños por defecto
DEFAULT_MAX_FILE_SIZE_MB = 10
DEFAULT_MAX_FILE_SIZE_BYTES = DEFAULT_MAX_FILE_SIZE_MB * BYTES_PER_MB

# Límites de seguridad
MAX_ALLOWED_FILE_SIZE_MB = 100
MIN_ALLOWED_FILE_SIZE_MB = 1

# ============================================================================
# CONFIGURACIONES DE LOGGING
# ============================================================================

# Niveles de logging válidos
VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

# Nivel de logging por defecto
DEFAULT_LOG_LEVEL = "INFO"

# Formato de logging por defecto
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class LoggerManager:
    """Gestor centralizado para configuración de logging del Universal Code Modifier"""

    def __init__(
        self,
        name: str = None,
        level: str = DEFAULT_LOG_LEVEL,
        format_str: str = DEFAULT_LOG_FORMAT,
    ):
        self.name = name or __name__
        self.level = getattr(logging, level.upper())
        self.format_str = format_str
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.level)
        self.formatters = {}
        self.handlers = {}

    def create_formatter(self, format_str: str = None) -> logging.Formatter:
        """Crea formatter con formato especificado o por defecto"""
        fmt = format_str or self.format_str
        if fmt not in self.formatters:
            self.formatters[fmt] = logging.Formatter(fmt)
        return self.formatters[fmt]

    def setup_console_handler(
        self, level: str = None, format_str: str = None
    ) -> logging.StreamHandler:
        """Configura handler de consola"""
        handler_key = "console"
        if handler_key not in self.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(getattr(logging, (level or DEFAULT_LOG_LEVEL).upper()))
            handler.setFormatter(self.create_formatter(format_str))
            self.logger.addHandler(handler)
            self.handlers[handler_key] = handler
        return self.handlers[handler_key]

    def setup_file_handler(
        self, filename: str, level: str = None, format_str: str = None
    ) -> logging.FileHandler:
        """Configura handler de archivo"""
        handler_key = f"file_{filename}"
        if handler_key not in self.handlers:
            handler = logging.FileHandler(filename)
            handler.setLevel(getattr(logging, (level or DEFAULT_LOG_LEVEL).upper()))
            handler.setFormatter(self.create_formatter(format_str))
            self.logger.addHandler(handler)
            self.handlers[handler_key] = handler
        return self.handlers[handler_key]

    def log_operation_start(self, operation: str, context: dict = None):
        """Log inicio de operación con contexto"""
        ctx_str = f" | Contexto: {context}" if context else ""
        self.logger.info(f"🔄 INICIANDO: {operation}{ctx_str}")

    def log_operation_end(
        self, operation: str, success: bool = True, context: dict = None
    ):
        """Log fin de operación con resultado"""
        status = "✅ COMPLETADO" if success else "❌ FALLÓ"
        ctx_str = f" | Contexto: {context}" if context else ""
        self.logger.info(f"{status}: {operation}{ctx_str}")

    def log_performance(self, operation: str, duration: float, context: dict = None):
        """Log información de performance"""
        ctx_str = f" | Contexto: {context}" if context else ""
        self.logger.info(
            f"⏱️ PERFORMANCE: {operation} ejecutado en {duration:.3f}s{ctx_str}"
        )

    def log_error_with_context(
        self, operation: str, error: Exception, context: dict = None
    ):
        """Log error con contexto completo"""
        ctx_str = f" | Contexto: {context}" if context else ""
        self.logger.error(
            f"🚨 ERROR en {operation}: {str(error)}{ctx_str}", exc_info=True
        )


# ============================================================================
# CONFIGURACIONES DE BACKUP Y SEGURIDAD
# ============================================================================

# Sufijo para archivos de backup
BACKUP_SUFFIX = ".backup"

# Configuraciones por defecto de seguridad
DEFAULT_BACKUP_ENABLED = True


class BackupManager:
    """Gestor automático de backups con timestamp, rotación y limpieza"""

    def __init__(
        self,
        backup_dir: Path = None,
        max_backups_per_file: int = 5,
        max_total_size_mb: float = 100,
    ):
        self.backup_dir = backup_dir
        self.max_backups_per_file = max_backups_per_file
        self.max_total_size_mb = max_total_size_mb
        self.logger = logging.getLogger(f"{__name__}.BackupManager")

    def create_timestamped_backup(self, file_path: Union[str, Path]) -> Optional[Path]:
        """Crea backup con timestamp automático"""
        from datetime import datetime

        file_path = Path(file_path)
        if not file_path.exists():
            self.logger.warning(f"Archivo no existe para backup: {file_path}")
            return None

        # Generar timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.backup_{timestamp}"

        # Determinar directorio de backup
        if self.backup_dir:
            backup_path = self.backup_dir / backup_name
        else:
            backup_path = file_path.parent / backup_name

        try:
            import shutil

            shutil.copy2(file_path, backup_path)
            self.logger.info(f"✅ Backup creado: {backup_path}")

            # Ejecutar rotación automática
            self._rotate_backups(file_path)

            return backup_path
        except Exception as e:
            self.logger.error(f"❌ Error creando backup: {e}")
            return None

    def list_backups_for_file(self, file_path: Union[str, Path]) -> list:
        """Lista todos los backups de un archivo específico"""
        file_path = Path(file_path)
        pattern = f"{file_path.name}.backup_*"

        if self.backup_dir:
            search_dir = self.backup_dir
        else:
            search_dir = file_path.parent

        import glob

        backups = list(search_dir.glob(pattern))
        return sorted(backups, key=lambda x: x.stat().st_mtime, reverse=True)

    def _rotate_backups(self, file_path: Union[str, Path]):
        """Rota backups manteniendo solo max_backups_per_file"""
        backups = self.list_backups_for_file(file_path)

        if len(backups) > self.max_backups_per_file:
            # Eliminar backups más antiguos
            for old_backup in backups[self.max_backups_per_file :]:
                try:
                    old_backup.unlink()
                    self.logger.info(f"🗑️ Backup antiguo eliminado: {old_backup.name}")
                except Exception as e:
                    self.logger.error(f"Error eliminando backup: {e}")

    def calculate_total_backup_size(self) -> int:
        """Calcula tamaño total de todos los backups en bytes"""
        total_size = 0

        search_dirs = [self.backup_dir] if self.backup_dir else []

        # Si no hay directorio específico, buscar en directorios comunes
        if not search_dirs:
            import os

            current_dir = Path(".")
            search_dirs = [current_dir]

        for search_dir in search_dirs:
            if search_dir and search_dir.exists():
                for backup_file in search_dir.glob("*.backup_*"):
                    total_size += backup_file.stat().st_size

        return total_size

    def cleanup_by_size_limit(self):
        """Limpia backups si exceden el límite de tamaño total"""
        if self.max_total_size_mb <= 0:
            return

        max_size_bytes = self.max_total_size_mb * 1024 * 1024
        current_size = self.calculate_total_backup_size()

        if current_size > max_size_bytes:
            self.logger.info(
                f"🧹 Tamaño de backups ({current_size/1024/1024:.1f}MB) excede límite ({self.max_total_size_mb}MB)"
            )

            # Obtener todos los backups ordenados por fecha (más antiguos primero)
            all_backups = []
            search_dirs = [self.backup_dir] if self.backup_dir else [Path(".")]

            for search_dir in search_dirs:
                if search_dir and search_dir.exists():
                    for backup_file in search_dir.glob("*.backup_*"):
                        all_backups.append(backup_file)

            # Ordenar por fecha de modificación (más antiguos primero)
            all_backups.sort(key=lambda x: x.stat().st_mtime)

            # Eliminar backups antiguos hasta estar bajo el límite
            for backup_file in all_backups:
                if self.calculate_total_backup_size() <= max_size_bytes:
                    break
                try:
                    backup_file.unlink()
                    self.logger.info(
                        f"🗑️ Backup eliminado por límite de tamaño: {backup_file.name}"
                    )
                except Exception as e:
                    self.logger.error(f"Error eliminando backup por tamaño: {e}")


DEFAULT_DRY_RUN_MODE = False
DEFAULT_VALIDATE_SYNTAX = True

# ============================================================================
# CONFIGURACIONES DE COMENTARIOS POR LENGUAJE
# ============================================================================

# Prefijos de comentarios de línea por lenguaje
SINGLE_LINE_COMMENT_PREFIXES = {
    "Python": "#",
    "JavaScript": "//",
    "TypeScript": "//",
    "Java": "//",
    "C++": "//",
    "C": "//",
    "C#": "//",
    "Go": "//",
    "Rust": "//",
    "PHP": "//",
    "Swift": "//",
    "Kotlin": "//",
}

# Delimitadores de comentarios multilínea
MULTI_LINE_COMMENT_DELIMITERS = {
    "Python": ('"""', '"""'),
    "JavaScript": ("/*", "*/"),
    "TypeScript": ("/*", "*/"),
    "Java": ("/*", "*/"),
    "C++": ("/*", "*/"),
    "C": ("/*", "*/"),
    "C#": ("/*", "*/"),
    "Go": ("/*", "*/"),
    "Rust": ("/*", "*/"),
    "PHP": ("/*", "*/"),
    "Swift": ("/*", "*/"),
    "Kotlin": ("/*", "*/"),
}

# ============================================================================
# CONFIGURACIONES POR DEFECTO PARA LA CLASE
# ============================================================================

# Configuración por defecto completa
DEFAULT_CONFIG = {
    "backup_enabled": DEFAULT_BACKUP_ENABLED,
    "dry_run_mode": DEFAULT_DRY_RUN_MODE,
    "max_file_size_mb": DEFAULT_MAX_FILE_SIZE_MB,
    "file_encoding": DEFAULT_FILE_ENCODING,
    "validate_syntax": DEFAULT_VALIDATE_SYNTAX,
    "log_level": DEFAULT_LOG_LEVEL,
    "supported_extensions": DEFAULT_SUPPORTED_EXTENSIONS.copy(),
    "excluded_dirs": DEFAULT_EXCLUDED_DIRS.copy(),
}

# ============================================================================
# FIN DE CONSTANTES Y CONFIGURACIONES GLOBALES
# ============================================================================


class PatternValidator:
    """
    Validador de patrones y sintaxis para múltiples lenguajes de programación.
    Proporciona validación avanzada de código usando AST para Python y regex para otros lenguajes.
    """

    def __init__(self):
        """Inicializar el validador de patrones."""
        self.supported_languages = {
            "python": self._validate_python_syntax,
            "javascript": self._validate_javascript_syntax,
            "typescript": self._validate_typescript_syntax,
            "java": self._validate_generic_syntax,
            "c": self._validate_generic_syntax,
            "cpp": self._validate_generic_syntax,
        }
        self.rules_config = {
            "naming_convention": True,
            "max_line_length": 100,
            "max_function_name_length": 30,
            "detect_single_char_vars": True,
            "severity_levels": ["WARNING", "ERROR", "CRITICAL"],
        }

    def validate_syntax(self, file_path: str, language: str = None) -> bool:
        """
        Validar sintaxis del archivo usando el validador apropiado.
        Args:
            file_path: Ruta al archivo a validar
            language: Lenguaje del archivo (se detecta automáticamente si es None)
        Returns:
            bool: True si la sintaxis es válida, False en caso contrario
        """
        if language is None:
            language = self._detect_language(file_path)

        validator = self.supported_languages.get(language.lower())
        if not validator:
            return True  # Si no hay validador específico, asumimos válido

        try:
            return validator(file_path)
        except Exception:
            return False

    def validate_patterns(
        self, file_path: str, language: str = None
    ) -> Dict[str, List[str]]:
        """
        Validar patrones de código y convenciones.
        Args:
            file_path: Ruta al archivo a validar
            language: Lenguaje del archivo (se detecta automáticamente si es None)
        Returns:
            Dict: Diccionario con 'warnings' y 'errors' encontrados
        """
        if language is None:
            language = self._detect_language(file_path)

        issues = {"warnings": [], "errors": []}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if language == "python":
                issues = self._validate_python_patterns(content, file_path)
            elif language == "javascript":
                issues = self._validate_javascript_patterns(content, file_path)
            elif language == "typescript":
                issues = self._validate_typescript_patterns(content, file_path)

        except Exception as e:
            issues["errors"].append(
                f"Error leyendo archivo para validación de patrones: {e}"
            )

        return issues

    def is_pattern_unique(
        self,
        file_path: str,
        pattern: str,
        pattern_type: str = "regex",
        ignore_case: bool = False,
        ignore_comments: bool = True,
    ) -> tuple:
        """Verificar si un patrón específico aparece exactamente una vez en un archivo."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            count = 0
            if pattern_type == "string":
                count = content.count(pattern)
            elif pattern_type == "regex":
                import re

                matches = re.findall(pattern, content)
                count = len(matches)
            elif pattern_type == "function_name":
                import re

                language = self._detect_language(file_path)
                if language == "python":
                    func_pattern = f"def {re.escape(pattern)}\\s*\\("
                elif language in ["javascript", "typescript"]:
                    func_pattern = f"function {re.escape(pattern)}\\s*\\("
                else:
                    func_pattern = pattern
                matches = re.findall(func_pattern, content)
                count = len(matches)
            is_unique = count == 1
            return (is_unique, count)
        except Exception as e:
            return (False, 0)

    def configure_rules(self, rules_config: Dict[str, any]):
        """
        Configurar reglas de validación personalizadas.
        Args:
            rules_config: Diccionario con configuración de reglas
        """
        self.rules_config.update(rules_config)

    def get_validation_report(self) -> Dict[str, any]:
        """
        Generar reporte de configuración actual.
        Returns:
            Dict: Reporte completo de configuración y estado
        """
        return {
            "supported_languages": list(self.supported_languages.keys()),
            "rules_configured": bool(self.rules_config),
            "active_rules": self.rules_config,
            "validation_methods": ["syntax", "patterns"],
            "status": "operational",
            "version": "1.0.0",
        }

    def _detect_language(self, file_path: str) -> str:
        """Detectar lenguaje basado en la extensión del archivo."""
        extension = Path(file_path).suffix.lower()
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".cc": "cpp",
        }
        return extension_map.get(extension, "unknown")

    def _validate_python_syntax(self, file_path: str) -> bool:
        """Validar sintaxis Python usando AST."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            ast.parse(content)
            return True
        except (SyntaxError, UnicodeDecodeError):
            return False

    def _validate_javascript_syntax(self, file_path: str) -> bool:
        """Validar sintaxis JavaScript usando patrones básicos."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Verificar balanceado de llaves, paréntesis y corchetes
            brackets = {"(": ")", "{": "}", "[": "]"}
            stack = []
            for char in content:
                if char in brackets:
                    stack.append(char)
                elif char in brackets.values():
                    if not stack or brackets.get(stack.pop()) != char:
                        return False
            return len(stack) == 0
        except UnicodeDecodeError:
            return False

    def _validate_typescript_syntax(self, file_path: str) -> bool:
        """Validar sintaxis TypeScript (similar a JavaScript por ahora)."""
        return self._validate_javascript_syntax(file_path)

    def _validate_generic_syntax(self, file_path: str) -> bool:
        """Validador genérico para lenguajes tipo C."""
        return self._validate_javascript_syntax(file_path)  # Usar validación de llaves

    def _validate_python_patterns(
        self, content: str, file_path: str
    ) -> Dict[str, List[str]]:
        """Validar patrones específicos de Python."""
        issues = {"warnings": [], "errors": []}
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Detectar funciones con nombres muy largos
            if "def " in line and self.rules_config.get("naming_convention", True):
                func_match = line.split("def ")[1].split("(")[0].strip()
                if len(func_match) > self.rules_config.get(
                    "max_function_name_length", 30
                ):
                    issues["warnings"].append(
                        f"Línea {i}: Nombre de función muy largo: {func_match}"
                    )

            # Detectar variables con nombres poco descriptivos
            if (
                "=" in line
                and not line.strip().startswith("#")
                and self.rules_config.get("detect_single_char_vars", True)
            ):
                var_parts = line.split("=")[0].strip().split()
                if (
                    var_parts
                    and len(var_parts[-1]) == 1
                    and var_parts[-1] not in ["i", "j", "k", "x", "y", "z"]
                ):
                    issues["warnings"].append(
                        f"Línea {i}: Variable con nombre poco descriptivo: {var_parts[-1]}"
                    )

            # Detectar líneas muy largas
            max_length = self.rules_config.get("max_line_length", 100)
            if len(line) > max_length:
                issues["warnings"].append(
                    f"Línea {i}: Línea demasiado larga ({len(line)} caracteres)"
                )

            # Detectar imports no utilizados (básico)
            if line.strip().startswith("import ") and "import" in line:
                import_name = line.split("import ")[1].split()[0]
                if content.count(import_name) == 1:  # Solo aparece en el import
                    issues["warnings"].append(
                        f"Línea {i}: Posible import no utilizado: {import_name}"
                    )

        return issues

    def _validate_javascript_patterns(
        self, content: str, file_path: str
    ) -> Dict[str, List[str]]:
        """Validar patrones específicos de JavaScript."""
        issues = {"warnings": [], "errors": []}
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Detectar funciones con nombres muy largos
            if "function " in line and self.rules_config.get("naming_convention", True):
                func_match = line.split("function ")[1].split("(")[0].strip()
                if len(func_match) > self.rules_config.get(
                    "max_function_name_length", 30
                ):
                    issues["warnings"].append(
                        f"Línea {i}: Nombre de función muy largo: {func_match}"
                    )

            # Detectar uso de var en lugar de let/const
            if " var " in line:
                issues["warnings"].append(f"Línea {i}: Usar let/const en lugar de var")

            # Detectar líneas muy largas
            max_length = self.rules_config.get("max_line_length", 100)
            if len(line) > max_length:
                issues["warnings"].append(
                    f"Línea {i}: Línea demasiado larga ({len(line)} caracteres)"
                )

            # Detectar console.log en código de producción
            if "console.log" in line:
                issues["warnings"].append(
                    f"Línea {i}: console.log encontrado (remover en producción)"
                )

        return issues

    def _validate_typescript_patterns(
        self, content: str, file_path: str
    ) -> Dict[str, List[str]]:
        """Validar patrones específicos de TypeScript."""
        issues = self._validate_javascript_patterns(content, file_path)  # Hereda de JS
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Detectar uso de any type
            if ": any" in line or " any " in line:
                issues["warnings"].append(f'Línea {i}: Evitar el uso de tipo "any"')

            # Detectar interfaces sin usar
            if line.strip().startswith("interface "):
                interface_name = line.split("interface ")[1].split()[0]
                if content.count(interface_name) == 1:
                    issues["warnings"].append(
                        f"Línea {i}: Interface posiblemente no utilizada: {interface_name}"
                    )

        return issues


class UniversalCodeModifier:
    """
    Clase principal para modificaciones universales de código.

    Esta clase proporciona la funcionalidad base para modificar
    archivos de código de diferentes lenguajes de forma segura y controlada.
    """

    def __init__(
        self,
        base_path: Optional[str] = None,
        backup_enabled: bool = True,
        dry_run_mode: bool = False,
        max_file_size_mb: int = 10,
        custom_extensions: Optional[List[str]] = None,
        excluded_dirs: Optional[List[str]] = None,
        log_level: str = DEFAULT_LOG_LEVEL,
        backup_dir: Optional[str] = None,
        file_encoding: str = DEFAULT_FILE_ENCODING,
        validate_syntax: bool = True,
    ):
        """
        Inicializar el modificador universal de código con configuración avanzada.

        Args:
            base_path (str, optional): Ruta base para operaciones de archivos
            backup_enabled (bool): Si crear respaldos automáticamente (default: True)
            dry_run_mode (bool): Modo de prueba sin modificaciones reales (default: False)
            max_file_size_mb (int): Tamaño máximo de archivo en MB (default: 10)
            custom_extensions (List[str], optional): Extensiones personalizadas adicionales
            excluded_dirs (List[str], optional): Directorios a excluir del procesamiento
            log_level (str): Nivel de logging (DEBUG, INFO, WARNING, ERROR) (default: INFO)
            backup_dir (str, optional): Directorio específico para backups
            file_encoding (str): Encoding por defecto para archivos (default: utf-8)
            validate_syntax (bool): Si validar sintaxis antes de modificar (default: True)

        Raises:
            ValueError: Si los parámetros no son válidos
            FileNotFoundError: Si base_path no existe
            PermissionError: Si no hay permisos en el directorio base
        """
        # Validación y configuración de base_path
        if base_path:
            self.base_path = Path(base_path).resolve()
            if not self.base_path.exists():
                raise FileNotFoundError(
                    f"El directorio base no existe: {self.base_path}"
                )
            if not self.base_path.is_dir():
                raise ValueError(f"base_path debe ser un directorio: {self.base_path}")
            if not os.access(self.base_path, os.R_OK):
                raise PermissionError(f"Sin permisos de lectura en: {self.base_path}")
        else:
            self.base_path = Path.cwd()

        # Configuración de extensiones soportadas
        self.default_extensions = DEFAULT_SUPPORTED_EXTENSIONS.copy()
        if custom_extensions:
            # Validar formato de extensiones personalizadas
            validated_extensions = []
            for ext in custom_extensions:
                if not ext.startswith("."):
                    ext = "." + ext
                if len(ext) > 1 and ext.isascii():
                    validated_extensions.append(ext.lower())
                else:
                    self.logger.warning(f"Extensión inválida ignorada: {ext}")
            self.supported_extensions = list(
                set(self.default_extensions + validated_extensions)
            )
        else:
            self.supported_extensions = self.default_extensions.copy()

        # Configuración de directorios excluidos
        default_excluded = DEFAULT_EXCLUDED_DIRS.copy()
        if excluded_dirs:
            self.excluded_dirs = default_excluded.union(set(excluded_dirs))
        else:
            self.excluded_dirs = default_excluded

        # Configuración de tamaño máximo de archivo
        if max_file_size_mb <= 0:
            raise ValueError("max_file_size_mb debe ser mayor a 0")
        self.max_file_size = max_file_size_mb * BYTES_PER_MB  # Convertir a bytes

        # Configuración de backup
        self.backup_enabled = backup_enabled

        if backup_dir:
            self.backup_dir = Path(backup_dir)
            if not self.backup_dir.exists():
                self.backup_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.backup_dir = None

        # Inicializar BackupManager automático
        self.backup_manager = BackupManager(
            backup_dir=self.backup_dir, max_backups_per_file=5, max_total_size_mb=100
        )

        # Configuración de modo de operación
        self.dry_run_mode = dry_run_mode
        self.validate_syntax = validate_syntax
        # Inicializar validador de patrones
        self.pattern_validator = PatternValidator()
        self.file_encoding = file_encoding

        # Validar encoding
        try:
            "test".encode(file_encoding)
        except LookupError:
            raise ValueError(f"Encoding no válido: {file_encoding}")

        # Configuración de logging
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if log_level.upper() not in valid_log_levels:
            raise ValueError(f"log_level debe ser uno de: {valid_log_levels}")

        # Usar LoggerManager para configuración avanzada
        self.logger_manager = LoggerManager(
            f"{__name__}.{self.__class__.__name__}", log_level
        )
        self.logger = self.logger_manager.logger
        self.modification_count = 0
        self.files_processed = 0
        self.errors_count = 0
        self.start_time = None

        # Configuración adicional
        self.config = {
            "base_path": str(self.base_path),
            "backup_enabled": self.backup_enabled,
            "dry_run_mode": self.dry_run_mode,
            "max_file_size_mb": max_file_size_mb,
            "supported_extensions": self.supported_extensions,
            "excluded_dirs": list(self.excluded_dirs),
            "log_level": log_level.upper(),
            "file_encoding": self.file_encoding,
            "validate_syntax": self.validate_syntax,
        }

        # Log de inicialización
        self.logger.info(f"UniversalCodeModifier inicializado exitosamente")
        self.logger.info(f"Directorio base: {self.base_path}")
        self.logger.info(f"Modo dry-run: {self.dry_run_mode}")
        self.logger.info(f"Backup habilitado: {self.backup_enabled}")
        self.logger.info(
            f"Extensiones soportadas: {len(self.supported_extensions)} tipos"
        )
        self.logger.debug(f"Configuración completa: {self.config}")

    def get_config(self) -> Dict[str, any]:
        """
        Obtener la configuración actual del modificador.

        Returns:
            Dict: Configuración completa actual
        """
        current_config = self.config.copy()
        current_config.update(
            {
                "modification_count": self.modification_count,
                "files_processed": self.files_processed,
                "errors_count": self.errors_count,
                "uptime_seconds": self._get_uptime(),
            }
        )
        return current_config

    def update_config(self, **kwargs) -> bool:
        """
        Actualizar configuración en tiempo de ejecución.

        Args:
            **kwargs: Parámetros de configuración a actualizar

        Returns:
            bool: True si la actualización fue exitosa
        """
        valid_params = {
            "backup_enabled",
            "dry_run_mode",
            "max_file_size_mb",
            "log_level",
            "file_encoding",
            "validate_syntax",
        }

        updated = False
        for key, value in kwargs.items():
            if key not in valid_params:
                self.logger.warning(f"Parámetro de configuración inválido: {key}")
                continue

            try:
                if key == "max_file_size_mb":
                    if value <= 0:
                        raise ValueError("max_file_size_mb debe ser mayor a 0")
                    self.max_file_size = value * 1024 * 1024
                    self.config[key] = value
                elif key == "log_level":
                    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
                    if value.upper() not in valid_levels:
                        raise ValueError(f"log_level debe ser uno de: {valid_levels}")
                    self.logger.setLevel(getattr(logging, value.upper()))
                    self.config[key] = value.upper()
                elif key == "file_encoding":
                    "test".encode(value)  # Validar encoding
                    setattr(self, key, value)
                    self.config[key] = value
                else:
                    setattr(self, key, value)
                    self.config[key] = value

                updated = True
                self.logger.info(f"Configuración actualizada: {key} = {value}")

            except Exception as e:
                self.logger.error(f"Error actualizando {key}: {e}")
                return False

        return updated

    def reset_counters(self):
        """Resetear contadores de estadísticas."""
        self.modification_count = 0
        self.files_processed = 0
        self.errors_count = 0
        self.start_time = None
        self.logger.info("Contadores de estadísticas reseteados")

    def validate_permissions(self) -> bool:
        """
        Validar permisos en el directorio base.

        Returns:
            bool: True si tiene permisos necesarios
        """
        try:
            # Verificar lectura
            if not os.access(self.base_path, os.R_OK):
                self.logger.error(f"Sin permisos de lectura en: {self.base_path}")
                return False

            # Verificar escritura si no es dry-run
            if not self.dry_run_mode and not os.access(self.base_path, os.W_OK):
                self.logger.error(f"Sin permisos de escritura en: {self.base_path}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validando permisos: {e}")
            return False

    def _get_uptime(self) -> float:
        """
        Calcular tiempo de vida de la instancia.

        Returns:
            float: Tiempo en segundos desde la inicialización
        """
        if not self.start_time:
            self.start_time = time.time()
            return 0.0
        return time.time() - self.start_time

    def get_stats(self) -> Dict[str, any]:
        """
        Obtener estadísticas de la sesión actual.

        Returns:
            Dict: Estadísticas detalladas
        """
        uptime = self._get_uptime()
        return {
            "files_processed": self.files_processed,
            "modifications_made": self.modification_count,
            "errors_encountered": self.errors_count,
            "uptime_seconds": uptime,
            "uptime_formatted": f"{uptime:.2f}s",
            "success_rate": (
                (self.files_processed - self.errors_count)
                / max(self.files_processed, 1)
                * 100
                if self.files_processed > 0
                else 0.0
            ),
            "avg_files_per_second": (
                self.files_processed / max(uptime, 1) if uptime > 0 else 0.0
            ),
        }

    def get_project_info(self) -> Dict[str, str]:
        """
        Obtener información del proyecto y constantes globales.

        Returns:
            Dict: Información del proyecto y configuraciones
        """
        return {
            "project_name": PROJECT_NAME,
            "version": VERSION,
            "author": AUTHOR,
            "supported_extensions_count": len(DEFAULT_SUPPORTED_EXTENSIONS),
            "excluded_dirs_count": len(DEFAULT_EXCLUDED_DIRS),
            "supported_encodings_count": len(SUPPORTED_ENCODINGS),
            "default_max_file_size_mb": DEFAULT_MAX_FILE_SIZE_MB,
            "default_encoding": DEFAULT_FILE_ENCODING,
            "default_log_level": DEFAULT_LOG_LEVEL,
        }

    @staticmethod
    def get_all_constants() -> Dict[str, any]:
        """
        Obtener todas las constantes globales definidas.

        Returns:
            Dict: Todas las constantes organizadas por categoría
        """
        return {
            "project_info": {
                "name": PROJECT_NAME,
                "version": VERSION,
                "author": AUTHOR,
            },
            "file_extensions": {
                "supported": DEFAULT_SUPPORTED_EXTENSIONS,
                "language_mapping": EXTENSION_TO_LANGUAGE,
            },
            "directories": {
                "excluded": list(DEFAULT_EXCLUDED_DIRS),
            },
            "file_settings": {
                "encodings": SUPPORTED_ENCODINGS,
                "default_encoding": DEFAULT_FILE_ENCODING,
                "max_size_mb": DEFAULT_MAX_FILE_SIZE_MB,
            },
            "logging": {
                "valid_levels": list(VALID_LOG_LEVELS),
                "default_level": DEFAULT_LOG_LEVEL,
                "format": DEFAULT_LOG_FORMAT,
            },
            "backup": {
                "suffix": BACKUP_SUFFIX,
                "enabled_by_default": DEFAULT_BACKUP_ENABLED,
            },
            "comments": {
                "single_line": SINGLE_LINE_COMMENT_PREFIXES,
                "multi_line": MULTI_LINE_COMMENT_DELIMITERS,
            },
        }

    def validate_file(self, file_path: Union[str, Path]) -> bool:
        """
        Validar que el archivo existe y es modificable.

        Args:
            file_path: Ruta al archivo a validar

        Returns:
            bool: True si el archivo es válido, False en caso contrario
        """
        path = Path(file_path)

        if not path.exists():
            self.logger.error(f"Archivo no encontrado: {path}")
            return False

        if not path.is_file():
            self.logger.error(f"La ruta no es un archivo: {path}")
            return False

        if path.suffix not in self.supported_extensions:
            self.logger.warning(f"Extensión no soportada: {path.suffix}")
            return False

        # Validación adicional de sintaxis si está habilitada
        if self.validate_syntax:
            if not self.pattern_validator.validate_syntax(str(path)):
                self.logger.error(f"Archivo con sintaxis inválida: {path}")
                return False
            self.logger.debug(f"Sintaxis validada correctamente: {path}")

        return True

    def create_backup(self, file_path: Union[str, Path]) -> Optional[Path]:
        """
        Crear respaldo de un archivo antes de modificarlo.

        Args:
            file_path: Ruta al archivo original

        Returns:
            Path: Ruta al archivo de respaldo creado, None si falla
        """
        if not self.backup_enabled:
            return None

        # Usar BackupManager avanzado si está disponible
        if hasattr(self, "backup_manager") and self.backup_manager:
            return self.backup_manager.create_timestamped_backup(file_path)

        original_path = Path(file_path)
        backup_path = original_path.with_suffix(f"{original_path.suffix}.backup")

        try:
            backup_path.write_text(original_path.read_text(encoding="utf-8"))
            self.logger.info(f"Backup creado: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Error creando backup: {e}")
            return None

    def list_files(
        self, directory: Optional[Union[str, Path]] = None, recursive: bool = True
    ) -> List[Path]:
        """
        Listar archivos de código en un directorio.

        Args:
            directory: Directorio a escanear (por defecto: base_path)
            recursive: Si buscar recursivamente en subdirectorios

        Returns:
            List[Path]: Lista de archivos encontrados
        """
        search_path = Path(directory) if directory else self.base_path
        found_files = []

        try:
            if recursive:
                for ext in self.supported_extensions:
                    found_files.extend(search_path.rglob(f"*{ext}"))
            else:
                for ext in self.supported_extensions:
                    found_files.extend(search_path.glob(f"*{ext}"))

            self.logger.info(
                f"Encontrados {len(found_files)} archivos en {search_path}"
            )
            return sorted(found_files)

        except Exception as e:
            self.logger.error(f"Error listando archivos: {e}")
            return []

    def detect_language(self, file_path: Union[str, Path]) -> Optional[str]:
        """
        Detectar el lenguaje de programación basado en la extensión del archivo.
        """
        path = Path(file_path)
        # Usar mapeo global de extensiones a lenguajes
        return EXTENSION_TO_LANGUAGE.get(path.suffix.lower(), "Unknown")

    def analyze_file_metrics(self, file_path: Union[str, Path]) -> Dict[str, int]:
        """
        Analizar métricas básicas de un archivo de código.
        """
        content = (
            self.read_file_safe(file_path) if hasattr(self, "read_file_safe") else None
        )
        if not content:
            try:
                content = Path(file_path).read_text()
            except:
                return {}
        lines = content.split("\n")
        return {
            "total_lines": len(lines),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "total_characters": len(content),
        }


def main():
    """Función principal para demostración de constantes y configuraciones globales."""
    print(f"{PROJECT_NAME} v{VERSION}")
    print(f"Desarrollado por: {AUTHOR}")
    print("=" * 70)

    # Demostrar información del proyecto
    print("\n📋 Información del Proyecto:")
    modifier = UniversalCodeModifier()
    project_info = modifier.get_project_info()
    for key, value in project_info.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")

    # Demostrar configuración con constantes
    print("\n🔧 Configuración con Constantes Globales:")
    constants = UniversalCodeModifier.get_all_constants()

    # Mostrar extensiones soportadas
    print(f"  Extensiones soportadas: {len(constants['file_extensions']['supported'])}")
    print(f"  Primeras 5: {constants['file_extensions']['supported'][:5]}")

    # Mostrar configuraciones de archivo
    print(f"  Encodings soportados: {len(constants['file_settings']['encodings'])}")
    print(f"  Encoding por defecto: {constants['file_settings']['default_encoding']}")
    print(f"  Tamaño máximo por defecto: {constants['file_settings']['max_size_mb']}MB")

    # Mostrar directorios excluidos
    print(f"  Directorios excluidos: {len(constants['directories']['excluded'])}")
    print(f"  Primeros 5: {list(constants['directories']['excluded'])[:5]}")

    # Demostrar detección de lenguaje usando constantes
    print("\n🔍 Detección de Lenguajes (usando constantes):")
    test_files = ["script.py", "app.js", "component.ts", "Main.java", "program.cpp"]
    for file in test_files:
        language = modifier.detect_language(file)
        print(f"  {file}: {language}")

    # Mostrar configuración actual
    print("\n⚙️ Configuración Actual:")
    config = modifier.get_config()
    important_configs = [
        "dry_run_mode",
        "backup_enabled",
        "max_file_size_mb",
        "log_level",
    ]
    for key in important_configs:
        if key in config:
            print(f"  {key.replace('_', ' ').title()}: {config[key]}")

    # Demostrar PatternValidator
    print("\n🔍 Demostración de PatternValidator:")
    pattern_validator = PatternValidator()
    report = pattern_validator.get_validation_report()
    print(f"  Lenguajes soportados: {', '.join(report['supported_languages'])}")
    print(f"  Métodos de validación: {', '.join(report['validation_methods'])}")
    print(f"  Estado: {report['status']}")

    # Verificar integridad de constantes
    print("\n✅ Verificación de Integridad de Constantes:")

    # Verificar que las extensiones tienen mapeos de lenguaje
    missing_mappings = []
    for ext in DEFAULT_SUPPORTED_EXTENSIONS:
        if ext not in EXTENSION_TO_LANGUAGE:
            missing_mappings.append(ext)

    if missing_mappings:
        print(f"  ⚠️  Extensiones sin mapeo de lenguaje: {missing_mappings}")
    else:
        print("  ✅ Todas las extensiones tienen mapeo de lenguaje")

    # Verificar configuración por defecto
    try:
        test_modifier = UniversalCodeModifier(**DEFAULT_CONFIG)
        print("  ✅ Configuración por defecto es válida")
    except Exception as e:
        print(f"  ❌ Error en configuración por defecto: {e}")

    print(f"\n🎉 Demostración de {PROJECT_NAME} v{VERSION} completada!")


if __name__ == "__main__":
    main()
