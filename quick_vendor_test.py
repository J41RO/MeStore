#!/usr/bin/env python3
"""
Quick Vendor Registration Test
============================
Simple test to verify basic functionality after fixes
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_basic_registration():
    """Test basic auth registration"""
    register_data = {
        "email": "quicktest@mestore.com",
        "password": "QuickTest123!",
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/auth/register",
        json=register_data
    )

    print(f"Registration Status: {response.status_code}")
    if response.text:
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        except:
            print(f"Raw response: {response.text}")

    return response.status_code in [200, 201]

def test_vendedores_endpoint():
    """Test vendedores endpoint availability"""
    test_data = {
        "email": "vendor.test@mestore.com",
        "password": "VendorTest123!",
        "nombre": "Test",
        "apellido": "Vendor",
        "cedula": "12345678",
        "telefono": "+573001234567"
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/vendedores/registro",
        json=test_data
    )

    print(f"Vendedores Status: {response.status_code}")
    if response.text:
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        except:
            print(f"Raw response: {response.text}")

    return response.status_code in [200, 201]

def main():
    print("🚀 Quick Vendor Registration Test")
    print("=" * 40)

    print("1. Testing basic auth registration...")
    reg_success = test_basic_registration()
    print(f"   Result: {'✅ PASS' if reg_success else '❌ FAIL'}")
    print()

    print("2. Testing vendedores endpoint...")
    vend_success = test_vendedores_endpoint()
    print(f"   Result: {'✅ PASS' if vend_success else '❌ FAIL'}")
    print()

    overall = reg_success and vend_success
    print(f"Overall: {'✅ PASS' if overall else '❌ FAIL'}")

if __name__ == "__main__":
    main()