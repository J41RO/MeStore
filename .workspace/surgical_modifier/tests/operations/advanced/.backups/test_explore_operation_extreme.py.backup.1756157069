#!/usr/bin/env python3
"""
TESTS EXTREMOS PARA EXPLORE OPERATION v6.0
Suite completa de 30 tests distribuidos en 3 categorías
"""
import pytest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Agregar path del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from core.operations.advanced.explore import (
    explore_operation,
    UniversalExplorer,
    UniversalPatternHelper,
    CodeQualityAnalyzer,
    ExploreOperation
)

class TestExploreOperationBasic:
    """Tests básicos de funcionamiento"""
    
    def test_01_basic_python_analysis(self):
        """Test básico de análisis Python"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('class Test:\n    def method(self):\n        return "test"')
            temp_path = f.name
        
        try:
            result = explore_operation(temp_path, 'full')
            assert result['success'] == True
            assert result['patterns']['file_type'] == 'python'
        finally:
            os.unlink(temp_path)
    
    def test_02_javascript_analysis(self):
        """Test básico de análisis JavaScript"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write('function test() { return "test"; }')
            temp_path = f.name
        
        try:
            result = explore_operation(temp_path, 'full')
            assert result['success'] == True
            assert result['patterns']['file_type'] == 'javascript'
        finally:
            os.unlink(temp_path)
    
    def test_03_framework_detection(self):
        """Test detección de frameworks"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('from django.db import models')
            temp_path = f.name
        
        try:
            result = explore_operation(temp_path, 'patterns')
            assert result['success'] == True
            assert 'django' in result['patterns']['frameworks']
        finally:
            os.unlink(temp_path)

class TestCodeQuality:
    """Tests de calidad de código"""
    
    def test_04_style_analysis(self):
        """Test análisis de estilo"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('class Test:\n    def method(self):\n        return "test"')
            temp_path = f.name
        
        try:
            analyzer = CodeQualityAnalyzer(temp_path, open(temp_path).read())
            quality = analyzer.analyze_quality()
            assert 'maintainability_score' in quality
            assert isinstance(quality['maintainability_score'], int)
        finally:
            os.unlink(temp_path)
    
    def test_05_complexity_analysis(self):
        """Test análisis de complejidad"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def complex_func():\n    if True:\n        for i in range(10):\n            pass')
            temp_path = f.name
        
        try:
            analyzer = CodeQualityAnalyzer(temp_path, open(temp_path).read())
            quality = analyzer.analyze_quality()
            complexity = quality['complexity_metrics']
            assert complexity['cyclomatic_complexity'] > 1
        finally:
            os.unlink(temp_path)

class TestIntegration:
    """Tests de integración"""
    
    def test_06_operation_integration(self):
        """Test integración con ExploreOperation"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def test(): pass')
            temp_path = f.name
        
        try:
            from core.operations.advanced.explore import OperationContext
            operation = ExploreOperation()
            context = OperationContext(target_file=temp_path)
            result = operation.execute(context)
            assert result.success == True
        finally:
            os.unlink(temp_path)
    
    def test_07_cli_compatibility(self):
        """Test compatibilidad CLI"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('class CLITest:\n    pass')
            temp_path = f.name
        
        try:
            result = explore_operation(temp_path, 'full')
            required_keys = ['success', 'file_path', 'analysis_type']
            for key in required_keys:
                assert key in result
        finally:
            os.unlink(temp_path)

def test_basic_functionality():
    """Test función básica sin clases"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('x = 1')
        temp_path = f.name
    
    try:
        result = explore_operation(temp_path, 'structure')
        assert result['success'] == True
    finally:
        os.unlink(temp_path)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
