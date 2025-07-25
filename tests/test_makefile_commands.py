"""
Tests para verificar funcionamiento de comandos Makefile de migraciones.

Este módulo valida que todos los targets del Makefile funcionen correctamente
y mantengan compatibilidad con la infraestructura existente.
"""

import os
import subprocess
import pytest
from typing import Dict, List, Any
import tempfile
import shutil
from pathlib import Path


class TestMakefileCommands:
    """Tests para comandos Makefile de migraciones."""

    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Setup del entorno de testing."""
        self.original_dir = os.getcwd()
        self.makefile_path = Path("Makefile")

        # Verificar que Makefile existe
        assert self.makefile_path.exists(), "Makefile no encontrado"

        # Variables de entorno para testing
        self.test_env = {
            **os.environ,
            "ENV": "testing",
            "ENVIRONMENT": "testing"
        }

    def run_make_command(self, target: str, env_vars: Dict[str, str] = None) -> subprocess.CompletedProcess:
        """Ejecutar comando make con manejo de errores."""
        env = env_vars or self.test_env

        try:
            result = subprocess.run(
                ["make", target],
                capture_output=True,
                text=True,
                env=env,
                timeout=30
            )
            return result
        except subprocess.TimeoutExpired:
            pytest.fail(f"Timeout ejecutando 'make {target}'")
        except Exception as e:
            pytest.fail(f"Error ejecutando 'make {target}': {e}")

    def test_makefile_exists(self):
        """Test que Makefile existe y es legible."""
        assert self.makefile_path.exists(), "Makefile no existe"
        assert self.makefile_path.is_file(), "Makefile no es un archivo"
        assert os.access(self.makefile_path, os.R_OK), "Makefile no es legible"

    def test_help_command(self):
        """Test que comando help funciona."""
        result = self.run_make_command("help")

        assert result.returncode == 0, f"Help falló: {result.stderr}"
        assert "MESTORE MAKEFILE" in result.stdout, "Help no contiene título esperado"
        assert "AYUDA Y DOCUMENTACION" in result.stdout, "Help no contiene secciones esperadas"

    def test_migrate_help_command(self):
        """Test que comando migrate-help funciona."""
        result = self.run_make_command("migrate-help")

        assert result.returncode == 0, f"Migrate-help falló: {result.stderr}"
        assert "GUIA COMPLETA DE MIGRACIONES" in result.stdout, "Migrate-help no contiene título"
        assert "COMANDOS BASICOS" in result.stdout, "Migrate-help no contiene secciones"

    def test_show_config_command(self):
        """Test que comando show-config funciona."""
        result = self.run_make_command("show-config")

        assert result.returncode == 0, f"Show-config falló: {result.stderr}"
        assert "ENV:" in result.stdout, "Show-config no muestra ENV"
        assert "Python:" in result.stdout, "Show-config no muestra versión Python"

    @pytest.mark.parametrize("target", [
        "help",
        "migrate-help", 
        "show-config",
        "clean-migrations"
    ])
    def test_safe_commands(self, target: str):
        """Test comandos seguros que no modifican la DB."""
        result = self.run_make_command(target)

        # Estos comandos deben ejecutarse sin errores
        assert result.returncode == 0, f"Comando '{target}' falló: {result.stderr}"

    def test_required_targets_exist(self):
        """Test que todos los targets requeridos existen en Makefile."""
        required_targets = [
            # Ayuda
            "help", "migrate-help",
            # Básicos
            "migrate-upgrade", "migrate-downgrade", "migrate-current", 
            "migrate-history", "migrate-check",
            # Generación
            "migrate-auto", "migrate-manual",
            # Entornos
            "migrate-dev", "migrate-test", "migrate-prod",
            # Docker
            "migrate-docker", "migrate-docker-dev",
            # Utilidades
            "migrate-reset", "migrate-validate", "db-status",
            # Aliases
            "up", "down", "status", "check"
        ]

        with open(self.makefile_path, 'r') as f:
            makefile_content = f.read()

        missing_targets = []
        for target in required_targets:
            if f"{target}:" not in makefile_content:
                missing_targets.append(target)

        assert not missing_targets, f"Targets faltantes en Makefile: {missing_targets}"

    def test_integration_with_existing_scripts(self):
        """Test integración con scripts existentes."""
        # Verificar que scripts críticos existen
        critical_scripts = [
            "scripts/run_migrations.py",
            "scripts/deploy_migrations_python.sh"
        ]

        for script_path in critical_scripts:
            assert Path(script_path).exists(), f"Script crítico {script_path} no encontrado"
            assert os.access(script_path, os.X_OK), f"Script {script_path} no es ejecutable"

    def test_makefile_syntax(self):
        """Test que Makefile tiene sintaxis válida."""
        # Test básico de sintaxis ejecutando target de ayuda
        result = subprocess.run(
            ["make", "-n", "help"],  # -n = dry run
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"Makefile tiene errores de sintaxis: {result.stderr}"

    def test_color_support(self):
        """Test que Makefile tiene soporte para colores."""
        with open(self.makefile_path, 'r') as f:
            makefile_content = f.read()

        # Verificar variables de color
        color_vars = ["CYAN", "GREEN", "YELLOW", "RED", "NC"]
        for color_var in color_vars:
            assert f"{color_var} :=" in makefile_content, f"Variable de color {color_var} no definida"


class TestMakefileIntegration:
    """Tests de integración específicos para el entorno MeStore."""

    def test_project_structure_compatibility(self):
        """Test que Makefile es compatible con estructura del proyecto."""
        # Verificar estructura esperada
        expected_paths = [
            "scripts/run_migrations.py",
            "scripts/deploy_migrations_python.sh", 
            "alembic.ini",
            "alembic/",
            "docker-compose.yml"
        ]

        missing_paths = []
        for path in expected_paths:
            if not Path(path).exists():
                missing_paths.append(path)

        assert not missing_paths, f"Estructura de proyecto incompleta: {missing_paths}"

    def test_backwards_compatibility(self):
        """Test que comandos tradicionales siguen funcionando."""
        # Test comando alembic directo
        result = subprocess.run(
            ["alembic", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Alembic debe seguir funcionando
        assert result.returncode == 0, "Alembic no funciona directamente"
        assert "usage" in result.stdout.lower(), "Alembic help no funciona"


# Marks para categorizar tests
pytestmark = [
    pytest.mark.integration,  # Tests de integración
    pytest.mark.makefile      # Tests específicos de Makefile
]