import pytest
import tempfile
import os
import shutil
from coordinators.after import AfterCoordinator


class TestAfterCoordinatorFunctional:
    """Tests funcionales reales para AfterCoordinator - verificación de operación real"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.coordinator = AfterCoordinator()
        self.temp_dir = tempfile.mkdtemp()
        self.test_file_path = os.path.join(self.temp_dir, "test_after.py")

    def teardown_method(self):
        """Cleanup después de cada test"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_after_simple_insertion(self):
        """Test inserción simple después del target"""
        # Crear archivo de prueba
        with open(self.test_file_path, 'w') as f:
            f.write("def hello():\n    print('Hello')\n")
        
        # Ejecutar inserción
        result = self.coordinator.execute(
            self.test_file_path, 
            "def hello():", 
            "    # Comment after hello"
        )
        
        # Verificar resultado
        assert result['success'] is True
        assert 'message' in result
        
        # Verificar contenido del archivo
        with open(self.test_file_path, 'r') as f:
            content = f.read()
        
        # Verificar que el comentario está presente
        assert "# Comment after hello" in content
        assert "def hello():" in content
        
        # Verificar orden correcto usando posiciones en contenido
        def_pos = content.find("def hello():")
        comment_pos = content.find("# Comment after hello")
        assert def_pos < comment_pos, "El comentario debe estar después de la función"

    def test_after_vs_before_differentiation(self):
        """Test que AFTER inserta después (no antes) del target"""
        with open(self.test_file_path, 'w') as f:
            f.write("def target_function():\n    existing_code = 1\n")
        
        result = self.coordinator.execute(
            self.test_file_path, 
            "def target_function():", 
            "    # After target"
        )
        
        assert result['success'] is True
        
        with open(self.test_file_path, 'r') as f:
            content = f.read()
        
        # Verificar orden usando posiciones
        target_pos = content.find("def target_function():")
        comment_pos = content.find("# After target")
        assert target_pos < comment_pos, "El comentario debe estar después del target"

    def test_after_multiline_insertion(self):
        """Test inserción de contenido multi-línea"""
        with open(self.test_file_path, 'w') as f:
            f.write("class Test:\n    def method(self):\n        return True\n")
        
        multiline_content = "        # Multi-line comment\n        # Another line"
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

    def test_after_target_not_found(self):
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

    def test_after_file_not_found(self):
        """Test error con archivo inexistente"""
        result = self.coordinator.execute(
            "nonexistent_file.py", 
            "target", 
            "content"
        )
        
        assert result['success'] is False
        assert 'error' in result

    def test_after_complex_python_file(self):
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
            "        # Get user by ID method"
        )
        
        assert result['success'] is True
        
        with open(self.test_file_path, 'r') as f:
            final_content = f.read()
        
        assert "# Get user by ID method" in final_content
        
        # Verificar que el comentario está después del método usando posiciones
        method_pos = final_content.find("def get_user(self, user_id):")
        comment_pos = final_content.find("# Get user by ID method")
        assert method_pos < comment_pos, "El comentario debe estar después del método"
        
        # Verificar sintaxis Python válida
        try:
            compile(final_content, self.test_file_path, 'exec')
        except SyntaxError:
            pytest.fail("El archivo resultante tiene errores de sintaxis")

    def test_after_preserves_file_structure(self):
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
            "def add(self, a, b):",
            "        # Addition method"
        )
        
        assert result['success'] is True
        
        with open(self.test_file_path, 'r') as f:
            final_content = f.read()
        
        # Verificar que el comentario se insertó después del método add
        add_pos = final_content.find("def add(self, a, b):")
        comment_pos = final_content.find("# Addition method")
        assert add_pos < comment_pos, "El comentario debe estar después del método add"
        
        # Verificar que toda la estructura original se mantiene
        assert "import os" in final_content
        assert "import sys" in final_content
        assert "class Calculator:" in final_content
        assert "def subtract(self, a, b):" in final_content
        assert 'if __name__ == "__main__":' in final_content

    def test_after_multiple_insertions_same_file(self):
        """Test múltiples inserciones en el mismo archivo"""
        with open(self.test_file_path, 'w') as f:
            f.write("def first():\n    pass\n\ndef second():\n    pass\n")
        
        # Primera inserción
        result1 = self.coordinator.execute(
            self.test_file_path,
            "def first():",
            "    # First function comment"
        )
        assert result1['success'] is True
        
        # Segunda inserción
        result2 = self.coordinator.execute(
            self.test_file_path,
            "def second():",
            "    # Second function comment"
        )
        assert result2['success'] is True
        
        # Verificar ambas inserciones
        with open(self.test_file_path, 'r') as f:
            content = f.read()
        
        assert "# First function comment" in content
        assert "# Second function comment" in content

    def test_after_insertion_positioning(self):
        """Test posicionamiento preciso de inserción después del target"""
        with open(self.test_file_path, 'w') as f:
            f.write("def function():\n    line1 = 1\n    line2 = 2\n    return line1 + line2\n")
        
        result = self.coordinator.execute(
            self.test_file_path,
            "line1 = 1",
            "    # Inserted after line1"
        )
        
        assert result['success'] is True
        
        with open(self.test_file_path, 'r') as f:
            content = f.read()
        
        # Verificar posicionamiento usando posiciones en contenido
        line1_pos = content.find("line1 = 1")
        comment_pos = content.find("# Inserted after line1")
        line2_pos = content.find("line2 = 2")
        
        # El comentario debe estar entre line1 y line2
        assert line1_pos < comment_pos < line2_pos, "El comentario debe estar entre line1 y line2"

    def test_after_error_handling(self):
        """Test manejo robusto de errores"""
        # Test con directorio temporal limpio
        error_file = os.path.join(self.temp_dir, "error_test.py")
        
        # Test archivo vacío
        with open(error_file, 'w') as f:
            f.write("")
        
        result = self.coordinator.execute(error_file, "nonexistent", "content")
        assert result['success'] is False
        assert 'error' in result