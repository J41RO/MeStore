"""
Database dependency injection for FastAPI endpoints.

This module provides standardized database session dependencies
for all API endpoints, consolidating session management in a single location.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Standard database dependency for FastAPI endpoints.

    This is the primary dependency that should be used in all endpoints
    requiring database access. It provides proper session management
    with automatic commit/rollback handling.

    Yields:
        AsyncSession: Database session with transaction management

    Example:
        @router.get("/users/")
        async def get_users(db: AsyncSession = Depends(get_db)):
            # Use db session here
            pass
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Alias for get_db() for backwards compatibility.

    Note: Prefer using get_db() directly for new code.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Export the main dependency for easy import
__all__ = ["get_db", "get_db_session"]