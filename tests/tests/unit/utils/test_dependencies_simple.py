from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.models.base import Base

# Engine sync para testing
test_engine = create_engine(
    settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"),
    echo=False,
    pool_pre_ping=True,
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def get_test_db():
    db = TestSessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

def create_test_tables():
    # Drop existing tables first to ensure clean state
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
