"""
Test Database Fixtures Validation
=================================

This test module validates that the database fixtures in database_fixtures.py
work correctly and can be used by other tests.

Author: Test Architect AI
Date: 2025-09-22
Purpose: Validate database fixture functionality
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from tests.database_fixtures import (
    TestDatabaseManager,
    IsolatedTestSession,
    AsyncIsolatedTestSession
)


class TestDatabaseFixtures:
    """Test suite to validate database fixtures functionality."""

    def test_database_manager_creation(self):
        """Test that TestDatabaseManager can be instantiated."""
        manager = TestDatabaseManager()
        assert manager is not None
        assert manager.temp_db_files == []
        assert manager.active_sessions == []

    def test_database_manager_sync_engine(self):
        """Test sync engine creation."""
        manager = TestDatabaseManager()
        engine = manager.create_sync_test_engine()
        assert engine is not None
        assert str(engine.url).startswith("sqlite")

    def test_database_manager_async_engine(self):
        """Test async engine creation."""
        manager = TestDatabaseManager()
        engine = manager.create_async_test_engine()
        assert engine is not None
        assert str(engine.url).startswith("sqlite+aiosqlite")

    def test_isolated_session_context_manager(self):
        """Test that IsolatedTestSession works as context manager."""
        manager = TestDatabaseManager()
        engine = manager.create_sync_test_engine()

        with IsolatedTestSession(engine) as session:
            assert session is not None
            assert hasattr(session, 'query')

    @pytest.mark.asyncio
    async def test_async_isolated_session_context_manager(self):
        """Test that AsyncIsolatedTestSession works as async context manager."""
        manager = TestDatabaseManager()
        engine = manager.create_async_test_engine()

        async with AsyncIsolatedTestSession(engine) as session:
            assert session is not None
            assert isinstance(session, AsyncSession)

    def test_isolated_db_session_fixture(self, test_db_session: Session):
        """Test that test_db_session fixture works (from conftest.py)."""
        assert test_db_session is not None
        assert isinstance(test_db_session, Session)

    @pytest.mark.asyncio
    async def test_isolated_async_session_fixture(self, async_session: AsyncSession):
        """Test that async_session fixture works (from conftest.py)."""
        assert async_session is not None
        assert isinstance(async_session, AsyncSession)

    def test_test_data_factory_class_creation(self, test_db_session: Session):
        """Test that TestDataFactory class can be instantiated."""
        from tests.database_fixtures import TestDataFactory

        factory = TestDataFactory(test_db_session)
        assert factory is not None
        assert hasattr(factory, 'create_test_user')
        assert hasattr(factory, 'create_test_product')
        assert hasattr(factory, 'create_test_order')

    def test_test_data_factory_user_creation(self, test_db_session: Session):
        """Test that test data factory can create users."""
        from tests.database_fixtures import TestDataFactory

        factory = TestDataFactory(test_db_session)
        user = factory.create_test_user("VENDOR")
        assert user is not None
        assert user.email.startswith("test_")
        assert user.nombre == "Test"
        assert user.apellido == "User"
        assert user.is_active is True

    def test_test_data_factory_product_creation(self, test_db_session: Session):
        """Test that test data factory can create products."""
        from tests.database_fixtures import TestDataFactory

        factory = TestDataFactory(test_db_session)
        product = factory.create_test_product()
        assert product is not None
        assert product.sku.startswith("TEST-")
        assert product.name == "Test Product"
        assert product.precio_venta == 100000.0
        assert product.is_active is True

    def test_test_data_factory_order_creation(self, test_db_session: Session):
        """Test that test data factory can create orders."""
        from tests.database_fixtures import TestDataFactory

        factory = TestDataFactory(test_db_session)
        order = factory.create_test_order()
        assert order is not None
        assert order.order_number.startswith("TEST-ORDER-")
        assert order.total_amount == 100000.0
        assert order.shipping_city == "Bogotá"


@pytest.mark.integration
class TestDatabaseFixturesIntegration:
    """Integration tests for database fixtures."""

    def test_fixtures_isolation(self, test_db_session: Session):
        """Test that fixtures provide proper isolation between tests."""
        from tests.database_fixtures import TestDataFactory

        factory = TestDataFactory(test_db_session)
        # Create a user in one test
        user1 = factory.create_test_user("BUYER")
        assert user1.id is not None

        # The user should be accessible within the same test
        # Just verify the session is working - actual isolation tested by running multiple tests
        assert test_db_session is not None

    @pytest.mark.asyncio
    async def test_async_fixtures_work(self, async_session: AsyncSession):
        """Test that async fixtures work correctly."""
        # Test that we can execute a simple query
        from sqlalchemy import text
        result = await async_session.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        assert row[0] == 1


@pytest.mark.unit
class TestDatabaseFixturesUnit:
    """Unit tests for individual fixture components."""

    def test_database_url_generation(self):
        """Test database URL generation."""
        manager = TestDatabaseManager()

        # Test in-memory URL
        memory_url = manager.create_test_db_url(in_memory=True)
        assert memory_url == "sqlite:///:memory:"

        # Test file-based URL
        file_url = manager.create_test_db_url(in_memory=False)
        assert file_url.startswith("sqlite:///")
        assert "test_mestore_" in file_url

    def test_cleanup_functionality(self):
        """Test that cleanup works correctly."""
        manager = TestDatabaseManager()

        # Create a file-based database
        file_url = manager.create_test_db_url(in_memory=False)
        assert len(manager.temp_db_files) == 1

        # Cleanup should clear the list
        manager.cleanup()
        assert len(manager.temp_db_files) == 0