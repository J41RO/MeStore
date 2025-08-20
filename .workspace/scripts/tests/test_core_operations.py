"""
Tests exhaustivos para operaciones core del SurgicalModifier Ultimate
Cubre: create, replace, after, before, append
"""

import os
import tempfile
from pathlib import Path

import pytest
from surgical_modifier_ultimate import SurgicalModifierUltimate


class TestCreateOperation:
    """Tests para operación CREATE - creación de archivos y directorios"""

    def setup_method(self):
        """Setup para cada test"""
        self.modifier = SurgicalModifierUltimate()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup después de cada test"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_create_simple_file(self):
        """Test creación básica de archivo nuevo"""
        file_path = os.path.join(self.temp_dir, "test_file.py")
        content = "print('Hello World')"

        result = self.modifier.execute("create", file_path, "", content)

        assert result["success"] is True, "Create operation should succeed"
        assert "file_path" in result, "Result should contain file_path"
        assert os.path.exists(file_path), "File should be created"

        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        assert content in file_content, "Content should be written correctly"

    def test_create_with_auto_directory_creation(self):
        """Test creación automática de directorios padre"""
        nested_path = os.path.join(
            self.temp_dir, "subdir1", "subdir2", "nested_file.py"
        )
        content = "# Nested file content"

        result = self.modifier.execute("create", nested_path, "", content)

        assert result["success"] is True, "Create with nested dirs should succeed"
        assert result["operation"] == "create", "Operation should be create"
        assert os.path.exists(nested_path), "Nested file should be created"
        assert os.path.exists(
            os.path.dirname(nested_path)
        ), "Parent directories should be created"

        with open(nested_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        assert content in file_content, "Content should be preserved in nested file"

    def test_create_overwrite_existing_file(self):
        """Test sobrescritura de archivo existente"""
        file_path = os.path.join(self.temp_dir, "existing_file.py")
        original_content = "original content"
        new_content = "new content replacing original"

        # Crear archivo inicial
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        result = self.modifier.execute("create", file_path, "", new_content)

        assert result["success"] is True, "Create should overwrite existing file"
        assert result["operation"] == "create", "Operation should be create"

        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        assert new_content in file_content, "New content should replace original"
        assert original_content not in file_content, "Original content should be gone"

    def test_create_with_utf8_encoding(self):
        """Test creación con caracteres UTF-8 especiales"""
        file_path = os.path.join(self.temp_dir, "unicode_test.py")
        content = "# Contenido con ñáéíóú y emojis 🚀📊✅"

        result = self.modifier.execute("create", file_path, "", content)

        assert result["success"] is True, "Create with UTF-8 should succeed"
        assert result["operation"] == "create", "Operation should be create"

        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        assert (
            content == file_content.strip()
        ), "UTF-8 content should be preserved exactly"

    def test_create_empty_file(self):
        """Test creación de archivo vacío"""
        file_path = os.path.join(self.temp_dir, "empty_file.py")

        result = self.modifier.execute("create", file_path, "", "")

        assert result["success"] is True, "Create empty file should succeed"
        assert result["operation"] == "create", "Operation should be create"
        assert os.path.exists(file_path), "Empty file should be created"

        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        assert file_content == "", "File should be truly empty"


class TestReplaceOperation:
    """Tests para operación REPLACE - reemplazo directo con validación"""

    def setup_method(self):
        """Setup para cada test"""
        self.modifier = SurgicalModifierUltimate()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup después de cada test"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_replace_basic_line(self):
        """Test reemplazo básico de línea completa"""
        file_path = os.path.join(self.temp_dir, "test_replace.py")
        original_content = """line1 = 'original'
line2 = 'keep this'
line3 = 'original'"""

        # Crear archivo con contenido inicial
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        result = self.modifier.execute(
            "replace", file_path, "line1 = 'original'", "line1 = 'replaced'"
        )

        assert result["success"] is True, "Replace operation should succeed"
        assert result["operation"] == "replace", "Operation should be replace"

        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        assert "line1 = 'replaced'" in file_content, "Replacement should be applied"
        assert "line2 = 'keep this'" in file_content, "Other lines should be preserved"

    def test_replace_partial_in_line(self):
        """Test reemplazo parcial dentro de una línea"""
        file_path = os.path.join(self.temp_dir, "test_partial.py")
        original_content = "def function_old_name(param1, param2):"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        result = self.modifier.execute(
            "replace", file_path, "function_old_name", "function_new_name"
        )

        assert result["success"] is True, "Partial replace should succeed"

        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        assert "function_new_name" in file_content, "Function name should be replaced"
        assert "(param1, param2):" in file_content, "Parameters should be preserved"

    def test_replace_pattern_validation(self):
        """Test validación de patrón existente"""
        file_path = os.path.join(self.temp_dir, "test_validation.py")
        content = "existing_line = 'value'"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Test: patrón que SÍ existe
        result = self.modifier.execute(
            "replace", file_path, "existing_line", "new_line"
        )
        assert result["success"] is True, "Replace of existing pattern should succeed"

        # Verificar cambio aplicado
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        assert "new_line" in file_content, "Pattern should be replaced"

    def test_replace_nonexistent_pattern(self):
        """Test error cuando patrón no existe"""
        file_path = os.path.join(self.temp_dir, "test_error.py")
        content = "existing_content = 'value'"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Test: patrón que NO existe
        result = self.modifier.execute(
            "replace", file_path, "nonexistent_pattern", "replacement"
        )

        # El resultado puede ser False o un dict con success=False
        if isinstance(result, dict):
            assert (
                result["success"] is False
            ), "Replace of nonexistent pattern should fail"
        else:
            assert result is False, "Replace of nonexistent pattern should return False"

        # Verificar que contenido original no cambió
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        assert (
            content == file_content.strip()
        ), "Original content should be preserved on failed replace"

    def test_replace_preserve_content(self):
        """Test preservación de contenido restante"""
        file_path = os.path.join(self.temp_dir, "test_preserve.py")
        original_content = """# Header comment
import os
import sys

def main():
   old_variable = 'replace_me'
   other_variable = 'keep_me'
   return True

if __name__ == '__main__':
   main()"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        result = self.modifier.execute(
            "replace",
            file_path,
            "old_variable = 'replace_me'",
            "new_variable = 'replaced'",
        )

        assert result["success"] is True, "Replace should succeed"

        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        # Verificar reemplazo correcto
        assert (
            "new_variable = 'replaced'" in file_content
        ), "Target line should be replaced"

        # Verificar preservación del resto
        assert "# Header comment" in file_content, "Header should be preserved"
        assert "import os" in file_content, "Imports should be preserved"
        assert (
            "other_variable = 'keep_me'" in file_content
        ), "Other variables should be preserved"
        assert (
            "if __name__ == '__main__':" in file_content
        ), "Main block should be preserved"


class TestAfterOperation:
    """Tests para operación AFTER - inserción después preservando indentación"""

    def setup_method(self):
        """Setup para cada test"""
        self.modifier = SurgicalModifierUltimate()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup después de cada test"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_after_basic_insertion(self):
        """Test inserción básica después de línea específica"""
        file_path = os.path.join(self.temp_dir, "test_after.py")
        original_content = """import os
import sys
# Insert after this comment
print('existing code')"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        result = self.modifier.execute(
            "after", file_path, "# Insert after this comment", "import json"
        )

        assert result["success"] is True, "After operation should succeed"
        assert result["operation"] == "after", "Operation should be after"

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Verificar que import json está después del comentario
        comment_index = -1
        json_index = -1
        for i, line in enumerate(lines):
            if "# Insert after this comment" in line:
                comment_index = i
            if "import json" in line:
                json_index = i

        assert comment_index >= 0, "Comment line should exist"
        assert json_index >= 0, "New import should exist"
        assert (
            json_index == comment_index + 1
        ), "New import should be right after comment"

    def test_after_preserve_indentation(self):
        """Test preservación de indentación existente"""
        file_path = os.path.join(self.temp_dir, "test_indent.py")
        original_content = """class MyClass:
    def __init__(self):
        self.value = 'original'
        # Add new method after this comment
        pass

    def existing_method(self):
        return True"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        new_method = """    def new_method(self):
        return 'new_method_result'"""

        result = self.modifier.execute(
            "after", file_path, "# Add new method after this comment", new_method
        )

        assert result["success"] is True, "After with indentation should succeed"

        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        assert "def new_method(self):" in file_content, "New method should be added"
        assert (
            "return 'new_method_result'" in file_content
        ), "Method body should be preserved"
        assert (
            "def existing_method(self):" in file_content
        ), "Existing method should remain"

    def test_after_multiple_insertions(self):
        """Test inserción múltiple después del mismo patrón"""
        file_path = os.path.join(self.temp_dir, "test_multiple.py")
        original_content = """# Configuration section
