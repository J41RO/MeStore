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

from app.core.config import settings


def test_settings_loaded():
    """Test que la configuración se carga correctamente"""
    # Verificar DATABASE_URL (acepta postgresql, postgresql+asyncpg y sqlite)
    assert settings.DATABASE_URL.startswith(("postgresql://", "postgresql+asyncpg://", "sqlite+aiosqlite://"))
    # Solo verificar mestocker en PostgreSQL, no en SQLite
    if settings.DATABASE_URL.startswith("sqlite"):
        assert "mestore" in settings.DATABASE_URL
    else:
        assert "mestocker" in settings.DATABASE_URL

    # Verificar REDIS_URL
    assert settings.REDIS_URL.startswith("redis://")
    assert "6379" in settings.REDIS_URL

    # Verificar SECRET_KEY existe
    assert settings.SECRET_KEY
    assert len(settings.SECRET_KEY) > 10

    print(f"✅ DATABASE_URL: {settings.DATABASE_URL[:30]}...")
    print(f"✅ REDIS_URL: {settings.REDIS_URL}")
    print(f"✅ SECRET_KEY: Configurado correctamente")


def test_database_url_format():
    """Test formato específico de DATABASE_URL"""
    # Puede ser PostgreSQL o SQLite dependiendo del entorno
    valid_starts = ("postgresql+asyncpg://", "sqlite+aiosqlite://")
    assert settings.DATABASE_URL.startswith(valid_starts)

    # Para PostgreSQL, verificar host
    if settings.DATABASE_URL.startswith("postgresql+asyncpg://"):
        assert "localhost" in settings.DATABASE_URL or "127.0.0.1" in settings.DATABASE_URL


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
