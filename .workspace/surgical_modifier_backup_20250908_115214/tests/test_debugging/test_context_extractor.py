import pytest
import tempfile
import os
from pathlib import Path
from functions.debugging.context_extractor import ContextExtractor


class TestContextExtractor:
    
    def setup_method(self):
        """Setup para cada test"""
        self.extractor = ContextExtractor()
        
    def test_extract_surrounding_lines_basic(self):
        """Test básico de extracción de líneas circundantes"""
        # Crear archivo temporal
        content = """line 1
line 2
target line
line 4
line 5"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_path = f.name
            
        try:
            result = self.extractor.extract_surrounding_lines(temp_path, 3, 1)
            
            assert result['target_line_number'] == 3
            assert result['target_line'] == 'target line'
            assert len(result['before_lines']) == 1
            assert len(result['after_lines']) == 1
            assert result['before_lines'][0]['content'] == 'line 2'
            assert result['after_lines'][0]['content'] == 'line 4'
            
        finally:
            os.unlink(temp_path)
    
    def test_extract_pattern_context_found_similar(self):
        """Test extracción de contexto cuando hay patrones similares"""
        content = """def function_name():
    return value
def Function_Name():
    return other"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write(content)
            temp_path = f.name
            
        try:
            result = self.extractor.extract_pattern_context(temp_path, 'function_name')
            
            assert result['pattern_searched'] == 'function_name'
            assert result['file_info']['total_lines'] == 4
            assert len(result['potential_matches']) > 0
            
        finally:
            os.unlink(temp_path)
    
    def test_suggest_alternatives_case_sensitivity(self):
        """Test sugerencias para problemas de case sensitivity"""
        content = """Hello World
HELLO WORLD
hello world"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_path = f.name
            
        try:
            result = self.extractor.suggest_alternatives(temp_path, 'hello')
            
            assert 'similar_patterns' in result
            assert 'common_case_suggestions' in result
            assert len(result['common_case_suggestions']) > 0
            
        finally:
            os.unlink(temp_path)
    
    def test_analyze_file_structure_python(self):
        """Test análisis de estructura para archivo Python"""
        content = """import os
import sys

class MyClass:
    def my_method(self):
        pass

def my_function():
    return True"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write(content)
            temp_path = f.name
            
        try:
            result = self.extractor.analyze_file_structure(temp_path)
            
            assert result['file_info']['total_lines'] == 9
            assert result['content_analysis']['has_imports'] == True
            assert result['content_analysis']['has_functions'] == True
            assert result['content_analysis']['has_classes'] == True
            assert 'File contains function definitions' in result['structure_hints']
            assert 'File contains class definitions' in result['structure_hints']
            
        finally:
            os.unlink(temp_path)
    
    def test_error_handling_nonexistent_file(self):
        """Test manejo de errores para archivo inexistente"""
        result = self.extractor.extract_surrounding_lines('/path/does/not/exist', 1)
        assert 'error' in result
        
        result = self.extractor.extract_pattern_context('/path/does/not/exist', 'pattern')
        assert 'error' in result
        
        result = self.extractor.suggest_alternatives('/path/does/not/exist', 'pattern')
        assert 'error' in result
    
    def test_extract_surrounding_lines_edge_cases(self):
        """Test casos extremos para extracción de líneas"""
        content = "single line"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_path = f.name
            
        try:
            # Test línea que no existe  
            result = self.extractor.extract_surrounding_lines(temp_path, 5, 2)
            # Si devuelve error, está bien porque la línea no existe
            assert 'error' in result or result.get('target_line') is None
            
            # Test primera línea
            result = self.extractor.extract_surrounding_lines(temp_path, 1, 2)
            assert result['target_line'] == 'single line'
            assert len(result['before_lines']) == 0
            
        finally:
            os.unlink(temp_path)
            
    def test_indentation_detection(self):
        """Test detección de estilo de indentación"""
        # Test con espacios
        content_spaces = """def func():
    return True"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write(content_spaces)
            temp_path = f.name
            
        try:
            result = self.extractor.analyze_file_structure(temp_path)
            assert result['content_analysis']['indentation_style'] == 'spaces'
            
        finally:
            os.unlink(temp_path)
            
    def test_fuzzy_matching_suggestions(self):
        """Test sugerencias usando fuzzy matching"""
        content = """function_name_old
function_name_new
some_other_function"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_path = f.name
            
        try:
            result = self.extractor.suggest_alternatives(temp_path, 'function_name', threshold=0.5)
            
            assert 'similar_patterns' in result
            patterns = result['similar_patterns']
            assert len(patterns) > 0
            
            # Verificar que encontró patrones similares
            found_similar = any('function_name' in p['suggested_pattern'] for p in patterns)
            assert found_similar
            
        finally:
            os.unlink(temp_path)