#!/usr/bin/env python3
"""
Production Database Initialization Script
==========================================

This script initializes the production database by running Alembic migrations.

Usage:
    python scripts/init_production_db.py

Environment Variables Required:
    DATABASE_URL - PostgreSQL connection string

Author: Claude Code
Date: 2025-10-07
"""

import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def validate_environment():
    """Validate required environment variables are set."""
    logger.info("Validating environment variables...")

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set")
        return False

    # Check if it's a valid PostgreSQL URL
    if not database_url.startswith(("postgresql://", "postgresql+asyncpg://")):
        logger.warning(f"⚠️  DATABASE_URL doesn't look like PostgreSQL: {database_url[:30]}...")

    logger.info(f"✅ DATABASE_URL configured: {database_url[:50]}...")
    return True


def check_database_connection():
    """Test database connectivity before running migrations."""
    logger.info("Testing database connection...")

    try:
        from sqlalchemy import create_engine, text
        from app.core.config import settings

        # Create sync engine for connection test
        database_url = settings.DATABASE_URL
        # Convert async URL to sync if needed
        if "asyncpg" in database_url:
            database_url = database_url.replace("+asyncpg", "")
        if "aiosqlite" in database_url:
            database_url = database_url.replace("+aiosqlite", "")

        engine = create_engine(database_url)

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()

        logger.info("✅ Database connection successful")
        engine.dispose()
        return True

    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False


def run_alembic_migrations():
    """Run Alembic migrations to upgrade database to head."""
    logger.info("Running Alembic migrations...")
    logger.info("Command: alembic upgrade head")

    try:
        # Change to project root directory
        os.chdir(project_root)

        # Run alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )

        # Log output
        if result.stdout:
            for line in result.stdout.split('\n'):
                if line.strip():
                    logger.info(f"  {line}")

        if result.stderr:
            for line in result.stderr.split('\n'):
                if line.strip():
                    logger.warning(f"  {line}")

        if result.returncode == 0:
            logger.info("✅ Alembic migrations completed successfully")
            return True
        else:
            logger.error(f"❌ Alembic migration failed with exit code {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("❌ Alembic migration timed out after 5 minutes")
        return False
    except FileNotFoundError:
        logger.error("❌ Alembic command not found. Is it installed?")
        logger.info("   Run: pip install alembic")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error running migrations: {str(e)}")
        return False


def verify_migrations():
    """Verify that migrations were applied successfully."""
    logger.info("Verifying migration status...")

    try:
        result = subprocess.run(
            ["alembic", "current"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            current_revision = result.stdout.strip()
            logger.info(f"✅ Current database revision: {current_revision}")
            return True
        else:
            logger.warning("⚠️  Could not verify current revision")
            return False

    except Exception as e:
        logger.warning(f"⚠️  Could not verify migrations: {str(e)}")
        return False


async def create_admin_user():
    """Create initial users (OWNER and SUPERUSER) if they don't exist."""
    logger.info("Checking for initial users...")

    try:
        from app.database import AsyncSessionLocal
        from app.models.user import User
        from app.utils.password import hash_password
        from sqlalchemy import select
        from uuid import uuid4
        from datetime import datetime

        async with AsyncSessionLocal() as db:
            from sqlalchemy import text

            # Add new user roles to PostgreSQL enum
            new_roles = ['OWNER', 'ADMIN_SALES', 'ADMIN_SUPPORT', 'ADMIN_LOGISTICS', 'ADMIN_MARKETING', 'CUSTOMER']
            logger.info("🔧 Updating usertype enum with new roles...")
            for role in new_roles:
                try:
                    await db.execute(text(f"ALTER TYPE usertype ADD VALUE '{role}'"))
                    await db.commit()
                    logger.info(f"   ✅ Added role: {role}")
                except Exception as e:
                    # Role already exists or other error - this is fine
                    await db.rollback()
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        logger.info(f"   ℹ️  Role already exists: {role}")
                    else:
                        logger.warning(f"   ⚠️  Role {role}: {str(e)[:50]}")

            # Add permissions column if it doesn't exist
            try:
                await db.execute(text(
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS permissions JSON DEFAULT '[]'::json"
                ))
                await db.commit()
                logger.info("✅ Permissions column verified/created")
            except Exception as e:
                logger.warning(f"⚠️  Permissions column check: {str(e)}")
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
                logger.info("✅ OWNER user created successfully")
                logger.info("   Email: jairo.colina.co@gmail.com")
                logger.info("   Role: OWNER (nivel 100)")
                logger.info("   Permissions: ALL (hardcoded)")
            else:
                logger.info("✅ OWNER user already exists")

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
                logger.info("✅ SUPERUSER user created successfully")
                logger.info("   Email: andreita2516@gmail.com")
                logger.info("   Role: SUPERUSER (nivel 50)")
                logger.info("   Permissions: users.*, products.*, orders.*, vendors.manage, reports.view, analytics.view")
            else:
                logger.info("✅ SUPERUSER user already exists")

            logger.info("")
            logger.info("📋 Password for both users: Admin123456")
            return True

    except Exception as e:
        logger.error(f"❌ Failed to create initial users: {str(e)}")
        return False


async def main():
    """Main initialization function."""
    logger.info("=" * 70)
    logger.info("PRODUCTION DATABASE INITIALIZATION")
    logger.info("=" * 70)
    logger.info("")

    # Step 1: Validate environment
    if not validate_environment():
        logger.error("❌ Environment validation failed")
        sys.exit(1)

    logger.info("")

    # Step 2: Test database connection
    if not check_database_connection():
        logger.error("❌ Database connection test failed")
        sys.exit(1)

    logger.info("")

    # Step 3: Run migrations
    if not run_alembic_migrations():
        logger.error("❌ Database migration failed")
        sys.exit(1)

    logger.info("")

    # Step 4: Verify migrations
    verify_migrations()

    logger.info("")

    # Step 5: Create admin user
    await create_admin_user()

    logger.info("")
    logger.info("=" * 70)
    logger.info("✅ DATABASE INITIALIZATION COMPLETED SUCCESSFULLY")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Next steps:")
    logger.info("  1. Start the application: uvicorn app.main_production:app")
    logger.info("  2. Access the API: http://localhost:8000/docs")
    logger.info("  3. Login with admin credentials")
    logger.info("")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)
