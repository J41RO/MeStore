"""
Excepciones personalizadas para el sistema Surgical Modifier
"""

class SurgicalModifierError(Exception):
    """Excepción base para errores del Surgical Modifier"""
    pass

class InvalidPatternError(SurgicalModifierError):
    """Error cuando un patrón de búsqueda es inválido"""
    pass

class FileNotFoundError(SurgicalModifierError):
    """Error cuando no se encuentra el archivo especificado"""
    pass

class PermissionError(SurgicalModifierError):
    """Error cuando no hay permisos para acceder al archivo"""
    pass

class ValidationError(SurgicalModifierError):
    """Error de validación de datos o parámetros"""
    pass

class ConfigurationError(SurgicalModifierError):
    """Error de configuración del sistema"""
    pass

class CoordinatorError(SurgicalModifierError):
    """Error en coordinadores del sistema"""
    pass

class BackupError(SurgicalModifierError):
    """Error en operaciones de backup"""
    pass

class FileOperationError(SurgicalModifierError):
    """Error en operaciones de archivo"""
    pass

class PatternMatchError(SurgicalModifierError):
    """Error en matching de patrones"""
    pass
