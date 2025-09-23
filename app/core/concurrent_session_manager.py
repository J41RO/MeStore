"""
GREEN PHASE: Minimal concurrent session management for admin endpoints

This module provides the minimal concurrent session management functionality
required to make the test_concurrent_admin_session_management test pass.

TDD GREEN PHASE: Just enough code to make the test pass.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db


class ConcurrentSessionManager:
    """Minimal concurrent session manager for GREEN phase"""

    def __init__(self):
        self.active_sessions: Dict[str, AsyncSession] = {}
        self.session_locks: Dict[str, asyncio.Lock] = {}

    @asynccontextmanager
    async def get_concurrent_session(self, session_id: str = None) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a concurrent-safe database session

        Args:
            session_id: Optional session identifier, uses task ID if not provided

        Yields:
            AsyncSession: Isolated database session for concurrent use
        """
        if session_id is None:
            # Use current task as session identifier for automatic isolation
            current_task = asyncio.current_task()
            session_id = f"task_{id(current_task)}" if current_task else "default"

        # Ensure each session_id gets its own lock
        if session_id not in self.session_locks:
            self.session_locks[session_id] = asyncio.Lock()

        async with self.session_locks[session_id]:
            # Create a new session for each concurrent request
            async for db_session in get_async_db():
                try:
                    yield db_session
                finally:
                    await db_session.close()
                    # Clean up completed sessions
                    if session_id in self.active_sessions:
                        del self.active_sessions[session_id]
                break

    async def cleanup_sessions(self):
        """Clean up all active sessions"""
        for session in self.active_sessions.values():
            try:
                await session.close()
            except Exception:
                pass  # Ignore cleanup errors in GREEN phase
        self.active_sessions.clear()


# Global concurrent session manager
concurrent_session_manager = ConcurrentSessionManager()


async def get_concurrent_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get a concurrent-safe database session

    This replaces the regular get_db dependency for admin endpoints
    that need to handle concurrent requests safely.
    """
    # For GREEN phase, just use the regular database dependency
    # The concurrent management is handled by the session manager context
    from app.database import get_async_db
    async for session in get_async_db():
        yield session