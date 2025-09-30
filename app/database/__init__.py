

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os

# Database URL from environment - SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mestore.db")
# Convert SQLite URL to async format for aiosqlite
ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")

# Create engines
engine = create_engine(DATABASE_URL)
# Create async engine for SQLite using aiosqlite
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)

# Session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Async session maker for SQLite
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    # Use proper async session
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

def get_sync_db():
    """Synchronous database session dependency for admin endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()