#!/usr/bin/env python3
"""
Test authentication endpoints with fixed passwords
"""

import asyncio
import json
import aiohttp

async def test_login(email, password):
    """Test login endpoint with given credentials"""

    login_data = {
        "email": email,
        "password": password
    }

    print(f"🔐 Testing login: {email} / {password}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://localhost:8000/api/v1/auth/login',
                json=login_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                status = response.status
                text = await response.text()

                print(f"  📊 Status: {status}")

                if status == 200:
                    data = json.loads(text)
                    print(f"  ✅ LOGIN SUCCESS!")
                    print(f"  🎫 Token: {data.get('access_token', 'N/A')[:20]}...")
                    print(f"  👤 User type: {data.get('token_type', 'N/A')}")
                    return True
                else:
                    print(f"  ❌ LOGIN FAILED")
                    print(f"  📄 Response: {text}")
                    return False

    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

async def test_all_logins():
    """Test login for all test users"""

    print("🚀 Testing authentication endpoints...")
    print("=" * 60)

    # Check if server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/docs') as response:
                if response.status == 200:
                    print("✅ Server is running at http://localhost:8000")
                else:
                    print("⚠️  Server responded but might have issues")
    except Exception as e:
        print("❌ Server is not running or not accessible")
        print("   Start the server with: uvicorn app.main:app --reload")
        return False

    print("=" * 60)

    # Test credentials
    test_credentials = [
        ("admin@test.com", "admin123"),
        ("vendor@test.com", "vendor123"),
        ("buyer@test.com", "buyer123")
    ]

    results = []
    for email, password in test_credentials:
        result = await test_login(email, password)
        results.append((email, result))
        print()

    print("=" * 60)
    print("📊 SUMMARY:")
    for email, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"  {status} {email}")

    return all(result for _, result in results)

if __name__ == "__main__":
    success = asyncio.run(test_all_logins())
    if success:
        print("\n🎉 All authentication tests passed!")
    else:
        print("\n❌ Some authentication tests failed")
    exit(0 if success else 1)