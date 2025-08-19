"""
🚀 CodeCraft Ultimate v6.0 - Core Tests
Basic test suite for core functionality
"""

import pytest
import os
import tempfile
from pathlib import Path

from codecraft_ultimate.core.engine import CodeCraftEngine, OperationResult
from codecraft_ultimate.core.command_parser import CommandParser
from codecraft_ultimate.analyzers.universal_analyzer import UniversalAnalyzer


class TestUniversalAnalyzer:
    """Tests for the UniversalAnalyzer"""
    
    def test_detect_file_type(self):
        """Test file type detection"""
        analyzer = UniversalAnalyzer()
        
        assert analyzer.detect_file_type("test.py") == "python"
        assert analyzer.detect_file_type("test.js") == "javascript"
        assert analyzer.detect_file_type("test.tsx") == "typescript"
        assert analyzer.detect_file_type("test.java") == "java"
        assert analyzer.detect_file_type("test.unknown") == "unknown"
    
    def test_analyze_complexity_python(self):
        """Test Python complexity analysis"""
        analyzer = UniversalAnalyzer()
        
        python_code = '''
def simple_function():
    return "hello"

class SimpleClass:
    def method(self):
        if True:
            for i in range(10):
                print(i)
        return self
'''
        
        result = analyzer.analyze_complexity(python_code, "test.py")
        
        assert result.functions >= 1
        assert result.classes >= 1
        assert result.lines_of_code > 0
        assert result.cyclomatic_complexity >= 1
    
    def test_extract_dependencies_python(self):
        """Test Python dependency extraction"""
        analyzer = UniversalAnalyzer()
        
        python_code = '''
import os
import sys
from datetime import datetime
from typing import List, Dict
'''
        
        dependencies = analyzer.extract_dependencies(python_code, "test.py")
        
        dep_names = [dep.name for dep in dependencies]
        assert "os" in dep_names
        assert "sys" in dep_names
        assert "datetime" in dep_names


class TestCommandParser:
    """Tests for the CommandParser"""
    
    def test_parse_simple_command(self):
        """Test parsing simple commands"""
        parser = CommandParser()
        
        result = parser.parse_command("create test.py content")
        
        assert result.operation == "create"
        assert "test.py" in result.primary_args
        assert "content" in result.primary_args
    
    def test_parse_command_with_options(self):
        """Test parsing commands with options"""
        parser = CommandParser()
        
        result = parser.parse_command("analyze-complexity . --format=json --verbose")
        
        assert result.operation == "analyze-complexity"
        assert "." in result.primary_args
        assert result.options.get("format") == "json"
        assert "verbose" in result.flags


class TestCodeCraftEngine:
    """Tests for the CodeCraftEngine"""
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        engine = CodeCraftEngine()
        
        assert engine.output_format == "structured"
        assert engine.config is not None
        assert engine.session_id is not None
    
    def test_find_project_root(self):
        """Test project root detection"""
        engine = CodeCraftEngine()
        
        # Should find current directory or parent with indicators
        project_root = engine._find_project_root()
        assert os.path.exists(project_root)


class TestOperationResult:
    """Tests for OperationResult"""
    
    def test_operation_result_creation(self):
        """Test OperationResult creation"""
        result = OperationResult(
            success=True,
            operation="test",
            message="Test successful"
        )
        
        assert result.success is True
        assert result.operation == "test" 
        assert result.message == "Test successful"
    
    def test_operation_result_to_dict(self):
        """Test OperationResult to dict conversion"""
        result = OperationResult(
            success=True,
            operation="test",
            message="Test successful",
            data={"key": "value"}
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict["success"] is True
        assert result_dict["data"]["key"] == "value"


# Integration tests with temporary files
class TestIntegration:
    """Integration tests using temporary files"""
    
    def test_create_and_analyze_file(self):
        """Test creating file and analyzing it"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file = os.path.join(temp_dir, "test.py")
            test_content = '''
def hello_world():
    """A simple hello world function"""
    name = "World"
    message = f"Hello, {name}!"
    return message

if __name__ == "__main__":
    print(hello_world())
'''
            
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            # Analyze the file
            analyzer = UniversalAnalyzer()
            complexity = analyzer.analyze_complexity(test_content, test_file)
            dependencies = analyzer.extract_dependencies(test_content, test_file)
            
            assert complexity.functions >= 1
            assert complexity.lines_of_code > 0
            assert isinstance(dependencies, list)


if __name__ == "__main__":
    pytest.main([__file__])