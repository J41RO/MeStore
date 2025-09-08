import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coordinators.create import CreateCoordinator
from coordinators.replace import ReplaceCoordinator
from coordinators.before import BeforeCoordinator
from coordinators.after import AfterCoordinator
from coordinators.append import AppendCoordinator

class TestPythonRegression:
    """Tests de regresión para verificar que funcionalidad Python se mantiene intacta"""
    
    def setup_method(self):
        """Crear directorio temporal para tests"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def teardown_method(self):
        """Limpiar después de cada test"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_create_coordinator_python(self):
        """Test CreateCoordinator con archivo Python"""
        coordinator = CreateCoordinator()
        test_file = 'test_create.py'
        content = 'def hello():\n    print("Hello World")'
        
        result = coordinator.execute(test_file, content=content)
        
        assert os.path.exists(test_file)
        with open(test_file, 'r') as f:
            file_content = f.read()
        assert 'def hello():' in file_content
        assert 'print("Hello World")' in file_content
    
    def test_replace_coordinator_python(self):
        """Test ReplaceCoordinator con archivo Python"""
        # Crear archivo inicial
        test_file = 'test_replace.py'
        with open(test_file, 'w') as f:
            f.write('def old_function():\n    pass')
        
        coordinator = ReplaceCoordinator()
        result = coordinator.execute(test_file, pattern='old_function', replacement='new_function')
        
        with open(test_file, 'r') as f:
            content = f.read()
        assert 'new_function' in content
        assert 'old_function' not in content
    
    def test_before_coordinator_python(self):
        """Test BeforeCoordinator con archivo Python"""
        # Crear archivo inicial
        test_file = 'test_before.py'
        with open(test_file, 'w') as f:
            f.write('class TestClass:\n    def method(self):\n        pass')
        
        coordinator = BeforeCoordinator()
        result = coordinator.execute(test_file, target='def method', content='    # Before method comment')
        
        with open(test_file, 'r') as f:
            content = f.read()
        assert '# Before method comment' in content
        assert content.find('# Before method comment') < content.find('def method')
    
    def test_after_coordinator_python(self):
        """Test AfterCoordinator con archivo Python"""
        # Crear archivo inicial
        test_file = 'test_after.py'
        with open(test_file, 'w') as f:
            f.write('class TestClass:\n    pass')
        
        coordinator = AfterCoordinator()
        result = coordinator.execute(test_file, target='class TestClass:', content='    # After class comment')
        
        with open(test_file, 'r') as f:
            content = f.read()
        assert '# After class comment' in content
        assert content.find('class TestClass:') < content.find('# After class comment')
    
    def test_append_coordinator_python(self):
        """Test AppendCoordinator con archivo Python"""
        # Crear archivo inicial
        test_file = 'test_append.py'
        with open(test_file, 'w') as f:
            f.write('def existing_function():\n    pass')
        
        coordinator = AppendCoordinator()
        result = coordinator.execute(test_file, target='', content_to_insert='\n# Appended content\nprint("End of file")')
        
        with open(test_file, 'r') as f:
            content = f.read()
        assert '# Appended content' in content
        assert 'print("End of file")' in content
        assert content.endswith('print("End of file")')
    
    def test_python_syntax_validation(self):
        """Test que los archivos generados tienen sintaxis Python válida"""
        test_file = 'test_syntax.py'
        coordinator = CreateCoordinator()
        
        # Crear archivo Python válido
        content = '''
def function_one():
    """Función de ejemplo"""
    x = 1 + 2
    return x

class ExampleClass:
    def __init__(self, value):
        self.value = value
    
    def get_value(self):
        return self.value

if __name__ == "__main__":
    obj = ExampleClass(42)
    print(f"Value: {obj.get_value()}")
'''
        
        result = coordinator.execute(test_file, content=content)
        
        # Verificar sintaxis compilando
        with open(test_file, 'r') as f:
            file_content = f.read()
        
        try:
            compile(file_content, test_file, 'exec')
            syntax_valid = True
        except SyntaxError:
            syntax_valid = False
        
        assert syntax_valid, "Archivo Python generado debe tener sintaxis válida"
