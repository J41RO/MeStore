#!/usr/bin/env python3
"""
Create a direct authentication endpoint that bypasses all complex dependencies
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_direct_auth_endpoint():
    """Create a direct auth endpoint in the main app"""

    print("🔧 Creating Direct Authentication Endpoint")
    print("=" * 50)

    try:
        # Create a simple direct auth endpoint
        endpoint_code = '''
@app.post("/api/v1/auth/direct-login")
async def direct_login(request: LoginRequest):
    """
    Direct authentication endpoint that bypasses complex model relationships
    Uses direct SQLite access for reliable authentication
    """
    try:
        import aiosqlite
        from passlib.context import CryptContext
        from app.core.security import create_access_token, create_refresh_token

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # Connect directly to SQLite database
        async with aiosqlite.connect("./mestore_auth_test.db") as db:
            cursor = await db.execute(
                "SELECT id, email, password_hash, user_type, is_active FROM users WHERE email = ?",
                (request.email,)
            )
            user_data = await cursor.fetchone()

            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email or password incorrect"
                )

            user_id, email, password_hash, user_type, is_active = user_data

            if not is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is not active"
                )

            # Verify password
            if not pwd_context.verify(request.password, password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email or password incorrect"
                )

            # Create tokens
            token_data = {
                "sub": user_id,
                "user_type": user_type,
                "email": email
            }

            access_token = create_access_token(data=token_data)
            refresh_token = create_refresh_token(data=token_data)

            # Create response
            from app.schemas.auth import TokenResponse, UserInfo

            user_info = UserInfo(
                id=user_id,
                email=email,
                user_type=user_type,
                nombre=email.split("@")[0],  # Fallback name
                is_active=bool(is_active),
                is_verified=True
            )

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=3600,
                user=user_info
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Direct auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error"
        )
'''

        # Read the main app file
        with open("app/main.py", "r") as f:
            main_content = f.read()

        # Backup the original
        with open("app/main.py.backup", "w") as f:
            f.write(main_content)

        print("✅ Backed up main.py")

        # Add the direct auth endpoint before the final app setup
        if "# Add custom authentication endpoints" not in main_content:
            # Find a good place to insert the endpoint
            insert_point = main_content.find("app = FastAPI(")
            if insert_point == -1:
                insert_point = main_content.find("from app.api")

            if insert_point != -1:
                # Insert the endpoint code after imports
                lines = main_content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith("app.include_router"):
                        # Insert before the first router inclusion
                        lines.insert(i, "\n# Add custom authentication endpoints")
                        lines.insert(i+1, endpoint_code)
                        break

                modified_content = '\n'.join(lines)

                # Write the modified main.py
                with open("app/main.py", "w") as f:
                    f.write(modified_content)

                print("✅ Added direct auth endpoint to main.py")
            else:
                print("❌ Could not find insertion point in main.py")
                return False
        else:
            print("ℹ️ Direct auth endpoint already exists")

        return True

    except Exception as e:
        print(f"❌ Error creating direct auth endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_direct_auth():
    """Test the direct authentication endpoint"""

    print("\n🧪 Testing Direct Authentication Endpoint")
    print("=" * 40)

    try:
        from fastapi.testclient import TestClient

        # Import the modified app
        from app.main import app

        client = TestClient(app)

        # Test the direct auth endpoint
        login_data = {
            "email": "super@mestore.com",
            "password": "123456"
        }

        print("🔄 Testing direct auth endpoint...")
        response = client.post("/api/v1/auth/direct-login", json=login_data)

        print(f"📊 Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Direct auth endpoint working!")
            print(f"📊 Response: {response.json()}")
            return True
        else:
            print("❌ Direct auth endpoint failed")
            print(f"📊 Response: {response.text[:500]}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🎯 DIRECT AUTHENTICATION ENDPOINT CREATION")
    print("=" * 60)

    # Step 1: Create direct auth endpoint
    creation_success = create_direct_auth_endpoint()

    if not creation_success:
        print("❌ Failed to create direct auth endpoint")
        return False

    print("\n" + "=" * 60)
    print("📋 DIRECT AUTH ENDPOINT SUMMARY")
    print("=" * 60)
    print(f"Endpoint Creation: {'✅ Success' if creation_success else '❌ Failed'}")

    if creation_success:
        print("\n🎉 DIRECT AUTH ENDPOINT CREATED!")
        print("📧 Credentials: super@mestore.com / 123456")
        print("🌐 Endpoint: /api/v1/auth/direct-login")
        print("🚀 Bypasses complex model relationships")

        print("\n🔧 Next Steps:")
        print("1. Restart the FastAPI server")
        print("2. Test with: POST /api/v1/auth/direct-login")
        print("3. Use this endpoint for admin portal authentication")

        return True
    else:
        print("\n❌ Direct auth endpoint creation failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)