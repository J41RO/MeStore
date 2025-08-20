"""
Comprehensive test suite for content handler - problematic cases
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_content_handler_import():
    """Test content handler imports correctly"""
    try:
        from utils.content_handler import content_handler, ContentType, ContentValidationResult
        from utils.template_engine import template_engine
        return True
    except Exception as e:
        print(f"Content handler import test failed: {e}")
        return False

def test_problematic_character_escape():
    """Test escape handling for problematic characters"""
    try:
        from utils.content_handler import content_handler
        
        # Test cases with problematic characters
        test_cases = [
            ('print("Hello \"World\"")', 'python_string'),
            ('{"key": "value with \"nested\" quotes"}', 'json_content'),
            ('echo "Hello $USER & friends"', 'shell_command'),
        ]
        
        for content, context in test_cases:
            escaped = content_handler.escape_content(content, context)
            assert isinstance(escaped, str), f"Escaped content should be string for {context}"
            assert len(escaped) >= len(content), f"Escaped content should not be shorter for {context}"
        
        return True
    except Exception as e:
        print(f"Problematic character escape test failed: {e}")
        return False

def test_content_type_detection():
    """Test intelligent content type detection"""
    try:
        from utils.content_handler import content_handler, ContentType
        
        test_cases = [
            ('def hello(): pass', ContentType.PYTHON),
            ('{"key": "value"}', ContentType.JSON),
            ('function test() { return true; }', ContentType.JAVASCRIPT),
            ('SELECT * FROM table', ContentType.SQL),
            ('Line 1\nLine 2\nLine 3\nLine 4', ContentType.MULTILINE),
            ('f"Hello {name}"', ContentType.TEMPLATE),
            ('Simple text', ContentType.PLAIN_TEXT),
        ]
        
        for content, expected_type in test_cases:
            detected_type = content_handler.detect_content_type(content)
            assert detected_type == expected_type, f"Expected {expected_type}, got {detected_type} for: {content}"
        
        return True
    except Exception as e:
        print(f"Content type detection test failed: {e}")
        return False

def test_incremental_mode():
    """Test incremental mode for large content"""
    try:
        from utils.content_handler import content_handler
        
        # Small content (should use direct mode)
        small_content = "Line 1\nLine 2\nLine 3"
        small_result = content_handler.process_large_content(small_content)
        assert small_result['mode'] == 'direct', "Small content should use direct mode"
        
        # Large content (should use incremental mode)
        large_content = '\n'.join([f"Line {i}" for i in range(1, 26)])  # 25 lines
        large_result = content_handler.process_large_content(large_content)
        assert large_result['mode'] == 'incremental', "Large content should use incremental mode"
        assert large_result['total_lines'] == 25, "Should count lines correctly"
        assert len(large_result['chunks']) > 1, "Should create multiple chunks"
        
        return True
    except Exception as e:
        print(f"Incremental mode test failed: {e}")
        return False

def test_content_validation():
    """Test content validation system"""
    try:
        from utils.content_handler import content_handler
        
        # Valid Python content
        valid_python = "def hello():\n    return 'world'"
        result = content_handler.validate_content(valid_python)
        assert result.is_valid, "Valid Python should pass validation"
        
        # Invalid Python content (syntax error)
        invalid_python = "def hello(\n    return 'world'"  # Missing closing parenthesis
        result = content_handler.validate_content(invalid_python)
        assert not result.is_valid, "Invalid Python should fail validation"
        assert len(result.issues) > 0, "Should report issues"
        
        # Valid JSON
        valid_json = '{"key": "value", "number": 42}'
        result = content_handler.validate_content(valid_json)
        assert result.is_valid, "Valid JSON should pass validation"
        
        # Invalid JSON
        invalid_json = '{"key": "value", "number": 42'  # Missing closing brace
        result = content_handler.validate_content(invalid_json)
        assert not result.is_valid, "Invalid JSON should fail validation"
        
        return True
    except Exception as e:
        print(f"Content validation test failed: {e}")
        return False

def test_template_system():
    """Test template generation system"""
    try:
        from utils.template_engine import template_engine
        
        # Test framework detection
        frameworks = template_engine.detect_project_frameworks()
        assert isinstance(frameworks, list), "Framework detection should return list"
        
        # Test template suggestions
        suggestions = template_engine.suggest_templates_for_content('api endpoint')
        assert isinstance(suggestions, list), "Template suggestions should return list"
        
        # Test template generation if frameworks available
        if frameworks:
            framework = frameworks[0]
            templates = template_engine.project_templates.get(framework, {})
            if templates:
                template_type = list(templates.keys())[0]
                
                # Get required parameters
                params = template_engine.get_template_parameters(framework, template_type)
                
                # Create dummy parameters
                template_kwargs = {param: f"test_{param}" for param in params}
                
                # Generate template
                generated = template_engine.get_template(framework, template_type, **template_kwargs)
                assert isinstance(generated, str), "Template generation should return string"
                assert len(generated) > 0, "Generated template should not be empty"
        
        return True
    except Exception as e:
        print(f"Template system test failed: {e}")
        return False

def test_prepare_content_integration():
    """Test main prepare_content method with all features"""
    try:
        from utils.content_handler import content_handler
        
        # Test with simple content
        simple_content = 'print("Hello World")'
        result = content_handler.prepare_content(
            simple_content,
            target_context='python_string',
            validate=True
        )
        
        assert 'original_content' in result, "Result should contain original content"
        assert 'processed_content' in result, "Result should contain processed content"
        assert 'content_type' in result, "Result should contain content type"
        assert 'validation_result' in result, "Result should contain validation result"
        assert result['escape_applied'], "Escape should be applied"
        
        # Test with large content
        large_content = '\n'.join([f"print('Line {i}')" for i in range(1, 26)])
        result = content_handler.prepare_content(large_content, validate=True)
        
        assert result['processing_mode'] == 'incremental', "Large content should use incremental mode"
        
        return True
    except Exception as e:
        print(f"Prepare content integration test failed: {e}")
        return False

def test_edge_cases():
    """Test edge cases and corner scenarios"""
    try:
        from utils.content_handler import content_handler
        
        # Empty content
        result = content_handler.prepare_content("", validate=True)
        assert not result['validation_result'].is_valid, "Empty content should fail validation"
        
        # Only whitespace
        result = content_handler.prepare_content("   \n\t   ", validate=True)
        assert not result['validation_result'].is_valid, "Whitespace-only content should fail validation"
        
        # Very long line
        long_line = "x" * 1000
        result = content_handler.prepare_content(long_line)
        assert len(result['processed_content']) >= len(long_line), "Long line should be handled"
        
        # Unicode content
        unicode_content = "print('Hello 🌍')"
        result = content_handler.prepare_content(unicode_content)
        assert result['validation_result'].is_valid, "Unicode content should be valid"
        
        return True
    except Exception as e:
        print(f"Edge cases test failed: {e}")
        return False

def test_performance():
    """Test performance of content handler operations"""
    try:
        from utils.content_handler import content_handler
        import time
        
        # Test escape performance
        test_content = 'print("Hello \"World\" with \\"quotes\\" everywhere")'
        
        start_time = time.time()
        for _ in range(100):
            content_handler.escape_content(test_content)
        escape_time = time.time() - start_time
        
        assert escape_time < 1.0, f"Escape operations should be reasonable, took {escape_time:.3f}s"
        
        # Test validation performance
        start_time = time.time()
        for _ in range(50):
            content_handler.validate_content(test_content)
        validation_time = time.time() - start_time
        
        assert validation_time < 2.0, f"Validation should be reasonable, took {validation_time:.3f}s"
        
        # Get statistics
        stats = content_handler.get_statistics()
        assert 'performance_stats' in stats, "Statistics should include performance data"
        
        print(f"✅ Performance: Escape {escape_time:.3f}s, Validation {validation_time:.3f}s")
        return True
    except Exception as e:
        print(f"Performance test failed: {e}")
        return False

def test_integration_with_logging():
    """Test integration with logging system"""
    try:
        from utils.content_handler import content_handler
        from utils.logger import logger
        
        # Test that operations integrate with logging
        logger.operation_start("Content Handler Test", "Testing content handler with logging")
        
        # Process content with logging
        test_content = "def test_function():\n    return 'success'"
        result = content_handler.prepare_content(test_content, validate=True)
        
        if result['validation_result'].is_valid:
            logger.success("Content validation passed")
        else:
            logger.warning("Content validation failed")
        
        logger.operation_end("Content Handler Test", success=True)
        
        return True
    except Exception as e:
        print(f"Integration with logging test failed: {e}")
        return False

def run_all_content_handler_tests():
    """Run all content handler tests and report results"""
    tests = [
        ("Content Handler Import", test_content_handler_import),
        ("Problematic Character Escape", test_problematic_character_escape),
        ("Content Type Detection", test_content_type_detection),
        ("Incremental Mode", test_incremental_mode),
        ("Content Validation", test_content_validation),
        ("Template System", test_template_system),
        ("Prepare Content Integration", test_prepare_content_integration),
        ("Edge Cases", test_edge_cases),
        ("Performance", test_performance),
        ("Integration with Logging", test_integration_with_logging),
    ]
    
    passed = 0
    total = len(tests)
    
    print("🧪 RUNNING CONTENT HANDLER PROBLEMATIC CASES TESTS")
    print("=" * 70)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("=" * 70)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL CONTENT HANDLER TESTS PASSED! Extreme system is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Review implementation.")
        return False

if __name__ == "__main__":
    success = run_all_content_handler_tests()
    sys.exit(0 if success else 1)
