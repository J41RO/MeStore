import pytest
import tempfile
import os
from pathlib import Path

from functions.analysis.structural_analyzer import StructuralAnalyzer
from functions.analysis.types import StructuralIssue

class TestStructuralAnalyzer:
    """Tests para StructuralAnalyzer"""
    
    def setup_method(self):
        self.analyzer = StructuralAnalyzer()
        
    def test_analyzer_initialization(self):
        """Test básico de inicialización"""
        assert self.analyzer is not None
        assert hasattr(self.analyzer, 'analyze_before_modification')
        assert hasattr(self.analyzer, 'detect_structural_issues')
        
    def test_supported_analysis_types(self):
        """Test de tipos de análisis soportados"""
        types = self.analyzer.get_supported_analysis_types()
        assert 'syntax' in types
        assert 'duplicates' in types
        assert 'circular' in types
        
    def test_python_syntax_analysis(self):
        """Test de análisis de sintaxis Python"""
        # Código Python válido
        valid_code = 'def hello():\n    return "Hello World"'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(valid_code)
            f.flush()
            
            result = self.analyzer.analyze_before_modification(f.name, valid_code)
            assert not result.has_issues
            
        os.unlink(f.name)
        
    def test_python_syntax_error(self):
        """Test de detección de errores de sintaxis Python"""
        # Código Python inválido
        invalid_code = 'def hello(:\n    return "Hello"'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(invalid_code)
            f.flush()
            
            result = self.analyzer.analyze_before_modification(f.name, invalid_code)
            assert result.has_issues
            critical_issues = result.get_critical_issues()
            assert len(critical_issues) > 0
            assert any('syntax' in issue.type for issue in critical_issues)
            
        os.unlink(f.name)
        
    def test_typescript_interface_duplicates(self):
        """Test de detección de interfaces duplicadas"""
        ts_code = '''
interface User {
    name: string;
}

interface User {
    age: number;
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
            f.write(ts_code)
            f.flush()
            
            result = self.analyzer.analyze_before_modification(f.name, ts_code, ['duplicates'])
            assert result.has_issues
            warnings = result.get_warnings()
            assert len(warnings) > 0
            assert any('duplicate' in issue.type for issue in warnings)
            
        os.unlink(f.name)
        
    def test_analysis_with_nonexistent_file(self):
        """Test con archivo que no existe"""
        result = self.analyzer.analyze_before_modification('/nonexistent/file.py')
        assert result.has_issues
        assert any('read_error' in issue.type for issue in result.issues)
        
    def test_skip_analysis_types(self):
        """Test de análisis selectivo"""
        valid_code = 'def test(): pass'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(valid_code)
            f.flush()
            
            # Solo análisis de sintaxis
            result = self.analyzer.analyze_before_modification(f.name, valid_code, ['syntax'])
            assert not result.has_issues
            
        os.unlink(f.name)