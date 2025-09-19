#!/usr/bin/env python3
"""
Debug authentication issue - find what password the hash corresponds to
"""

import asyncio
import sys
from passlib.context import CryptContext

# Same configuration as in the app
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_known_passwords():
    """Test what password the current hash corresponds to"""

    # Current hash from database
    stored_hash = "$2b$12$LQv3c1yqBwlVHpPjrCXmy.csv6a1aGp7qHt8qSksjX7LXsKtq1Rwy"

    # Common passwords to test
    test_passwords = [
        "admin123", "vendor123", "buyer123",
        "password", "test", "123456", "admin",
        "test123", "password123", "mestore123",
        "12345678", "qwerty", "letmein",
        "admin@test.com", "password1", "admin1",
        "test_password", "default", "secret",
        "changeme", "password12", "admin12"
    ]

    print("🔍 Testing common passwords against stored hash:")
    print(f"Hash: {stored_hash}")
    print("-" * 80)

    found_password = None
    for password in test_passwords:
        try:
            is_valid = pwd_context.verify(password, stored_hash)
            status = "✅ MATCH!" if is_valid else "❌"
            print(f"{status} '{password}'")
            if is_valid:
                found_password = password
                break
        except Exception as e:
            print(f"❌ '{password}' - ERROR: {e}")

    print("-" * 80)

    if found_password:
        print(f"🎉 FOUND! The password is: '{found_password}'")
    else:
        print("❌ No matching password found from common list")

    print("\n" + "="*80)
    print("🔧 Generating new correct hashes:")

    # Generate correct hashes for intended passwords
    intended_passwords = {
        "admin@test.com": "admin123",
        "vendor@test.com": "vendor123",
        "buyer@test.com": "buyer123"
    }

    for email, password in intended_passwords.items():
        hash_result = pwd_context.hash(password)
        print(f"\n📧 {email}")
        print(f"🔑 Password: {password}")
        print(f"🔐 Hash: {hash_result}")

        # Verify the new hash works
        verify_result = pwd_context.verify(password, hash_result)
        print(f"✅ Verification: {'WORKS' if verify_result else 'FAILED'}")

if __name__ == "__main__":
    test_known_passwords()