DEBUG = True
# Add more configs here"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        # Primera inserción
        result1 = self.modifier.execute(
            "after", file_path, "# Add more configs here", "VERBOSE = False"
        )
        assert result1["success"] is True, "First after insertion should succeed"

        # Segunda inserción después del mismo comentario
        result2 = self.modifier.execute(
            "after", file_path, "# Add more configs here", "LOG_LEVEL = 'INFO'"
        )
        assert result2["success"] is True, "Second after insertion should succeed"

        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        assert "VERBOSE = False" in file_content, "First insertion should exist"
        assert "LOG_LEVEL = 'INFO'" in file_content, "Second insertion should exist"
        assert "DEBUG = True" in file_content, "Original content should be preserved"

    def test_after_pattern_validation(self):
        """Test validación de patrón requerido"""
        file_path = os.path.join(self.temp_dir, "test_validation.py")
        content = """existing_line = 'value'
another_line = 'another'"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Test: patrón que SÍ existe
        result = self.modifier.execute(
            "after", file_path, "existing_line = 'value'", "new_line = 'inserted'"
        )
        assert result["success"] is True, "After with existing pattern should succeed"

        # Test: patrón que NO existe
        result_fail = self.modifier.execute(
            "after", file_path, "nonexistent_pattern", "should_not_be_added"
        )
        if isinstance(result_fail, dict):
            assert (
                result_fail["success"] is False
            ), "After with nonexistent pattern should fail"
        else:
            assert (
                result_fail is False
            ), "After with nonexistent pattern should return False"

        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        assert "new_line = 'inserted'" in file_content, "Valid insertion should exist"
        assert (
            "should_not_be_added" not in file_content
        ), "Invalid insertion should not exist"

    def test_after_newline_handling(self):
        """Test manejo correcto de newlines"""
        file_path = os.path.join(self.temp_dir, "test_newlines.py")
        original_content = """line1 = 'first'
