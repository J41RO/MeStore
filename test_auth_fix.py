#!/usr/bin/env python3
"""
Test script to verify the authentication fix
"""
import asyncio
import sys
from app.services.auth_service import AuthService
from app.core.database import AsyncSessionLocal

async def test_authentication():
    """Test the fixed authentication service"""

    print("🔧 Testing Authentication Fix...")
    print("=" * 50)

    auth_service = AuthService()

    # Test credentials
    email = "super@mestore.com"
    password = "123456"

    print(f"📧 Testing email: {email}")
    print(f"🔑 Testing password: {password}")
    print()

    try:
        # Test with async session
        async with AsyncSessionLocal() as db:
            print("🔄 Attempting authentication...")

            user_data = await auth_service.authenticate_user_simple(
                db=db,
                email=email,
                password=password
            )

            if user_data:
                print("✅ AUTHENTICATION SUCCESSFUL!")
                print("📋 User data returned:")
                for key, value in user_data.items():
                    print(f"   {key}: {value}")

                # Test password verification separately
                print("\n🔐 Testing password verification separately:")

                # Get password hash from database
                from sqlalchemy import select, text
                result = await db.execute(text("SELECT password_hash FROM users WHERE email = :email"), {"email": email})
                row = result.fetchone()

                if row:
                    stored_hash = row[0]
                    print(f"   Stored hash: {stored_hash[:50]}...")

                    # Verify password
                    is_valid = await auth_service.verify_password(password, stored_hash)
                    print(f"   Password verification: {'✅ VALID' if is_valid else '❌ INVALID'}")

                return True
            else:
                print("❌ AUTHENTICATION FAILED!")

                # Let's debug step by step
                print("\n🔍 DEBUGGING:")

                # Check if user exists
                from sqlalchemy import select, text
                result = await db.execute(text("SELECT email, user_type, password_hash FROM users WHERE email = :email"), {"email": email})
                row = result.fetchone()

                if row:
                    print(f"   ✅ User exists in database")
                    print(f"   📧 Email: {row[0]}")
                    print(f"   👤 Type: {row[1]}")
                    print(f"   🔑 Hash: {row[2][:50]}...")

                    # Test password verification
                    is_valid = await auth_service.verify_password(password, row[2])
                    print(f"   🔐 Password check: {'✅ VALID' if is_valid else '❌ INVALID'}")

                else:
                    print(f"   ❌ User NOT found in database!")

                return False

    except Exception as e:
        print(f"💥 ERROR during authentication test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_authentication())

    if success:
        print("\n🎉 Authentication fix is WORKING!")
        sys.exit(0)
    else:
        print("\n🚨 Authentication fix is NOT working!")
        sys.exit(1)