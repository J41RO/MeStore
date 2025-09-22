#!/usr/bin/env python3
"""
Test password verification directly
"""

import sys
sys.path.append('.')

from passlib.context import CryptContext

# Hash from database
db_hash = "$2b$12$5Ol/Kzbyj8AXojToUYiT6eXbPgql5UlEBzBLkigOi46HRMrqg5rSi"
password = "vendor123"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

print(f"🔍 Testing password verification")
print(f"Password: {password}")
print(f"Hash: {db_hash}")

# Test verification
try:
    is_valid = pwd_context.verify(password, db_hash)
    print(f"✅ Verification result: {is_valid}")

    # Test hash generation
    new_hash = pwd_context.hash(password)
    print(f"🆕 New hash: {new_hash}")

    # Test new hash verification
    new_valid = pwd_context.verify(password, new_hash)
    print(f"✅ New hash verification: {new_valid}")

except Exception as e:
    print(f"❌ Error: {e}")