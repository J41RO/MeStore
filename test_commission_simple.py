#!/usr/bin/env python3
"""
Simple Commission API Test - Direct testing without complex middleware chain
"""

import os
import sys
import asyncio
from fastapi.testclient import TestClient

# Set testing environment
os.environ["TESTING"] = "1"

# Add the app directory to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app

def test_commission_endpoint_basic():
    """Test basic commission endpoint access without authentication"""
    client = TestClient(app, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })

    # Test the health endpoint first to ensure basic API is working
    response = client.get("/health")
    assert response.status_code == 200

    # Test commission endpoint without auth (should return 401)
    response = client.get("/api/v1/commissions/")
    print(f"Commission endpoint response: {response.status_code}")
    print(f"Response body: {response.text}")

    # Should return 401 for authentication required
    assert response.status_code == 401

if __name__ == "__main__":
    test_commission_endpoint_basic()
    print("✅ Basic commission API test passed!")
