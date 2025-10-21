"""
Detailed Error Investigation for Payment Endpoints
==================================================

This script investigates the 500 errors in detail
"""

import requests
import json


def investigate_errors():
    """Investigate detailed error responses"""

    base_url = "http://192.168.1.137:8000/api/v1"

    # Authenticate
    auth_response = requests.post(
        f"{base_url}/auth/admin-login",
        json={
            "email": "admin@mestocker.com",
            "password": "Admin123456"
        }
    )

    if auth_response.status_code != 200:
        print("❌ Authentication failed")
        return

    token = auth_response.json().get("access_token")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    print("=" * 80)
    print("DETAILED ERROR INVESTIGATION")
    print("=" * 80)

    # Test 1: PayU Credit Card with detailed error
    print("\n1. PayU Credit Card - Full Response:")
    print("-" * 80)

    try:
        response = requests.post(
            f"{base_url}/payments/process/payu",
            json={
                "order_id": "1",
                "amount": 5000000,
                "currency": "COP",
                "payment_method": "CREDIT_CARD",
                "payer_email": "test@example.com",
                "payer_full_name": "Test User",
                "payer_phone": "+573001234567",
                "card_number": "4111111111111111",
                "card_expiration_date": "2025/12",
                "card_security_code": "123",
                "card_holder_name": "TEST USER",
                "installments": 1
            },
            headers=headers,
            timeout=30
        )

        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response Body:")
        print(json.dumps(response.json() if response.status_code < 500 else {"raw": response.text}, indent=2))

    except Exception as e:
        print(f"Error: {str(e)}")

    # Test 2: Efecty Code Generation
    print("\n\n2. Efecty Code Generation - Full Response:")
    print("-" * 80)

    try:
        response = requests.post(
            f"{base_url}/payments/process/efecty",
            json={
                "order_id": "1",
                "amount": 5000000,
                "customer_email": "test@example.com",
                "expiration_hours": 72
            },
            headers=headers,
            timeout=30
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json() if response.status_code < 500 else {"raw": response.text}, indent=2))

    except Exception as e:
        print(f"Error: {str(e)}")

    # Test 3: Check if PayU service is configured
    print("\n\n3. Checking Payment Methods Endpoint:")
    print("-" * 80)

    try:
        response = requests.get(
            f"{base_url}/payments/methods",
            timeout=30
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json() if response.status_code < 500 else {"raw": response.text}, indent=2))

    except Exception as e:
        print(f"Error: {str(e)}")

    # Test 4: Check payment config endpoint
    print("\n\n4. Checking Payment Config Endpoint:")
    print("-" * 80)

    try:
        response = requests.get(
            f"{base_url}/payments/config",
            timeout=30
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json() if response.status_code < 500 else {"raw": response.text}, indent=2))

    except Exception as e:
        print(f"Error: {str(e)}")

    # Test 5: Root payments endpoint
    print("\n\n5. Checking Root Payments Endpoint:")
    print("-" * 80)

    try:
        response = requests.get(
            f"{base_url}/payments/",
            timeout=30
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json() if response.status_code < 500 else {"raw": response.text}, indent=2))

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    investigate_errors()
