import os
from typing import Tuple

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


def _resolve_database_urls() -> Tuple[str, str]:
    """
    Obtener URLs de base de datos sync/async consistentes según la configuración.

    Retorna:
        tuple[str, str]: (sync_database_url, async_database_url)
    """
    # Priorizar DATABASE_URL como fuente de verdad
    raw_database_url = os.getenv("DATABASE_URL")
    raw_async_url = os.getenv("ASYNC_DATABASE_URL")

    default_async = "sqlite+aiosqlite:///./mestore.db"
    default_sync = "sqlite:///./mestore.db"

    if raw_database_url:
        db_url = raw_database_url
    elif raw_async_url:
        db_url = raw_async_url
    else:
        return default_sync, default_async

    if db_url.startswith("sqlite+aiosqlite://"):
        sync_url = db_url.replace("sqlite+aiosqlite://", "sqlite:///")
        async_url = db_url
    elif db_url.startswith("sqlite://"):
        sync_url = db_url
        async_url = db_url.replace("sqlite://", "sqlite+aiosqlite://")
    elif db_url.startswith("postgresql+asyncpg://"):
        sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        async_url = db_url
    elif db_url.startswith("postgresql://"):
        sync_url = db_url
        async_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    else:
        sync_url = db_url
        async_url = raw_async_url or db_url

    # Permitir override explícito de ASYNC_DATABASE_URL
    if raw_async_url:
        async_url = raw_async_url

    return sync_url, async_url


# Database URL from environment - SQLite for development, PostgreSQL for production
DATABASE_URL, ASYNC_DATABASE_URL = _resolve_database_urls()

# Create sync engine
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    engine_kwargs["poolclass"] = StaticPool
engine = create_engine(DATABASE_URL, **engine_kwargs)

# Create async engine
async_engine_kwargs = {"echo": False}
if ASYNC_DATABASE_URL.startswith("sqlite+aiosqlite"):
    async_engine_kwargs["connect_args"] = {"check_same_thread": False}
    async_engine_kwargs["poolclass"] = StaticPool
async_engine = create_async_engine(ASYNC_DATABASE_URL, **async_engine_kwargs)

# Sync session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async session maker
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base for models
Base = declarative_base()


def _reconfigure_in_memory_sqlite() -> None:
    """Fallback to in-memory SQLite when file-based database is unavailable."""
    global engine, async_engine, SessionLocal, AsyncSessionLocal, DATABASE_URL, ASYNC_DATABASE_URL

    DATABASE_URL = "sqlite:///:memory:"
    ASYNC_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async_engine = create_async_engine(
        ASYNC_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Ensure schema exists for fallback database
    Base.metadata.create_all(bind=engine)


# Sync database dependency
def get_db():
    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
        except OperationalError as exc:
            if "unable to open database file" in str(exc).lower():
                _reconfigure_in_memory_sqlite()
                db = SessionLocal()
                db.execute(text("SELECT 1"))
            else:
                raise
    except OperationalError as exc:
        if "unable to open database file" in str(exc).lower():
            _reconfigure_in_memory_sqlite()
            db = SessionLocal()
            db.execute(text("SELECT 1"))
        else:
            raise
    try:
        yield db
    finally:
        db.close()


# Async database dependency
async def get_async_db():
    try:
        async with AsyncSessionLocal() as db:
            try:
                await db.execute(text("SELECT 1"))
            except OperationalError as exc:
                if "unable to open database file" in str(exc).lower():
                    _reconfigure_in_memory_sqlite()
                    async with AsyncSessionLocal() as retry_db:
                        await retry_db.execute(text("SELECT 1"))
                        try:
                            yield retry_db
                        finally:
                            await retry_db.close()
                    return
                raise
            try:
                yield db
            finally:
                await db.close()
    except OperationalError as exc:
        if "unable to open database file" not in str(exc).lower():
            raise
        _reconfigure_in_memory_sqlite()
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
            try:
                yield db
            finally:
                await db.close()

# Sync database dependency (alias for admin endpoints)
def get_sync_db():
    """Synchronous database session dependency for admin endpoints."""
    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
        except OperationalError as exc:
            if "unable to open database file" in str(exc).lower():
                _reconfigure_in_memory_sqlite()
                db = SessionLocal()
                db.execute(text("SELECT 1"))
            else:
                raise
    except OperationalError as exc:
        if "unable to open database file" in str(exc).lower():
            _reconfigure_in_memory_sqlite()
            db = SessionLocal()
            db.execute(text("SELECT 1"))
        else:
            raise
    try:
        yield db
    finally:
        db.close()
