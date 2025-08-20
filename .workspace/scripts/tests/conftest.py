"""
Configuración común y fixtures para tests de Surgical Modifier Ultimate v5.3
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# Agregar el directorio padre al path para importar el módulo principal
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_dir():
    """Crea un directorio temporal para tests"""
    temp_path = tempfile.mkdtemp(prefix="surgical_modifier_test_")
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)


@pytest.fixture
def sample_python_file(temp_dir):
    """Crea un archivo Python de ejemplo para testing"""
    content = '''#!/usr/bin/env python3
"""Archivo de ejemplo para testing"""

class SampleClass:
    def __init__(self):
        self.name = "test"
    
    def sample_method(self):
        return "original_value"
    
    def another_method(self):
        print("Hello World")

def sample_function():
    return 42

if __name__ == "__main__":
    obj = SampleClass()
    print(obj.sample_method())
'''
    file_path = os.path.join(temp_dir, "sample.py")
    with open(file_path, "w") as f:
        f.write(content)
    return file_path


@pytest.fixture
def sample_text_file(temp_dir):
    """Crea un archivo de texto simple para testing"""
    content = """Line 1: Original content
Line 2: More content
Line 3: Final line"""
    file_path = os.path.join(temp_dir, "sample.txt")
    with open(file_path, "w") as f:
        f.write(content)
    return file_path


@pytest.fixture
def backup_config():
    """Configuración para tests de backup"""
    return {"enabled": True, "keep_backups": False, "max_backups": 5}
