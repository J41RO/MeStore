#!/usr/bin/env python3
"""
Railway Database Tables Checker
================================

Simple script to connect to Railway PostgreSQL and list all existing tables.
Uses SQLAlchemy Inspector to enumerate database tables.

Usage:
    DATABASE_URL="postgresql://..." python scripts/check_railway_tables.py

Environment Variables Required:
    DATABASE_URL - PostgreSQL connection string from Railway

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
    """Check Railway database tables."""

    print("=" * 70)
    print("🔍 RAILWAY DATABASE TABLES CHECKER")
    print("=" * 70)
    print()

    # Step 1: Get DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print()
        print("Usage:")
        print('  DATABASE_URL="postgresql://..." python scripts/check_railway_tables.py')
        print()
        sys.exit(1)

    print(f"✅ DATABASE_URL: {database_url[:50]}...")
    print()

    # Step 2: Create database engine
    print("🔌 Connecting to database...")
    try:
        from sqlalchemy import create_engine, inspect

        # Convert async URL to sync if needed
        sync_database_url = database_url
        if "asyncpg" in sync_database_url:
            sync_database_url = sync_database_url.replace("+asyncpg", "")
        if "aiosqlite" in sync_database_url:
            sync_database_url = sync_database_url.replace("+aiosqlite", "")

        # Create engine
        engine = create_engine(
            sync_database_url,
            echo=False,
            pool_pre_ping=True
        )

        print("✅ Database engine created")
        print()

    except Exception as e:
        print(f"❌ ERROR creating database engine: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Step 3: Test connection
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

    # Step 4: List all tables
    print("📋 Listing all tables in database...")
    try:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        if not table_names:
            print("⚠️  No tables found in database")
            print()
            print("The database exists but is empty.")
            print("You may need to run database initialization:")
            print("  - python scripts/init_railway_db.py")
            print("  - OR: alembic upgrade head")
            print()
        else:
            print(f"✅ Found {len(table_names)} table(s) in database:")
            print()

            # Display tables in sorted order
            for i, table_name in enumerate(sorted(table_names), 1):
                print(f"  {i:2d}. {table_name}")

            print()
            print(f"📊 Total: {len(table_names)} tables")
            print()

            # Show some additional info for each table
            print("📊 Table Details:")
            print()
            for table_name in sorted(table_names):
                columns = inspector.get_columns(table_name)
                print(f"  📁 {table_name}")
                print(f"     Columns: {len(columns)}")
                print(f"     Column names: {', '.join([col['name'] for col in columns[:5]])}")
                if len(columns) > 5:
                    print(f"                   ... and {len(columns) - 5} more")
                print()

    except Exception as e:
        print(f"❌ ERROR listing tables: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Cleanup
    engine.dispose()

    print("=" * 70)
    print("✅ DATABASE CHECK COMPLETED")
    print("=" * 70)
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
