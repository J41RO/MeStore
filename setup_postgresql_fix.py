#!/usr/bin/env python3
"""
PostgreSQL Database Setup Fix for MeStore
This script fixes the database connection issues by properly setting up the database and user
"""

import asyncio
import os
import subprocess
import sys
from pathlib import Path


async def setup_postgresql():
    """Set up PostgreSQL database and user"""

    print("🔧 PostgreSQL Database Setup Fix")
    print("=" * 50)

    # Method 1: Try to create using psql with different approaches
    sql_commands = [
        "CREATE USER test_user WITH PASSWORD 'secure_test_pass_123';",
        "CREATE DATABASE test_mestocker OWNER test_user;",
        "GRANT ALL PRIVILEGES ON DATABASE test_mestocker TO test_user;",
    ]

    print("📊 Method 1: Creating database using psql...")

    # Try various PostgreSQL connection approaches
    connection_attempts = [
        ["psql", "-d", "postgres"],  # Connect to default postgres database
        ["psql", "-U", "postgres"],  # Try as postgres user
        ["psql"],  # Try with current user
    ]

    for cmd_base in connection_attempts:
        try:
            print(f"🔄 Trying connection: {' '.join(cmd_base)}")

            # Test connection first
            test_cmd = cmd_base + ["-c", "SELECT version();"]
            result = subprocess.run(
                test_cmd, capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                print(f"✅ Connection successful with: {' '.join(cmd_base)}")
                print(f"PostgreSQL Version: {result.stdout.strip()}")

                # Execute setup commands
                for sql_cmd in sql_commands:
                    print(f"🔄 Executing: {sql_cmd}")
                    exec_cmd = cmd_base + ["-c", sql_cmd]

                    exec_result = subprocess.run(
                        exec_cmd, capture_output=True, text=True, timeout=10
                    )

                    if exec_result.returncode == 0:
                        print(f"✅ Success: {sql_cmd}")
                    else:
                        error_msg = exec_result.stderr.strip()
                        if "already exists" in error_msg:
                            print(f"ℹ️ Already exists: {sql_cmd}")
                        else:
                            print(f"⚠️ Error: {error_msg}")

                # Test the new connection
                test_new_conn = [
                    "psql",
                    "-U",
                    "test_user",
                    "-d",
                    "test_mestocker",
                    "-c",
                    "SELECT current_database();",
                ]
                test_result = subprocess.run(
                    test_new_conn,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    env={**os.environ, "PGPASSWORD": "secure_test_pass_123"},
                )

                if test_result.returncode == 0:
                    print("✅ New database connection test successful!")
                    return True
                else:
                    print(
                        f"❌ New database connection test failed: {test_result.stderr.strip()}"
                    )

            else:
                print(f"❌ Connection failed: {result.stderr.strip()}")

        except subprocess.TimeoutExpired:
            print(f"⏰ Connection timed out: {' '.join(cmd_base)}")
        except Exception as e:
            print(f"❌ Error with {' '.join(cmd_base)}: {e}")

    # Method 2: Try using createuser and createdb commands
    print("\n📊 Method 2: Using createuser and createdb...")

    try:
        # Create user
        print("🔄 Creating user with createuser...")
        create_user_cmd = ["createuser", "--no-password", "test_user"]
        result = subprocess.run(
            create_user_cmd, capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0 or "already exists" in result.stderr:
            print("✅ User created or already exists")

            # Set password
            print("🔄 Setting password...")
            set_pass_cmd = [
                "psql",
                "-c",
                "ALTER USER test_user WITH PASSWORD 'secure_test_pass_123';",
            ]
            subprocess.run(set_pass_cmd, capture_output=True, text=True, timeout=10)

            # Create database
            print("🔄 Creating database with createdb...")
            create_db_cmd = ["createdb", "-O", "test_user", "test_mestocker"]
            db_result = subprocess.run(
                create_db_cmd, capture_output=True, text=True, timeout=30
            )

            if db_result.returncode == 0 or "already exists" in db_result.stderr:
                print("✅ Database created or already exists")
                return True
            else:
                print(f"❌ Database creation failed: {db_result.stderr.strip()}")

        else:
            print(f"❌ User creation failed: {result.stderr.strip()}")

    except Exception as e:
        print(f"❌ Error in method 2: {e}")

    return False


async def test_application_connection():
    """Test if the application can connect with the fixed database"""

    print("\n🧪 Testing Application Database Connection")
    print("=" * 50)

    try:
        # Set environment for testing
        os.environ["DATABASE_URL"] = (
            "postgresql+asyncpg://test_user:secure_test_pass_123@localhost/test_mestocker"
        )

        # Import after setting environment
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        print("🔄 Testing async connection...")
        import asyncpg

        conn = await asyncpg.connect(
            "postgresql://test_user:secure_test_pass_123@localhost/test_mestocker"
        )
        result = await conn.fetch("SELECT current_database(), current_user")
        print(
            f"✅ Database: {result[0]['current_database']}, User: {result[0]['current_user']}"
        )
        await conn.close()

        print("🔄 Testing application database module...")
        from app.core.database import engine

        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1 as test")
            print("✅ Application database connection successful!")

        print("🔄 Testing database initialization...")
        from app.core.database import init_db

        await init_db()
        print("✅ Database tables created successfully!")

        return True

    except Exception as e:
        print(f"❌ Application connection test failed: {e}")
        return False


async def create_superuser_in_db():
    """Create the superuser in the properly configured database"""

    print("\n👤 Creating Superuser")
    print("=" * 50)

    try:
        # Import application modules
        from sqlalchemy import select

        from app.core.database import AsyncSessionLocal
        from app.models.user import User, UserType
        from app.utils.password import hash_password

        async with AsyncSessionLocal() as db:
            # Check if superuser already exists
            result = await db.execute(
                select(User).filter(User.email == "super@mestore.com")
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print("🔄 Updating existing superuser...")
                # Update password to ensure it's correct
                existing_user.password_hash = await hash_password("123456")
                existing_user.user_type = UserType.SUPERUSER
                existing_user.is_active = True
                existing_user.email_verified = True
                print("✅ Superuser updated with password: 123456")
            else:
                print("🔄 Creating new superuser...")
                # Create new superuser
                new_user = User(
                    email="super@mestore.com",
                    password_hash=await hash_password("123456"),
                    user_type=UserType.SUPERUSER,
                    nombre="Super",
                    apellido="Admin",
                    is_active=True,
                    email_verified=True,
                )
                db.add(new_user)
                print("✅ New superuser created with password: 123456")

            await db.commit()

            # Verify the user was created/updated
            result = await db.execute(
                select(User).filter(User.email == "super@mestore.com")
            )
            user = result.scalar_one_or_none()

            if user:
                print(f"✅ Superuser verified:")
                print(f"   Email: {user.email}")
                print(f"   Type: {user.user_type}")
                print(f"   Active: {user.is_active}")
                print(f"   Email Verified: {user.email_verified}")
                return True
            else:
                print("❌ Superuser verification failed")
                return False

    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        return False


async def main():
    """Main function to fix the database setup"""

    print("🚀 MeStore Database Setup Fix")
    print("=" * 60)

    # Step 1: Set up PostgreSQL database and user
    print("Step 1: PostgreSQL Setup")
    pg_success = await setup_postgresql()

    if not pg_success:
        print("⚠️ PostgreSQL setup had issues, but continuing with testing...")

    # Step 2: Test application connection
    print("\nStep 2: Application Connection Test")
    app_success = await test_application_connection()

    if not app_success:
        print("❌ Cannot proceed without database connection")
        return False

    # Step 3: Create superuser
    print("\nStep 3: Superuser Creation")
    user_success = await create_superuser_in_db()

    # Summary
    print("\n" + "=" * 60)
    print("📋 SETUP SUMMARY")
    print("=" * 60)
    print(f"PostgreSQL Setup: {'✅ Success' if pg_success else '⚠️ Partial'}")
    print(f"Application Connection: {'✅ Success' if app_success else '❌ Failed'}")
    print(f"Superuser Creation: {'✅ Success' if user_success else '❌ Failed'}")

    if user_success:
        print("\n🎉 DATABASE SETUP COMPLETE!")
        print("📧 Email: super@mestore.com")
        print("🔑 Password: 123456")
        print("🌐 Test login at: http://192.168.1.137:5173/admin-login")
        return True
    else:
        print("\n❌ Database setup incomplete")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
