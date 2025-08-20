"""
Tests de performance y robustez para archivos grandes (>10MB)
Valida manejo eficiente de memoria y timeouts apropiados
"""

import os
import sys
import tempfile
import time
from pathlib import Path

import pytest

# Agregar el directorio padre al path para importar surgical_modifier_ultimate
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import surgical_modifier_ultimate as smu


class TestLargeFilesPerformance:
    """Suite de tests para archivos grandes y performance"""

    @pytest.fixture
    def large_content_10mb(self):
        """Genera contenido de aproximadamente 10MB para tests"""
        line = "# This is a test line with some content " * 10 + chr(
            10
        )  # ~400 chars con newline
        return line * 26000  # ~10MB de contenido

    @pytest.fixture
    def temp_large_file(self, large_content_10mb):
        """Crea archivo temporal grande para tests"""
        with tempfile.NamedTemporaryFile(
            mode=chr(119), delete=False, suffix=chr(46) + chr(112) + chr(121)
        ) as f:
            f.write(large_content_10mb)
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_create_large_file_performance(self, large_content_10mb):
        """Test creacion de archivo grande con tiempo controlado"""
        with tempfile.NamedTemporaryFile(
            mode=chr(119), delete=False, suffix=chr(46) + chr(112) + chr(121)
        ) as temp_file:
            temp_path = temp_file.name

        try:
            start_time = time.time()
            sm = smu.SurgicalModifierUltimate(verbose=False)
            result = sm.execute("create", temp_path, "", large_content_10mb)
            end_time = time.time()

            assert result.get(
                "success", False
            ), "Creacion de archivo grande debe ser exitosa"
            assert os.path.exists(temp_path), "Archivo grande debe existir"
            assert (
                end_time - start_time < 30
            ), f"Creacion tomo {end_time - start_time:.2f}s, debe ser <30s"

            # Verificar que el contenido se escribio correctamente
            with open(temp_path, chr(114)) as f:
                content = f.read()
            assert len(content) > 10000000, "Archivo debe tener >10MB"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_replace_in_large_file_performance(self, temp_large_file):
        """Test replace en archivo grande con performance controlada"""
        start_time = time.time()
        sm = smu.SurgicalModifierUltimate(verbose=False)
        result = sm.execute(
            "replace",
            temp_large_file,
            "# This is a test line",
            "# This is a MODIFIED line",
        )
        end_time = time.time()

        assert result.get(
            "success", False
        ), "Replace en archivo grande debe ser exitoso"
        assert (
            end_time - start_time < 30
        ), f"Replace tomo {end_time - start_time:.2f}s, debe ser <30s"

        # Verificar que el replace funciono
        with open(temp_large_file, chr(114)) as f:
            content = f.read()
        assert "# This is a MODIFIED line" in content, "Replace debe haberse aplicado"

    def test_after_operation_large_file(self, temp_large_file):
        """Test operacion AFTER en archivo grande"""
        start_time = time.time()
        sm = smu.SurgicalModifierUltimate(verbose=False)
        result = sm.execute(
            "after", temp_large_file, "# This is a test line", "# INSERTED AFTER LINE"
        )
        end_time = time.time()

        assert result.get("success", False), "Operacion AFTER debe ser exitosa"
        assert (
            end_time - start_time < 30
        ), f"AFTER tomo {end_time - start_time:.2f}s, debe ser <30s"
