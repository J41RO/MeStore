#!/usr/bin/env python3
import json
import jwt
import httpx
import asyncio

async def debug_jwt():
    client = httpx.AsyncClient()
    try:
        # Login
        response = await client.post(
            "http://192.168.1.137:8000/api/v1/auth/login",
            json={"email": "vendor@test.com", "password": "vendor123"},
            headers={"Content-Type": "application/json", "Origin": "http://192.168.1.137:5173"}
        )

        if response.status_code == 200:
            data = response.json()
            token = data['access_token']

            print('Raw token response:')
            print(json.dumps(data, indent=2))
            print()

            print('Decoded JWT payload:')
            decoded = jwt.decode(token, options={'verify_signature': False})
            print(json.dumps(decoded, indent=2))

            # Test /me endpoint
            print('\nTesting /me endpoint:')
            me_response = await client.get(
                "http://192.168.1.137:8000/api/v1/auth/me",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Origin": "http://192.168.1.137:5173"
                }
            )
            print(f"Status: {me_response.status_code}")
            print(f"Response: {me_response.text}")

        else:
            print(f"Login failed: {response.status_code}")
            print(response.text)

    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(debug_jwt())