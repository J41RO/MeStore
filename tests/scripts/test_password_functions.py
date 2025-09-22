#!/usr/bin/env python3
"""
Test password hashing and verification functions
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.password import hash_password, verify_password
from app.core.security import get_password_hash
from passlib.context import CryptContext

# Test configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def test_password_functions():
    """Test all password-related functions"""

    print("🔧 Testing password hashing and verification functions...")
    print("=" * 70)

    test_passwords = ["admin123", "vendor123", "buyer123", "test_password"]

    for password in test_passwords:
        print(f"\n🔑 Testing password: '{password}'")

        # Test 1: app.utils.password.hash_password (async)
        try:
            hash1 = await hash_password(password)
            print(f"  ✅ hash_password: {hash1[:25]}...")

            # Verify with async function
            verify1 = await verify_password(password, hash1)
            print(f"  ✅ verify_password (async): {verify1}")

            # Verify with sync passlib
            verify1_sync = pwd_context.verify(password, hash1)
            print(f"  ✅ verify_password (sync): {verify1_sync}")

        except Exception as e:
            print(f"  ❌ hash_password error: {e}")

        # Test 2: app.core.security.get_password_hash (should be same as hash_password)
        try:
            hash2 = await get_password_hash(password)
            print(f"  ✅ get_password_hash: {hash2[:25]}...")

            # Verify compatibility
            verify2 = await verify_password(password, hash2)
            print(f"  ✅ get_password_hash verify: {verify2}")

        except Exception as e:
            print(f"  ❌ get_password_hash error: {e}")

        # Test 3: Direct passlib (sync)
        try:
            hash3 = pwd_context.hash(password)
            print(f"  ✅ passlib direct: {hash3[:25]}...")

            verify3 = pwd_context.verify(password, hash3)
            print(f"  ✅ passlib verify: {verify3}")

            # Cross-verify with async function
            verify3_async = await verify_password(password, hash3)
            print(f"  ✅ passlib->async verify: {verify3_async}")

        except Exception as e:
            print(f"  ❌ passlib direct error: {e}")

        print("  " + "-" * 50)

    print("\n" + "=" * 70)
    print("🎉 Password function testing completed!")

if __name__ == "__main__":
    asyncio.run(test_password_functions())