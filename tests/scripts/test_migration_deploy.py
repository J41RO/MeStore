#!/usr/bin/env python3
"""
Tests para scripts de deployment de migraciones.
Valida funcionalidad de run_migrations.sh y deploy_with_migrations.sh
"""

import os
import subprocess
import tempfile
import pytest
from pathlib import Path


class TestMigrationDeployScripts:
    """Test suite para scripts de deployment de migraciones."""

    @classmethod
    def setup_class(cls):
        """Setup para todos los tests."""
        cls.project_root = Path(__file__).parent.parent.parent
        cls.scripts_dir = cls.project_root / "scripts"
        cls.run_migrations_script = cls.scripts_dir / "run_migrations.sh"
        cls.deploy_script = cls.scripts_dir / "deploy_with_migrations.sh"

    def test_run_migrations_script_exists(self):
        """Verificar que el script run_migrations.sh existe y es ejecutable."""
        assert self.run_migrations_script.exists(), "Script run_migrations.sh no existe"
        assert os.access(self.run_migrations_script, os.X_OK), "Script no es ejecutable"

    def test_deploy_script_exists(self):
        """Verificar que el script deploy_with_migrations.sh existe y es ejecutable."""
        assert self.deploy_script.exists(), "Script deploy_with_migrations.sh no existe"
        assert os.access(self.deploy_script, os.X_OK), "Script no es ejecutable"

    def test_run_migrations_help(self):
        """Test que el comando --help funciona correctamente."""
        result = subprocess.run(
            [str(self.run_migrations_script), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0, f"Help comando falló: {result.stderr}"
        assert "MESTOCKER DEPLOYMENT MIGRATIONS SCRIPT" in result.stdout
        assert "development" in result.stdout
        assert "production" in result.stdout
        assert "--dry-run" in result.stdout

    def test_deploy_script_help(self):
        """Test que el comando --help del deploy script funciona."""
        result = subprocess.run(
            [str(self.deploy_script), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0, f"Deploy help falló: {result.stderr}"
        assert "MESTOCKER FULL DEPLOYMENT SCRIPT" in result.stdout
        assert "health check" in result.stdout
        assert "--check-only" in result.stdout

    def test_run_migrations_dry_run_development(self):
        """Test dry-run en development environment."""
        result = subprocess.run(
            [str(self.run_migrations_script), "--dry-run", "development"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(self.project_root)
        )

        # Dry-run no debe fallar, independientemente del estado de la DB
        assert result.returncode == 0, f"Dry-run falló: {result.stderr}"
        assert "DRY RUN" in result.stdout or "MIGRACIONES PENDIENTES" in result.stdout

    def test_invalid_environment_rejection(self):
        """Test que environments inválidos son rechazados."""
        result = subprocess.run(
            [str(self.run_migrations_script), "invalid_env"],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 1, "Environment inválido debería fallar"
        assert "Argumento desconocido" in result.stdout or "Environment debe ser" in result.stdout

    def test_deploy_check_only_development(self):
        """Test check-only mode del deployment script."""
        result = subprocess.run(
            [str(self.deploy_script), "--check-only", "development"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(self.project_root)
        )

        # Check-only puede fallar por DB no disponible, pero no debe crashear
        assert result.returncode in [0, 1], f"Check-only crasheó: {result.stderr}"
        assert "HEALTH CHECK" in result.stdout

    def test_alembic_helpers_functions_loaded(self):
        """Test que las funciones de alembic_helpers.sh están disponibles."""
        # Test que el archivo contiene las nuevas funciones
        alembic_helpers = self.scripts_dir / "alembic_helpers.sh"
        assert alembic_helpers.exists(), "alembic_helpers.sh no existe"

        with open(alembic_helpers, "r") as f:
            content = f.read()

        required_functions = [
            "health_check_database",
            "deploy_migrate", 
            "emergency_rollback",
            "prepare_deployment_environment"
        ]

        for func in required_functions:
            assert func in content, f"Función {func} no encontrada en alembic_helpers.sh"

    def test_log_directory_creation(self):
        """Test que los scripts crean el directorio de logs."""
        # Crear directorio temporal para test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Simular ejecución que debería crear logs/
            # Nota: Este test es más conceptual ya que depende de la DB
            logs_dir = self.project_root / "logs"

            # Si no existe, debería crearse al ejecutar scripts
            # Para este test, verificamos que la lógica está presente
            script_content = self.run_migrations_script.read_text()
            assert "mkdir -p" in script_content and "logs" in script_content

    def test_docker_integration_presence(self):
        """Test que la integración con Docker está configurada."""
        docker_compose = self.project_root / "docker-compose.yml"
        assert docker_compose.exists(), "docker-compose.yml no existe"

        with open(docker_compose, "r") as f:
            content = f.read()

        # Verificar que el servicio de migración está definido
        assert "migrations:" in content, "Servicio de migración no definido"
        assert "mestocker_migrations" in content, "Container de migración no configurado"
        assert "run_migrations.sh" in content, "Script no referenciado en Docker"

    def test_script_syntax_validation(self):
        """Test que todos los scripts tienen sintaxis bash válida."""
        bash_scripts = [
            self.run_migrations_script,
            self.deploy_script,
            self.scripts_dir / "alembic_helpers.sh"
        ]

        for script in bash_scripts:
            if script.exists():
                result = subprocess.run(
                    ["bash", "-n", str(script)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                assert result.returncode == 0, f"Error de sintaxis en {script.name}: {result.stderr}"


class TestDeploymentIntegration:
    """Tests de integración para el flujo completo de deployment."""

    def test_migration_service_docker_config(self):
        """Test configuración del servicio de migración en Docker."""
        docker_compose = Path(__file__).parent.parent.parent / "docker-compose.yml"

        with open(docker_compose, "r") as f:
            content = f.read()

        # Verificaciones de configuración
        migration_section = content[content.find("migrations:"):]

        assert "depends_on:" in migration_section, "Dependencias no configuradas"
        assert "postgres:" in migration_section, "Dependencia de postgres faltante"
        assert "service_healthy" in migration_section, "Health check dependency faltante"
        assert "profiles:" in migration_section, "Profile de migración no configurado"
        assert "- migration" in migration_section, "Profile migration no definido"

    def test_environment_detection_logic(self):
        """Test que la lógica de detección de environment funciona."""
        # Test conceptual - verificar que está implementada
        script_content = (Path(__file__).parent.parent.parent / "scripts" / "run_migrations.sh").read_text()

        assert "detect_environment" in script_content, "Función detect_environment no implementada"
        assert "ENVIRONMENT" in script_content, "Variable ENVIRONMENT no referenciada"
        assert ".env" in script_content, "Lectura de .env no implementada"


if __name__ == "__main__":
    # Ejecutar tests si se llama directamente
    pytest.main([__file__, "-v"])