line2 = 'second'
line3 = 'third'"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        result = self.modifier.execute(
            "after", file_path, "line2 = 'second'", "inserted_line = 'inserted'"
        )

        assert result["success"] is True, "After insertion should succeed"

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Verificar orden correcto
        line_contents = [line.strip() for line in lines if line.strip()]
        expected_order = [
            "line1 = 'first'",
            "line2 = 'second'",
            "inserted_line = 'inserted'",
            "line3 = 'third'",
        ]

        for expected in expected_order:
            assert (
                expected in line_contents
            ), f"Line '{expected}' should exist in correct order"

        # Verificar que inserted_line está entre line2 y line3
        line2_idx = line_contents.index("line2 = 'second'")
        inserted_idx = line_contents.index("inserted_line = 'inserted'")
        line3_idx = line_contents.index("line3 = 'third'")

        assert (
            line2_idx < inserted_idx < line3_idx
        ), "Inserted line should be between line2 and line3"


class TestBeforeOperation:
    """Tests para operación BEFORE - inserción antes con contexto"""

    def setup_method(self):
        """Setup para cada test"""
        self.modifier = SurgicalModifierUltimate()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup después de cada test"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_before_basic_insertion(self):
        """Test inserción básica antes de línea específica"""
        file_path = os.path.join(self.temp_dir, "test_before.py")
        original_content = """import os
import sys
# Insert before this comment
print('existing code')"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        result = self.modifier.execute(
            "before", file_path, "# Insert before this comment", "import json"
        )

        assert result["success"] is True, "Before operation should succeed"
        assert result["operation"] == "before", "Operation should be before"

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Verificar que import json está antes del comentario
        comment_index = -1
        json_index = -1
        for i, line in enumerate(lines):
            if "# Insert before this comment" in line:
                comment_index = i
            if "import json" in line:
                json_index = i

        assert comment_index >= 0, "Comment line should exist"
        assert json_index >= 0, "New import should exist"
        assert (
            json_index == comment_index - 1
        ), "New import should be right before comment"

    def test_before_preserve_context(self):
        """Test preservación de contexto y estructura"""
        file_path = os.path.join(self.temp_dir, "test_context.py")
        original_content = """class MyClass:
    def method1(self):
        return 'first'

    def target_method(self):
        return 'target'

    def method3(self):
        return 'third'"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        new_method = """    def new_method_before(self):
        return 'inserted_before'
    """

        result = self.modifier.execute(
            "before", file_path, "def target_method(self):", new_method
        )

        assert result["success"] is True, "Before with context should succeed"

        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        assert (
            "def new_method_before(self):" in file_content
        ), "New method should be added"
        assert (
            "return 'inserted_before'" in file_content
        ), "Method body should be preserved"
        assert "def target_method(self):" in file_content, "Target method should remain"
        assert "def method1(self):" in file_content, "Previous methods should remain"
        assert "def method3(self):" in file_content, "Following methods should remain"

    def test_before_pattern_validation(self):
        """Test validación de patrón existente"""
        file_path = os.path.join(self.temp_dir, "test_validation.py")
        content = """first_line = 'value1'
