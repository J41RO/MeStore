#!/usr/bin/env python3
"""
Update test user passwords with correct hashes
"""

import sqlite3
from passlib.context import CryptContext

# Same configuration as in the app
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def update_test_passwords():
    """Update database with correct password hashes for test users"""

    # Test users with their intended passwords
    test_users = {
        "admin@test.com": "admin123",
        "vendor@test.com": "vendor123",
        "buyer@test.com": "buyer123"
    }

    print("🔧 Updating test user passwords...")
    print("=" * 60)

    try:
        # Connect to database
        conn = sqlite3.connect('mestore_production.db')
        cursor = conn.cursor()

        # Check current users
        print("📋 Current users in database:")
        cursor.execute('SELECT email, user_type, is_active FROM users')
        users = cursor.fetchall()
        for email, user_type, is_active in users:
            print(f"  📧 {email} | Type: {user_type} | Active: {is_active}")

        print("\n" + "=" * 60)

        for email, password in test_users.items():
            print(f"\n📧 Processing: {email}")
            print(f"🔑 Setting password: {password}")

            # Generate new hash
            new_hash = pwd_context.hash(password)
            print(f"🔐 Generated hash: {new_hash[:20]}...")

            # Verify the hash works
            verify_result = pwd_context.verify(password, new_hash)
            if not verify_result:
                print(f"❌ ERROR: Hash verification failed for {email}")
                continue

            print(f"✅ Hash verification: PASSED")

            # Update database
            cursor.execute(
                'UPDATE users SET password_hash = ? WHERE email = ?',
                (new_hash, email)
            )

            if cursor.rowcount > 0:
                print(f"✅ Database updated successfully")
            else:
                print(f"⚠️  No user found with email: {email}")

        # Commit changes
        conn.commit()
        print("\n" + "=" * 60)
        print("🎉 All password updates committed!")

        # Final verification
        print("\n🔍 Final verification...")
        for email, password in test_users.items():
            cursor.execute(
                'SELECT password_hash FROM users WHERE email = ?',
                (email,)
            )
            result = cursor.fetchone()

            if result:
                stored_hash = result[0]
                verify_result = pwd_context.verify(password, stored_hash)
                status = "✅ WORKING" if verify_result else "❌ FAILED"
                print(f"{status} {email} with password '{password}'")
            else:
                print(f"❌ User not found: {email}")

        conn.close()

        print("\n" + "🎉" * 20)
        print("SUCCESS! You can now login with:")
        print("  📧 admin@test.com | 🔑 admin123")
        print("  📧 vendor@test.com | 🔑 vendor123")
        print("  📧 buyer@test.com | 🔑 buyer123")
        print("🎉" * 20)

    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

    return True

if __name__ == "__main__":
    success = update_test_passwords()
    exit(0 if success else 1)