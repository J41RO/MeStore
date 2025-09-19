#!/usr/bin/env python3
"""
Standalone Unit Tests for Database Session Module
================================================

Testing Strategy:
- Isolated tests without full conftest dependencies
- Focus on core database session functionality
- Mock external dependencies to avoid import issues

Coverage Goals:
- Database engine configuration: 100%
- Session factory creation: 100%
- Basic functionality validation: 100%

File: tests/unit/database/test_session_standalone.py
Author: Unit Testing AI - TDD Methodology
Date: 2025-09-17
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine


def test_database_session_imports():
    """Test that database session module imports correctly."""
    from app.database.session import engine, AsyncSessionLocal, get_session, get_db, init_db, close_db_engine, Base

    # Verify all imports are successful
    assert engine is not None
    assert AsyncSessionLocal is not None
    assert get_session is not None
    assert get_db is not None
    assert init_db is not None
    assert close_db_engine is not None
    assert Base is not None


def test_engine_is_async_engine():
    """Test that engine is an AsyncEngine instance."""
    from app.database.session import engine

    assert isinstance(engine, AsyncEngine)


def test_session_factory_is_callable():
    """Test that AsyncSessionLocal is callable."""
    from app.database.session import AsyncSessionLocal

    assert callable(AsyncSessionLocal)


def test_session_factory_creates_async_session():
    """Test that AsyncSessionLocal creates AsyncSession instances."""
    from app.database.session import AsyncSessionLocal

    session = AsyncSessionLocal()
    assert isinstance(session, AsyncSession)


@pytest.mark.asyncio
async def test_get_session_returns_async_session():
    """Test that get_session returns AsyncSession instance."""
    from app.database.session import get_session

    session = await get_session()
    assert isinstance(session, AsyncSession)
    await session.close()


@pytest.mark.asyncio
async def test_get_session_creates_different_sessions():
    """Test that get_session creates different session instances."""
    from app.database.session import get_session

    session1 = await get_session()
    session2 = await get_session()

    assert session1 is not session2

    await session1.close()
    await session2.close()


def test_base_is_declarative_base():
    """Test that Base is a declarative base class."""
    from app.database.session import Base
    from sqlalchemy.ext.declarative import DeclarativeMeta

    assert isinstance(Base, DeclarativeMeta)
    assert hasattr(Base, 'metadata')


@pytest.mark.asyncio
async def test_close_db_engine_calls_dispose():
    """Test that close_db_engine calls engine.dispose()."""
    from app.database.session import close_db_engine, engine

    with patch.object(engine, 'dispose', new_callable=AsyncMock) as mock_dispose:
        await close_db_engine()
        mock_dispose.assert_called_once()


@pytest.mark.asyncio
async def test_get_db_yields_session():
    """Test that get_db yields an AsyncSession."""
    from app.database.session import get_db

    with patch('app.database.session.AsyncSessionLocal') as mock_session_factory:
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        mock_session_factory.return_value.__aexit__.return_value = None

        async_gen = get_db()
        session = await async_gen.__anext__()

        assert session is mock_session


@pytest.mark.asyncio
async def test_init_db_creates_tables():
    """Test that init_db calls metadata.create_all."""
    from app.database.session import init_db, engine

    with patch.object(engine, 'begin', new_callable=AsyncMock) as mock_begin:
        mock_conn = AsyncMock()
        mock_begin.return_value.__aenter__.return_value = mock_conn

        with patch('app.models.user'):  # Mock the model import
            await init_db()

        mock_begin.assert_called_once()
        mock_conn.run_sync.assert_called_once()


def test_engine_configuration():
    """Test that engine has expected configuration."""
    from app.database.session import engine

    # Test that engine has the expected attributes
    assert hasattr(engine, 'pool')
    assert hasattr(engine, 'url')
    assert engine.pool_size == 10  # From our configuration


def test_session_factory_configuration():
    """Test that session factory has correct configuration."""
    from app.database.session import AsyncSessionLocal, engine

    session = AsyncSessionLocal()
    try:
        # Test session configuration
        assert session.bind == engine
        assert not session.autocommit
        assert session.autoflush
        assert not session.expire_on_commit
    finally:
        import asyncio
        asyncio.create_task(session.close())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])