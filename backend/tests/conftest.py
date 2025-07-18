"""
Configuración global de fixtures para testing del backend.
Archivo: backend/tests/conftest.py
Autor: Sistema de desarrollo
Fecha: 2025-07-18
Propósito: Fixtures centralizados para FastAPI testing con soporte async
"""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Fixture para event loop de asyncio compatible con pytest-asyncio.

    Scope: session - Un loop por sesión de testing completa.
    Yield: Event loop de asyncio para tests async.

    Nota: Con asyncio_mode = auto, pytest-asyncio maneja el loop automáticamente.
    Este fixture está disponible para casos específicos que lo requieran.
    """
    try:
        # Intentar obtener loop actual si existe
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # Si no hay loop corriendo, crear uno nuevo
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    yield loop

    # Solo cerrar si creamos el loop nosotros
    if not loop.is_running():
        loop.close()


@pytest.fixture(scope="module")
def client() -> TestClient:
    """
    Fixture para TestClient de FastAPI.

    Scope: module - Un cliente por módulo de tests.
    Returns: TestClient configurado con la app FastAPI principal.
    """
    return TestClient(app)


@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator[TestClient, None]:
    """
    Fixture async para TestClient cuando se requieren operaciones async.

    Scope: function - Nuevo cliente por test function.
    Yields: TestClient para operaciones async.
    """
    async with TestClient(app) as ac:
        yield ac


@pytest.fixture(scope="session")
def test_config():
    """
    Fixture para configuración específica de testing.

    Returns: Dict con configuración de test environment.
    """
    return {
        "testing": True,
        "database_url": "sqlite:///./test.db",
        "log_level": "DEBUG",
        "disable_auth": True,  # Para tests que no requieren autenticación
        "async_mode": "auto",  # Compatible con pytest-asyncio
    }


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """
    Fixture auto-ejecutado para limpiar datos entre tests.

    Autouse: True - Se ejecuta automáticamente en cada test.
    Yields: Permite ejecución del test, luego limpia.
    """
    # Setup antes del test
    yield
    # Cleanup después del test
    # Aquí irá limpieza de base de datos, cache, etc.
    pass


@pytest.fixture(scope="function")
def mock_database():
    """
    Fixture para base de datos mock/temporal.

    Returns: Configuración de base de datos temporal para tests.
    """
    return {
        "url": "sqlite:///:memory:",
        "echo": False,
        "pool_pre_ping": True,
    }
