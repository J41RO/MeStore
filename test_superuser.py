#!/usr/bin/env python3
"""
Test superuser creation and login functionality
"""

import sys
from pathlib import Path
import sqlite3
from passlib.context import CryptContext

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

DATABASE_FILE = "./mestore_production.db"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_superuser():
    """Test if superuser exists and password is correct"""
    print("🔍 Testing superuser in database...")

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    try:
        # Get superuser details
        cursor.execute("""
            SELECT id, email, password_hash, user_type, is_active, is_verified, email_verified
            FROM users WHERE email = ?
        """, ("super@mestore.com",))

        result = cursor.fetchone()

        if not result:
            print("❌ Superuser not found!")
            return False

        user_id, email, password_hash, user_type, is_active, is_verified, email_verified = result

        print(f"✅ Superuser found:")
        print(f"   ID: {user_id}")
        print(f"   Email: {email}")
        print(f"   User Type: {user_type}")
        print(f"   Active: {bool(is_active)}")
        print(f"   Verified: {bool(is_verified)}")
        print(f"   Email Verified: {bool(email_verified)}")

        # Test password verification
        password_valid = pwd_context.verify("123456", password_hash)
        print(f"   Password Test: {'✅ VALID' if password_valid else '❌ INVALID'}")

        # Test overall ready status
        ready = (
            user_type == "SUPERUSER" and
            bool(is_active) and
            bool(is_verified) and
            password_valid
        )

        print(f"\n🎯 Overall Status: {'✅ READY FOR LOGIN' if ready else '❌ NOT READY'}")

        return ready

    except Exception as e:
        print(f"❌ Error testing superuser: {e}")
        return False
    finally:
        conn.close()

def test_password_hash():
    """Test password hashing"""
    print("\n🔧 Testing password hashing...")

    test_password = "123456"
    hashed = pwd_context.hash(test_password)
    verified = pwd_context.verify(test_password, hashed)

    print(f"   Original: {test_password}")
    print(f"   Hashed: {hashed[:50]}...")
    print(f"   Verification: {'✅ SUCCESS' if verified else '❌ FAILED'}")

    return verified

if __name__ == "__main__":
    print("🚀 Testing MeStore Superuser Setup\n")

    # Test password hashing first
    hash_test = test_password_hash()

    # Test superuser
    superuser_test = test_superuser()

    print(f"\n🎉 Final Result: {'✅ ALL TESTS PASSED' if hash_test and superuser_test else '❌ TESTS FAILED'}")

    if hash_test and superuser_test:
        print("\n📋 Ready for login:")
        print("   URL: http://192.168.1.137:5173/admin-login")
        print("   Email: super@mestore.com")
        print("   Password: 123456")
    else:
        sys.exit(1)