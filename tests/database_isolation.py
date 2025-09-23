"""
Database Isolation Strategy for TDD Testing
==========================================

This module provides comprehensive database isolation for TDD testing,
ensuring each test runs in complete isolation with proper cleanup.

Features:
- Transaction-based isolation
- Test-specific database instances
- Automatic rollback and cleanup
- Async/sync session management
- Data seeding and fixtures
"""

import asyncio
import os
import tempfile
import uuid
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator, Dict, Any, List
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.user import User, UserType
from app.models.product import Product
from app.models.order import Order
from app.models.transaction import Transaction
from app.core.security import get_password_hash


class DatabaseIsolationManager:
    """
    Manages database isolation for TDD testing with multiple strategies.

    Strategies:
    1. Transaction rollback (fastest)
    2. Fresh database per test (most isolated)
    3. Shared test database with cleanup
    """

    def __init__(self, isolation_strategy: str = "transaction"):
        self.isolation_strategy = isolation_strategy
        self.test_engines = {}
        self.test_sessions = {}
        self.active_transactions = {}

    @asynccontextmanager
    async def isolated_async_session(self, test_id: str = None) -> AsyncGenerator[AsyncSession, None]:
        """
        Provide an isolated async database session for testing.

        Args:
            test_id: Unique identifier for the test (auto-generated if None)

        Yields:
            AsyncSession: Isolated database session
        """
        if not test_id:
            test_id = str(uuid.uuid4())

        if self.isolation_strategy == "transaction":
            async with self._transaction_isolation(test_id) as session:
                yield session
        elif self.isolation_strategy == "fresh_db":
            async with self._fresh_database_isolation(test_id) as session:
                yield session
        else:
            async with self._shared_db_isolation(test_id) as session:
                yield session

    @contextmanager
    def isolated_sync_session(self, test_id: str = None) -> Generator[Session, None, None]:
        """
        Provide an isolated sync database session for testing.

        Args:
            test_id: Unique identifier for the test

        Yields:
            Session: Isolated database session
        """
        if not test_id:
            test_id = str(uuid.uuid4())

        if self.isolation_strategy == "transaction":
            with self._sync_transaction_isolation(test_id) as session:
                yield session
        elif self.isolation_strategy == "fresh_db":
            with self._sync_fresh_database_isolation(test_id) as session:
                yield session
        else:
            with self._sync_shared_db_isolation(test_id) as session:
                yield session

    @asynccontextmanager
    async def _transaction_isolation(self, test_id: str) -> AsyncGenerator[AsyncSession, None]:
        """Transaction-based isolation - fastest method."""
        # Create async engine for this test
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,
            pool_pre_ping=True
        )

        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Create session factory
        async_session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        # Start transaction
        async with async_session_factory() as session:
            # Begin nested transaction
            transaction = await session.begin()

            try:
                self.active_transactions[test_id] = transaction
                yield session
            finally:
                # Always rollback to ensure isolation
                await transaction.rollback()
                await session.close()
                await engine.dispose()
                if test_id in self.active_transactions:
                    del self.active_transactions[test_id]

    @contextmanager
    def _sync_transaction_isolation(self, test_id: str) -> Generator[Session, None, None]:
        """Sync transaction-based isolation."""
        # Create sync engine for this test
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )

        # Create all tables
        Base.metadata.create_all(bind=engine)

        # Create session factory
        session_factory = sessionmaker(bind=engine)

        # Start transaction
        with session_factory() as session:
            transaction = session.begin()

            try:
                self.active_transactions[test_id] = transaction
                yield session
            finally:
                # Always rollback to ensure isolation
                try:
                    if transaction.is_active:
                        transaction.rollback()
                except Exception:
                    # Transaction might already be closed - ignore
                    pass

                try:
                    session.close()
                except Exception:
                    pass

                try:
                    engine.dispose()
                except Exception:
                    pass

                if test_id in self.active_transactions:
                    del self.active_transactions[test_id]

    @asynccontextmanager
    async def _fresh_database_isolation(self, test_id: str) -> AsyncGenerator[AsyncSession, None]:
        """Fresh database per test - maximum isolation."""
        # Create temporary database file
        db_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{test_id}.db")
        db_path = db_file.name
        db_file.close()

        try:
            # Create async engine with temporary database
            engine = create_async_engine(
                f"sqlite+aiosqlite:///{db_path}",
                echo=False,
                pool_pre_ping=True
            )

            # Create all tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            # Create session factory
            async_session_factory = async_sessionmaker(
                bind=engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            async with async_session_factory() as session:
                yield session

        finally:
            # Cleanup
            await engine.dispose()
            try:
                os.unlink(db_path)
            except OSError:
                pass  # File might already be deleted

    @contextmanager
    def _sync_fresh_database_isolation(self, test_id: str) -> Generator[Session, None, None]:
        """Sync fresh database per test."""
        # Create temporary database file
        db_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{test_id}.db")
        db_path = db_file.name
        db_file.close()

        try:
            # Create sync engine with temporary database
            engine = create_engine(
                f"sqlite:///{db_path}",
                echo=False
            )

            # Create all tables
            Base.metadata.create_all(bind=engine)

            # Create session factory
            session_factory = sessionmaker(bind=engine)

            with session_factory() as session:
                yield session

        finally:
            # Cleanup
            engine.dispose()
            try:
                os.unlink(db_path)
            except OSError:
                pass

    @asynccontextmanager
    async def _shared_db_isolation(self, test_id: str) -> AsyncGenerator[AsyncSession, None]:
        """Shared test database with cleanup."""
        # Create shared test engine if not exists
        if not hasattr(self, '_shared_async_engine'):
            self._shared_async_engine = create_async_engine(
                "sqlite+aiosqlite:///./test_shared.db",
                echo=False,
                pool_pre_ping=True
            )

            # Create all tables
            async with self._shared_async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

        # Create session factory
        async_session_factory = async_sessionmaker(
            bind=self._shared_async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with async_session_factory() as session:
            try:
                yield session
            finally:
                # Cleanup: Remove all data from tables
                await self._cleanup_test_data(session)

    @contextmanager
    def _sync_shared_db_isolation(self, test_id: str) -> Generator[Session, None, None]:
        """Sync shared test database with cleanup."""
        # Create shared test engine if not exists
        if not hasattr(self, '_shared_sync_engine'):
            self._shared_sync_engine = create_engine(
                "sqlite:///./test_shared.db",
                echo=False
            )

            # Create all tables
            Base.metadata.create_all(bind=self._shared_sync_engine)

        # Create session factory
        session_factory = sessionmaker(bind=self._shared_sync_engine)

        with session_factory() as session:
            try:
                yield session
            finally:
                # Cleanup: Remove all data from tables
                self._cleanup_test_data_sync(session)

    async def _cleanup_test_data(self, session: AsyncSession):
        """Clean up all test data from shared database."""
        try:
            # Delete in reverse order to handle foreign key constraints
            await session.execute("DELETE FROM transactions")
            await session.execute("DELETE FROM orders")
            await session.execute("DELETE FROM products")
            await session.execute("DELETE FROM users")
            await session.commit()
        except Exception:
            await session.rollback()
            raise

    def _cleanup_test_data_sync(self, session: Session):
        """Clean up all test data from shared database (sync)."""
        try:
            # Delete in reverse order to handle foreign key constraints
            session.execute("DELETE FROM transactions")
            session.execute("DELETE FROM orders")
            session.execute("DELETE FROM products")
            session.execute("DELETE FROM users")
            session.commit()
        except Exception:
            session.rollback()
            raise


class TDDDataSeeder:
    """
    Provides standardized test data seeding for TDD tests.

    Creates consistent, predictable test data for various scenarios.
    """

    @staticmethod
    async def seed_basic_users(session: AsyncSession) -> Dict[str, User]:
        """Seed basic user data for testing."""
        users = {}

        # Create admin user
        admin = User(
            id=uuid.uuid4(),
            email="admin@test.com",
            password_hash=await get_password_hash("admin123"),
            nombre="Test",
            apellido="Admin",
            user_type=UserType.SUPERUSER,
            is_active=True
        )
        session.add(admin)
        users["admin"] = admin

        # Create vendor user
        vendor = User(
            id=uuid.uuid4(),
            email="vendor@test.com",
            password_hash=await get_password_hash("vendor123"),
            nombre="Test",
            apellido="Vendor",
            user_type=UserType.VENDOR,
            is_active=True
        )
        session.add(vendor)
        users["vendor"] = vendor

        # Create buyer user
        buyer = User(
            id=uuid.uuid4(),
            email="buyer@test.com",
            password_hash=await get_password_hash("buyer123"),
            nombre="Test",
            apellido="Buyer",
            user_type=UserType.BUYER,
            is_active=True
        )
        session.add(buyer)
        users["buyer"] = buyer

        await session.commit()

        # Refresh objects to get generated IDs
        for user in users.values():
            await session.refresh(user)

        return users

    @staticmethod
    async def seed_sample_products(session: AsyncSession, vendor_id: uuid.UUID) -> List[Product]:
        """Seed sample product data for testing."""
        products = []

        product_data = [
            {
                "sku": "TEST-PROD-001",
                "nombre": "Test Product 1",
                "descripcion": "First test product",
                "precio_venta": 100000.0,
                "precio_costo": 75000.0,
                "stock": 10
            },
            {
                "sku": "TEST-PROD-002",
                "nombre": "Test Product 2",
                "descripcion": "Second test product",
                "precio_venta": 150000.0,
                "precio_costo": 100000.0,
                "stock": 5
            },
            {
                "sku": "TEST-PROD-003",
                "nombre": "Test Product 3",
                "descripcion": "Third test product",
                "precio_venta": 200000.0,
                "precio_costo": 150000.0,
                "stock": 0  # Out of stock product
            }
        ]

        for data in product_data:
            product = Product(
                id=uuid.uuid4(),
                vendor_id=vendor_id,
                **data
            )
            session.add(product)
            products.append(product)

        await session.commit()

        # Refresh to get generated IDs
        for product in products:
            await session.refresh(product)

        return products

    @staticmethod
    async def seed_sample_orders(session: AsyncSession, buyer_id: uuid.UUID) -> List[Order]:
        """Seed sample order data for testing."""
        orders = []

        order_data = [
            {
                "order_number": "TEST-ORD-001",
                "total_amount": 100000.0,
                "status": "PENDING",
                "shipping_name": "Test Customer",
                "shipping_phone": "3001234567",
                "shipping_address": "Test Address 123",
                "shipping_city": "Bogotá",
                "shipping_state": "Cundinamarca"
            },
            {
                "order_number": "TEST-ORD-002",
                "total_amount": 250000.0,
                "status": "CONFIRMED",
                "shipping_name": "Test Customer 2",
                "shipping_phone": "3007654321",
                "shipping_address": "Test Address 456",
                "shipping_city": "Medellín",
                "shipping_state": "Antioquia"
            }
        ]

        for data in order_data:
            order = Order(
                id=uuid.uuid4(),
                buyer_id=buyer_id,
                **data
            )
            session.add(order)
            orders.append(order)

        await session.commit()

        # Refresh to get generated IDs
        for order in orders:
            await session.refresh(order)

        return orders


# Global isolation manager instance
isolation_manager = DatabaseIsolationManager(
    isolation_strategy=os.getenv("TEST_ISOLATION_STRATEGY", "transaction")
)


# Pytest fixtures for database isolation
@pytest.fixture(scope="function")
async def isolated_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Pytest fixture for isolated async database session."""
    async with isolation_manager.isolated_async_session() as session:
        yield session


@pytest.fixture(scope="function")
def isolated_sync_session() -> Generator[Session, None, None]:
    """Pytest fixture for isolated sync database session."""
    with isolation_manager.isolated_sync_session() as session:
        yield session


@pytest.fixture(scope="function")
async def seeded_test_data(isolated_async_session: AsyncSession) -> Dict[str, Any]:
    """Pytest fixture for pre-seeded test data."""
    seeder = TDDDataSeeder()

    # Seed users
    users = await seeder.seed_basic_users(isolated_async_session)

    # Seed products for vendor
    products = await seeder.seed_sample_products(
        isolated_async_session,
        users["vendor"].id
    )

    # Seed orders for buyer
    orders = await seeder.seed_sample_orders(
        isolated_async_session,
        users["buyer"].id
    )

    return {
        "users": users,
        "products": products,
        "orders": orders,
        "session": isolated_async_session
    }


@pytest.fixture(autouse=True)
async def cleanup_database_connections():
    """Auto-cleanup fixture to ensure all database connections are closed."""
    yield

    # Cleanup any remaining connections
    for test_id, transaction in isolation_manager.active_transactions.items():
        try:
            if hasattr(transaction, 'rollback'):
                await transaction.rollback()
        except Exception:
            pass  # Transaction might already be closed

    isolation_manager.active_transactions.clear()


# Export key components
__all__ = [
    'DatabaseIsolationManager',
    'TDDDataSeeder',
    'isolation_manager',
    'isolated_async_session',
    'isolated_sync_session',
    'seeded_test_data'
]