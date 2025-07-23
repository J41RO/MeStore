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
from sqlalchemy.pool import QueuePool, NullPool
import os
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

# Base para modelos
Base = declarative_base()


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

# FastAPI Dependency
async def get_db():
    """
    FastAPI dependency para obtener sesión de base de datos async.
    
    Yields:
        AsyncSession: Sesión de base de datos async
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Inicializar base de datos creando todas las tablas."""
    async with engine.begin() as conn:
        # Importar todos los modelos aquí para que sean registrados
        from app.models import user  # noqa: F401
        
        # Crear todas las tablas
        await conn.run_sync(Base.metadata.create_all)


async def close_db_engine() -> None:
    """
    Close the database engine and all connections.

    This should be called during application shutdown to properly
    close all database connections and clean up resources.
    """
    await engine.dispose()