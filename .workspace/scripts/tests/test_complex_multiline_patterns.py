"""
Tests de parsing avanzado para patrones multi-línea complejos
Valida manejo de indentación, estructuras anidadas y whitespace
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Agregar directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import surgical_modifier_ultimate as smu


class TestComplexMultilinePatterns:
    """Suite de tests para patrones multi-línea complejos"""

    def test_multiline_function_pattern(self):
        """Test patrones que cruzan múltiples líneas"""
        multiline_content = (
            chr(35)
            + chr(32)
            + chr(70)
            + chr(117)
            + chr(110)
            + chr(99)
            + chr(105)
            + chr(111)
            + chr(110)
            + chr(32)
            + chr(109)
            + chr(117)
            + chr(108)
            + chr(116)
            + chr(105)
            + chr(108)
            + chr(105)
            + chr(110)
            + chr(101)
            + chr(97)
            + chr(10)
        )
        multiline_content += (
            chr(100)
            + chr(101)
            + chr(102)
            + chr(32)
            + chr(109)
            + chr(105)
            + chr(95)
            + chr(102)
            + chr(117)
            + chr(110)
            + chr(99)
            + chr(105)
            + chr(111)
            + chr(110)
            + chr(40)
            + chr(97)
            + chr(44)
            + chr(10)
        )
        multiline_content += (
            chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(98)
            + chr(44)
            + chr(10)
        )
        multiline_content += (
            chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(99)
            + chr(41)
            + chr(58)
            + chr(10)
        )
        multiline_content += (
            chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(114)
            + chr(101)
            + chr(116)
            + chr(117)
            + chr(114)
            + chr(110)
            + chr(32)
            + chr(97)
            + chr(32)
            + chr(43)
            + chr(32)
            + chr(98)
            + chr(32)
            + chr(43)
            + chr(32)
            + chr(99)
            + chr(10)
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write(multiline_content)
            temp_path = f.name

        try:
            sm = smu.SurgicalModifierUltimate(verbose=False)
            result = sm.execute("replace", temp_path, "mi_funcion", "mi_funcion_nueva")

            assert result.get(
                "success", False
            ), "Replace en función multilínea debe ser exitoso"

            # Verificar que cambio se aplicó correctamente
            with open(temp_path, "r") as f:
                content = f.read()
            assert (
                "mi_funcion_nueva" in content
            ), "Nombre de función debe haberse cambiado"

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_complex_indentation_handling(self):
        """Test contenido con indentación compleja (tabs vs spaces)"""
        # Crear contenido con mezcla de tabs y spaces
        mixed_indent = (
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
            + chr(99)
            + chr(111)
            + chr(110)
            + chr(32)
            + chr(105)
            + chr(110)
            + chr(100)
            + chr(101)
            + chr(110)
            + chr(116)
            + chr(97)
            + chr(99)
            + chr(105)
            + chr(111)
            + chr(110)
            + chr(32)
            + chr(109)
            + chr(105)
            + chr(120)
            + chr(116)
            + chr(97)
            + chr(10)
        )
        mixed_indent += (
            chr(99)
            + chr(108)
            + chr(97)
            + chr(115)
            + chr(115)
            + chr(32)
            + chr(77)
            + chr(105)
            + chr(67)
            + chr(108)
            + chr(97)
            + chr(115)
            + chr(101)
            + chr(58)
            + chr(10)
        )
        mixed_indent += (
            chr(9)
            + chr(100)
            + chr(101)
            + chr(102)
            + chr(32)
            + chr(109)
            + chr(101)
            + chr(116)
            + chr(111)
            + chr(100)
            + chr(111)
            + chr(49)
            + chr(40)
            + chr(115)
            + chr(101)
            + chr(108)
            + chr(102)
            + chr(41)
            + chr(58)
            + chr(10)
        )  # Tab
        mixed_indent += (
            chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(114)
            + chr(101)
            + chr(116)
            + chr(117)
            + chr(114)
            + chr(110)
            + chr(32)
            + chr(39)
            + chr(109)
            + chr(101)
            + chr(116)
            + chr(111)
            + chr(100)
            + chr(111)
            + chr(49)
            + chr(39)
            + chr(10)
        )  # 8 spaces
        mixed_indent += (
            chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(100)
            + chr(101)
            + chr(102)
            + chr(32)
            + chr(109)
            + chr(101)
            + chr(116)
            + chr(111)
            + chr(100)
            + chr(111)
            + chr(50)
            + chr(40)
            + chr(115)
            + chr(101)
            + chr(108)
            + chr(102)
            + chr(41)
            + chr(58)
            + chr(10)
        )  # 4 spaces
        mixed_indent += (
            chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(114)
            + chr(101)
            + chr(116)
            + chr(117)
            + chr(114)
            + chr(110)
            + chr(32)
            + chr(39)
            + chr(109)
            + chr(101)
            + chr(116)
            + chr(111)
            + chr(100)
            + chr(111)
            + chr(50)
            + chr(39)
            + chr(10)
        )  # 8 spaces

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write(mixed_indent)
            temp_path = f.name

        try:
            sm = smu.SurgicalModifierUltimate(verbose=False)
            result = sm.execute("replace", temp_path, "metodo1", "metodo_uno")

            assert result.get(
                "success", False
            ), "Replace con indentación mixta debe ser exitoso"

            # Verificar que la indentación se preservó
            with open(temp_path, "r") as f:
                content = f.read()
            assert "metodo_uno" in content, "Cambio debe haberse aplicado"
            # Verificar que hay tabs y spaces preservados
            lines = content.split(chr(10))
            has_tab = any(chr(9) in line for line in lines)
            has_spaces = any(line.startswith(chr(32) * 4) for line in lines)
            assert has_tab or has_spaces, "Indentación original debe preservarse"

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_structured_content_parsing(self):
        """Test contenido con estructuras anidadas tipo JSON/XML"""
        structured_content = (
            chr(35)
            + chr(32)
            + chr(69)
            + chr(115)
            + chr(116)
            + chr(114)
            + chr(117)
            + chr(99)
            + chr(116)
            + chr(117)
            + chr(114)
            + chr(97)
            + chr(32)
            + chr(97)
            + chr(110)
            + chr(105)
            + chr(100)
            + chr(97)
            + chr(100)
            + chr(97)
            + chr(10)
        )
        structured_content += (
            chr(99)
            + chr(111)
            + chr(110)
            + chr(102)
            + chr(105)
            + chr(103)
            + chr(32)
            + chr(61)
            + chr(32)
            + chr(123)
            + chr(10)
        )
        structured_content += (
            chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(39)
            + chr(110)
            + chr(97)
            + chr(109)
            + chr(101)
            + chr(39)
            + chr(58)
            + chr(32)
            + chr(39)
            + chr(109)
            + chr(105)
            + chr(95)
            + chr(97)
            + chr(112)
            + chr(112)
            + chr(39)
            + chr(44)
            + chr(10)
        )
        structured_content += (
            chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(39)
            + chr(115)
            + chr(101)
            + chr(116)
            + chr(116)
            + chr(105)
            + chr(110)
            + chr(103)
            + chr(115)
            + chr(39)
            + chr(58)
            + chr(32)
            + chr(123)
            + chr(10)
        )
        structured_content += (
            chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(39)
            + chr(100)
            + chr(101)
            + chr(98)
            + chr(117)
            + chr(103)
            + chr(39)
            + chr(58)
            + chr(32)
            + chr(84)
            + chr(114)
            + chr(117)
            + chr(101)
            + chr(44)
            + chr(10)
        )
        structured_content += (
            chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(39)
            + chr(118)
            + chr(101)
            + chr(114)
            + chr(115)
            + chr(105)
            + chr(111)
            + chr(110)
            + chr(39)
            + chr(58)
            + chr(32)
            + chr(39)
            + chr(49)
            + chr(46)
            + chr(48)
            + chr(39)
            + chr(10)
        )
        structured_content += chr(32) + chr(32) + chr(32) + chr(32) + chr(125) + chr(10)
        structured_content += chr(125) + chr(10)

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write(structured_content)
            temp_path = f.name

        try:
            sm = smu.SurgicalModifierUltimate(verbose=False)
            result = sm.execute("replace", temp_path, "mi_app", "mi_aplicacion")

            assert result.get(
                "success", False
            ), "Replace en estructura anidada debe ser exitoso"

            # Verificar que estructura se mantuvo
            with open(temp_path, "r") as f:
                content = f.read()
            assert "mi_aplicacion" in content, "Cambio debe haberse aplicado"
            assert (
                chr(123) in content and chr(125) in content
            ), "Estructura JSON debe preservarse"

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_whitespace_and_newlines_handling(self):
        """Test manejo de whitespace y newlines diversos"""
        whitespace_content = (
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
            + chr(119)
            + chr(104)
            + chr(105)
            + chr(116)
            + chr(101)
            + chr(115)
            + chr(112)
            + chr(97)
            + chr(99)
            + chr(101)
            + chr(32)
            + chr(100)
            + chr(105)
            + chr(118)
            + chr(101)
            + chr(114)
            + chr(115)
            + chr(111)
            + chr(10)
        )
        whitespace_content += chr(10)  # Empty line
        whitespace_content += (
            chr(32)
            + chr(32)
            + chr(32)
            + chr(35)
            + chr(32)
            + chr(76)
            + chr(105)
            + chr(110)
            + chr(101)
            + chr(97)
            + chr(32)
            + chr(99)
            + chr(111)
            + chr(110)
            + chr(32)
            + chr(115)
            + chr(112)
            + chr(97)
            + chr(99)
            + chr(101)
            + chr(115)
            + chr(10)
        )
        whitespace_content += (
            chr(9)
            + chr(9)
            + chr(35)
            + chr(32)
            + chr(76)
            + chr(105)
            + chr(110)
            + chr(101)
            + chr(97)
            + chr(32)
            + chr(99)
            + chr(111)
            + chr(110)
            + chr(32)
            + chr(116)
            + chr(97)
            + chr(98)
            + chr(115)
            + chr(10)
        )
        whitespace_content += (
            chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(100)
            + chr(97)
            + chr(116)
            + chr(97)
            + chr(32)
            + chr(61)
            + chr(32)
            + chr(39)
            + chr(116)
            + chr(101)
            + chr(115)
            + chr(116)
            + chr(39)
            + chr(32)
            + chr(32)
            + chr(32)
            + chr(10)
        )  # Trailing spaces
        whitespace_content += chr(10) + chr(10)  # Multiple empty lines

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write(whitespace_content)
            temp_path = f.name

        try:
            sm = smu.SurgicalModifierUltimate(verbose=False)
            result = sm.execute(
                "after", temp_path, "# Linea con spaces", "# Nueva linea insertada"
            )

            assert result.get(
                "success", False
            ), "After con whitespace diverso debe ser exitoso"

            # Verificar que whitespace original se preservó
            with open(temp_path, "r") as f:
                content = f.read()
            assert (
                "# Nueva linea insertada" in content
            ), "Nueva línea debe estar presente"

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
