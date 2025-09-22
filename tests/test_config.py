# ~/tests/core/test_config.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Tests Core Config
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""
Tests para configuración del core

Tests de verificación para:
- Settings cargados correctamente
- URLs de conexión válidas
- Variables de entorno configuradas
"""

from app.core.config import settings, Settings


def test_settings_loaded():
    """Test que la configuración se carga correctamente"""
    # Verificar DATABASE_URL (acepta postgresql, sqlite para testing)
    valid_db_prefixes = (
        "postgresql://", "postgresql+asyncpg://", "postgresql+psycopg://",
        "sqlite://", "sqlite+aiosqlite:///"
    )
    assert settings.DATABASE_URL.startswith(valid_db_prefixes), f"Invalid DATABASE_URL: {settings.DATABASE_URL}"

    # Verificar que contiene nombre relacionado con mestocker o testing
    db_contains_valid_name = any(name in settings.DATABASE_URL.lower() for name in ["mestocker", "mestore", "test"])
    assert db_contains_valid_name, f"DATABASE_URL should contain valid project name: {settings.DATABASE_URL}"

    # Verificar REDIS_URL
    assert settings.REDIS_URL.startswith("redis://")
    assert "6379" in settings.REDIS_URL

    # Verificar SECRET_KEY existe
    assert settings.SECRET_KEY
    assert len(settings.SECRET_KEY) > 10

    print(f"✅ DATABASE_URL: {settings.DATABASE_URL[:50]}...")
    print(f"✅ REDIS_URL: {settings.REDIS_URL}")
    print(f"✅ SECRET_KEY: Configurado correctamente")


def test_database_url_format():
    """Test formato específico de DATABASE_URL"""
    # Debe ser formato válido para FastAPI (PostgreSQL o SQLite para testing)
    valid_formats = (
        "postgresql+asyncpg://", "postgresql+psycopg://", "postgresql://",
        "sqlite+aiosqlite:///", "sqlite:///"
    )
    assert settings.DATABASE_URL.startswith(valid_formats), f"Invalid DATABASE_URL format: {settings.DATABASE_URL}"

    # Para PostgreSQL debe contener host, para SQLite es archivo local
    if settings.DATABASE_URL.startswith(("postgresql", "postgres")):
        assert "localhost" in settings.DATABASE_URL or "127.0.0.1" in settings.DATABASE_URL
    elif settings.DATABASE_URL.startswith("sqlite"):
        assert ".db" in settings.DATABASE_URL  # Debe ser archivo .db


def test_redis_url_format():
    """Test formato específico de REDIS_URL"""
    assert settings.REDIS_URL.startswith("redis://")
    assert ":6379" in settings.REDIS_URL


def test_debug_settings():
    """Test configuraciones de debug"""
    # En desarrollo, DEBUG debe estar configurado
    assert hasattr(settings, "DEBUG")
    print(f"✅ DEBUG mode: {settings.DEBUG}")


def test_all_required_settings():
    """Test que todas las configuraciones requeridas estén presentes"""
    required_settings = ["DATABASE_URL", "REDIS_URL", "SECRET_KEY"]

    for setting in required_settings:
        assert hasattr(settings, setting), f"Setting {setting} missing"
        value = getattr(settings, setting)
        assert value, f"Setting {setting} is empty"

    print("✅ Todas las configuraciones requeridas están presentes")


class TestDatabaseURLConfiguration:
   """Tests específicos para configuración DATABASE_URL."""

   def test_database_url_field_description(self):
       """Test que verifica que DATABASE_URL tiene Field con descripción."""
       settings = Settings()

       # Verificar que es un Field de Pydantic
       field_info = Settings.model_fields['DATABASE_URL']
       assert field_info.description is not None
       assert 'PostgreSQL' in field_info.description

   def test_db_echo_field_description(self):
       """Test que verifica que DB_ECHO tiene Field con descripción."""
       settings = Settings()

       field_info = Settings.model_fields['DB_ECHO']
       assert field_info.description is not None
       assert 'debugging' in field_info.description.lower()