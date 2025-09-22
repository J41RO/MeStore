#!/usr/bin/env python3
"""
Test WebSocket authentication for real-time analytics
"""
import asyncio
import websockets
import json
from app.core.security import create_access_token
from datetime import timedelta

async def test_websocket_auth():
    """Test WebSocket authentication with JWT token"""

    # Create a test token for a vendor
    token_data = {
        'sub': 'f47ac10b-58cc-4372-a567-0e02b2c3d479',  # Test vendor ID
        'user_type': 'VENDOR'
    }
    token = create_access_token(token_data, expires_delta=timedelta(hours=1))
    print(f"✅ Generated test token: {token[:50]}...")

    # WebSocket URL with authentication
    url = f"ws://192.168.1.137:8001/api/v1/analytics/ws/vendor/analytics?token={token}&vendor_id=f47ac10b-58cc-4372-a567-0e02b2c3d479"

    try:
        print(f"🔌 Connecting to WebSocket: {url}")

        async with websockets.connect(url) as websocket:
            print("✅ WebSocket connected successfully!")

            # Wait for initial messages
            try:
                # Expect connection confirmation
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📨 Received message: {data['type']}")

                if data['type'] == 'connection_status':
                    print(f"✅ Connection confirmed: {data['data']}")

                # Expect analytics data
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📊 Received analytics: {data['type']}")

                if data['type'] == 'analytics_update':
                    print(f"✅ Analytics data received successfully!")
                    print(f"   - Revenue: {data['data']['metrics']['revenue']['current'] if data['data']['metrics'] else 'N/A'}")
                    print(f"   - Orders: {data['data']['metrics']['orders']['current'] if data['data']['metrics'] else 'N/A'}")

                # Send a ping to test bidirectional communication
                ping_message = {
                    "type": "ping",
                    "timestamp": "2025-09-19T20:00:00Z"
                }
                await websocket.send(json.dumps(ping_message))
                print("📤 Sent ping message")

                # Wait for pong response
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📥 Received response: {data['type']}")

                if data['type'] == 'connection_status' and data['data'].get('type') == 'pong':
                    print("✅ Ping-pong successful!")

            except asyncio.TimeoutError:
                print("⏰ Timeout waiting for messages")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")

    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed: {e}")
        if e.code == 4001:
            print("🔒 Authentication error - token invalid or missing")
        elif e.code == 4003:
            print("🚫 Access denied - vendor account required")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

async def test_websocket_without_auth():
    """Test WebSocket without authentication (should fail)"""
    url = "ws://192.168.1.137:8001/api/v1/analytics/ws/vendor/analytics"

    try:
        print(f"\n🔌 Testing connection without auth: {url}")
        async with websockets.connect(url) as websocket:
            print("❌ Should not connect without auth!")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"✅ Correctly rejected without auth: code {e.code} - {e.reason}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

async def test_websocket_invalid_token():
    """Test WebSocket with invalid token (should fail)"""
    invalid_token = "invalid.token.here"
    url = f"ws://192.168.1.137:8001/api/v1/analytics/ws/vendor/analytics?token={invalid_token}"

    try:
        print(f"\n🔌 Testing connection with invalid token: {url}")
        async with websockets.connect(url) as websocket:
            print("❌ Should not connect with invalid token!")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"✅ Correctly rejected invalid token: code {e.code} - {e.reason}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🧪 WebSocket Authentication Test Suite")
    print("=" * 50)

    asyncio.run(test_websocket_auth())
    asyncio.run(test_websocket_without_auth())
    asyncio.run(test_websocket_invalid_token())

    print("\n✅ WebSocket authentication tests completed!")