"""
🚀 CodeCraft Ultimate v6.0 - Excepciones Personalizadas
"""


class CodeCraftException(Exception):
    """Excepción base de CodeCraft"""
    pass


class FileNotFoundError(CodeCraftException):
    """Archivo no encontrado"""
    pass


class PatternNotFoundError(CodeCraftException):
    """Patrón no encontrado en archivo"""
    pass


class SyntaxValidationError(CodeCraftException):
    """Error de validación de sintaxis"""
    pass


class BackupError(CodeCraftException):
    """Error en operaciones de backup"""
    pass


class PluginError(CodeCraftException):
    """Error en sistema de plugins"""
    pass


class ConfigurationError(CodeCraftException):
    """Error de configuración"""
    pass


class RefactoringError(CodeCraftException):
    """Error en operaciones de refactoring"""
    pass


class AnalysisError(CodeCraftException):
    """Error en análisis de código"""
    pass


class GenerationError(CodeCraftException):
    """Error en generación de código"""
    pass


class AIIntegrationError(CodeCraftException):
    """Error en integración con IA"""
    pass