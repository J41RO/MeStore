#!/usr/bin/env python3
"""
Simple direct authentication test to verify the superuser works
"""

import asyncio
import aiosqlite
from passlib.context import CryptContext

async def test_simple_auth():
    """Test authentication directly with the database"""

    print("🔄 Testing Direct Authentication")
    print("=" * 40)

    try:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # Connect to the database
        async with aiosqlite.connect("./mestore_auth_test.db") as db:
            # Query the user
            cursor = await db.execute(
                "SELECT password_hash, user_type, is_active FROM users WHERE email = ?",
                ("super@mestore.com",)
            )
            user_data = await cursor.fetchone()

            if not user_data:
                print("❌ User not found")
                return False

            password_hash, user_type, is_active = user_data

            # Test password verification
            if pwd_context.verify("123456", password_hash):
                print("✅ Authentication successful!")
                print(f"   Email: super@mestore.com")
                print(f"   Type: {user_type}")
                print(f"   Active: {bool(is_active)}")
                return True
            else:
                print("❌ Password verification failed")
                return False

    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

async def create_simple_login_api():
    """Create a simple FastAPI app with just the login endpoint"""

    print("\n🔄 Creating Simple Login API")
    print("=" * 40)

    try:
        # Create a simple FastAPI app
        simple_app_code = '''
from fastapi import FastAPI, HTTPException
from passlib.context import CryptContext
import aiosqlite
from pydantic import BaseModel

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    user_type: str = None

@app.post("/simple-login", response_model=LoginResponse)
async def simple_login(login_data: LoginRequest):
    """Simple authentication endpoint without complex dependencies"""

    try:
        async with aiosqlite.connect("./mestore_auth_test.db") as db:
            cursor = await db.execute(
                "SELECT password_hash, user_type, is_active FROM users WHERE email = ?",
                (login_data.email,)
            )
            user_data = await cursor.fetchone()

            if not user_data:
                raise HTTPException(status_code=401, detail="User not found")

            password_hash, user_type, is_active = user_data

            if not is_active:
                raise HTTPException(status_code=401, detail="User not active")

            if pwd_context.verify(login_data.password, password_hash):
                return LoginResponse(
                    success=True,
                    message="Authentication successful",
                    user_type=user_type
                )
            else:
                raise HTTPException(status_code=401, detail="Invalid password")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Simple MeStore Auth"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
'''

        with open("simple_auth_app.py", "w") as f:
            f.write(simple_app_code)

        print("✅ Simple auth app created: simple_auth_app.py")

        # Test the simple app
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        # Import and test the simple app
        import sys
        sys.path.insert(0, ".")

        # Create test client for the simple app
        exec(simple_app_code)
        client = TestClient(app)

        # Test health endpoint
        response = client.get("/health")
        print(f"📊 Health endpoint: {response.status_code}")

        # Test login endpoint
        login_data = {
            "email": "super@mestore.com",
            "password": "123456"
        }

        response = client.post("/simple-login", json=login_data)
        print(f"📊 Simple login: {response.status_code}")
        print(f"📊 Response: {response.json()}")

        if response.status_code == 200:
            print("✅ Simple authentication API working!")
            return True
        else:
            print("❌ Simple authentication API failed")
            return False

    except Exception as e:
        print(f"❌ Simple API creation failed: {e}")
        return False

async def main():
    print("🎯 SIMPLE AUTHENTICATION TEST")
    print("=" * 60)

    # Test 1: Direct authentication
    auth_success = await test_simple_auth()

    # Test 2: Simple API
    api_success = await create_simple_login_api()

    print("\n" + "=" * 60)
    print("📋 SIMPLE AUTH TEST SUMMARY")
    print("=" * 60)
    print(f"Direct Authentication: {'✅ Success' if auth_success else '❌ Failed'}")
    print(f"Simple API Test: {'✅ Success' if api_success else '❌ Failed'}")

    if auth_success and api_success:
        print("\n🎉 SIMPLE AUTHENTICATION WORKING!")
        print("📧 Credentials: super@mestore.com / 123456")
        print("🚀 Start simple server: python simple_auth_app.py")
        print("🌐 Test at: http://localhost:8001/simple-login")
        return True
    else:
        print("\n❌ Authentication test failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)