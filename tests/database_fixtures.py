"""
Advanced Test Database Configuration for TDD
===========================================

This module provides comprehensive database configuration for TDD testing
with proper isolation, cleanup, and performance optimization.

Author: TDD Specialist AI
Date: 2025-09-17
Purpose: Establish robust test database infrastructure for TDD methodology
"""

import asyncio
import os
import tempfile
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Generator

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base


class TestDatabaseManager:
    """
    Advanced test database manager with isolation and cleanup.

    Features:
    - Per-test database isolation
    - Automatic cleanup
    - Transaction rollback for speed
    - Async and sync session support
    - Performance monitoring
    """

    def __init__(self):
        self.temp_db_files = []
        self.active_sessions = []

    def create_test_db_url(self, in_memory: bool = True) -> str:
        """Create a test database URL with optional file-based storage."""
        if in_memory:
            return "sqlite:///:memory:"
        else:
            # Create temporary file for persistent testing
            temp_file = tempfile.NamedTemporaryFile(
                suffix=".db", prefix="test_mestore_", delete=False
            )
            self.temp_db_files.append(temp_file.name)
            return f"sqlite:///{temp_file.name}"

    def create_sync_test_engine(self, database_url: str = None):
        """Create synchronous test engine with optimized settings."""
        if database_url is None:
            database_url = self.create_test_db_url()

        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False,  # Set to True for SQL debugging
            future=True,
        )

        # Enable WAL mode for better concurrency (file-based SQLite only)
        if not database_url.endswith(":memory:"):
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        return engine

    def create_async_test_engine(self, database_url: str = None):
        """Create asynchronous test engine with optimized settings."""
        if database_url is None:
            database_url = "sqlite+aiosqlite:///:memory:"

        engine = create_async_engine(
            database_url,
            echo=False,  # Set to True for SQL debugging
            pool_pre_ping=True,
            future=True,
        )

        return engine

    def cleanup(self):
        """Clean up temporary database files."""
        for db_file in self.temp_db_files:
            try:
                os.unlink(db_file)
            except FileNotFoundError:
                pass
        self.temp_db_files.clear()

    def __del__(self):
        """Cleanup on object destruction."""
        self.cleanup()


# Global test database manager
test_db_manager = TestDatabaseManager()


class IsolatedTestSession:
    """
    Test session with complete isolation using transactions.

    Each test runs in a transaction that is rolled back at the end,
    ensuring no data persists between tests while maintaining speed.
    """

    def __init__(self, engine):
        self.engine = engine
        self.connection = None
        self.transaction = None
        self.session = None

    def __enter__(self):
        """Start isolated session with transaction."""
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()

        # Create session bound to this connection
        session_factory = sessionmaker(bind=self.connection)
        self.session = session_factory()

        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Rollback transaction and cleanup."""
        if self.session:
            self.session.close()
        if self.transaction:
            self.transaction.rollback()
        if self.connection:
            self.connection.close()


class AsyncIsolatedTestSession:
    """
    Async version of isolated test session.
    """

    def __init__(self, engine):
        self.engine = engine
        self.connection = None
        self.transaction = None
        self.session = None

    async def __aenter__(self):
        """Start isolated async session with transaction."""
        self.connection = await self.engine.connect()
        self.transaction = await self.connection.begin()

        # Create async session bound to this connection
        session_factory = async_sessionmaker(bind=self.connection, class_=AsyncSession)
        self.session = session_factory()

        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Rollback transaction and cleanup."""
        if self.session:
            await self.session.close()
        if self.transaction:
            await self.transaction.rollback()
        if self.connection:
            await self.connection.close()


# Test Database Fixtures

@pytest.fixture(scope="session")
def test_engine():
    """Session-scoped test engine for performance."""
    engine = test_db_manager.create_sync_test_engine()

    # Create all tables once per session
    Base.metadata.create_all(engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="session")
def async_test_engine():
    """Session-scoped async test engine."""
    engine = test_db_manager.create_async_test_engine()

    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # Run table creation
    asyncio.get_event_loop().run_until_complete(create_tables())

    yield engine

    # Cleanup
    async def drop_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    asyncio.get_event_loop().run_until_complete(drop_tables())
    engine.sync_close()


@pytest.fixture(scope="function")
def isolated_db_session(test_engine) -> Generator[Session, None, None]:
    """
    Function-scoped isolated database session.

    Uses transaction rollback for complete isolation between tests
    while maintaining high performance.
    """
    with IsolatedTestSession(test_engine) as session:
        yield session


