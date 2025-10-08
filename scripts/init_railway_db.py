#!/usr/bin/env python3
"""
Railway Database Initialization Script (Simple)
================================================

Simple script to create all database tables using SQLAlchemy metadata.
Works with both local testing and Railway PostgreSQL.

Usage:
    DATABASE_URL="postgresql://..." python scripts/init_railway_db.py

Environment Variables Required:
    DATABASE_URL - Database connection string (PostgreSQL for Railway)

Author: Claude Code
Date: 2025-10-07
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Initialize database by creating all tables."""

    print("=" * 70)
    print("RAILWAY DATABASE INITIALIZATION")
    print("=" * 70)
    print()

    # Step 1: Check DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print()
        print("Usage:")
        print('  DATABASE_URL="postgresql://..." python scripts/init_railway_db.py')
        print()
        sys.exit(1)

    print(f"✅ DATABASE_URL: {database_url[:50]}...")
    print()

    # Step 2: Import Base and all models
    print("📦 Importing models...")
    try:
        from app.models.base import BaseModel

        # Import all models to register them with Base.metadata
        import app.models  # This auto-imports all models via __init__.py

        # Explicitly import key models to ensure they're loaded
        from app.models.user import User
        from app.models.product import Product
        from app.models.order import Order
        from app.models.category import Category
        from app.models.inventory import Inventory
        from app.models.storage import Storage
        from app.models.transaction import Transaction

        print(f"✅ Loaded {len(BaseModel.metadata.tables)} table definitions")
        print()

        # Show tables that will be created
        print("📋 Tables to create:")
        for table_name in sorted(BaseModel.metadata.tables.keys()):
            print(f"   - {table_name}")
        print()

    except Exception as e:
        print(f"❌ ERROR importing models: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Step 3: Create database engine
    print("🔌 Connecting to database...")
    try:
        from sqlalchemy import create_engine

        # Convert async URL to sync if needed
        sync_database_url = database_url
        if "asyncpg" in sync_database_url:
            sync_database_url = sync_database_url.replace("+asyncpg", "")
        if "aiosqlite" in sync_database_url:
            sync_database_url = sync_database_url.replace("+aiosqlite", "")

        # Create engine with explicit settings
        engine = create_engine(
            sync_database_url,
            echo=False,  # Set to True for SQL debugging
            pool_pre_ping=True,  # Verify connections before using
        )

        print("✅ Database engine created")
        print()

    except Exception as e:
        print(f"❌ ERROR creating database engine: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Step 4: Test connection
    print("🔍 Testing database connection...")
    try:
        from sqlalchemy import text

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()

        print("✅ Database connection successful")
        print()

    except Exception as e:
        print(f"❌ ERROR connecting to database: {str(e)}")
        print()
        print("Common issues:")
        print("  - Check DATABASE_URL is correct")
        print("  - Verify database server is running")
        print("  - Check network connectivity")
        print("  - Verify credentials are correct")
        print()
        sys.exit(1)

    # Step 5: Create all tables
    print("🏗️  Creating database tables...")
    try:
        # Create all tables from metadata
        BaseModel.metadata.create_all(bind=engine)

        print("✅ All tables created successfully")
        print()

    except Exception as e:
        print(f"❌ ERROR creating tables: {str(e)}")
        import traceback
        traceback.print_exc()
        print()
        print("Note: Some errors are normal if tables already exist")
        print()
        sys.exit(1)

    # Step 6: Verify tables were created
    print("🔍 Verifying tables...")
    try:
        from sqlalchemy import inspect

        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        print(f"✅ Found {len(existing_tables)} tables in database:")
        for table_name in sorted(existing_tables):
            print(f"   - {table_name}")
        print()

    except Exception as e:
        print(f"⚠️  Could not verify tables: {str(e)}")
        print()

    # Step 7: Create initial users (OWNER and SUPERUSER)
    print("👤 Creating initial users...")
    try:
        import asyncio
        from app.database import AsyncSessionLocal
        from app.models.user import User
        from app.utils.password import hash_password
        from sqlalchemy import select
        from uuid import uuid4
        from datetime import datetime

        async def create_initial_users():
            async with AsyncSessionLocal() as db:
                from sqlalchemy import text

                # Add new user roles to PostgreSQL enum
                new_roles = ['OWNER', 'ADMIN_SALES', 'ADMIN_SUPPORT', 'ADMIN_LOGISTICS', 'ADMIN_MARKETING', 'CUSTOMER']
                print("🔧 Updating usertype enum with new roles...")
                for role in new_roles:
                    try:
                        await db.execute(text(f"ALTER TYPE usertype ADD VALUE '{role}'"))
                        await db.commit()
                        print(f"   ✅ Added role: {role}")
                    except Exception as e:
                        # Role already exists or other error - this is fine
                        await db.rollback()
                        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                            print(f"   ℹ️  Role already exists: {role}")
                        else:
                            print(f"   ⚠️  Role {role}: {str(e)[:50]}")

                # Add permissions column if it doesn't exist
                try:
                    await db.execute(text(
                        "ALTER TABLE users ADD COLUMN IF NOT EXISTS permissions JSON DEFAULT '[]'::json"
                    ))
                    await db.commit()
                    print("✅ Permissions column verified/created")
                except Exception as e:
                    print(f"⚠️  Permissions column check: {str(e)}")
                    await db.rollback()

                # User 1: OWNER (jairo.colina.co@gmail.com)
                result = await db.execute(
                    select(User).where(User.email == "jairo.colina.co@gmail.com")
                )
                existing_owner = result.scalar_one_or_none()

                if not existing_owner:
                    hashed_password = await hash_password("Admin123456")
                    owner = User(
                        id=str(uuid4()),
                        email="jairo.colina.co@gmail.com",
                        password_hash=hashed_password,
                        nombre="Jairo",
                        apellido="Colina",
                        user_type="OWNER",
                        permissions=[],  # OWNER has all permissions by default (hardcoded)
                        is_active=True,
                        is_verified=True,
                        email_verified=True,
                        phone_verified=False,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(owner)
                    await db.commit()
                    print("✅ OWNER user created")
                    print("   Email: jairo.colina.co@gmail.com")
                    print("   Role: OWNER (nivel 100)")
                    print("   Permissions: ALL (hardcoded)")
                else:
                    print("✅ OWNER user already exists")

                # User 2: SUPERUSER (andreita2516@gmail.com)
                result = await db.execute(
                    select(User).where(User.email == "andreita2516@gmail.com")
                )
                existing_superuser = result.scalar_one_or_none()

                if not existing_superuser:
                    hashed_password = await hash_password("Admin123456")
                    superuser = User(
                        id=str(uuid4()),
                        email="andreita2516@gmail.com",
                        password_hash=hashed_password,
                        nombre="Andrea",
                        apellido="Admin",
                        user_type="SUPERUSER",
                        permissions=[
                            "users.*",
                            "products.*",
                            "orders.*",
                            "vendors.manage",
                            "reports.view",
                            "analytics.view"
                        ],
                        is_active=True,
                        is_verified=True,
                        email_verified=True,
                        phone_verified=False,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(superuser)
                    await db.commit()
                    print("✅ SUPERUSER user created")
                    print("   Email: andreita2516@gmail.com")
                    print("   Role: SUPERUSER (nivel 50)")
                    print("   Permissions: users.*, products.*, orders.*, vendors.manage, reports.view, analytics.view")
                else:
                    print("✅ SUPERUSER user already exists")

                print()
                print("📋 Password for both users: Admin123456")

        asyncio.run(create_initial_users())
        print()

    except Exception as e:
        print(f"⚠️  Could not create initial users: {str(e)}")
        print("   You can create them manually later")
        print()

    # Cleanup
    engine.dispose()

    # Success summary
    print("=" * 70)
    print("✅ DATABASE INITIALIZATION COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Start your application")
    print("  2. Access the API documentation")
    print("  3. Login with admin credentials")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
