"""
Tests unitarios para PositionCalculator.
Cobertura mínima: 90% de métodos principales.
Incluye integración con IndentationDetector.
"""

import pytest
from unittest.mock import Mock, patch
from functions.insertion.position_calculator import (
    PositionCalculator, PositionType, InsertionPosition
)
from functions.insertion.indentation_detector import IndentationDetector


class TestPositionCalculator:
    """Tests para PositionCalculator."""
    
    def setup_method(self):
        """Setup para cada test."""
        self.calculator = PositionCalculator()
        self.sample_content = '''class TestClass:
    def method1(self):
        if condition:
            do_something()
        else:
            do_other()
    
    def method2(self):
        pass'''
    
    def test_initialization(self):
        """Test inicialización correcta."""
        calc = PositionCalculator()
        assert calc.indentation_detector is not None
        assert isinstance(calc.indentation_detector, IndentationDetector)
        assert isinstance(calc._cache, dict)
    
    def test_calculate_line_position_valid(self):
        """Test cálculo de posición en línea válida."""
        position = self.calculator.calculate_line_position(self.sample_content, 1)
        
        assert position.line_number == 1
        assert position.position_type == PositionType.AFTER
        assert position.is_safe == True
        assert 'line_content' in position.context_info
    
    def test_calculate_line_position_invalid(self):
        """Test cálculo con línea fuera de rango."""
        position = self.calculator.calculate_line_position(self.sample_content, 999)
        
        assert position.line_number == 999
        assert position.is_safe == False
        assert 'error' in position.context_info
    
    def test_find_insertion_point_found(self):
        """Test encontrar punto de inserción existente."""
        position = self.calculator.find_insertion_point(self.sample_content, 'def method1')
        
        assert position is not None
        assert position.position_type == PositionType.AFTER
        assert 'matched_line' in position.context_info
        assert 'def method1' in position.context_info['matched_line']
    
    def test_find_insertion_point_not_found(self):
        """Test cuando no se encuentra el patrón."""
        position = self.calculator.find_insertion_point(self.sample_content, 'nonexistent_pattern')
        
        assert position is None
    
    def test_calculate_before_position(self):
        """Test cálculo de posición antes de patrón."""
        position = self.calculator.calculate_before_position(
            self.sample_content, 'def method1', '    # Comment before method'
        )
        
        assert position is not None
        assert position.position_type == PositionType.BEFORE
        assert position.column == 0
        assert 'target_line' in position.context_info
    
    def test_calculate_after_position(self):
        """Test cálculo de posición después de patrón."""
        position = self.calculator.calculate_after_position(
            self.sample_content, 'class TestClass:', '    new_method'
        )
        
        assert position is not None
        assert position.position_type == PositionType.AFTER
        assert position.line_number > 0
        assert 'target_line' in position.context_info
    
    def test_calculate_inside_block(self):
        """Test cálculo de posición dentro de bloque."""
        position = self.calculator.calculate_inside_block(
            self.sample_content, 'if condition:', 'new_statement'
        )
        
        assert position is not None
        assert position.position_type == PositionType.INSIDE
        assert 'block_start' in position.context_info
        assert position.context_info['block_type'] == 'if'
    
    def test_handle_nested_structures(self):
        """Test manejo de estructuras anidadas."""
        positions = self.calculator.handle_nested_structures(
            self.sample_content, 'def method', 0
        )
        
        assert len(positions) >= 2
        assert all(pos.position_type == PositionType.AFTER for pos in positions)
        assert all('nesting_depth' in pos.context_info for pos in positions)
    
    def test_detect_block_boundaries(self):
        """Test detección de límites de bloque."""
        start, end = self.calculator.detect_block_boundaries(self.sample_content, 0)
        
        assert start == 0
        assert end >= start
    
    def test_analyze_context(self):
        """Test análisis de contexto."""
        context = self.calculator.analyze_context(self.sample_content, 1)
        
        assert 'current_line' in context
        assert 'current_line_number' in context
        assert 'indentation_level' in context
        assert 'block_type' in context
        assert context['current_line_number'] == 1
    
    def test_find_pattern_positions_regex(self):
        """Test búsqueda con patrones regex."""
        positions = self.calculator.find_pattern_positions(
            self.sample_content, r'def method\d+'
        )
        
        assert len(positions) == 2
        for position in positions:
            assert 'matched_text' in position.context_info
            assert 'pattern' in position.context_info
    
    def test_calculate_relative_position(self):
        """Test cálculo de posición relativa."""
        position = self.calculator.calculate_relative_position(
            self.sample_content, 'class TestClass:', 2, 'after'
        )
        
        assert position is not None
        assert 'anchor_line' in position.context_info
        assert position.context_info['offset_lines'] == 2
    
    def test_handle_multiple_matches_first(self):
        """Test manejo de múltiples coincidencias - primera."""
        position = self.calculator.handle_multiple_matches(
            self.sample_content, r'def method', 'first'
        )
        
        assert position is not None
        assert 'def method' in position.context_info['matched_text']
    
    def test_handle_multiple_matches_last(self):
        """Test manejo de múltiples coincidencias - última."""
        position = self.calculator.handle_multiple_matches(
            self.sample_content, r'def method', 'last'
        )
        
        assert position is not None
        assert 'def method' in position.context_info['matched_text']
    
    def test_handle_multiple_matches_all(self):
        """Test manejo de múltiples coincidencias - todas."""
        position = self.calculator.handle_multiple_matches(
            self.sample_content, r'def method', 'all'
        )
        
        assert position is not None
        assert position.line_number == -1
        assert position.context_info['strategy'] == 'all'
        assert position.context_info['total_matches'] == 2
    
    def test_validate_insertion_safety_valid(self):
        """Test validación de inserción segura."""
        position = InsertionPosition(
            line_number=1, column=0, position_type=PositionType.AFTER,
            indentation_level=4, context_info={}, is_safe=True
        )
        
        is_safe = self.calculator.validate_insertion_safety(
            self.sample_content, position, '    new_code'
        )
        
        assert is_safe == True
    
    def test_validate_insertion_safety_invalid_line(self):
        """Test validación con línea inválida."""
        position = InsertionPosition(
            line_number=999, column=0, position_type=PositionType.AFTER,
            indentation_level=4, context_info={}, is_safe=True
        )
        
        is_safe = self.calculator.validate_insertion_safety(
            self.sample_content, position, '    new_code'
        )
        
        assert is_safe == False
    
    def test_handle_empty_file(self):
        """Test manejo de archivo vacío."""
        position = self.calculator.handle_empty_file('new_content')
        
        assert position.line_number == 0
        assert position.column == 0
        assert position.position_type == PositionType.AFTER
        assert position.indentation_level == 0
        assert position.context_info['file_state'] == 'empty'
        assert position.is_safe == True
    
    def test_handle_large_files(self):
        """Test manejo de archivos grandes."""
        large_content = 'def func():\n    pass\n' * 1000
        
        position = self.calculator.handle_large_files(
            large_content, 'def func():', 100
        )
        
        assert position is not None
        assert 'sampled_from_large_file' in position.context_info
        assert position.context_info['original_file_lines'] >= 2000
    
    def test_handle_encoding_variants_string(self):
        """Test manejo de encoding - string."""
        result = self.calculator.handle_encoding_variants('test_string')
        assert result == 'test_string'
    
    def test_handle_encoding_variants_bytes(self):
        """Test manejo de encoding - bytes."""
        test_bytes = 'test_string'.encode('utf-8')
        result = self.calculator.handle_encoding_variants(test_bytes)
        assert result == 'test_string'
    
    def test_validate_position_valid(self):
        """Test validación de posición válida."""
        position = InsertionPosition(
            line_number=1, column=5, position_type=PositionType.AFTER,
            indentation_level=4, context_info={}, is_safe=True
        )
        
        is_valid = self.calculator.validate_position(self.sample_content, position)
        assert is_valid == True
    
    def test_validate_position_invalid_line(self):
        """Test validación con línea inválida."""
        position = InsertionPosition(
            line_number=-1, column=0, position_type=PositionType.AFTER,
            indentation_level=4, context_info={}, is_safe=True
        )
        
        is_valid = self.calculator.validate_position(self.sample_content, position)
        assert is_valid == False
    
    def test_performance_stats(self):
        """Test estadísticas de performance."""
        self.calculator._cache['test_key'] = 'test_value'
        
        stats = self.calculator.performance_stats()
        
        assert 'cache_entries' in stats
        assert 'cache_size_bytes' in stats
        assert 'methods_available' in stats
        assert stats['cache_entries'] >= 1
    
    def test_cache_functionality(self):
        """Test funcionalidad de cache."""
        key = self.calculator._cache_key('content', 'operation', 'arg1', 'arg2')
        assert isinstance(key, str)
        assert 'operation' in key
        
        self.calculator._cache_result('test_key', 'test_value')
        result = self.calculator._get_cached_result('test_key')
        assert result == 'test_value'
        
        result = self.calculator._get_cached_result('nonexistent_key')
        assert result is None
    
    def test_optimized_methods_with_cache(self):
        """Test métodos optimizados usando cache."""
        position1 = self.calculator.calculate_after_position_optimized(
            self.sample_content, 'class TestClass:', 'new_method'
        )
        
        position2 = self.calculator.calculate_after_position_optimized(
            self.sample_content, 'class TestClass:', 'new_method'
        )
        
        assert position1 is not None
        assert position2 is not None
        assert position1.line_number == position2.line_number
    
    def test_integration_with_indentation_detector(self):
        """Test integración específica con IndentationDetector."""
        position = self.calculator.calculate_after_position(
            'class Test:\n    def method(self): pass',
            'class Test:', 'new_method'
        )
        
        assert position is not None
        assert position.indentation_level > 0
        assert 'indentation_string' in position.context_info


class TestIntegrationWithIndentationDetector:
    """Tests específicos de integración con IndentationDetector."""
    
    def setup_method(self):
        """Setup para tests de integración."""
        self.calculator = PositionCalculator()
    
    def test_indentation_detector_methods_used(self):
        """Test que métodos de IndentationDetector son utilizados."""
        content = 'class Test:\n    def method(self): pass'
        
        with patch.object(self.calculator.indentation_detector, 'analyze_line') as mock_analyze:
            mock_analyze.return_value = Mock(level=4, type=Mock(value=' '))
            
            position = self.calculator.calculate_line_position(content, 1)
            
            assert mock_analyze.called
            assert position.indentation_level == 4
    
    def test_suggest_indentation_integration(self):
        """Test integración con suggest_indentation."""
        content = 'class Test:\n    pass'
        
        with patch.object(self.calculator.indentation_detector, 'suggest_indentation') as mock_suggest:
            mock_suggest.return_value = '    '
            
            position = self.calculator.calculate_after_position(
                content, 'class Test:', 'new_method'
            )
            
            assert mock_suggest.called
            assert position.indentation_level == 4


if __name__ == '__main__':
    pytest.main([__file__, '-v'])