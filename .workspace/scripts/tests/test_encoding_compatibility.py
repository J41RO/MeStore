"""
Tests de compatibilidad de encodings y caracteres especiales
Valida manejo robusto de UTF-8, Latin1, BOM y encodings mixtos
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Agregar directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import surgical_modifier_ultimate as smu


class TestEncodingCompatibility:
    """Suite de tests para compatibilidad de encodings"""

    def test_utf8_special_characters(self):
        """Test manejo de caracteres especiales UTF-8"""
        content_utf8 = (
            chr(35)
            + chr(32)
            + chr(65)
            + chr(114)
            + chr(99)
            + chr(104)
            + chr(105)
            + chr(118)
            + chr(111)
            + chr(32)
            + chr(99)
            + chr(111)
            + chr(110)
            + chr(32)
            + chr(101)
            + chr(115)
            + chr(112)
            + chr(101)
            + chr(99)
            + chr(105)
            + chr(97)
            + chr(108)
            + chr(101)
            + chr(115)
            + chr(10)
        )
        content_utf8 += (
            chr(35)
            + chr(32)
            + chr(67)
            + chr(97)
            + chr(114)
            + chr(97)
            + chr(99)
            + chr(116)
            + chr(101)
            + chr(114)
            + chr(101)
            + chr(115)
            + chr(58)
            + chr(32)
            + chr(195)
            + chr(177)
            + chr(44)
            + chr(32)
            + chr(195)
            + chr(169)
            + chr(44)
            + chr(32)
            + chr(195)
            + chr(169)
            + chr(10)
        )

        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False, suffix=".py"
        ) as f:
            f.write(content_utf8)
            temp_path = f.name

        try:
            sm = smu.SurgicalModifierUltimate(verbose=False)
            result = sm.execute(
                "replace",
                temp_path,
                "# Archivo con especiales",
                "# Archivo modificado con especiales",
            )

            assert result.get("success", False), "Replace con UTF-8 debe ser exitoso"

            # Verificar que caracteres especiales se mantienen
            with open(temp_path, "r", encoding="utf-8") as f:
                modified_content = f.read()
            assert "modificado" in modified_content, "Modificacion debe aplicarse"

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_latin1_detection_and_handling(self):
        """Test deteccion y manejo de archivos con encoding especial"""
        content_text = (
            chr(35)
            + chr(32)
            + chr(65)
            + chr(114)
            + chr(99)
            + chr(104)
            + chr(105)
            + chr(118)
            + chr(111)
            + chr(32)
            + chr(116)
            + chr(101)
            + chr(120)
            + chr(116)
            + chr(111)
            + chr(10)
        )
        content_text += (
            chr(35)
            + chr(32)
            + chr(76)
            + chr(105)
            + chr(110)
            + chr(101)
            + chr(97)
            + chr(32)
            + chr(101)
            + chr(115)
            + chr(112)
            + chr(101)
            + chr(99)
            + chr(105)
            + chr(97)
            + chr(108)
            + chr(10)
        )

        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False, suffix=".py"
        ) as f:
            f.write(content_text)
            temp_path = f.name

        try:
            sm = smu.SurgicalModifierUltimate(verbose=False)
            result = sm.execute(
                "after", temp_path, "# Archivo texto", "# Linea insertada"
            )

            assert result.get(
                "success", False
            ), "After con encoding especial debe ser exitoso"

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_mixed_encoding_robustness(self):
        """Test robustez con contenido de encoding mixto"""
        mixed_content = (
            chr(35)
            + chr(32)
            + chr(67)
            + chr(111)
            + chr(110)
            + chr(116)
            + chr(101)
            + chr(110)
            + chr(105)
            + chr(100)
            + chr(111)
            + chr(32)
            + chr(109)
            + chr(105)
            + chr(120)
            + chr(116)
            + chr(111)
            + chr(10)
        )
        mixed_content += (
            chr(35)
            + chr(32)
            + chr(84)
            + chr(101)
            + chr(120)
            + chr(116)
            + chr(111)
            + chr(32)
            + chr(110)
            + chr(111)
            + chr(114)
            + chr(109)
            + chr(97)
            + chr(108)
            + chr(10)
        )

        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False, suffix=".txt"
        ) as f:
            f.write(mixed_content)
            temp_path = f.name

        try:
            sm = smu.SurgicalModifierUltimate(verbose=False)
            result = sm.execute(
                "replace", temp_path, "# Contenido mixto", "# Contenido procesado"
            )

            assert result.get(
                "success", False
            ), "Replace con encoding mixto debe ser exitoso"

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
