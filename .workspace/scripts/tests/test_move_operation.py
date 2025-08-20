import os
import tempfile

import pytest
from surgical_modifier_ultimate import EnhancedSurgicalModifier


class TestMoveOperation:
    """Tests para la nueva operación MOVE con actualización automática de imports"""

    def test_move_function_between_files(self):
        """Test básico: mover función completa entre archivos"""
        # Crear archivos temporales
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as source_file:
            source_file.write(
                """import os
import sys

def hello_world():
    print("Hello, World!")
    return "greeting"

def another_function():
    return "stay here"
"""
            )
            source_path = source_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as dest_file:
            dest_file.write("# Destination file\n")
            dest_path = dest_file.name

        try:
            modifier = EnhancedSurgicalModifier()

            # Ejecutar operación MOVE
            result = modifier.execute(
                operation="move",
                file_path=source_path,
                pattern="def hello_world():",
                content=dest_path,
            )

            # Verificar resultado exitoso
            assert result is True

            # Verificar que función se movió al destino
            with open(dest_path, "r") as f:
                dest_content = f.read()
            assert "def hello_world():" in dest_content
            assert 'print("Hello, World!")' in dest_content

            # Verificar que función se ELIMINÓ del origen
            with open(source_path, "r") as f:
                source_content = f.read()
            assert "def hello_world():" not in source_content
            assert "def another_function():" in source_content  # Debe mantenerse

        finally:
            # Limpiar archivos temporales
            os.unlink(source_path)
            os.unlink(dest_path)
