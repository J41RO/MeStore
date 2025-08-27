"""
Tests avanzados para --check-integrity de Surgical Modifier Ultimate
Micro-fase 5: Verificación completa de integridad end-to-end
"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest
from surgical_modifier_ultimate import (
    EnhancedSurgicalModifier,
    IntegrityChecker,
    ProjectContext,
)


class TestCheckIntegrityIntegration:
    """Tests completos para verificación de integridad end-to-end"""

    @pytest.fixture
    def temp_valid_python_file(self):
        """Crear archivo Python temporal válido"""
        fd, path = tempfile.mkstemp(suffix=".py")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(
                    """# Valid Python file
import os
import sys

class TestClass:
    def __init__(self):
        self.value = 42

    def test_method(self):
        return "test"

def standalone_function():
    return True
"""
                )
            yield path
        finally:
            os.unlink(path)

    @pytest.fixture
    def temp_invalid_python_file(self):
        """Crear archivo Python temporal con errores de sintaxis"""
        fd, path = tempfile.mkstemp(suffix=".py")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(
                    """# Invalid Python file
import os

class TestClass:
    def __init__(self:  # Sintaxis inválida - falta paréntesis
        self.value = 42

    def test_method(self):
        return "test"
"""
                )
            yield path
        finally:
            os.unlink(path)

    def test_enhanced_surgical_modifier_initialization(self):
        """Test inicialización de EnhancedSurgicalModifier"""
        modifier = EnhancedSurgicalModifier(
            verbose=True, confirm=False, keep_backups=True
        )

        assert modifier.verbose is True
        assert modifier.confirm is False
        assert modifier.backup_manager.keep_successful_backups is True

    def test_execute_with_integrity_check_valid_file(self, temp_valid_python_file):
        """Test verificación de integridad con archivo válido"""
        modifier = EnhancedSurgicalModifier(verbose=False, confirm=False)

        with patch("builtins.print"):  # Suprimir output para test limpio
            result = modifier.execute_with_integrity_check(
                "replace", temp_valid_python_file, "test_method", "new_method"
            )

        # Verificar estructura del resultado
        assert isinstance(result, dict)
        assert "success" in result
        assert "pre_check" in result
        assert "post_check" in result

        # Verificar que las verificaciones están presentes
        assert isinstance(result["pre_check"], dict)
        assert isinstance(result["post_check"], dict)

    def test_execute_with_integrity_check_invalid_syntax(
        self, temp_invalid_python_file
    ):
        """Test verificación de integridad con archivo de sintaxis inválida"""
        modifier = EnhancedSurgicalModifier(verbose=False, confirm=False)

        with patch("builtins.print"):
            result = modifier.execute_with_integrity_check(
                "replace", temp_invalid_python_file, "test_method", "new_method"
            )

        # Debe detectar error de sintaxis y detener ejecución
        assert result["success"] is False
        assert "error" in result
        assert "sintaxis" in result["error"].lower()
        assert "details" in result

    def test_integrity_check_pre_modification(self, temp_valid_python_file):
        """Test verificación pre-modificación específica"""
        project_context = ProjectContext()
        checker = IntegrityChecker(temp_valid_python_file, project_context)

        pre_check = checker.pre_modification_check(
            "replace", "test_method", "new_method"
        )

        # Verificar estructura de respuesta
        expected_keys = [
            "syntax_valid",
            "dependencies_intact",
            "imports_valid",
            "references_safe",
            "warnings",
            "errors",
        ]

        for key in expected_keys:
            assert key in pre_check

        # Para archivo válido, sintaxis debe ser OK
        assert pre_check["syntax_valid"] is True

    def test_integrity_check_post_modification(self, temp_valid_python_file):
        """Test verificación post-modificación"""
        project_context = ProjectContext()
        checker = IntegrityChecker(temp_valid_python_file, project_context)

        post_check = checker.post_modification_check()

        # Verificar que devuelve dict con información de verificación
        assert isinstance(post_check, dict)
        assert "syntax_valid" in post_check

    def test_report_integrity_check_display(self, temp_valid_python_file):
        """Test reporte de verificación de integridad"""
        modifier = EnhancedSurgicalModifier()

        # Mock check result
        check_result = {
            "syntax_valid": True,
            "dependencies_intact": True,
            "errors": [],
            "warnings": ["Test warning"],
            "impact_analysis": {
                "risk_level": "low",
                "affected_areas": ["test_area"],
                "recommendations": ["Test recommendation"],
            },
        }

        with patch("builtins.print") as mock_print:
            modifier._report_integrity_check("TEST", check_result)

            # Verificar que se imprimió información de reporte
            print_calls = [
                call.args[0] for call in mock_print.call_args_list if call.args
            ]

            report_elements = ["REPORTE TEST", "Sintaxis", "Dependencias"]

            for element in report_elements:
                found = any(element in str(call) for call in print_calls)
                assert found, f"Debe mostrar {element} en reporte"

    def test_report_integrity_check_with_errors(self):
        """Test reporte con errores y advertencias"""
        modifier = EnhancedSurgicalModifier()

        check_result = {
            "syntax_valid": False,
            "dependencies_intact": False,
            "errors": ["Error de sintaxis en línea 5", "Import faltante"],
            "warnings": ["Advertencia de estilo"],
            "tests_pass": False,
        }

        with patch("builtins.print") as mock_print:
            modifier._report_integrity_check("ERROR-TEST", check_result)

            print_calls = [
                call.args[0] for call in mock_print.call_args_list if call.args
            ]

            # Verificar elementos de error
            error_elements = [
                "❌ ERROR",
                "⚠️ PROBLEMAS",
                "❌ FALLAN",
                "Errores encontrados",
                "Advertencias",
            ]

            for element in error_elements:
                found = any(element in str(call) for call in print_calls)
                assert found, f"Debe mostrar {element} en reporte de errores"

    def test_integrity_check_risk_levels(self):
        """Test análisis de niveles de riesgo"""
        modifier = EnhancedSurgicalModifier()

        risk_levels = ["low", "medium", "high"]
        risk_icons = {"low": "🟢", "medium": "🟡", "high": "🔴"}

        for risk_level in risk_levels:
            check_result = {
                "syntax_valid": True,
                "dependencies_intact": True,
                "impact_analysis": {
                    "risk_level": risk_level,
                    "affected_areas": [],
                    "recommendations": [],
                },
            }

            with patch("builtins.print") as mock_print:
                modifier._report_integrity_check(
                    f"RISK-{risk_level.upper()}", check_result
                )

                print_calls = [
                    call.args[0] for call in mock_print.call_args_list if call.args
                ]

                # Verificar que se muestra el nivel de riesgo correcto
                risk_found = any(
                    risk_level.upper() in str(call) for call in print_calls
                )
                icon_found = any(
                    risk_icons[risk_level] in str(call) for call in print_calls
                )

                assert risk_found, f"Debe mostrar nivel de riesgo {risk_level}"
                assert icon_found, f"Debe mostrar ícono para riesgo {risk_level}"

    def test_integrity_check_with_backup_recommendation(self, temp_valid_python_file):
        """Test verificación que recomienda backup"""
        modifier = EnhancedSurgicalModifier(verbose=False, confirm=False)

        # Mock post_check para simular errores
        with patch.object(
            IntegrityChecker, "post_modification_check"
        ) as mock_post_check:
            mock_post_check.return_value = {
                "syntax_valid": False,
                "errors": ["Sintaxis inválida después de modificación"],
            }

            with patch("builtins.print"):
                result = modifier.execute_with_integrity_check(
                    "replace", temp_valid_python_file, "test_method", "new_method"
                )

            # Debe recomendar backup cuando hay errores post-modificación
            assert "integrity_warnings" in result
            assert "backup_recommended" in result
            assert result["backup_recommended"] is True

    def test_integration_with_project_context(self, temp_valid_python_file):
        """Test integración completa con ProjectContext"""
        modifier = EnhancedSurgicalModifier()

        with patch("builtins.print"):
            result = modifier.execute_with_integrity_check(
                "after", temp_valid_python_file, "class TestClass:", "    # New comment"
            )

        # Verificar que ProjectContext fue utilizado
        assert "pre_check" in result
        assert "post_check" in result

        # Las verificaciones deben tener información de contexto
        pre_check = result["pre_check"]
        assert isinstance(pre_check, dict)

    def test_integrity_check_performance_large_file(self):
        """Test rendimiento con archivo grande"""
        # Crear archivo temporal grande
        fd, path = tempfile.mkstemp(suffix=".py")
        try:
            with os.fdopen(fd, "w") as f:
                # Escribir contenido repetitivo grande
                for i in range(1000):
                    f.write(f"def function_{i}():\n    return {i}\n\n")

            modifier = EnhancedSurgicalModifier(verbose=False, confirm=False)

            import time

            start_time = time.time()

            with patch("builtins.print"):
                result = modifier.execute_with_integrity_check(
                    "replace", path, "function_500", "function_500_modified"
                )

            end_time = time.time()
            execution_time = end_time - start_time

            # Verificar que se ejecuta en tiempo razonable (< 5 segundos)
            assert execution_time < 5.0, f"Ejecución muy lenta: {execution_time}s"

            # Verificar que la verificación se completó
            assert "pre_check" in result
            assert "post_check" in result

        finally:
            os.unlink(path)
