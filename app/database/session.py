"""
Database session configuration for MeStore.

This module provides the central database engine and session factory
for all database operations in the application.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import QueuePool

from app.core.config import settings


# Create async engine with optimized connection pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    # Connection pooling configuration
    pool_size=10,                # Minimum number of connections in pool
    max_overflow=20,             # Maximum additional connections beyond pool_size
    pool_timeout=30,             # Seconds to wait for connection from pool
    pool_recycle=1800,           # Seconds before connection is recreated (30 min)
    pool_pre_ping=True,          # Validate connections before use
    # poolclass defaults to AsyncAdaptedQueuePool for async engines
    # Logging configuration
    echo=settings.DB_ECHO,       # Log SQL statements if enabled
    echo_pool=False,             # Set to True for pool debugging
    # Additional async configuration
    future=True,                 # Use SQLAlchemy 2.0+ features
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,      # Keep objects accessible after commit
    autocommit=False,            # Explicit transaction control
    autoflush=True,              # Auto-flush before queries
)


async def get_session() -> AsyncSession:
    """
    Create a new database session.

    This function creates a new async session that should be used
    within an async context manager or properly closed after use.

    Returns:
        AsyncSession: New database session

    Example:
        async with get_session() as session:
            result = await session.execute(select(User))
    """
    return AsyncSessionLocal()


async def close_db_engine() -> None:
    """
    Close the database engine and all connections.

    This should be called during application shutdown to properly
    close all database connections and clean up resources.
    """
    await engine.dispose()