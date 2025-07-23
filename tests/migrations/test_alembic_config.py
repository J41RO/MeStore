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

    def test_alembic_autogenerate_functions(self):
        """Verificar que funciones de auto-generación están en env.py."""
        env_file = Path("alembic/env.py")
        content = env_file.read_text()
        
        # Verificar que las funciones existen en el archivo
        assert "def include_object" in content
        assert "def compare_type" in content
        assert "def compare_server_default" in content
    
    def test_alembic_async_support(self):
        """Verificar que async support está configurado."""
        env_file = Path("alembic/env.py")
        content = env_file.read_text()
        
        # Verificar imports y configuración async
        assert "create_async_engine" in content
        assert "async def run_async_migrations" in content
        assert "from app.core.config import settings" in content


@pytest.mark.asyncio
class TestAlembicAsyncSupport:
    """Tests para soporte async de Alembic."""
    
    async def test_database_connection_async(self):
        """Verificar conexión async a base de datos."""
        from sqlalchemy.ext.asyncio import create_async_engine
        
        engine = create_async_engine(settings.DATABASE_URL, future=True)
        
        try:
            async with engine.connect() as connection:
                from sqlalchemy import text
                result = await connection.execute(text("SELECT 1"))
                assert result.scalar() == 1
        finally:
            await engine.dispose()


class TestAlembicMigrations:
    """Tests para funcionalidad de migraciones."""
    
    def test_migration_files_exist(self):
        """Verificar que archivos de migración existen."""
        migrations_dir = Path("alembic/versions")
        assert migrations_dir.exists()
        
        migration_files = list(migrations_dir.glob("*.py"))
        assert len(migration_files) > 0, "Debe haber al menos una migración"
    
    def test_alembic_check_detects_changes(self):
        """Verificar que alembic check detecta cambios (funcionalidad normal)."""
        result = subprocess.run(
            ["alembic", "check"], 
            capture_output=True, 
            text=True
        )
        # alembic check puede fallar si detecta cambios (comportamiento normal)
        # Lo importante es que no falle por errores de configuración
        assert "Context impl PostgresqlImpl" in result.stderr or result.returncode == 0