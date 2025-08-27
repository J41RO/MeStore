"""
Tests avanzados para --explore mode de Surgical Modifier Ultimate
Micro-fase 3: Estructura y búsqueda de archivos
"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest
from surgical_modifier_ultimate import (
    ProjectContext,
    SurgicalModifierUltimate,
    UniversalExplorer,
)


class TestExploreModeAdvanced:
    """Tests completos para modo --explore"""

    @pytest.fixture
    def temp_python_file_with_content(self):
        """Crear archivo Python temporal con contenido estructurado"""
        fd, path = tempfile.mkstemp(suffix=".py")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(
                    """# Test module for exploration
import os
import sys
from typing import List

class TestClass:
    \"\"\"Test class for exploration\"\"\"

    def __init__(self):
        self.value = 42

    def test_method(self) -> str:
        return "test result"

    def another_method(self, param: int) -> bool:
        return param > 0

def standalone_function():
    \"\"\"Standalone function\"\"\"
    return True

# Constants
TEST_CONSTANT = "test_value"
ANOTHER_CONSTANT = 100
"""
                )
            yield path
        finally:
            os.unlink(path)

    @pytest.fixture
    def temp_js_file_with_content(self):
        """Crear archivo JavaScript temporal con contenido"""
        fd, path = tempfile.mkstemp(suffix=".js")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(
                    """// Test JavaScript file
import React from 'react';
import { useState, useEffect } from 'react';

function TestComponent() {
    const [count, setCount] = useState(0);

    useEffect(() => {
        console.log('Component mounted');
    }, []);

    return <div>Hello World</div>;
}

