#!/usr/bin/env python3
"""
Direct test of the admin login endpoint using FastAPI test client
"""
import asyncio
from fastapi.testclient import TestClient
from app.main import app

def test_admin_login_endpoint():
    """Test the admin login endpoint directly"""
    print("🔧 Testing Admin Login API Endpoint Directly...")
    print("=" * 60)

    # Create test client
    client = TestClient(app)

    # Test credentials
    login_data = {
        "email": "super@mestore.com",
        "password": "123456"
    }

    print(f"📧 Testing email: {login_data['email']}")
    print(f"🔑 Testing password: {login_data['password']}")
    print()

    try:
        print("🔄 Making POST request to /api/v1/auth/admin-login...")

        response = client.post(
            "/api/v1/auth/admin-login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )

        print(f"📊 Response status code: {response.status_code}")
        print(f"📋 Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("✅ AUTHENTICATION API SUCCESSFUL!")
            response_data = response.json()
            print("📋 Response data:")
            for key, value in response_data.items():
                if key == 'access_token':
                    print(f"   {key}: {value[:20]}...")
                elif key == 'refresh_token':
                    print(f"   {key}: {value[:20]}...")
                else:
                    print(f"   {key}: {value}")
            return True
        else:
            print("❌ AUTHENTICATION API FAILED!")
            print("📋 Response content:")
            print(f"   {response.text}")
            return False

    except Exception as e:
        print(f"💥 ERROR during API test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_admin_login_endpoint()

    if success:
        print("\n🎉 Admin Login API is WORKING!")
        exit(0)
    else:
        print("\n🚨 Admin Login API is NOT working!")
        exit(1)