target_line = 'target'
last_line = 'value3'"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Test: patrón que SÍ existe
        result = self.modifier.execute(
            "before",
            file_path,
            "target_line = 'target'",
            "inserted_line = 'before_target'",
        )
        assert result["success"] is True, "Before with existing pattern should succeed"

        # Test: patrón que NO existe
        result_fail = self.modifier.execute(
            "before", file_path, "nonexistent_pattern", "should_not_be_added"
        )
        if isinstance(result_fail, dict):
            assert (
                result_fail["success"] is False
            ), "Before with nonexistent pattern should fail"
        else:
            assert (
                result_fail is False
            ), "Before with nonexistent pattern should return False"

        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        assert (
            "inserted_line = 'before_target'" in file_content
        ), "Valid insertion should exist"
        assert (
            "should_not_be_added" not in file_content
        ), "Invalid insertion should not exist"

    def test_before_index_handling(self):
        """Test manejo correcto de índices"""
        file_path = os.path.join(self.temp_dir, "test_indices.py")
        original_content = """line_0 = 'zero'
line_1 = 'one'
line_2 = 'two'
line_3 = 'three'"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        result = self.modifier.execute(
            "before", file_path, "line_2 = 'two'", "inserted = 'before_two'"
        )

        assert result["success"] is True, "Before insertion should succeed"

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Verificar orden correcto
        line_contents = [line.strip() for line in lines if line.strip()]
        expected_order = [
            "line_0 = 'zero'",
            "line_1 = 'one'",
            "inserted = 'before_two'",
            "line_2 = 'two'",
            "line_3 = 'three'",
        ]

        for expected in expected_order:
            assert (
                expected in line_contents
            ), f"Line '{expected}' should exist in correct order"

        # Verificar que inserted está justo antes de line_2
        line1_idx = line_contents.index("line_1 = 'one'")
        inserted_idx = line_contents.index("inserted = 'before_two'")
        line2_idx = line_contents.index("line_2 = 'two'")

        assert (
            line1_idx < inserted_idx < line2_idx
        ), "Inserted line should be between line1 and line2"


class TestAppendOperation:
    """Tests para operación APPEND - agregar al final con newlines"""

    def setup_method(self):
        """Setup para cada test"""
        self.modifier = SurgicalModifierUltimate()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup después de cada test"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_append_basic(self):
        """Test append básico al final de archivo"""
        file_path = os.path.join(self.temp_dir, "test_append.py")
        original_content = """import os
