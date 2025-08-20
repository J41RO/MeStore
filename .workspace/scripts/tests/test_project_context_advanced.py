"""
Tests avanzados para ProjectContext de Surgical Modifier Ultimate
Micro-fase 1: Detección automática y gestión contextual
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from surgical_modifier_ultimate import ProjectContext


class TestProjectContextAdvanced:
    """Tests completos para ProjectContext - detección automática"""

    @pytest.fixture
    def temp_project_structure(self):
        """Crear estructura temporal de proyecto para tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear estructura básica
            backend_dir = Path(temp_dir) / "backend"
            frontend_dir = Path(temp_dir) / "frontend"
            backend_dir.mkdir()
            frontend_dir.mkdir()

            # Crear archivos indicadores
            (Path(temp_dir) / "package.json").write_text('{"name": "test"}')
            (backend_dir / "app.py").write_text("# Backend app")
            (frontend_dir / "index.html").write_text("<html></html>")

            yield temp_dir

    def test_detect_context_backend(self):
        """Test detección de contexto backend"""
        with patch("os.getcwd", return_value="/project/backend/api"):
            context = ProjectContext()
            assert context.context == "backend"

    def test_detect_context_frontend(self):
        """Test detección de contexto frontend"""
        with patch("os.getcwd", return_value="/project/frontend/src"):
            context = ProjectContext()
            assert context.context == "frontend"

    def test_detect_context_scripts(self):
        """Test detección de contexto scripts"""
        with patch("os.getcwd", return_value="/project/scripts/tools"):
            context = ProjectContext()
            assert context.context == "scripts"

    def test_detect_context_root_default(self):
        """Test detección de contexto por defecto (root)"""
        with patch("os.getcwd", return_value="/unknown/path"):
            context = ProjectContext()
            assert context.context == "root"

    def test_find_project_root_with_package_json(self, temp_project_structure):
        """Test búsqueda de raíz con package.json"""
        backend_path = os.path.join(temp_project_structure, "backend")
        with patch("os.getcwd", return_value=backend_path):
            context = ProjectContext()
            assert context.project_root == temp_project_structure

    def test_resolve_file_path_absolute(self):
        """Test resolución de path absoluto"""
        context = ProjectContext()
        abs_path = "/absolute/path/file.py"
        result = context.resolve_file_path(abs_path)
        assert result == abs_path

    def test_resolve_file_path_relative_dot(self):
        """Test resolución de path relativo con ./"""
        with patch("os.getcwd", return_value="/current"):
            context = ProjectContext()
            result = context.resolve_file_path("./file.py")
            assert result == "/current/file.py"

    def test_resolve_file_path_current_dir(self):
        """Test resolución de archivo en directorio actual"""
        with patch("os.getcwd", return_value="/current"):
            context = ProjectContext()
            result = context.resolve_file_path("file.py")
            assert result == "/current/file.py"

    def test_get_backup_directory_backend(self):
        """Test directorio backup para contexto backend"""
        with patch("os.getcwd", return_value="/project/backend"):
            with patch.object(
                ProjectContext, "_find_project_root", return_value="/project"
            ):
                context = ProjectContext()
                backup_dir = context.get_backup_directory("test.py")
                assert backup_dir == "/project/backend/backup"

    def test_get_backup_directory_frontend(self):
        """Test directorio backup para contexto frontend"""
        with patch("os.getcwd", return_value="/project/frontend"):
            with patch.object(
                ProjectContext, "_find_project_root", return_value="/project"
            ):
                context = ProjectContext()
                backup_dir = context.get_backup_directory("test.js")
                assert backup_dir == "/project/frontend/backup"

    def test_get_backup_directory_root_default(self):
        """Test directorio backup por defecto (.backup)"""
        with patch("os.getcwd", return_value="/project"):
            with patch.object(
                ProjectContext, "_find_project_root", return_value="/project"
            ):
                context = ProjectContext()
                backup_dir = context.get_backup_directory("test.py")
                assert backup_dir == "/project/.backup"

    def test_analyze_project_structure_basic(self, temp_project_structure):
        """Test análisis básico de estructura de proyecto"""
        with patch("os.getcwd", return_value=temp_project_structure):
            context = ProjectContext()
            structure = context.structure
            assert isinstance(structure, dict)
            assert "project_type" in structure
            assert "languages" in structure
            assert "frameworks" in structure
            assert "has_backend" in structure
            assert "has_frontend" in structure
