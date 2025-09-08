import pytest
import tempfile
import os
from coordinators.before import BeforeCoordinator


class TestBeforeCoordinatorFunctional:
    """Tests funcionales reales para BeforeCoordinator - verificación de operación real"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.coordinator = BeforeCoordinator()
        self.temp_dir = tempfile.mkdtemp()
        self.test_file_path = os.path.join(self.temp_dir, "test_before.py")

    def teardown_method(self):
        """Cleanup después de cada test"""
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_before_simple_insertion(self):
        """Test inserción simple antes del target"""
        # Crear archivo de prueba
        with open(self.test_file_path, 'w') as f:
            f.write("def hello():\n    print('Hello')\n")
        
        # Ejecutar inserción
        result = self.coordinator.execute(
            self.test_file_path, 
            "def hello():", 
            "# Comment before hello"
        )
        
        # Verificar resultado
        assert result['success'] is True
        assert 'message' in result
        
        # Verificar contenido del archivo
        with open(self.test_file_path, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        assert "# Comment before hello" in lines
        assert "def hello():" in lines
        
        # Verificar orden correcto (comment antes de def)
        comment_index = next(i for i, line in enumerate(lines) if "# Comment before hello" in line)
        def_index = next(i for i, line in enumerate(lines) if "def hello():" in line)
        assert comment_index < def_index

    def test_before_multiline_insertion(self):
        """Test inserción de contenido multi-línea"""
        with open(self.test_file_path, 'w') as f:
            f.write("class Test:\n    def method(self):\n        pass\n")
        
        multiline_content = "    # Multi-line comment\n    # Another line"
        result = self.coordinator.execute(
            self.test_file_path, 
            "def method(self):", 
            multiline_content
        )
        
        assert result['success'] is True
        
        with open(self.test_file_path, 'r') as f:
            content = f.read()
        
        assert "# Multi-line comment" in content
        assert "# Another line" in content

    def test_before_target_not_found(self):
        """Test error cuando target no existe"""
        with open(self.test_file_path, 'w') as f:
            f.write("def hello():\n    pass\n")
        
        result = self.coordinator.execute(
            self.test_file_path, 
            "nonexistent_target", 
            "content"
        )
        
        assert result['success'] is False
        assert 'error' in result
        assert "not found" in result['error'].lower()

    def test_before_file_not_found(self):
        """Test error con archivo inexistente"""
        result = self.coordinator.execute(
            "nonexistent_file.py", 
            "target", 
            "content"
        )
        
        assert result['success'] is False
        assert 'error' in result

    def test_before_complex_python_file(self):
        """Test inserción en archivo Python complejo"""
        complex_content = '''class UserService:
    def __init__(self):
        self.users = []
    
    def get_user(self, user_id):
        return self.find_user(user_id)
    
    def find_user(self, user_id):
        return None
'''
        
        with open(self.test_file_path, 'w') as f:
            f.write(complex_content)
        
        result = self.coordinator.execute(
            self.test_file_path,
            "def get_user(self, user_id):",
            "    # Get user by ID"
        )
        
        assert result['success'] is True
        
        with open(self.test_file_path, 'r') as f:
            final_content = f.read()
        
        assert "# Get user by ID" in final_content
        
        # Verificar sintaxis Python válida
        try:
            compile(final_content, self.test_file_path, 'exec')
        except SyntaxError:
            pytest.fail("El archivo resultante tiene errores de sintaxis")

    def test_before_preserves_file_structure(self):
        """Test que la estructura del archivo se preserva correctamente"""
        original_content = """import os
import sys

class Calculator:
    def add(self, a, b):
        return a + b
        
    def subtract(self, a, b):
        return a - b

if __name__ == "__main__":
    calc = Calculator()
    print(calc.add(1, 2))
"""
        
        with open(self.test_file_path, 'w') as f:
            f.write(original_content)
        
        result = self.coordinator.execute(
            self.test_file_path,
            "class Calculator:",
            "# Calculator class for basic operations"
        )
        
        assert result['success'] is True
        
        with open(self.test_file_path, 'r') as f:
            final_content = f.read()
        
        # Verificar que el comentario se insertó antes de la clase
        lines = final_content.split('\n')
        comment_line = next(i for i, line in enumerate(lines) if "# Calculator class" in line)
        class_line = next(i for i, line in enumerate(lines) if "class Calculator:" in line)
        assert comment_line < class_line
        
        # Verificar que toda la estructura original se mantiene
        assert "import os" in final_content
        assert "import sys" in final_content
        assert "def add(self, a, b):" in final_content
        assert "def subtract(self, a, b):" in final_content
        assert 'if __name__ == "__main__":' in final_content

    def test_before_multiple_insertions_same_file(self):
        """Test múltiples inserciones en el mismo archivo"""
        with open(self.test_file_path, 'w') as f:
            f.write("def first():\n    pass\n\ndef second():\n    pass\n")
        
        # Primera inserción
        result1 = self.coordinator.execute(
            self.test_file_path,
            "def first():",
            "# First function comment"
        )
        assert result1['success'] is True
        
        # Segunda inserción
        result2 = self.coordinator.execute(
            self.test_file_path,
            "def second():",
            "# Second function comment"
        )
        assert result2['success'] is True
        
        # Verificar ambas inserciones
        with open(self.test_file_path, 'r') as f:
            content = f.read()
        
        assert "# First function comment" in content
        assert "# Second function comment" in content