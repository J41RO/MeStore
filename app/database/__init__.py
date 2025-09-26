

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import os

# Database URL from environment - SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mestore_production.db")
# SQLite doesn't support async, so we use synchronous for both
ASYNC_DATABASE_URL = DATABASE_URL

# Create engines - SQLite doesn't support async properly
engine = create_engine(DATABASE_URL)
# For SQLite, we use the same synchronous engine
async_engine = None

# Session makers - SQLite compatible
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# For SQLite, use synchronous sessions
AsyncSessionLocal = SessionLocal

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
    # For SQLite, use synchronous session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_sync_db():
    """Synchronous database session dependency for admin endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()