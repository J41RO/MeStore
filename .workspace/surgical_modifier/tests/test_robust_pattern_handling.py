"""
Tests for Robust Pattern Handling System
Comprehensive tests for multiline patterns, block parsing, raw mode, and content validation
"""
import pytest
import tempfile
import os
from pathlib import Path
from utils.universal_pattern_helper import UniversalPatternHelper
from utils.block_parser import IntelligentBlockParser
from utils.escape_processor import EscapeProcessor
from utils.content_validator import PreInsertionValidator


class TestUniversalPatternHelper:
    """Tests for UniversalPatternHelper multiline functionality"""
    
    def test_process_multiline_patterns_basic(self):
        """Test basic multiline pattern processing"""
        helper = UniversalPatternHelper()
        pattern = 'class Test:\\n    def __init__(self):'
        result = helper.process_multiline_patterns(pattern)
        
        assert '\n' in result
        assert 'class Test:' in result
        assert '__init__' in result
        assert len(result.split('\n')) == 2
    
    def test_process_multiline_patterns_no_convert(self):
        """Test multiline pattern processing without conversion"""
        helper = UniversalPatternHelper()
        pattern = 'class Test:\\n    def __init__(self):'
        result = helper.process_multiline_patterns(pattern, convert_newlines=False)
        
        assert '\\n' in result
        assert result == pattern
    
    def test_multiline_pattern_caching(self):
        """Test that multiline patterns are cached properly"""
        helper = UniversalPatternHelper()
        pattern = 'def test():\\n    pass'
        
        # First call
        result1 = helper.process_multiline_patterns(pattern)
        cache_size_1 = len(helper.pattern_cache)
        
        # Second call - should use cache
        result2 = helper.process_multiline_patterns(pattern)
        cache_size_2 = len(helper.pattern_cache)
        
        assert result1 == result2
        assert cache_size_1 == cache_size_2


class TestIntelligentBlockParser:
    """Tests for IntelligentBlockParser functionality"""
    
    def test_extract_method_block(self):
        """Test extracting a method block"""
        parser = IntelligentBlockParser()
        test_code = '''
class Example:
    def method_one(self):
        return 'test'
    
    def method_two(self, param):
        if param:
            return True
        return False
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            f.flush()
            
            try:
                result = parser.extract_complete_block(f.name, 'method_two')
                
                assert result is not None
                assert result['name'] == 'method_two'
                assert result['type'] == 'FunctionDef'
                assert 'method_two' in result['content']
                assert 'if param:' in result['content']
            finally:
                os.unlink(f.name)
    
    def test_extract_class_block(self):
        """Test extracting a class block"""
        parser = IntelligentBlockParser()
        test_code = '''
def function_before():
    pass

class TestClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value

