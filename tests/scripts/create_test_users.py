#!/usr/bin/env python3
"""
Script para crear usuarios de prueba en MeStore
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User

async def create_test_users():
    """Create test users for development"""

    # Create async engine
    if settings.DATABASE_URL.startswith("sqlite"):
        # For SQLite, use aiosqlite
        database_url = settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
    else:
        # For PostgreSQL, use asyncpg
        database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

    engine = create_async_engine(database_url, echo=True)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        try:
            # Check if users already exist
            existing_admin = await session.get(User, 1)
            if existing_admin:
                print(f"✅ Admin user already exists: {existing_admin.email}")
            else:
                # Create admin user
                admin_user = User(
                    email="admin@test.com",
                    hashed_password=get_password_hash("admin123"),
                    first_name="Admin",
                    last_name="Test",
                    user_type="ADMIN",
                    is_active=True,
                    is_verified=True
                )
                session.add(admin_user)
                print("✅ Created admin user: admin@test.com / admin123")

            # Create vendor user
            vendor_user = User(
                email="vendor@test.com",
                hashed_password=get_password_hash("vendor123"),
                first_name="Vendor",
                last_name="Test",
                user_type="VENDEDOR",
                is_active=True,
                is_verified=True
            )
            session.add(vendor_user)
            print("✅ Created vendor user: vendor@test.com / vendor123")

            # Create buyer user
            buyer_user = User(
                email="buyer@test.com",
                hashed_password=get_password_hash("buyer123"),
                first_name="Buyer",
                last_name="Test",
                user_type="COMPRADOR",
                is_active=True,
                is_verified=True
            )
            session.add(buyer_user)
            print("✅ Created buyer user: buyer@test.com / buyer123")

            await session.commit()
            print("\n🎉 All test users created successfully!")

        except Exception as e:
            print(f"❌ Error creating users: {e}")
            await session.rollback()
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_test_users())