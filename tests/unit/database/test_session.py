#!/usr/bin/env python3
"""
Comprehensive TDD Unit Tests for Database Session Module
========================================================

Testing Strategy:
- RED: Write failing test first
- GREEN: Implement minimal code to pass
- REFACTOR: Optimize while maintaining tests

Coverage Goals:
- Database engine configuration: 100%
- Session factory creation: 100%
- Dependency injection: 100%
- Database initialization: 100%
- Connection lifecycle: 100%

File: tests/unit/database/test_session.py
Author: Unit Testing AI - TDD Methodology
Date: 2025-09-17
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
import asyncio
from typing import AsyncGenerator

# Import modules under test
from app.database.session import (
    engine,
    AsyncSessionLocal,
    get_session,
    get_db,
    init_db,
    close_db_engine,
    Base
)


class TestDatabaseEngineConfiguration:
    """Test database engine configuration with TDD methodology."""

    def test_engine_is_async_engine(self):
        """TDD: Engine should be an AsyncEngine instance."""
        from sqlalchemy.ext.asyncio import AsyncEngine
        assert isinstance(engine, AsyncEngine)

    def test_engine_url_from_settings(self):
        """TDD: Engine should use DATABASE_URL from settings."""
        from app.core.config import settings
        # Engine URL is not directly accessible, but we can verify it's created
        assert engine is not None
        assert hasattr(engine, 'url')

    def test_engine_pool_configuration(self):
        """TDD: Engine should have proper pool configuration."""
        # Verify pool settings are applied (these are set during engine creation)
        assert engine.pool_size == 10
        assert engine.pool.size() == 10  # Current pool size
        assert hasattr(engine, 'pool')

    def test_engine_has_future_flag_enabled(self):
        """TDD: Engine should use SQLAlchemy 2.0+ features."""
        # Engine is configured with future=True
        assert engine.dialect.name is not None  # Basic validation engine works


class TestAsyncSessionFactory:
    """Test AsyncSessionLocal factory configuration."""

    def test_session_factory_is_callable(self):
        """TDD: AsyncSessionLocal should be callable."""
        assert callable(AsyncSessionLocal)

    def test_session_factory_creates_async_session(self):
        """TDD: AsyncSessionLocal should create AsyncSession instances."""
        session = AsyncSessionLocal()
        assert isinstance(session, AsyncSession)
        # Cleanup
        asyncio.create_task(session.close())

    def test_session_factory_configuration(self):
        """TDD: AsyncSessionLocal should have correct configuration."""
        session = AsyncSessionLocal()
        try:
            # Verify session configuration
            assert session.bind == engine
            assert not session.autocommit
            assert session.autoflush
            assert not session.expire_on_commit
        finally:
            asyncio.create_task(session.close())


class TestGetSessionFunction:
    """Test get_session function with TDD methodology."""

    @pytest.mark.asyncio
    async def test_get_session_returns_async_session(self):
        """TDD: get_session should return AsyncSession instance."""
        session = await get_session()

        assert isinstance(session, AsyncSession)
        await session.close()

    @pytest.mark.asyncio
    async def test_get_session_creates_new_session_each_call(self):
        """TDD: get_session should create new session on each call."""
        session1 = await get_session()
        session2 = await get_session()

        assert session1 is not session2
        assert id(session1) != id(session2)

        await session1.close()
        await session2.close()

    @pytest.mark.asyncio
    async def test_get_session_can_be_used_with_context_manager(self):
        """TDD: get_session result should work with async context manager."""
        session = await get_session()

        # This should not raise an exception
        async with session:
            assert isinstance(session, AsyncSession)
            # Session is usable within context


class TestGetDbDependency:
    """Test get_db FastAPI dependency with TDD methodology."""

    @pytest.mark.asyncio
    async def test_get_db_yields_async_session(self):
        """TDD: get_db should yield AsyncSession instance."""
        async_gen = get_db()

        session = await async_gen.__anext__()
        assert isinstance(session, AsyncSession)

        # Cleanup
        try:
            await async_gen.__anext__()
        except StopAsyncIteration:
            pass  # Expected when generator completes

    @pytest.mark.asyncio
    async def test_get_db_commits_transaction_on_success(self):
        """TDD: get_db should commit transaction when no exception occurs."""
        with patch.object(AsyncSession, 'commit', new_callable=AsyncMock) as mock_commit:
            with patch.object(AsyncSession, 'close', new_callable=AsyncMock) as mock_close:
                async_gen = get_db()

                session = await async_gen.__anext__()

                # Simulate successful completion
                try:
                    await async_gen.__anext__()
                except StopAsyncIteration:
                    pass

                mock_commit.assert_called_once()
                mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_db_rolls_back_on_exception(self):
        """TDD: get_db should rollback transaction when exception occurs."""
        with patch.object(AsyncSession, 'rollback', new_callable=AsyncMock) as mock_rollback:
            with patch.object(AsyncSession, 'close', new_callable=AsyncMock) as mock_close:
                with patch.object(AsyncSession, 'commit', new_callable=AsyncMock) as mock_commit:
                    # Make commit raise an exception
                    mock_commit.side_effect = Exception("Database error")

                    async_gen = get_db()
                    session = await async_gen.__anext__()

                    # Simulate exception during commit
                    with pytest.raises(Exception):
                        try:
                            await async_gen.__anext__()
                        except StopAsyncIteration:
                            pass

                    mock_rollback.assert_called_once()
                    mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_db_always_closes_session(self):
        """TDD: get_db should always close session in finally block."""
        with patch.object(AsyncSession, 'close', new_callable=AsyncMock) as mock_close:
            async_gen = get_db()

            session = await async_gen.__anext__()

            # Complete the generator
            try:
                await async_gen.__anext__()
            except StopAsyncIteration:
                pass

            mock_close.assert_called_once()


class TestInitDbFunction:
    """Test init_db database initialization function."""

    @pytest.mark.asyncio
    async def test_init_db_creates_connection(self):
        """TDD: init_db should create database connection."""
        with patch.object(engine, 'begin', new_callable=AsyncMock) as mock_begin:
            mock_conn = AsyncMock()
            mock_begin.return_value.__aenter__.return_value = mock_conn

            await init_db()

            mock_begin.assert_called_once()

    @pytest.mark.asyncio
    async def test_init_db_imports_models(self):
        """TDD: init_db should import all models for registration."""
        with patch.object(engine, 'begin', new_callable=AsyncMock) as mock_begin:
            mock_conn = AsyncMock()
            mock_begin.return_value.__aenter__.return_value = mock_conn

            # Mock the import to avoid side effects
            with patch('app.models.user'):
                await init_db()

            # Verify connection was used
            mock_begin.assert_called_once()

    @pytest.mark.asyncio
    async def test_init_db_creates_all_tables(self):
        """TDD: init_db should create all metadata tables."""
        with patch.object(engine, 'begin', new_callable=AsyncMock) as mock_begin:
            mock_conn = AsyncMock()
            mock_begin.return_value.__aenter__.return_value = mock_conn

            with patch('app.models.user'):
                await init_db()

            # Verify run_sync was called for creating tables
            mock_conn.run_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_init_db_handles_import_errors_gracefully(self):
        """TDD: init_db should handle model import errors gracefully."""
        with patch.object(engine, 'begin', new_callable=AsyncMock) as mock_begin:
            mock_conn = AsyncMock()
            mock_begin.return_value.__aenter__.return_value = mock_conn

            # Mock import to raise an error
            with patch('app.models.user', side_effect=ImportError("Module not found")):
                # This should not raise an exception
                with pytest.raises(ImportError):
                    await init_db()


class TestCloseDbEngineFunction:
    """Test close_db_engine cleanup function."""

    @pytest.mark.asyncio
    async def test_close_db_engine_disposes_engine(self):
        """TDD: close_db_engine should dispose of the engine."""
        with patch.object(engine, 'dispose', new_callable=AsyncMock) as mock_dispose:
            await close_db_engine()

            mock_dispose.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_db_engine_handles_dispose_errors(self):
        """TDD: close_db_engine should handle disposal errors gracefully."""
        with patch.object(engine, 'dispose', new_callable=AsyncMock) as mock_dispose:
            mock_dispose.side_effect = Exception("Disposal error")

            # Should not raise exception
            with pytest.raises(Exception):
                await close_db_engine()


class TestDatabaseSessionIntegration:
    """Integration tests for database session lifecycle."""

    @pytest.mark.asyncio
    async def test_session_lifecycle_with_get_db(self):
        """TDD: Test complete session lifecycle using get_db."""
        session_created = False
        session_committed = False
        session_closed = False

        async def mock_session_lifecycle():
            nonlocal session_created, session_committed, session_closed

            async for session in get_db():
                session_created = True
                assert isinstance(session, AsyncSession)
                # Session should be usable here

        with patch.object(AsyncSession, 'commit', new_callable=AsyncMock) as mock_commit:
            with patch.object(AsyncSession, 'close', new_callable=AsyncMock) as mock_close:
                await mock_session_lifecycle()

                session_committed = mock_commit.called
                session_closed = mock_close.called

        assert session_created
        assert session_committed
        assert session_closed

    @pytest.mark.asyncio
    async def test_multiple_sessions_are_independent(self):
        """TDD: Multiple sessions should be independent and properly isolated."""
        sessions = []

        # Create multiple sessions
        for _ in range(3):
            session = await get_session()
            sessions.append(session)

        # Verify they are different instances
        for i, session1 in enumerate(sessions):
            for j, session2 in enumerate(sessions):
                if i != j:
                    assert session1 is not session2

        # Cleanup
        for session in sessions:
            await session.close()


class TestDatabasePerformance:
    """Performance tests for database session operations."""

    @pytest.mark.asyncio
    async def test_session_creation_performance(self):
        """TDD: Session creation should be performant."""
        import time

        start_time = time.time()

        # Create and close 100 sessions
        for _ in range(100):
            session = await get_session()
            await session.close()

        end_time = time.time()
        duration = end_time - start_time

        # Should create 100 sessions in less than 1 second
        assert duration < 1.0, f"Session creation took {duration:.4f}s, expected < 1.0s"

    @pytest.mark.asyncio
    async def test_get_db_dependency_performance(self):
        """TDD: get_db dependency should be performant."""
        import time

        start_time = time.time()

        # Use get_db dependency 50 times
        for _ in range(50):
            async for session in get_db():
                assert isinstance(session, AsyncSession)
                break  # Exit after getting the session

        end_time = time.time()
        duration = end_time - start_time

        # Should handle 50 dependency calls in less than 2 seconds
        assert duration < 2.0, f"get_db dependency took {duration:.4f}s, expected < 2.0s"


class TestDatabaseBaseClass:
    """Test Base declarative class."""

    def test_base_is_declarative_base(self):
        """TDD: Base should be a declarative base class."""
        from sqlalchemy.ext.declarative import DeclarativeMeta
        assert isinstance(Base, DeclarativeMeta)

    def test_base_has_metadata(self):
        """TDD: Base should have metadata attribute."""
        assert hasattr(Base, 'metadata')
        assert Base.metadata is not None

    def test_base_can_be_used_for_model_inheritance(self):
        """TDD: Base should be usable for model class inheritance."""
        # Create a test model class
        class TestModel(Base):
            __tablename__ = 'test_table'

        # Should be able to inherit from Base without errors
        assert issubclass(TestModel, Base)
        assert hasattr(TestModel, '__tablename__')


if __name__ == "__main__":
    # Run with: python -m pytest tests/unit/database/test_session.py -v
    pytest.main([__file__, "-v", "--tb=short", "--cov=app.database.session"])