"""
Tests para UniversalPatternHelper - Cobertura completa de funcionalidad.
"""

import pytest
from utils.universal_pattern_helper import UniversalPatternHelper


class TestUniversalPatternHelper:
    """Tests completos para UniversalPatternHelper."""
    
    def setup_method(self):
        """Setup para cada test."""
        self.helper = UniversalPatternHelper()
    
    def test_init(self):
        """Test inicialización correcta."""
        assert self.helper is not None
        assert hasattr(self.helper, 'logger')
        assert hasattr(self.helper, 'pattern_cache')
        assert hasattr(self.helper, 'migration_history')
    
    def test_detect_code_patterns_functions(self):
        """Test detección de funciones."""
        code = 'def function_one():\n    pass\n\ndef function_two(param):\n    return param'
        result = self.helper.detect_code_patterns(code)
        assert 'functions' in result
        assert 'function_one' in result['functions']
        assert 'function_two' in result['functions']
    
    def test_migrate_exact_pattern_success(self):
        """Test migración exitosa."""
        content = 'old_function() should become new_function()'
        result = self.helper.migrate_exact_pattern('old_function', 'new_function', content)
        assert result == 'new_function() should become new_function()'
        assert len(self.helper.migration_history) == 1
    
    def test_preserve_formatting(self):
        """Test preservación de formato."""
        original = '    def old_function():'
        new_content = 'def new_function():'
        formatted = self.helper.preserve_formatting(original, new_content)
        assert formatted == '    def new_function():'
    
    def test_get_operation_compatible_patterns(self):
        """Test obtención de patrones compatibles."""
        compat = self.helper.get_operation_compatible_patterns()
        assert 'supported_operations' in compat
        assert 'pattern_types' in compat
        assert 'migration_modes' in compat
        assert 'detect' in compat['supported_operations']
        assert 'migrate' in compat['supported_operations']
        
    def test_get_sqlalchemy_patterns(self):
            """Test obtención de patrones SQLAlchemy."""
            patterns = self.helper._get_sqlalchemy_patterns()
            assert isinstance(patterns, dict)
            assert 'Column' in patterns
            assert 'relationship' in patterns
            assert 'ForeignKey' in patterns
            assert 'Table' in patterns
            assert len(patterns) == 4

    def test_detect_sqlalchemy_patterns_success(self):
        """Test detección exitosa de patrones SQLAlchemy."""
        test_code = '''
    class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    posts = db.relationship("Post", backref="author", lazy=True)
    '''
        result = self.helper.detect_sqlalchemy_patterns(test_code)
        assert isinstance(result, dict)
        assert 'Column' in result
        assert 'relationship' in result
        assert len(result['Column']) == 2  # id and email
        assert len(result['relationship']) == 1  # posts

    def test_detect_sqlalchemy_patterns_empty(self):
        """Test detección con código sin patrones SQLAlchemy."""
        test_code = "def simple_function():\n    return 'hello'"
        result = self.helper.detect_sqlalchemy_patterns(test_code)
        assert isinstance(result, dict)
        assert len(result) == 0

    def test_migrate_sqlalchemy_patterns_success(self):
        """Test migración exitosa de patrones SQLAlchemy."""
        old_code = 'id = db.Column(db.Integer, primary_key=True)'
        new_patterns = {'Column': {'old': 'db.Integer', 'new': 'sa.Integer'}}
        result = self.helper.migrate_sqlalchemy_patterns(old_code, new_patterns)
        assert result is not None
        assert 'sa.Integer' in result
        assert len(self.helper.migration_history) > 0

    def test_migrate_sqlalchemy_patterns_invalid_type(self):
        """Test migración con tipo de patrón inválido."""
        old_code = 'id = db.Column(db.Integer, primary_key=True)'
        new_patterns = {'InvalidType': {'old': 'db.Integer', 'new': 'sa.Integer'}}
        result = self.helper.migrate_sqlalchemy_patterns(old_code, new_patterns)
        assert result == old_code  # Sin cambios

    def test_sqlalchemy_integration_compatibility(self):
        """Test integración SQLAlchemy en operaciones compatibles."""
        compat = self.helper.get_operation_compatible_patterns()
        assert 'detect_sqlalchemy' in compat['supported_operations']
        assert 'migrate_sqlalchemy' in compat['supported_operations']
    
    def test_get_pytest_patterns(self):
        """Test obtención de patrones pytest."""
        patterns = self.helper._get_pytest_patterns()
        assert isinstance(patterns, dict)
        assert 'test_functions' in patterns
        assert 'fixtures' in patterns
        assert 'decorators' in patterns
        assert 'assertions' in patterns
        assert 'markers' in patterns
        assert 'parametrize' in patterns

    def test_detect_pytest_patterns_success(self):
        """Test detección exitosa de patrones pytest."""
        test_code = '''
import pytest

@pytest.fixture
def sample_data():
    return {'key': 'value'}

def test_example_function(sample_data):
    assert sample_data['key'] == 'value'

@pytest.mark.slow
def test_slow_operation():
    assert True
'''
        result = self.helper.detect_pytest_patterns(test_code)
        assert isinstance(result, dict)
        assert len(result) > 0
        assert 'test_functions' in result
        assert 'fixtures' in result
        assert 'decorators' in result

    def test_migrate_pytest_patterns_success(self):
        """Test migración exitosa de patrones pytest."""
        old_code = 'def test_example(self): self.assertEqual(a, b)'
        new_patterns = {'assertions': {'old': 'self.assertEqual', 'new': 'assert'}}
        result = self.helper.migrate_pytest_patterns(old_code, new_patterns)
        assert result is not None
        assert 'assert' in result
        assert len(self.helper.migration_history) > 0

    def test_migrate_pytest_patterns_invalid_type(self):
        """Test migración con tipo de patrón pytest inválido."""
        old_code = 'def test_example(): pass'
        new_patterns = {'InvalidType': {'old': 'old', 'new': 'new'}}
        result = self.helper.migrate_pytest_patterns(old_code, new_patterns)
        assert result == old_code  # Sin cambios

    def test_pytest_integration_compatibility(self):
        """Test integración pytest en operaciones compatibles."""
        compat = self.helper.get_operation_compatible_patterns()
        assert 'detect_pytest' in compat['supported_operations']
        assert 'migrate_pytest' in compat['supported_operations']