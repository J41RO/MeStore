"""
Tests corregidos para configuración de Alembic.
Tests realistas que verifican funcionalidad sin imports problemáticos.
"""
import pytest
import subprocess
from pathlib import Path
from alembic.config import Config
from app.core.config import settings


class TestAlembicConfiguration:
    """Tests para la configuración de Alembic."""
    
    def test_alembic_config_exists(self):
        """Verificar que alembic.ini existe y es válido."""
        alembic_ini = Path("alembic.ini")
        assert alembic_ini.exists(), "alembic.ini debe existir"
        
        # Verificar configuración básica
        config = Config("alembic.ini")
        assert config.get_main_option("script_location").endswith("alembic")
        
    def test_alembic_env_file_exists(self):
        """Verificar que env.py existe y es sintácticamente válido."""
        env_file = Path("alembic/env.py")
        assert env_file.exists(), "alembic/env.py debe existir"
        
        # Verificar sintaxis compilando
        import py_compile
        py_compile.compile(str(env_file), doraise=True)
    
    def test_alembic_current_command(self):
        """Verificar que alembic current funciona."""
        result = subprocess.run(
            ["alembic", "current"], 
            capture_output=True, 
            text=True
        )
        assert result.returncode == 0, f"alembic current falló: {result.stderr}"
    
    def test_database_url_configuration(self):
        """Verificar que DATABASE_URL está configurada correctamente."""
        assert settings.DATABASE_URL is not None
        assert "postgresql" in settings.DATABASE_URL
        assert "mestocker" in settings.DATABASE_URL
    
    def test_file_template_configuration(self):
        """Verificar que file_template está configurado para timestamps."""
        config = Config("alembic.ini")
        file_template = config.get_main_option("file_template")
        
        assert file_template is not None
        assert "%(year)d" in file_template
        assert "%(month).2d" in file_template
        assert "%(day).2d" in file_template
        assert "%(hour).2d" in file_template
        assert "%(minute).2d" in file_template
    
    def test_revision_environment_enabled(self):
        """Verificar que revision_environment está habilitado."""
        config = Config("alembic.ini")
        revision_env = config.get_main_option("revision_environment")
        assert revision_env == "true"