import sys
print('existing code')"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        result = self.modifier.execute(
            "append", file_path, "", "print('appended content')"
        )

        assert result["success"] is True, "Append operation should succeed"
        assert result["operation"] == "append", "Operation should be append"

        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        assert "import os" in file_content, "Original content should be preserved"
        assert (
            "print('existing code')" in file_content
        ), "Original code should be preserved"
        assert (
            "print('appended content')" in file_content
        ), "Appended content should exist"

        # Verificar que el contenido agregado está al final
        lines = file_content.strip().split("\n")
        assert (
            "print('appended content')" in lines[-1]
        ), "Appended content should be at the end"

    def test_append_newline_handling(self):
        """Test manejo correcto de newlines"""
        file_path = os.path.join(self.temp_dir, "test_newlines.py")
        original_content = "line1\nline2\nline3"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        result = self.modifier.execute("append", file_path, "", "line4")

        assert result["success"] is True, "Append with newlines should succeed"

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.strip().split("\n")
        assert len(lines) == 4, "Should have 4 lines after append"
        assert lines[-1] == "line4", "Last line should be the appended content"

    def test_append_multiple_times(self):
        """Test append múltiple (acumulativo)"""
        file_path = os.path.join(self.temp_dir, "test_multiple.py")
        original_content = "original_line"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(original_content)

        # Primera append
        result1 = self.modifier.execute("append", file_path, "", "appended_1")
        assert result1["success"] is True, "First append should succeed"

        # Segunda append
        result2 = self.modifier.execute("append", file_path, "", "appended_2")
        assert result2["success"] is True, "Second append should succeed"

        # Tercera append
        result3 = self.modifier.execute("append", file_path, "", "appended_3")
        assert result3["success"] is True, "Third append should succeed"

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "original_line" in content, "Original content should be preserved"
        assert "appended_1" in content, "First append should exist"
        assert "appended_2" in content, "Second append should exist"
        assert "appended_3" in content, "Third append should exist"

        lines = content.strip().split("\n")
        assert lines[0] == "original_line", "Original line should be first"
        assert lines[1] == "appended_1", "First append should be second"
        assert lines[2] == "appended_2", "Second append should be third"
        assert lines[3] == "appended_3", "Third append should be last"


# Tests de verificación integrada para todas las operaciones core
def test_all_operations_integration():
    """Test integración de todas las operaciones core"""
    import os
    import tempfile

    modifier = SurgicalModifierUltimate()
    temp_dir = tempfile.mkdtemp()

    try:
        file_path = os.path.join(temp_dir, "integration_test.py")

        # 1. CREATE
        result = modifier.execute("create", file_path, "", "# Initial file\nimport os")
        assert result["success"] is True, "CREATE should work"

        # 2. APPEND
        result = modifier.execute("append", file_path, "", "print('end of file')")
        assert result["success"] is True, "APPEND should work"

        # 3. AFTER
        result = modifier.execute("after", file_path, "import os", "import sys")
        assert result["success"] is True, "AFTER should work"

        # 4. BEFORE
        result = modifier.execute(
            "before", file_path, "print('end of file')", "# Before print"
        )
        assert result["success"] is True, "BEFORE should work"

        # 5. REPLACE
        result = modifier.execute(
            "replace", file_path, "# Initial file", "# Modified file"
        )
        assert result["success"] is True, "REPLACE should work"

        # Verificar resultado final
        with open(file_path, "r", encoding="utf-8") as f:
            final_content = f.read()

        assert "# Modified file" in final_content, "REPLACE result should exist"
        assert "import sys" in final_content, "AFTER result should exist"
        assert "# Before print" in final_content, "BEFORE result should exist"
        assert "print('end of file')" in final_content, "APPEND result should exist"

    finally:
        import shutil

        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