def function_after():
    pass
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            f.flush()
            
            try:
                result = parser.extract_complete_block(f.name, 'TestClass')
                
                assert result is not None
                assert result['name'] == 'TestClass'
                assert result['type'] == 'ClassDef'
                assert 'class TestClass:' in result['content']
                assert '__init__' in result['content']
            finally:
                os.unlink(f.name)
    
    def test_method_signature_parsing(self):
        """Test method signature parsing"""
        parser = IntelligentBlockParser()
        test_code = '''
class Example:
    def complex_method(self, 
                      param1: str,
                      param2: int = 42,
                      *args,
                      **kwargs) -> bool:
        return True
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            f.flush()
            
            try:
                result = parser.extract_complete_block(f.name, 'complex_method')
                
                assert result is not None
                signature = result['signature']
                assert 'def complex_method' in signature
                assert 'param1: str' in signature
                assert '-> bool:' in signature
            finally:
                os.unlink(f.name)


class TestEscapeProcessor:
    """Tests for EscapeProcessor raw mode functionality"""
    
    def test_process_raw_content_preserve(self):
        """Test raw content processing in preserve mode"""
        processor = EscapeProcessor()
        content = r'print("Hello\nWorld\t\"test\"")'
        result = processor.process_raw_content(content, mode='preserve')
        
        assert len(result) > 0
        assert result is not None
    
    def test_process_raw_content_convert(self):
        """Test raw content processing in convert mode"""
        processor = EscapeProcessor()
        content = r'print(\"Hello\\nWorld\\t\\\"test\\\"\")'
        result = processor.process_raw_content(content, mode='convert')
        
        assert len(result) > 0
        assert result is not None
    
    def test_process_raw_content_auto(self):
        """Test raw content processing in auto mode"""
        processor = EscapeProcessor()
        content = r'print("test\\\\escape")'
        result = processor.process_raw_content(content, mode='auto')
        
        assert len(result) > 0
        assert result is not None


class TestPreInsertionValidator:
    """Tests for PreInsertionValidator functionality"""
    
    def test_validate_syntax_compatibility_valid(self):
        """Test syntax validation with valid content"""
        validator = PreInsertionValidator()
        content = '    def new_method(self):\n        return True'
        
        is_valid, issues = validator.validate_syntax_compatibility(content, 'class_method')
        
        assert is_valid is True
        assert len(issues) == 0
    
    def test_validate_syntax_compatibility_invalid(self):
        """Test syntax validation with invalid content"""
        validator = PreInsertionValidator()
        content = 'def invalid_syntax(\n    incomplete'
        
        is_valid, issues = validator.validate_syntax_compatibility(content, 'class_method')
        
        assert is_valid is False
        assert len(issues) > 0
    
    def test_validate_indentation_consistency_valid(self):
        """Test indentation validation with valid content"""
        validator = PreInsertionValidator()
        content = '    def method(self):\n        return True\n        # comment'
        
        is_valid, issues = validator.validate_indentation_consistency(content)
        
        assert is_valid is True
        assert len(issues) == 0
    
    def test_validate_indentation_consistency_invalid(self):
        """Test indentation validation with invalid content"""
        validator = PreInsertionValidator()
        content = '   def method(self):\n      return True'  # Wrong indentation
        
        is_valid, issues = validator.validate_indentation_consistency(content)
        
        assert is_valid is False
        assert len(issues) > 0
    
    def test_validation_caching(self):
        """Test that validation results are cached"""
        validator = PreInsertionValidator()
        content = '    def test_method(self):\n        pass'
        context = 'class_method'
        
        # First validation
        result1 = validator.validate_syntax_compatibility(content, context)
        cache_size_1 = len(validator.validation_cache)
        
        # Second validation - should use cache
        result2 = validator.validate_syntax_compatibility(content, context)
        cache_size_2 = len(validator.validation_cache)
        
        assert result1 == result2
        assert cache_size_1 == cache_size_2


class TestIntegration:
    """Integration tests for all components working together"""
    
    def test_multiline_with_validation(self):
        """Test multiline pattern processing with content validation"""
        helper = UniversalPatternHelper()
        validator = PreInsertionValidator()
        
        # Usar un patrón sintácticamente válido
        pattern = 'def test_method(self):\\n    return True'
        processed_pattern = helper.process_multiline_patterns(pattern)
        
        # Validate the processed pattern
        is_valid, issues = validator.validate_syntax_compatibility(processed_pattern, 'class_method')
        
        assert '\n' in processed_pattern
        assert is_valid is True
        assert len(issues) == 0
    
    def test_block_parser_with_validator(self):
        """Test block parser with content validator"""
        parser = IntelligentBlockParser()
        validator = PreInsertionValidator()
        
        test_code = '''
class Example:
    def valid_method(self):
        return "test"
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            f.flush()
            
            try:
                block = parser.extract_complete_block(f.name, 'valid_method')
                assert block is not None
                
                content = block['content']
                is_valid, issues = validator.validate_syntax_compatibility(content, 'class_method')
                
                assert is_valid is True
                assert len(issues) == 0
            finally:
                os.unlink(f.name)