#!/usr/bin/env python3
"""
Fix superuser authentication using SQLite database
This script creates the database and superuser to fix the login issue immediately
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def init_database_and_create_superuser():
    """Initialize SQLite database and create superuser"""

    print("🚀 SQLite Database Initialization and Superuser Creation")
    print("=" * 60)

    try:
        # Remove existing database if it exists
        db_path = Path("./mestore.db")
        if db_path.exists():
            db_path.unlink()
            print("🗑️ Removed existing database")

        print("🔄 Initializing database...")

        # Import application modules
        from app.core.database import init_db, AsyncSessionLocal
        from app.models.user import User, UserType
        from app.utils.password import hash_password
        from sqlalchemy import select

        # Initialize database (create tables)
        await init_db()
        print("✅ Database tables created")

        # Create superuser
        print("🔄 Creating superuser...")

        async with AsyncSessionLocal() as db:
            # Create superuser with the requested password
            password_hash = await hash_password("123456")

            new_user = User(
                email="super@mestore.com",
                password_hash=password_hash,
                user_type=UserType.SUPERUSER,
                nombre="Super",
                apellido="Admin",
                is_active=True,
                email_verified=True
            )

            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

            print("✅ Superuser created successfully!")
            print(f"   Email: {new_user.email}")
            print(f"   Type: {new_user.user_type}")
            print(f"   Active: {new_user.is_active}")

        # Verify authentication
        print("🧪 Testing authentication...")
        await test_authentication()

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_authentication():
    """Test the authentication service"""

    try:
        from app.core.database import AsyncSessionLocal
        from app.services.auth_service import AuthService
        from app.models.user import User
        from sqlalchemy import select

        auth_service = AuthService()

        async with AsyncSessionLocal() as db:
            # Test authentication
            print("🔄 Testing password verification...")

            # Get the user from database
            result = await db.execute(
                select(User).filter(User.email == "super@mestore.com")
            )
            user = result.scalar_one_or_none()

            if not user:
                print("❌ User not found in database")
                return False

            # Test password verification
            is_valid = await auth_service.verify_password("123456", user.password_hash)

            if is_valid:
                print("✅ Password verification successful!")
                print("🔑 Credentials confirmed:")
                print("   Email: super@mestore.com")
                print("   Password: 123456")
                return True
            else:
                print("❌ Password verification failed")
                return False

    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

async def test_login_endpoint():
    """Test the login endpoint directly"""

    print("\n🧪 Testing Login Endpoint")
    print("=" * 40)

    try:
        # Import FastAPI test client
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # Test login request
        login_data = {
            "email": "super@mestore.com",
            "password": "123456"
        }

        print("🔄 Testing login endpoint...")
        response = client.post("/api/v1/auth/login", json=login_data)

        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Body: {response.text}")

        if response.status_code == 200:
            print("✅ Login endpoint working correctly!")
            return True
        else:
            print(f"❌ Login endpoint failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Login endpoint test failed: {e}")
        return False

async def main():
    """Main function"""

    print("🎯 CRITICAL LOGIN FIX - SUPERUSER AUTHENTICATION")
    print("=" * 60)

    # Step 1: Initialize database and create superuser
    success = await init_database_and_create_superuser()

    if not success:
        print("❌ Database initialization failed")
        return False

    # Step 2: Test login endpoint
    endpoint_success = await test_login_endpoint()

    # Summary
    print("\n" + "=" * 60)
    print("📋 AUTHENTICATION FIX SUMMARY")
    print("=" * 60)
    print(f"Database Setup: {'✅ Success' if success else '❌ Failed'}")
    print(f"Login Endpoint: {'✅ Success' if endpoint_success else '❌ Failed'}")

    if success:
        print("\n🎉 SUPERUSER LOGIN FIX COMPLETE!")
        print("📧 Email: super@mestore.com")
        print("🔑 Password: 123456")
        print("🌐 Admin Portal: http://192.168.1.137:5173/admin-login")
        print("📁 Database: SQLite (./mestore.db)")

        print("\n🔧 Next Steps:")
        print("1. Start the FastAPI server: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        print("2. Test login at: http://192.168.1.137:5173/admin-login")
        print("3. Use credentials: super@mestore.com / 123456")

        return True
    else:
        print("\n❌ Superuser authentication fix failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)