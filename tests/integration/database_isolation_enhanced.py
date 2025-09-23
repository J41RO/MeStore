#!/usr/bin/env python3
"""
Enhanced Database Isolation for Integration Tests
================================================

This module provides enhanced database session management for integration tests
to prevent ResourceClosedError and ensure proper transaction isolation.

Key Features:
1. Proper async session lifecycle management
2. Transaction rollback isolation between tests
3. Prevention of ResourceClosedError during cleanup
4. FastAPI dependency override management
5. Session state monitoring and recovery

Issues Fixed:
- ResourceClosedError during test teardown
- Session sharing between test fixtures and FastAPI endpoints
- Transaction isolation between test cases
- Proper async session cleanup

Author: Integration Testing Specialist
Date: 2025-09-23
"""

import asyncio
import contextlib
from typing import AsyncGenerator, Optional
import logging

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy import event
# from sqlalchemy.engine.events import PoolEvents  # Not needed for this implementation

from app.database import Base, get_async_db
from app.main import app

# Configure logging for database operations
logger = logging.getLogger(__name__)


class EnhancedAsyncSessionManager:
    """
    Enhanced async session manager for integration tests.

    Provides proper session lifecycle management and transaction isolation
    to prevent ResourceClosedError and ensure clean test isolation.
    """

    def __init__(self):
        self._engine = None
        self._session_factory = None
        self._active_sessions = set()
        self._dependency_overrides = {}

    async def initialize(self):
        """Initialize the async engine and session factory."""
        if self._engine is None:
            # Create async engine with proper configuration
            self._engine = create_async_engine(
                "sqlite+aiosqlite:///:memory:",
                echo=False,
                poolclass=StaticPool,
                pool_pre_ping=True,
                pool_recycle=300,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30,
                }
            )

            # Create session factory
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False
            )

            # Create all tables
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            logger.info("Enhanced async session manager initialized")

    async def create_session(self) -> AsyncSession:
        """
        Create a new async session with proper tracking.

        Returns:
            AsyncSession: New session instance with transaction isolation
        """
        if self._session_factory is None:
            await self.initialize()

        session = self._session_factory()
        self._active_sessions.add(session)

        logger.debug(f"Created session {id(session)}, active sessions: {len(self._active_sessions)}")
        return session

    async def close_session(self, session: AsyncSession):
        """
        Properly close a session with error handling.

        Args:
            session: Session to close
        """
        try:
            if session in self._active_sessions:
                # Check if session is still active
                if hasattr(session, 'is_active') and session.is_active:
                    # Rollback any pending transaction
                    if session.in_transaction():
                        await session.rollback()

                # Close the session
                await session.close()
                self._active_sessions.discard(session)

                logger.debug(f"Closed session {id(session)}, remaining: {len(self._active_sessions)}")
        except Exception as e:
            logger.error(f"Error closing session {id(session)}: {e}")
            # Force remove from tracking even if close failed
            self._active_sessions.discard(session)

    async def cleanup_all_sessions(self):
        """Close all tracked sessions to prevent ResourceClosedError."""
        sessions_to_close = list(self._active_sessions)
        for session in sessions_to_close:
            await self.close_session(session)

        logger.info(f"Cleaned up {len(sessions_to_close)} sessions")

    def setup_dependency_override(self, session: AsyncSession):
        """
        Setup FastAPI dependency override for the given session.

        Args:
            session: Session to use for dependency injection
        """
        async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
            """Test database dependency that yields the test session."""
            try:
                yield session
            except Exception as e:
                logger.error(f"Error in test database dependency: {e}")
                raise

        # Override both sync and async database dependencies
        self._dependency_overrides[get_async_db] = get_test_db
        app.dependency_overrides.update(self._dependency_overrides)

        logger.debug(f"Setup dependency override for session {id(session)}")

    def clear_dependency_overrides(self):
        """Clear all FastAPI dependency overrides."""
        app.dependency_overrides.clear()
        self._dependency_overrides.clear()
        logger.debug("Cleared all dependency overrides")

    async def shutdown(self):
        """Shutdown the session manager and cleanup resources."""
        # Close all active sessions
        await self.cleanup_all_sessions()

        # Clear dependency overrides
        self.clear_dependency_overrides()

        # Dispose of the engine
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

        logger.info("Enhanced async session manager shutdown complete")


