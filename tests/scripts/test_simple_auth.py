#!/usr/bin/env python3
"""
Simple authentication test to isolate the login issue
"""

import asyncio
import sys
sys.path.append('.')

from app.utils.password import verify_password
from app.core.security import create_access_token, decode_access_token
from app.database import get_db
from app.models.user import User
from sqlalchemy import select
import sqlite3

async def test_simple_auth():
    """Test authentication with direct database queries"""

    # Test 1: Check password verification
    print("=== PASSWORD VERIFICATION TEST ===")
    conn = sqlite3.connect('mestore_production.db')
    cursor = conn.cursor()
    cursor.execute('SELECT email, password_hash FROM users WHERE email = ?', ('admin@test.com',))
    result = cursor.fetchone()
    conn.close()

    if result:
        email, stored_hash = result
        password_valid = await verify_password('admin123', stored_hash)
        print(f"Password for {email}: {password_valid}")
    else:
        print("Admin user not found!")
        return

    # Test 2: Direct user lookup with SQLAlchemy
    print("\n=== DIRECT USER LOOKUP TEST ===")
    db_gen = get_db()
    db = next(db_gen)
    try:
        # Find user by email
        user = db.query(User).filter(User.email == 'admin@test.com').first()
        if user:
            print(f"User found: {user.email}, Type: {user.user_type}, Active: {user.is_active}")

            # Test password verification
            password_valid = await verify_password('admin123', user.password_hash)
            print(f"Password valid: {password_valid}")

            if password_valid:
                # Test 3: Token creation and verification
                print("\n=== TOKEN CREATION TEST ===")
                token_data = {"sub": str(user.id)}
                access_token = create_access_token(token_data)
                print(f"Created token: {access_token[:50]}...")

                # Verify token
                decoded = decode_access_token(access_token)
                print(f"Decoded token: {decoded}")

                return {
                    'user_found': True,
                    'password_valid': password_valid,
                    'token_created': bool(access_token),
                    'token_decoded': bool(decoded),
                    'user_id': str(user.id),
                    'user_type': str(user.user_type)
                }
        else:
            print("User not found in database!")
            return {'user_found': False}

    except Exception as e:
        print(f"Error during user lookup: {e}")
        return {'error': str(e)}
    finally:
        db.close()

async def test_curl_simulation():
    """Simulate the exact curl request to identify the issue"""
    import json
    from fastapi.testclient import TestClient
    from app.main import app

    print("\n=== FASTAPI TEST CLIENT SIMULATION ===")

    client = TestClient(app)

    # Test the login endpoint
    login_data = {
        "email": "admin@test.com",
        "password": "admin123"
    }

    try:
        response = client.post("/api/v1/auth/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")

        if response.status_code == 200:
            print("✅ Login successful!")
            return response.json()
        else:
            print("❌ Login failed!")
            return {"error": response.text, "status_code": response.status_code}

    except Exception as e:
        print(f"Error during test client request: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    print("Starting simple authentication tests...")

    # Run async tests
    result = asyncio.run(test_simple_auth())
    print(f"\nDirect Auth Test Result: {result}")

    # Run FastAPI test client simulation
    result2 = asyncio.run(test_curl_simulation())
    print(f"\nFastAPI Test Result: {result2}")