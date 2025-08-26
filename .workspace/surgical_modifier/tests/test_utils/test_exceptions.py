import pytest
from surgical_modifier.exceptions import (
    SurgicalModifierError, CoordinatorError, ValidationError,
    BackupError, FileOperationError, PatternMatchError, ConfigurationError
)

class TestExceptions:
    """Tests unitarios para excepciones personalizadas"""
    
    def test_can_import_all_exceptions(self):
        """Test que todas las excepciones se pueden importar"""
        exceptions = [
            SurgicalModifierError, CoordinatorError, ValidationError,
            BackupError, FileOperationError, PatternMatchError, ConfigurationError
        ]
        for exc in exceptions:
            assert exc is not None
            assert issubclass(exc, Exception)
    
    def test_base_exception_hierarchy(self):
        """Test jerarquía de excepciones - todas heredan de SurgicalModifierError"""
        child_exceptions = [
            CoordinatorError, ValidationError, BackupError,
            FileOperationError, PatternMatchError, ConfigurationError
        ]
        
        for exc in child_exceptions:
            assert issubclass(exc, SurgicalModifierError)
            assert issubclass(exc, Exception)
    
    def test_surgical_modifier_error_instantiation(self):
        """Test instanciación de excepción base"""
        exc = SurgicalModifierError("Test message")
        assert str(exc) == "Test message"
        assert isinstance(exc, Exception)
    
    def test_coordinator_error_instantiation(self):
        """Test instanciación de CoordinatorError"""
        exc = CoordinatorError("Coordinator failed")
        assert str(exc) == "Coordinator failed"
        assert isinstance(exc, SurgicalModifierError)
    
    def test_validation_error_instantiation(self):
        """Test instanciación de ValidationError"""
        exc = ValidationError("Validation failed")
        assert str(exc) == "Validation failed"
        assert isinstance(exc, SurgicalModifierError)
    
    def test_backup_error_instantiation(self):
        """Test instanciación de BackupError"""
        exc = BackupError("Backup operation failed")
        assert str(exc) == "Backup operation failed"
        assert isinstance(exc, SurgicalModifierError)
    
    def test_file_operation_error_instantiation(self):
        """Test instanciación de FileOperationError"""
        exc = FileOperationError("File operation failed")
        assert str(exc) == "File operation failed"
        assert isinstance(exc, SurgicalModifierError)
    
    def test_pattern_match_error_instantiation(self):
        """Test instanciación de PatternMatchError"""
        exc = PatternMatchError("Pattern not found")
        assert str(exc) == "Pattern not found"
        assert isinstance(exc, SurgicalModifierError)
    
    def test_configuration_error_instantiation(self):
        """Test instanciación de ConfigurationError"""
        exc = ConfigurationError("Invalid configuration")
        assert str(exc) == "Invalid configuration"
        assert isinstance(exc, SurgicalModifierError)
    
    def test_exceptions_can_be_raised_and_caught(self):
        """Test que excepciones se pueden lanzar y capturar"""
        with pytest.raises(SurgicalModifierError):
            raise SurgicalModifierError("Test error")
        
        with pytest.raises(CoordinatorError):
            raise CoordinatorError("Test coordinator error")
        
        # Test que se puede capturar excepción específica como base
        with pytest.raises(SurgicalModifierError):
            raise ValidationError("Test validation error")
    
    def test_exception_without_message(self):
        """Test excepciones sin mensaje"""
        exc = SurgicalModifierError()
        assert str(exc) == ""
        
        exc2 = CoordinatorError()
        assert isinstance(exc2, SurgicalModifierError)