# Global session manager instance
session_manager = EnhancedAsyncSessionManager()


@pytest.fixture(scope="function")
async def enhanced_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Enhanced async session fixture with proper isolation and cleanup.

    This fixture provides:
    - Proper transaction isolation between tests
    - Prevention of ResourceClosedError
    - Session state monitoring
    - Automatic cleanup on test completion

    Yields:
        AsyncSession: Isolated session for the test
    """
    # Initialize session manager if needed
    await session_manager.initialize()

    # Create new session for this test
    session = await session_manager.create_session()

    try:
        # Begin transaction for isolation
        await session.begin()

        # Setup dependency override
        session_manager.setup_dependency_override(session)

        logger.info(f"Enhanced session {id(session)} created for test")
        yield session

    except Exception as e:
        logger.error(f"Error in enhanced session {id(session)}: {e}")
        # Rollback on error
        if session.in_transaction():
            await session.rollback()
        raise

    finally:
        try:
            # Rollback transaction to clean up test data
            if session.in_transaction():
                await session.rollback()

            # Clear dependency overrides
            session_manager.clear_dependency_overrides()

            # Close session
            await session_manager.close_session(session)

            logger.info(f"Enhanced session {id(session)} cleanup complete")

        except Exception as cleanup_error:
            logger.error(f"Error during session cleanup: {cleanup_error}")


@pytest.fixture(scope="session", autouse=True)
async def session_manager_lifecycle():
    """
    Session-scoped fixture to manage the session manager lifecycle.

    This fixture:
    - Initializes the session manager at the start of the test session
    - Ensures proper cleanup at the end of the test session
    - Prevents resource leaks and ResourceClosedError
    """
    # Setup
    await session_manager.initialize()
    logger.info("Session manager lifecycle started")

    yield

    # Teardown
    await session_manager.shutdown()
    logger.info("Session manager lifecycle ended")


@contextlib.asynccontextmanager
async def isolated_transaction(session: AsyncSession):
    """
    Context manager for isolated transactions within tests.

    Args:
        session: Session to create transaction in

    Yields:
        AsyncSession: Session with active transaction
    """
    savepoint = await session.begin_nested()
    try:
        yield session
        await savepoint.commit()
    except Exception:
        await savepoint.rollback()
        raise


async def ensure_session_health(session: AsyncSession) -> bool:
    """
    Check if a session is healthy and can be used.

    Args:
        session: Session to check

    Returns:
        bool: True if session is healthy, False otherwise
    """
    try:
        # Check if session is active
        if not hasattr(session, 'is_active') or not session.is_active:
            return False

        # Try a simple query to verify connection
        await session.execute("SELECT 1")
        return True

    except Exception as e:
        logger.warning(f"Session health check failed: {e}")
        return False


async def recover_session(session: AsyncSession) -> Optional[AsyncSession]:
    """
    Attempt to recover a failed session.

    Args:
        session: Failed session to recover

    Returns:
        Optional[AsyncSession]: New session if recovery successful, None otherwise
    """
    try:
        # Close the failed session
        await session_manager.close_session(session)

        # Create a new session
        new_session = await session_manager.create_session()

        logger.info(f"Session recovered: {id(session)} -> {id(new_session)}")
        return new_session

    except Exception as e:
        logger.error(f"Session recovery failed: {e}")
        return None


# Event listeners for debugging session issues - simplified for compatibility
# Note: Some events may not be available for AsyncSession, using basic logging instead