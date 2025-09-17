"""
Database Configuration - SQLAlchemy Async

Configuración optimizada para:
- Conexiones asíncronas de alta performance con asyncpg
- Pool de conexiones configurado para desarrollo
- Sesiones con expire_on_commit=False para async
- Support para migrations automáticas
"""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Base para modelos
Base = declarative_base()

# Convertir DATABASE_URL para usar asyncpg si está usando psycopg2
def get_async_database_url() -> str:
    """
    Convierte la DATABASE_URL para usar el driver async apropriado
    
    Returns:
        str: URL de base de datos con driver async
    """
    database_url = settings.DATABASE_URL
    
    # Si la URL usa postgresql:// (psycopg2), convertir a postgresql+asyncpg://
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    elif database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://")
    
    return database_url


# Configuración de engine dependiendo del tipo de base de datos
def get_engine_config() -> dict:
    """
    Retorna la configuración apropiada para el engine según el tipo de base de datos

    Returns:
        dict: Configuración del engine
    """
    database_url = get_async_database_url()
    base_config = {
        "echo": settings.DB_ECHO,
        "future": True,
    }

    # Configuración específica para SQLite
    if "sqlite" in database_url:
        return {
            **base_config,
            "poolclass": NullPool,  # SQLite no soporta connection pooling
        }

    # Configuración específica para PostgreSQL
    else:
        return {
            **base_config,
            "pool_pre_ping": True,  # Verificar conexiones antes de usar
            "pool_recycle": 300,  # Reciclar conexiones cada 5 minutos
            "max_overflow": 20,  # Conexiones adicionales permitidas
            "pool_size": 10,  # Tamaño base del pool
            "poolclass": (
                NullPool if "pytest" in os.environ.get("PYTEST_CURRENT_TEST", "") else None
            ),
        }


# Motor async optimizado con configuración dinámica
engine = create_async_engine(
    get_async_database_url(),
    **get_engine_config()
)

# Session factory async
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Importante para async
    autoflush=True,
    autocommit=False,
)


# Dependency para FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para obtener sesión de base de datos async

    Yields:
        AsyncSession: Sesión de base de datos async
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Función para inicializar base de datos
async def init_db() -> None:
    """Inicializar base de datos creando todas las tablas"""
    async with engine.begin() as conn:
        # Importar todos los modelos aquí para que sean registrados
        from app.models import user  # noqa: F401

        # Crear todas las tablas
        await conn.run_sync(Base.metadata.create_all)


# Función para cerrar conexiones
async def close_db() -> None:
    """Cerrar todas las conexiones de base de datos"""
    await engine.dispose()


async def get_session() -> AsyncSession:
    """Obtener sesión async de base de datos"""
    async with AsyncSessionLocal() as session:
        try:
            return session
        finally:
            await session.close()