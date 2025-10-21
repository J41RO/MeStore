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
os.environ["ENVIRONMENT"] = "testing"  # Enable performance optimizations
os.environ["CORS_ORIGINS"] = (
    "http://localhost:3000,http://localhost:8000,http://test.mestore.local"
)
# Forzar uso de base de datos SQLite aislada durante los tests.
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_async.db"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["ASYNC_DATABASE_URL"] = TEST_DATABASE_URL
# Disable problematic imports in testing
os.environ["DISABLE_SEARCH_SERVICE"] = "1"
os.environ["DISABLE_CHROMA_SERVICE"] = "1"
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """
    Fixture para TestClient de FastAPI.

    Scope: function - Cliente nuevo por test con base de datos aislada.
    Returns: TestClient configurado con la app FastAPI principal.
    """
    async def setup_db():
        async with async_test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(setup_db())

    async def override_get_db():
        async with AsyncTestingSessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_async_db] = override_get_db

    # Headers con User-Agent válido para evitar bloqueo de middleware
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    try:
        with TestClient(app, headers=headers) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        async def teardown_db():
            async with async_test_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
        asyncio.run(teardown_db())


@pytest_asyncio.fixture(scope="function")
async def async_client(async_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture async para AsyncClient cuando se requieren operaciones async.

    Scope: function - Nuevo cliente por test function.
    Yields: AsyncClient para operaciones async.

    Fixed to prevent event loop hanging issues by:
    - Storing original dependency overrides
    - Adding explicit timeout
    - Ensuring proper cleanup with small delay
    """
    async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
        """Override de get_db para testing"""
        yield async_session

    # Store original overrides to restore later
    original_overrides = app.dependency_overrides.copy()

    # Override de la dependencia get_db Y get_async_db ANTES de crear el cliente
    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[get_async_db] = get_test_db

    try:
        # Headers con User-Agent válido para evitar bloqueo de middleware
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
            headers=headers,
            timeout=10.0  # Explicit timeout to prevent hanging
        ) as ac:
            yield ac
            # Allow pending tasks to complete before cleanup
            await asyncio.sleep(0.001)
    finally:
        # Restore original dependency state
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


@pytest.fixture(scope="function")
def event_loop():
    """
    Create a new event loop for each test function to prevent hanging.

    This fixture ensures each test gets a fresh event loop, preventing
    event loop conflicts and hanging tests.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    # Cleanup: cancel all pending tasks and close loop
    try:
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        if pending:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    except Exception:
        pass
    finally:
        loop.close()


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
def performance_monitor():
    """
    Mock fixture for performance monitoring in tests.

    Returns a mock performance monitor that doesn't actually
    monitor performance but allows tests to run.
    """
    from unittest.mock import Mock

    mock_monitor = Mock()
    mock_monitor.start_monitoring = Mock()
    mock_monitor.stop_monitoring = Mock()
    mock_monitor.get_metrics = Mock(return_value={
        'response_time': 0.05,
        'cpu_usage': 10.0,
        'memory_usage': 50.0
    })

    return mock_monitor


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
from app.models.order import Order

# Configuración de base de datos de testing - Using in-memory SQLite for faster tests
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


# Engine async para testing - Using in-memory SQLite for faster tests
async_test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False,
    pool_pre_ping=True,
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool,
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


@pytest_asyncio.fixture(scope="function")
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


@pytest_asyncio.fixture(scope="function")
async def async_db_session(async_session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """
    Alias explícito para tests que esperan fixture async_db_session.

    Reutiliza la sesión async de testing para compatibilidad con suites legadas.
    """
    yield async_session


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


@pytest_asyncio.fixture(autouse=True)
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


# === USER FIXTURES FOR TESTING ===

@pytest_asyncio.fixture(scope="function")
async def test_vendor_user(async_session: AsyncSession) -> User:
    """Fixture para usuario vendor de testing."""
    from app.models.user import User, UserType
    import uuid
    from app.core.security import get_password_hash
    from app.core.types import generate_uuid

    vendor = User(
        id=generate_uuid(),  # Explicitly set UUID as string for SQLite compatibility
        email="test_vendor@example.com",
        password_hash=await get_password_hash("testpass123"),
        nombre="Test Vendor",
        apellido="User",
        user_type=UserType.VENDOR,
        is_active=True
    )

    async_session.add(vendor)
    await async_session.commit()
    await async_session.refresh(vendor)
    return vendor


@pytest_asyncio.fixture(scope="function")
async def test_admin_user(async_session: AsyncSession) -> User:
    """Fixture para usuario admin de testing."""
    from app.models.user import User, UserType
    import uuid
    from app.core.security import get_password_hash
    from app.core.types import generate_uuid

    admin = User(
        id=generate_uuid(),  # Explicitly set UUID as string for SQLite compatibility
        email="test_admin@example.com",
        password_hash=await get_password_hash("testpass123"),
        nombre="Test Admin",
        apellido="User",
        user_type=UserType.SUPERUSER,
        is_active=True
    )

    async_session.add(admin)
    await async_session.commit()
    await async_session.refresh(admin)
    return admin


@pytest_asyncio.fixture(scope="function")
async def test_buyer_user(async_session: AsyncSession) -> User:
    """Fixture para usuario buyer de testing."""
    from app.models.user import User, UserType
    import uuid
    from app.core.security import get_password_hash
    from app.core.types import generate_uuid

    buyer = User(
        id=generate_uuid(),  # Explicitly set UUID as string for SQLite compatibility
        email="test_buyer@example.com",
        password_hash=await get_password_hash("testpass123"),
        nombre="Test Buyer",
        apellido="User",
        user_type=UserType.BUYER,
        is_active=True
    )

    async_session.add(buyer)
    await async_session.commit()
    await async_session.refresh(buyer)
    return buyer


@pytest_asyncio.fixture(scope="function")
async def test_buyer(test_buyer_user: User) -> User:
    """Compat fixture que reutiliza test_buyer_user para pruebas legadas."""
    return test_buyer_user


# === AUTHENTICATION TEST FIXTURES ===

@pytest_asyncio.fixture(scope="function")
async def auth_token_vendor(test_vendor_user: User) -> str:
    """Generate valid JWT token for vendor user"""
    from app.core.security import create_access_token
    token_data = {
        "sub": str(test_vendor_user.id),
        "email": test_vendor_user.email,
        "user_type": test_vendor_user.user_type.value,
        "nombre": test_vendor_user.nombre,
        "apellido": test_vendor_user.apellido
    }
    return create_access_token(data=token_data)


@pytest.fixture(scope="function")
def auth_token_admin(test_admin_user: User) -> str:
    """Generate valid JWT token for admin user"""
    from app.core.security import create_access_token
    token_data = {
        "sub": str(test_admin_user.id),
        "email": test_admin_user.email,
        "user_type": test_admin_user.user_type.value,
        "nombre": test_admin_user.nombre,
        "apellido": test_admin_user.apellido
    }
    return create_access_token(data=token_data)


@pytest.fixture(scope="function")
def auth_token_buyer(test_buyer_user: User) -> str:
    """Generate valid JWT token for buyer user"""
    from app.core.security import create_access_token
    token_data = {
        "sub": str(test_buyer_user.id),
        "email": test_buyer_user.email,
        "user_type": test_buyer_user.user_type.value,
        "nombre": test_buyer_user.nombre,
        "apellido": test_buyer_user.apellido
    }
    return create_access_token(data=token_data)


@pytest.fixture(scope="function")
def auth_headers_vendor(auth_token_vendor: str) -> dict:
    """Valid authentication headers for vendor user"""
    return {"Authorization": f"Bearer {auth_token_vendor}"}


@pytest.fixture(scope="function")
def auth_headers_admin(auth_token_admin: str) -> dict:
    """Valid authentication headers for admin user"""
    return {"Authorization": f"Bearer {auth_token_admin}"}


@pytest.fixture(scope="function")
def auth_headers_buyer(auth_token_buyer: str) -> dict:
    """Valid authentication headers for buyer user"""
    return {"Authorization": f"Bearer {auth_token_buyer}"}


# === ORDER TEST FIXTURES ===

@pytest.fixture(scope="function")
def valid_order_payload() -> dict:
    """
    Fixture para payload válido de orden para tests de authentication/authorization.

    Returns: Dict con estructura mínima válida para crear una orden.
    """
    return {
        "items": [{"product_id": "test-product-123", "quantity": 2}],
        "shipping_name": "Test User",
        "shipping_phone": "3001234567",
        "shipping_address": "Test Address 123",
        "shipping_city": "Bogotá",
        "shipping_state": "Cundinamarca"
    }


@pytest.fixture(scope="function")
def customer_user_data() -> dict:
    """
    Fixture para datos de usuario CUSTOMER para tests de authentication.

    Returns: Dict con datos de usuario customer con estructura JWT.
    """
    from app.core.types import generate_uuid
    from app.models.user import UserType

    return {
        "id": generate_uuid(),
        "email": "test_customer@example.com",
        "nombre": "Test Customer",
        "apellido": "User",
        "user_type": UserType.CUSTOMER,
        "is_active": True,
        "is_verified": True
    }


@pytest.fixture(scope="function")
def customer_auth_headers(customer_user_data: dict) -> dict:
    """
    Fixture para headers de autenticación de usuario CUSTOMER.

    Args:
        customer_user_data: Datos del usuario customer

    Returns: Dict con Authorization header y JWT token válido.
    """
    from app.core.security import create_access_token

    token_data = {
        "sub": customer_user_data["id"],
        "email": customer_user_data["email"],
        "nombre": customer_user_data["nombre"],
        "apellido": customer_user_data.get("apellido", ""),
        "user_type": customer_user_data["user_type"].value,
        "is_active": customer_user_data["is_active"],
        "is_verified": customer_user_data["is_verified"]
    }
    token = create_access_token(data=token_data)
    return {"Authorization": f"Bearer {token}"}


# === FINANCIAL TEST FIXTURES ===

@pytest.fixture(scope="function")
def db_session(test_db_session: Session) -> Session:
    """Alias fixture for tests expecting db_session instead of test_db_session."""
    return test_db_session


@pytest.fixture(scope="function")
def audit_logger():
    """Mock audit logger for financial tests."""
    from unittest.mock import Mock
    mock_logger = Mock()
    mock_logger.log_commission_calculation = Mock()
    mock_logger.log_commission_error = Mock()
    mock_logger.log_commission_approval = Mock()
    mock_logger.log_transaction_event = Mock()
    return mock_logger


@pytest.fixture(scope="function")
def test_commission_service(db_session: Session, monkeypatch):
    """Fixture for CommissionService with test database."""
    from app.services.commission_service import CommissionService
    # Set test environment
    monkeypatch.setenv('ENVIRONMENT', 'test')
    monkeypatch.setenv('COMMISSION_AUDIT_LEVEL', 'standard')
    monkeypatch.setenv('COMMISSION_BATCH_SIZE', '50')
    monkeypatch.setenv('COMMISSION_ASYNC_THRESHOLD', '25')

    # Create service with sync session
    service = CommissionService(db_session=db_session)
    return service


@pytest.fixture(scope="function")
def test_confirmed_order(db_session: Session):
    """Fixture for a confirmed test order."""
    from app.models.order import Order, OrderStatus
    from app.models.user import User, UserType
    from decimal import Decimal
    import uuid
    from app.core.types import generate_uuid

    # Create test buyer with explicit UUID for SQLite compatibility
    buyer = User(
        id=generate_uuid(),  # Explicitly set UUID as string for SQLite compatibility
        email="test_buyer@example.com",
        password_hash="$2b$12$test.hash.for.testing",
        nombre="Test Buyer",
        apellido="User",
        user_type=UserType.BUYER,
        is_active=True
    )

    db_session.add(buyer)
    db_session.commit()
    db_session.refresh(buyer)  # Refresh to get auto-generated id

    # Create a simple order without vendor_id since it's not in the model
    order = Order(
        order_number=f"TEST-ORDER-{uuid.uuid4().hex[:8]}",
        buyer_id=buyer.id,
        total_amount=100000.0,  # Float type as per model
        status=OrderStatus.CONFIRMED,
        shipping_name="Test User",
        shipping_phone="3001234567",
        shipping_address="Test Address 123, Test City",
        shipping_city="Bogotá",
        shipping_state="Cundinamarca"
    )

    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


@pytest.fixture(scope="function")
def sample_commission_data():
    """Sample commission data for testing."""
    from decimal import Decimal
    return {
        "commission_rate": Decimal("0.05"),  # 5%
        "order_amount": Decimal("100000.00"),  # 100k COP
        "commission_type": "STANDARD",
        "currency": "COP"
    }


# === FINANCIAL FACTORIES INTEGRATION ===

@pytest.fixture(scope="function")
def financial_factory(test_db_session: Session):
    """Fixture for financial factories with test database."""
    from tests.fixtures.financial.financial_factories import FinancialScenarioFactory
    return FinancialScenarioFactory(test_db_session)


@pytest.fixture(scope="function")
def edge_case_factory(test_db_session: Session):
    """Fixture for edge case financial factories."""
    from tests.fixtures.financial.financial_factories import EdgeCaseFinancialFactory
    return EdgeCaseFinancialFactory(test_db_session)


# === CUSTOM PYTEST MARKERS ===

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "integration_financial: Financial integration tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "auth: Authentication tests")
    config.addinivalue_line("markers", "database: Database tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "financial: Financial system tests")
    config.addinivalue_line("markers", "commission: Commission calculation tests")
    config.addinivalue_line("markers", "transaction: Transaction processing tests")
    config.addinivalue_line("markers", "critical: Critical functionality tests")
    config.addinivalue_line("markers", "smoke: Smoke tests for basic functionality")
    config.addinivalue_line("markers", "sms_security: SMS security and rate limiting tests")



# =============================================================================
# ASYNC SESSION MAKER PARA E2E TESTS
# =============================================================================
# Alias para compatibilidad con tests E2E existentes
async_session_maker = AsyncTestingSessionLocal


# =============================================================================
# SMS SECURITY TEST FIXTURES
# =============================================================================

@pytest.fixture
def mock_redis_service():
    """Mock de RedisService para testing SMS security"""
    mock = AsyncMock()

    # Storage in-memory para simular Redis
    mock._storage = {}

    async def cache_get(key: str):
        return mock._storage.get(key)

    async def cache_set(key: str, value: str, expire: int):
        mock._storage[key] = value
        return True

    async def cache_delete(key: str):
        if key in mock._storage:
            del mock._storage[key]
        return True

    # Mock redis.incr
    mock.redis = AsyncMock()
    async def incr(key: str):
        current = int(mock._storage.get(key, "0"))
        mock._storage[key] = str(current + 1)
        return current + 1
    mock.redis.incr = incr

    mock.cache_get = cache_get
    mock.cache_set = cache_set
    mock.cache_delete = cache_delete

    return mock


@pytest.fixture
def mock_request():
    """Mock de FastAPI Request para testing IP extraction"""
    from unittest.mock import Mock
    from fastapi import Request

    request = Mock(spec=Request)
    request.client = Mock()
    request.client.host = "203.0.113.1"
    request.headers = {}
    return request


@pytest.fixture
def mock_sms_service_success(monkeypatch):
    """Mock SMSService que simula éxito de Twilio"""
    async def mock_send_verification(*args, **kwargs):
        return {
            "success": True,
            "status": "pending",
            "sid": "SM1234567890"
        }

    from app.services import sms_service
    monkeypatch.setattr(
        sms_service.SMSService,
        "send_verification_code",
        mock_send_verification
    )


@pytest_asyncio.fixture
async def redis_service_with_storage(monkeypatch):
    """
    Mock RedisService with persistent in-memory storage for SMS rate limiting tests.
    Overrides the autouse mock_redis_for_testing fixture.
    """
    from app.core.redis import RedisService

    # Storage dict that persists across calls
    storage = {}

    # Create mock RedisService instance
    mock_redis_service = AsyncMock(spec=RedisService)

    async def mock_cache_get(key: str):
        return storage.get(key)

    async def mock_cache_set(key: str, value: str, expire: int = 600):
        storage[key] = value
        return True

    async def mock_cache_delete(key: str):
        if key in storage:
            del storage[key]
        return True

    # Mock redis client for incr operation
    mock_redis_client = AsyncMock()

    async def mock_incr(key: str):
        current = int(storage.get(key, "0"))
        storage[key] = str(current + 1)
        return current + 1

    async def mock_setex(key: str, expire: int, value: str):
        storage[key] = value
        return True

    mock_redis_client.incr = mock_incr
    mock_redis_client.setex = mock_setex

    # Assign mock methods to service
    mock_redis_service.cache_get = mock_cache_get
    mock_redis_service.cache_set = mock_cache_set
    mock_redis_service.cache_delete = mock_cache_delete
    mock_redis_service.redis = mock_redis_client

    # Override the get_redis_service dependency in FastAPI app
    from app.main import app
    from app.core.redis.dependencies import get_redis_service as get_redis_service_dep

    def get_test_redis_service():
        return mock_redis_service

    # Override FastAPI dependency
    app.dependency_overrides[get_redis_service_dep] = get_test_redis_service

    yield mock_redis_service

    # Cleanup - remove override after test
    if get_redis_service_dep in app.dependency_overrides:
        del app.dependency_overrides[get_redis_service_dep]
