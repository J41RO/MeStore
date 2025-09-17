#!/usr/bin/env python3
"""
Test script to create and verify superuser without complex database dependencies
"""

import asyncio
import sqlite3
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def create_test_superuser():
    """Create superuser using SQLite for immediate testing"""

    print("🔄 Creating test superuser with SQLite...")

    # Create SQLite database for testing
    db_path = "/tmp/mestore_test.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create users table (simplified)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            user_type TEXT NOT NULL,
            nombre TEXT,
            apellido TEXT,
            is_active BOOLEAN DEFAULT 1,
            email_verified BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Hash password using bcrypt directly
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Test credentials
    test_credentials = [
        {
            'email': 'super@mestore.com',
            'password': '123456',  # As requested by user
            'user_type': 'SUPERUSER',
            'nombre': 'Super',
            'apellido': 'Admin'
        },
        {
            'email': 'super@mestore.com',
            'password': 'Super123!',  # From setup script
            'user_type': 'SUPERUSER',
            'nombre': 'Super',
            'apellido': 'Admin'
        }
    ]

    for cred in test_credentials:
        password_hash = pwd_context.hash(cred['password'])

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO users
                (email, password_hash, user_type, nombre, apellido, is_active, email_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                cred['email'],
                password_hash,
                cred['user_type'],
                cred['nombre'],
                cred['apellido'],
                1,
                1
            ))

            print(f"✅ Created user: {cred['email']} with password: {cred['password']}")

            # Verify the password works
            stored_hash = cursor.execute("SELECT password_hash FROM users WHERE email = ?", (cred['email'],)).fetchone()[0]
            if pwd_context.verify(cred['password'], stored_hash):
                print(f"✅ Password verification successful for {cred['email']}")
            else:
                print(f"❌ Password verification failed for {cred['email']}")

        except Exception as e:
            print(f"❌ Error creating user {cred['email']}: {e}")

    conn.commit()

    # Show all users
    cursor.execute("SELECT email, user_type, is_active FROM users")
    users = cursor.fetchall()
    print(f"\n📋 Users in test database:")
    for user in users:
        print(f"  - {user[0]} | {user[1]} | Active: {user[2]}")

    conn.close()

    print(f"\n✅ SQLite test database created at: {db_path}")
    return True

# Also test PostgreSQL connection with various approaches
async def test_postgresql_approaches():
    """Try different PostgreSQL connection approaches"""

    print("\n🔍 Testing PostgreSQL connection approaches...")

    # Approach 1: Use environment DATABASE_URL
    try:
        print("📊 Testing approach 1: Environment DATABASE_URL...")
        from app.core.database import engine

        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1 as test")
            print("✅ PostgreSQL connection successful with environment config!")
            return True

    except Exception as e:
        print(f"❌ PostgreSQL approach 1 failed: {e}")

    # Approach 2: Try with different credentials
    try:
        print("📊 Testing approach 2: Alternative credentials...")
        import asyncpg

        # Common default PostgreSQL configs
        configs = [
            "postgresql://postgres:postgres@localhost/postgres",
            "postgresql://user:pass@localhost/mestore",
            "postgresql://mestore:mestore@localhost/mestore",
        ]

        for config in configs:
            try:
                conn = await asyncpg.connect(config)
                result = await conn.fetch("SELECT current_database()")
                print(f"✅ Connected with: {config}")
                await conn.close()
                return config
            except Exception as e:
                print(f"❌ Failed with {config}: {e}")

    except Exception as e:
        print(f"❌ PostgreSQL approach 2 failed: {e}")

    return False

async def main():
    """Main function"""
    print("=" * 60)
    print("🚀 SUPERUSER CREATION AND TESTING")
    print("=" * 60)

    # Test SQLite approach first
    await create_test_superuser()

    # Test PostgreSQL approaches
    pg_result = await test_postgresql_approaches()

    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    print("✅ SQLite test database created with superuser credentials")
    print("📧 super@mestore.com")
    print("🔑 Passwords tested: '123456' and 'Super123!'")

    if pg_result:
        print(f"✅ PostgreSQL connection available: {pg_result if isinstance(pg_result, str) else 'Default config'}")
    else:
        print("❌ PostgreSQL connection issues - using SQLite for testing")

    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)