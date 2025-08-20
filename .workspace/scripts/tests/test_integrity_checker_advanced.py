"""
Tests avanzados para IntegrityChecker de Surgical Modifier Ultimate
Micro-fase 2: Validación de sintaxis y dependencias
"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest
from surgical_modifier_ultimate import IntegrityChecker, ProjectContext


class TestIntegrityCheckerAdvanced:
    """Tests completos para IntegrityChecker - validación sintaxis/deps"""

    @pytest.fixture
    def mock_project_context(self):
        """Mock de ProjectContext para tests"""
        context = Mock()
        context.project_root = "/test/project"
        context.context = "backend"
        return context

    @pytest.fixture
    def temp_python_file(self):
        """Crear archivo Python temporal válido"""
        fd, path = tempfile.mkstemp(suffix=".py")
        try:
            with os.fdopen(fd, "w") as f:
                f.write("import os\ndef test_function():\n    return True\n")
            yield path
        finally:
            os.unlink(path)

    def test_detect_file_type_python(self, mock_project_context):
        """Test detección de tipo Python"""
        checker = IntegrityChecker("/test/file.py", mock_project_context)
        assert checker.file_type == "python"

    def test_detect_file_type_javascript(self, mock_project_context):
        """Test detección de tipo JavaScript"""
        checker = IntegrityChecker("/test/file.js", mock_project_context)
        assert checker.file_type == "javascript"

    def test_detect_file_type_typescript(self, mock_project_context):
        """Test detección de tipo TypeScript"""
        checker = IntegrityChecker("/test/file.ts", mock_project_context)
        assert checker.file_type == "typescript"

    def test_detect_file_type_generic(self, mock_project_context):
        """Test detección de tipo genérico"""
        checker = IntegrityChecker("/test/file.txt", mock_project_context)
        assert checker.file_type == "generic"

    def test_check_python_syntax_valid(self, temp_python_file, mock_project_context):
        """Test verificación de sintaxis Python válida"""
        checker = IntegrityChecker(temp_python_file, mock_project_context)
        result = checker._check_python_syntax()
        assert result["syntax_valid"] is True
        assert result["ast_valid"] is True

    def test_check_python_syntax_invalid(self, mock_project_context):
        """Test verificación de sintaxis Python inválida"""
        fd, path = tempfile.mkstemp(suffix=".py")
        try:
            with os.fdopen(fd, "w") as f:
                f.write("def invalid_syntax(:\n    pass")  # Sintaxis inválida

            checker = IntegrityChecker(path, mock_project_context)
            result = checker._check_python_syntax()
            assert result["syntax_valid"] is False
            assert "errors" in result
            assert len(result["errors"]) > 0
        finally:
            os.unlink(path)

    def test_pre_modification_check_python(
        self, temp_python_file, mock_project_context
    ):
        """Test verificación pre-modificación Python"""
        checker = IntegrityChecker(temp_python_file, mock_project_context)
        result = checker.pre_modification_check(
            "replace", "test_function", "new_function"
        )

        assert isinstance(result, dict)
        assert "syntax_valid" in result
        assert "dependencies_intact" in result
        assert "imports_valid" in result
        assert "warnings" in result
        assert "errors" in result

    def test_post_modification_check(self, temp_python_file, mock_project_context):
        """Test verificación post-modificación"""
        checker = IntegrityChecker(temp_python_file, mock_project_context)
        result = checker.post_modification_check()

        assert isinstance(result, dict)
        assert "syntax_valid" in result

    @patch("subprocess.run")
    def test_check_js_syntax_with_node_success(self, mock_run, mock_project_context):
        """Test verificación JS con node disponible - éxito"""
        mock_run.return_value = Mock(returncode=0, stderr="")

        fd, path = tempfile.mkstemp(suffix=".js")
        try:
            with os.fdopen(fd, "w") as f:
                f.write("console.log('Hello World');")

            checker = IntegrityChecker(path, mock_project_context)
            result = checker._check_js_syntax()
            assert result["syntax_valid"] is True
        finally:
            os.unlink(path)

    def test_check_dependencies_basic(self, temp_python_file, mock_project_context):
        """Test verificación básica de dependencias"""
        checker = IntegrityChecker(temp_python_file, mock_project_context)
        result = checker._check_dependencies()

        assert isinstance(result, dict)
        assert "dependencies_intact" in result

    def test_analyze_change_impact_replace(self, mock_project_context):
        """Test análisis de impacto para operación replace"""
        fd, path = tempfile.mkstemp(suffix=".py")
        try:
            with os.fdopen(fd, "w") as f:
                f.write("def old_function():\n    return 'old'\n")

            checker = IntegrityChecker(path, mock_project_context)
            result = checker._analyze_change_impact(
                "replace", "old_function", "new_function"
            )

            assert isinstance(result, dict)
            assert "affected_areas" in result
            assert result["risk_level"] in ["low", "medium", "high"]
        finally:
            os.unlink(path)
