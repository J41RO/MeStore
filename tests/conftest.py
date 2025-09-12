"""
Configuración global de fixtures para testing del backend.
Archivo: backend/tests/conftest.py
Autor: Sistema de desarrollo
Fecha: 2025-07-18
Propósito: Fixtures centralizados para FastAPI testing con soporte async
"""

import asyncio
import os
from typing import AsyncGenerator

# Configurar variables de entorno para testing ANTES de importar app
os.environ["TESTING"] = "1"
os.environ["CORS_ORIGINS"] = (
    "http://localhost:3000,http://localhost:8000,https://mestocker.com"
)
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    """
    Fixture para TestClient de FastAPI.

    Scope: module - Un cliente por módulo de tests.
    Returns: TestClient configurado con la app FastAPI principal.
    """
    return TestClient(app)


@pytest.fixture(scope="function")
async def async_client(async_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture async para AsyncClient cuando se requieren operaciones async.

    Scope: function - Nuevo cliente por test function.
    Yields: AsyncClient para operaciones async.
    """
    async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
        """Override de get_db para testing"""
        try:
            yield async_session
        finally:
            pass

    # Override de la dependencia get_db Y get_async_db ANTES de crear el cliente
    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[get_async_db] = get_test_db

    try:
            # Headers con User-Agent válido para evitar bloqueo de middleware
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport, base_url="http://testserver", headers=headers
        ) as ac:
            yield ac
    finally:
        # Limpiar override después del test
        app.dependency_overrides.clear()


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


# === FIXTURES DE BASE DE DATOS DE TESTING ===

import tempfile
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.database import Base, get_async_db
from app.main import app

# Import all models to ensure they're registered with Base.metadata
from app.models.transaction import Transaction
from app.models.commission_dispute import ComissionDispute
from app.models.payout_request import PayoutRequest
from app.models.payout_history import PayoutHistory
from app.models.user import User
from app.models.product import Product

# Configuración de base de datos de testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Engine de testing con configuración específica para SQLite en memoria
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },  # Permitir múltiples threads para testing
    poolclass=StaticPool,  # Pool estático para SQLite en memoria
    echo=False,  # Cambiar a True para debug SQL
)

# SessionLocal para testing
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# Engine async para testing
async_test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:", echo=False, pool_pre_ping=True
)

# SessionLocal async para testing
AsyncTestingSessionLocal = async_sessionmaker(
    bind=async_test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="function")
def test_db_session() -> Generator[Session, None, None]:
    """
    Fixture para sesión de base de datos de testing.

    Scope: function - Nueva DB limpia por cada test.
    Creates: Todas las tablas en SQLite en memoria.
    Yields: Sesión de SQLAlchemy para el test.
    Cleanup: Cierra sesión y destruye tablas.
    """
    # Crear todas las tablas en la base de datos de testing
    Base.metadata.create_all(bind=test_engine)

    # Crear sesión para el test
    db_session = TestingSessionLocal()

    try:
        yield db_session
    finally:
        db_session.close()
        # Limpiar todas las tablas después del test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture para sesión async de base de datos de testing.

    Scope: function - Nueva DB async limpia por cada test.
    Yields: AsyncSession de SQLAlchemy para tests async.
    """
    # Crear todas las tablas
    async with async_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Crear sesión async para el test
    async with AsyncTestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

    # Limpiar tablas después del test
    async with async_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def override_get_db(async_session: AsyncSession) -> Generator[None, None, None]:
    """
    Fixture para override de dependencia get_db de FastAPI.

    Scope: function - Override por test individual.
    Effect: Redirige get_db() a la sesión de testing.
    Cleanup: Restaura dependencia original.
    """

    async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
        """Dependencia de testing que retorna la sesión de test."""
        try:
            yield async_session
        finally:
            pass  # Session cleanup manejado por test_db_session fixture

    # Override de la dependencia get_db Y get_async_db
    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[get_async_db] = get_test_db

    yield

    # Limpiar override después del test
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_with_test_db(override_get_db) -> TestClient:
    """
    Fixture para TestClient con base de datos de testing configurada.

    Scope: function - Cliente limpio por test.
    Requires: override_get_db fixture activo.
    Returns: TestClient que usa base de datos de testing.
    """
    return TestClient(app)


@pytest.fixture(scope="function")
def test_db_url() -> str:
    """
    Fixture que retorna la URL de la base de datos de testing.

    Returns: URL de SQLite en memoria para logging/debugging.
    """
    return SQLALCHEMY_TEST_DATABASE_URL


@pytest.fixture(autouse=True)
async def mock_redis_for_testing(monkeypatch):
    """Mock Redis para tests sin autenticación"""
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = 1

    async def mock_get_redis():
        return mock_redis

    monkeypatch.setattr("app.core.redis.redis_manager.get_redis", mock_get_redis)
    return mock_redis
@pytest.fixture(scope="function")
def sample_product_data():
    """Datos de muestra para crear productos en tests."""
    import time
    timestamp = int(time.time() * 1000)
    
    return {
        "sku": f"TEST-SAMPLE-{timestamp}",
        "name": "Producto Test Muestra",
        "description": "Producto creado para tests de muestra",
        "precio_venta": 150000.0,
        "precio_costo": 120000.0,
        "categoria": "Test Category",
        "peso": 1.5,
        "dimensiones": {"largo": 20.0, "ancho": 15.0, "alto": 5.0},
        "tags": ["test", "muestra"]
    }
