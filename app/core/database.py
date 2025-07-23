"""
Database Configuration - SQLAlchemy Async

Configuración optimizada para:
- Conexiones asíncronas de alta performance
- Pool de conexiones configurado para desarrollo
- Sesiones con expire_on_commit=False para async
- Support para migrations automáticas
"""

# Unified configuration through settings
from typing import AsyncGenerator
from app.core.config import settings
import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool

# Base para modelos
Base = declarative_base()

# Use unified configuration from settings

# Motor async optimizado para desarrollo
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,  # Configurado desde settings
    future=True,
    pool_pre_ping=True,  # Verificar conexiones antes de usar
    pool_recycle=300,  # Reciclar conexiones cada 5 minutos
    max_overflow=20,  # Conexiones adicionales permitidas
    pool_size=10,  # Tamaño base del pool
    poolclass=(
        NullPool if "pytest" in os.environ.get("PYTEST_CURRENT_TEST", "") else None
    ),
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
            await session.commit()
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
            yield session
        finally:
            await session.close()