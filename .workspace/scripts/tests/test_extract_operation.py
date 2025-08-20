import os
import tempfile

import pytest
from surgical_modifier_ultimate import EnhancedSurgicalModifier


class TestExtractOperation:
    """Tests para la nueva operación EXTRACT"""

    @pytest.fixture
    def temp_files(self):
        """Fixture para crear archivos temporales de test"""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_file = os.path.join(temp_dir, "source.py")
            dest_file = os.path.join(temp_dir, "dest.py")
            yield source_file, dest_file

    def test_extract_function_complete(self, temp_files):
        """Test extracción de función completa desde archivo fuente"""
        source_file, dest_file = temp_files

        # Crear archivo fuente con función de test
        source_content = '''def simple_function():
    """Una función simple para test"""
    return "hello world"

def another_function():
    return "otro contenido"
'''

        # Crear archivo destino inicial
        dest_content = "# Archivo destino\n"

        with open(source_file, "w") as f:
            f.write(source_content)
        with open(dest_file, "w") as f:
            f.write(dest_content)

        # Ejecutar extracción
        modifier = EnhancedSurgicalModifier()
        result = modifier._extract_content(
            source_file, dest_file, "def simple_function():", ""
        )

        # Verificaciones
        assert result == True, "Extracción debe ser exitosa"

        # Verificar que función se copió al destino
        with open(dest_file, "r") as f:
            dest_result = f.read()

        assert "def simple_function():" in dest_result
        assert '"Una función simple para test"' in dest_result
        assert 'return "hello world"' in dest_result

        # Verificar que archivo original permanece intacto
        with open(source_file, "r") as f:
            source_result = f.read()

        assert (
            source_result == source_content
        ), "Archivo original debe permanecer sin cambios"
        assert "def simple_function():" in source_result
        assert "def another_function():" in source_result

    def test_extract_with_imports_detection(self, temp_files):
        """Test detección automática de imports necesarios para función extraída"""
        source_file, dest_file = temp_files

        # Crear archivo fuente con imports y función que los usa
        source_content = '''import os
import sys
from datetime import datetime
import json

def function_with_imports():
    """Función que usa varios imports"""
    current_time = datetime.now()
    file_path = os.path.join("test", "file.txt")
    data = {"time": current_time.isoformat()}
    return json.dumps(data)

def simple_function():
    return "no imports needed"
'''

        # Crear archivo destino con algunos imports existentes
        dest_content = """import sys
# Archivo destino con import existente
"""

        with open(source_file, "w") as f:
            f.write(source_content)
        with open(dest_file, "w") as f:
            f.write(dest_content)

        # Ejecutar extracción
        modifier = EnhancedSurgicalModifier()
        result = modifier._extract_content(
            source_file, dest_file, "def function_with_imports():", ""
        )

        # Verificaciones
        assert result == True, "Extracción debe ser exitosa"

        # Verificar que función se copió al destino
        with open(dest_file, "r") as f:
            dest_result = f.read()

        # Verificar que imports necesarios se detectaron e incluyeron
        assert "import os" in dest_result
        assert "from datetime import datetime" in dest_result
        assert "import json" in dest_result
        assert "def function_with_imports():" in dest_result

        # Verificar que import sys no se duplicó (ya existía)
        sys_count = dest_result.count("import sys")
        assert (
            sys_count == 1
        ), f"import sys debe aparecer solo una vez, encontrado {sys_count} veces"

        # Verificar que archivo original permanece intacto
        with open(source_file, "r") as f:
            source_result = f.read()
        assert (
            source_result == source_content
        ), "Archivo original debe permanecer sin cambios"

    def test_extract_preserve_original(self, temp_files):
        """Test que archivo fuente NO se modifica después de extracción"""
        source_file, dest_file = temp_files

        # Crear archivo fuente con múltiples funciones
        source_content = '''#!/usr/bin/env python3
"""Archivo fuente con múltiples funciones"""

import hashlib

def target_function():
    """Función objetivo para extraer"""
    data = "test data"
    return hashlib.md5(data.encode()).hexdigest()

def keep_function():
    """Esta función debe permanecer"""
    return "should stay"

class KeepClass:
    """Esta clase debe permanecer"""
    def method(self):
        return "class method"

# Comentario final que debe preservarse
'''

        dest_content = "# Archivo destino vacío\n"

        with open(source_file, "w") as f:
            f.write(source_content)
        with open(dest_file, "w") as f:
            f.write(dest_content)

        # Calcular hash del archivo original antes de extracción
        import hashlib

        with open(source_file, "rb") as f:
            original_hash = hashlib.md5(f.read()).hexdigest()

        # Obtener stats del archivo original
        original_stats = os.stat(source_file)

        # Ejecutar extracción
        modifier = EnhancedSurgicalModifier()
        result = modifier._extract_content(
            source_file, dest_file, "def target_function():", ""
        )

        # Verificaciones de preservación
        assert result == True, "Extracción debe ser exitosa"

        # Verificar que hash del archivo original no cambió
        with open(source_file, "rb") as f:
            new_hash = hashlib.md5(f.read()).hexdigest()

        assert (
            original_hash == new_hash
        ), "Hash del archivo original cambió - archivo fue modificado"

        # Verificar que contenido original está intacto
        with open(source_file, "r") as f:
            current_content = f.read()

        assert (
            current_content == source_content
        ), "Contenido del archivo original fue modificado"
        assert "def target_function():" in current_content
        assert "def keep_function():" in current_content
        assert "class KeepClass:" in current_content
        assert "#!/usr/bin/env python3" in current_content

        # Verificar que función se copió al destino
        with open(dest_file, "r") as f:
            dest_result = f.read()

        assert "def target_function():" in dest_result
        assert "import hashlib" in dest_result  # Import debe detectarse e incluirse
