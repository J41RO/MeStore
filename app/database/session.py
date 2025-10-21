"""
Database session configuration for MeStore.

This module provides the central database engine and session factory
for all database operations in the application.
"""

import os
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool, StaticPool

from app.core.config import settings

# Base declarativa para todos los modelos
Base = declarative_base()

# URL de conexión de la base de datos
database_url = settings.DATABASE_URL

# Argumentos comunes del motor
engine_kwargs = {
    "echo": settings.DB_ECHO,
    "echo_pool": False,
    "future": True,
    "pool_pre_ping": True,
}

# Determinar tipo de backend (SQLite, PostgreSQL, etc.)
try:
    url_obj = make_url(database_url)
except Exception:  # pragma: no cover - fallback para URLs no estándar
    url_obj = URL.create(database_url.split(":")[0])

# Configuración específica según backend
if url_obj.drivername.startswith("sqlite"):
    # ⚙️ Ajuste especial para SQLite (ideal para testing)
    # Evita bloqueos concurrentes y errores "database is locked"
    engine_kwargs.update(
        {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
            "pool_pre_ping": False,
        }
    )
else:
    # Configuración estándar para backends como PostgreSQL o MySQL
    engine_kwargs.update(
        {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_timeout": 30,
            "pool_recycle": 1800,
        }
    )

# 🚀 Crear motor asíncrono con configuración adaptada
engine = create_async_engine(database_url, **engine_kwargs)

# 🧩 Crear fábrica de sesiones asíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Mantiene los objetos accesibles tras commit
    autocommit=False,
    autoflush=True,
)

# ===========================================================
# 🧠 Dependencias y funciones utilitarias
# ===========================================================

async def get_session() -> AsyncSession:
    """
    Create a new async session (manual management).
    Example:
        async with get_session() as session:
            result = await session.execute(select(User))
    """
    return AsyncSessionLocal()


# FastAPI Dependency
async def get_db():
    """
    FastAPI dependency para obtener sesión de base de datos async.
    Gestiona automáticamente commit, rollback y cierre.
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


# Inicialización del esquema
async def init_db() -> None:
    """
    Inicializar la base de datos creando todas las tablas registradas.
    """
    async with engine.begin() as conn:
        from app.models import user  # Importar modelos para registro
        await conn.run_sync(Base.metadata.create_all)


# Cierre ordenado del motor
async def close_db_engine() -> None:
    """
    Close the database engine and all connections.
    """
    await engine.dispose()
