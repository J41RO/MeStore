import pytest
from functions.response.response_builder import ResponseBuilder


class TestResponseBuilderDebugMethods:
    
    def setup_method(self):
        """Setup para cada test"""
        self.builder = ResponseBuilder()
        
    def test_build_context_error_response(self):
        """Test construcción de respuesta de error con contexto"""
        result = self.builder.build_context_error_response(
            error='Test error',
            file_path='/test/file.py',
            pattern='missing_pattern',
            line_number=10,
            surrounding_context='line 9\nline 10\nline 11',
            file_content_sample='sample content'
        )
        
        assert result['success'] == False
        assert result['error'] == 'Test error'
        assert result['error_type'] == 'context_error'
        assert result['details']['pattern_searched'] == 'missing_pattern'
        assert result['details']['line_number'] == 10
        assert result['details']['surrounding_context'] == 'line 9\nline 10\nline 11'
        assert result['phase'] == 'pattern_matching'
        
    def test_build_pattern_mismatch_response(self):
        """Test construcción de respuesta específica para patterns no encontrados"""
        file_content = """line 1
line 2
line 3"""
        suggestions = ['similar_pattern1', 'similar_pattern2']
        
        result = self.builder.build_pattern_mismatch_response(
            pattern='target_pattern',
            file_path='/test/file.py',
            file_content=file_content,
            suggestions=suggestions
        )
        
        assert result['success'] == False
        assert result['error'] == "Pattern 'target_pattern' not found in file"
        assert result['error_type'] == 'pattern_mismatch'
        assert result['details']['pattern_searched'] == 'target_pattern'
        assert result['details']['total_lines'] == 3
        assert result['details']['suggestions'] == suggestions
        assert len(result['details']['first_few_lines']) == 3
        assert result['phase'] == 'pattern_matching'
        
    def test_build_verbose_error_response(self):
        """Test construcción de respuesta de error verbose"""
        debug_info = {
            'file_size': 1024,
            'encoding': 'utf-8',
            'last_modified': '2023-01-01'
        }
        suggestions = ['suggestion1']
        
        result = self.builder.build_verbose_error_response(
            error='Verbose test error',
            file_path='/test/file.py',
            pattern='test_pattern',
            debug_info=debug_info,
            suggestions=suggestions
        )
        
        assert result['success'] == False
        assert result['error'] == 'Verbose test error'
        assert result['error_type'] == 'verbose_error'
        assert result['details']['pattern_searched'] == 'test_pattern'
        assert result['details']['debug_info'] == debug_info
        assert result['details']['suggestions'] == suggestions
        assert len(result['details']['troubleshooting_tips']) > 0
        assert result['phase'] == 'pattern_matching'
        
    def test_context_error_response_minimal(self):
        """Test respuesta de error con información mínima"""
        result = self.builder.build_context_error_response(
            error='Minimal error',
            file_path='/test/file.py',
            pattern='test'
        )
        
        assert result['success'] == False
        assert result['error'] == 'Minimal error'
        assert result['details']['pattern_searched'] == 'test'
        assert result['details']['line_number'] is None
        assert result['details']['surrounding_context'] is None
        
    def test_pattern_mismatch_empty_suggestions(self):
        """Test respuesta de pattern mismatch sin sugerencias"""
        result = self.builder.build_pattern_mismatch_response(
            pattern='test',
            file_path='/test/file.py',
            file_content='content'
        )
        
        assert result['details']['suggestions'] == []
        
    def test_verbose_error_no_suggestions(self):
        """Test respuesta verbose sin sugerencias"""
        result = self.builder.build_verbose_error_response(
            error='Test',
            file_path='/test/file.py',
            pattern='test',
            debug_info={}
        )
        
        assert result['details']['suggestions'] == []
        assert len(result['details']['troubleshooting_tips']) > 0