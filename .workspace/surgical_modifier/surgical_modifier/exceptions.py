"""Excepciones personalizadas de Surgical Modifier."""


class SurgicalModifierError(Exception):
    """Excepción base para errores de Surgical Modifier."""
    pass


class CoordinatorError(SurgicalModifierError):
    """Error relacionado con coordinadores."""
    pass


class ValidationError(SurgicalModifierError):
    """Error de validación de inputs o configuración."""
    pass


class BackupError(SurgicalModifierError):
    """Error en operaciones de backup."""
    pass


class FileOperationError(SurgicalModifierError):
    """Error en operaciones de archivos."""
    pass


class PatternMatchError(SurgicalModifierError):
    """Error en matching de patrones."""
    pass


class ConfigurationError(SurgicalModifierError):
    """Error en configuración del sistema."""
    pass