@pytest.fixture(scope="function")
async def isolated_async_session(async_test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Function-scoped isolated async database session.
    """
    async with AsyncIsolatedTestSession(async_test_engine) as session:
        yield session


@pytest.fixture(scope="function")
def transactional_db_session(test_engine) -> Generator[Session, None, None]:
    """
    Alternative session fixture using explicit transaction control.

    Useful for tests that need to control transaction boundaries.
    """
    connection = test_engine.connect()
    transaction = connection.begin()

    try:
        session = sessionmaker(bind=connection)()
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def clean_db_session(test_engine) -> Generator[Session, None, None]:
    """
    Clean database session that actually commits data.

    Use sparingly for integration tests that need persistent data.
    Automatically cleans up after test completion.
    """
    session = sessionmaker(bind=test_engine)()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        # Clean up all data after test
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()


@pytest.fixture(scope="function")
def db_performance_monitor():
    """
    Database performance monitoring for TDD tests.

    Helps identify slow queries and optimization opportunities.
    """
    import time
    from collections import defaultdict

    class PerformanceMonitor:
        def __init__(self):
            self.query_times = defaultdict(list)
            self.start_time = None

        def start_monitoring(self):
            self.start_time = time.time()

        def stop_monitoring(self):
            if self.start_time:
                return time.time() - self.start_time
            return 0

        def log_query(self, query: str, execution_time: float):
            self.query_times[query].append(execution_time)

        def get_slow_queries(self, threshold: float = 0.1) -> dict:
            """Get queries that took longer than threshold."""
            slow_queries = {}
            for query, times in self.query_times.items():
                avg_time = sum(times) / len(times)
                if avg_time > threshold:
                    slow_queries[query] = {
                        'avg_time': avg_time,
                        'max_time': max(times),
                        'call_count': len(times)
                    }
            return slow_queries

    return PerformanceMonitor()


# Test Data Factories

class TestDataFactory:
    """
    Factory for creating test data with proper relationships.

    Provides methods to create valid test data that respects
    business rules and database constraints.
    """

    def __init__(self, session: Session):
        self.session = session
        self._created_objects = []

    def create_test_user(self, user_type: str = "BUYER", **kwargs):
        """Create a test user with valid data."""
        from app.models.user import User, UserType
        import asyncio

        # Use sync password hashing for sync tests
        defaults = {
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "password_hash": "$2b$12$test.hash.for.testing.only",  # Static test hash
            "nombre": "Test",
            "apellido": "User",
            "user_type": UserType[user_type],
            "is_active": True
        }
        defaults.update(kwargs)

        user = User(**defaults)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        self._created_objects.append(user)

        return user

    def create_test_product(self, vendor_id: str = None, **kwargs):
        """Create a test product with valid data."""
        from app.models.product import Product

        if vendor_id is None:
            vendor = self.create_test_user("VENDOR")
            vendor_id = vendor.id

        defaults = {
            "sku": f"TEST-{uuid.uuid4().hex[:8].upper()}",
            "name": "Test Product",
            "description": "A test product for TDD testing",
            "precio_venta": 100000.0,
            "precio_costo": 80000.0,
            "is_active": True,
            "vendedor_id": vendor_id
        }
        defaults.update(kwargs)

        product = Product(**defaults)
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        self._created_objects.append(product)

        return product

    def create_test_order(self, buyer_id: str = None, **kwargs):
        """Create a test order with valid data."""
        from app.models.order import Order, OrderStatus

        if buyer_id is None:
            buyer = self.create_test_user("BUYER")
            buyer_id = buyer.id

        defaults = {
            "order_number": f"TEST-ORDER-{uuid.uuid4().hex[:8].upper()}",
            "buyer_id": buyer_id,
            "total_amount": 100000.0,
            "status": OrderStatus.PENDING,
            "shipping_name": "Test Buyer",
            "shipping_phone": "3001234567",
            "shipping_address": "Test Address 123",
            "shipping_city": "Bogotá",
            "shipping_state": "Cundinamarca"
        }
        defaults.update(kwargs)

        order = Order(**defaults)
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        self._created_objects.append(order)

        return order

    def cleanup(self):
        """Clean up all created test objects."""
        for obj in reversed(self._created_objects):
            try:
                self.session.delete(obj)
            except Exception:
                pass
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
        self._created_objects.clear()


@pytest.fixture(scope="function")
def test_data_factory(isolated_db_session: Session):
    """Fixture providing test data factory."""
    factory = TestDataFactory(isolated_db_session)
    yield factory
    factory.cleanup()


# Cleanup fixture
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_databases():
    """Auto-cleanup fixture for test databases."""
    yield
    test_db_manager.cleanup()


if __name__ == "__main__":
    print("Test Database Configuration for TDD")
    print("==================================")
    print("Features:")
    print("- Isolated test sessions with transaction rollback")
    print("- Async and sync database support")
    print("- Performance monitoring")
    print("- Test data factories")
    print("- Automatic cleanup")