export default TestComponent;
"""
                )
            yield path
        finally:
            os.unlink(path)

    def test_execute_explore_mode_without_search_term(
        self, temp_python_file_with_content
    ):
        """Test exploración básica sin término de búsqueda"""
        modifier = SurgicalModifierUltimate(explore=True)

        # Capturar output para verificar
        with patch("builtins.print") as mock_print:
            modifier.execute_explore_mode(temp_python_file_with_content)

            # Verificar que se imprimió información de estructura
            print_calls = [
                call.args[0] for call in mock_print.call_args_list if call.args
            ]
            structure_found = any(
                "ESTRUCTURA DE ARCHIVO" in str(call) for call in print_calls
            )
            assert structure_found, "Debe mostrar estructura del archivo"

    def test_execute_explore_mode_with_search_term(self, temp_python_file_with_content):
        """Test exploración con término de búsqueda específico"""
        modifier = SurgicalModifierUltimate(explore=True)

        with patch("builtins.print") as mock_print:
            modifier.execute_explore_mode(temp_python_file_with_content, "test_method")

            # Verificar que se imprimió información de búsqueda
            print_calls = [
                call.args[0] for call in mock_print.call_args_list if call.args
            ]
            search_found = any("BÚSQUEDA" in str(call) for call in print_calls)
            assert search_found, "Debe mostrar resultados de búsqueda"

    def test_execute_explore_mode_file_not_found(self):
        """Test exploración con archivo inexistente"""
        modifier = SurgicalModifierUltimate(explore=True)

        with patch("builtins.print") as mock_print:
            modifier.execute_explore_mode("/nonexistent/file.py")

            # Verificar mensaje de error
            print_calls = [
                call.args[0] for call in mock_print.call_args_list if call.args
            ]
            error_found = any(
                "no encontrado" in str(call).lower() for call in print_calls
            )
            assert error_found, "Debe mostrar error de archivo no encontrado"

    def test_universal_explorer_show_file_structure(
        self, temp_python_file_with_content
    ):
        """Test estructura de archivo con UniversalExplorer"""
        with patch("builtins.print") as mock_print:
            UniversalExplorer.show_file_structure(temp_python_file_with_content)

            # Verificar que se imprimió estructura
            print_calls = [
                call.args[0] for call in mock_print.call_args_list if call.args
            ]
            structure_elements = [
                "ESTRUCTURA DE ARCHIVO",
                "Total líneas",
                "ESTADÍSTICAS",
            ]

            for element in structure_elements:
                found = any(element in str(call) for call in print_calls)
                assert found, f"Debe mostrar {element}"

    def test_universal_explorer_search_in_file_found(
        self, temp_python_file_with_content
    ):
        """Test búsqueda en archivo - término encontrado"""
        with patch("builtins.print") as mock_print:
            UniversalExplorer.search_in_file(
                temp_python_file_with_content, "test_method"
            )

            # Verificar resultados de búsqueda
            print_calls = [
                call.args[0] for call in mock_print.call_args_list if call.args
            ]
            search_elements = ["BÚSQUEDA", "Coincidencia", "Se encontraron"]

            for element in search_elements:
                found = any(element in str(call) for call in print_calls)
                assert found, f"Debe mostrar {element}"

    def test_universal_explorer_search_in_file_not_found(
        self, temp_python_file_with_content
    ):
        """Test búsqueda en archivo - término no encontrado"""
        with patch("builtins.print") as mock_print:
            UniversalExplorer.search_in_file(
                temp_python_file_with_content, "nonexistent_term"
            )

            # Verificar mensaje de no encontrado
            print_calls = [
                call.args[0] for call in mock_print.call_args_list if call.args
            ]
            not_found = any(
                "No se encontraron coincidencias" in str(call) for call in print_calls
            )
            assert not_found, "Debe mostrar mensaje de no encontrado"

    def test_universal_explorer_search_case_sensitive(
        self, temp_python_file_with_content
    ):
        """Test búsqueda sensible a mayúsculas"""
        with patch("builtins.print") as mock_print:
            UniversalExplorer.search_in_file(
                temp_python_file_with_content, "TEST_CONSTANT", case_sensitive=True
            )

            # Verificar que encontró el término exacto
            print_calls = [
                call.args[0] for call in mock_print.call_args_list if call.args
            ]
            found = any("Coincidencia" in str(call) for call in print_calls)
            assert found, "Debe encontrar término con sensibilidad a mayúsculas"

    def test_universal_explorer_search_case_insensitive(
        self, temp_python_file_with_content
    ):
        """Test búsqueda insensible a mayúsculas"""
        with patch("builtins.print") as mock_print:
            UniversalExplorer.search_in_file(
                temp_python_file_with_content, "testclass", case_sensitive=False
            )

            # Verificar que encontró el término ignorando mayúsculas
            print_calls = [
                call.args[0] for call in mock_print.call_args_list if call.args
            ]
            found = any("Coincidencia" in str(call) for call in print_calls)
            assert found, "Debe encontrar término ignorando mayúsculas"

    def test_explore_mode_with_javascript_file(self, temp_js_file_with_content):
        """Test exploración con archivo JavaScript"""
        with patch("builtins.print") as mock_print:
            UniversalExplorer.show_file_structure(temp_js_file_with_content)

            # Verificar detección de tipo JavaScript
            print_calls = [
                call.args[0] for call in mock_print.call_args_list if call.args
            ]
            js_detected = any(
                "javascript" in str(call).lower() or "js" in str(call).lower()
                for call in print_calls
            )
            assert js_detected, "Debe detectar archivo JavaScript"

    def test_explore_mode_analysis_integration(self, temp_python_file_with_content):
        """Test integración con análisis de contexto de proyecto"""
        modifier = SurgicalModifierUltimate(explore=True)

        with patch("builtins.print") as mock_print:
            modifier.execute_explore_mode(temp_python_file_with_content)

            # Verificar análisis de contexto
            print_calls = [
                call.args[0] for call in mock_print.call_args_list if call.args
            ]
            analysis_elements = [
                "ANÁLISIS UNIVERSAL",
                "Contexto detectado",
                "Tipo de archivo",
            ]

            for element in analysis_elements:
                found = any(element in str(call) for call in print_calls)
                assert found, f"Debe mostrar {element} en análisis"

    def test_explore_mode_with_context_lines(self, temp_python_file_with_content):
        """Test búsqueda con líneas de contexto"""
        with patch("builtins.print") as mock_print:
            UniversalExplorer.search_in_file(
                temp_python_file_with_content, "test_method", context_lines=3
            )

            # Verificar que se muestran líneas de contexto
            print_calls = [
                call.args[0] for call in mock_print.call_args_list if call.args
            ]
            context_found = any(
                ">>>" in str(call) for call in print_calls
            )  # Línea resaltada
            assert context_found, "Debe mostrar líneas de contexto"
