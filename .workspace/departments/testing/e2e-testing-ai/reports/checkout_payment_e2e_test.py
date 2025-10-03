#!/usr/bin/env python3
"""
E2E Testing Script for MeStore Checkout and Payment Flows
=========================================================

Tests all payment methods and checkout scenarios:
1. PayU Credit Card payment
2. PSE payment
3. Efecty cash payment
4. Admin Efecty confirmation

Author: E2E Testing AI
Date: 2025-10-02
Purpose: Comprehensive checkout and payment flow validation
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

# Test Configuration
BASE_URL = "http://192.168.1.137:8000"
FRONTEND_URL = "http://192.168.1.137:5173"

# Test Results Storage
test_results = []
errors_found = []
ux_issues = []

class TestResult:
    def __init__(self, test_name: str, status: str, details: str = "", response_data: Optional[Dict] = None):
        self.test_name = test_name
        self.status = status  # PASS, FAIL, SKIP
        self.details = details
        self.response_data = response_data
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            "test_name": self.test_name,
            "status": self.status,
            "details": self.details,
            "response_data": self.response_data,
            "timestamp": self.timestamp
        }

def log_test(test_name: str, status: str, details: str = "", response_data: Optional[Dict] = None):
    """Log test result"""
    result = TestResult(test_name, status, details, response_data)
    test_results.append(result)

    status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭️"
    print(f"{status_icon} {test_name}: {status}")
    if details:
        print(f"   Details: {details}")
    print()

def log_error(error_type: str, details: str, response: Optional[requests.Response] = None):
    """Log error found during testing"""
    error_info = {
        "type": error_type,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    if response:
        error_info["status_code"] = response.status_code
        error_info["response"] = response.text[:500]  # First 500 chars

    errors_found.append(error_info)
    print(f"🚨 ERROR: {error_type}")
    print(f"   {details}")
    if response:
        print(f"   Status: {response.status_code}")
    print()

def log_ux_issue(issue_type: str, details: str, severity: str = "MEDIUM"):
    """Log UX issue"""
    ux_issues.append({
        "type": issue_type,
        "details": details,
        "severity": severity,
        "timestamp": datetime.now().isoformat()
    })
    print(f"⚠️ UX ISSUE ({severity}): {issue_type}")
    print(f"   {details}")
    print()

# ====================================================================================
# TEST 1: CREATE TEST USER AND LOGIN
# ====================================================================================

def test_user_registration_and_login():
    """Test user registration and login flow"""
    print("=" * 80)
    print("TEST 1: USER REGISTRATION AND LOGIN")
    print("=" * 80)

    # Create test user
    test_user = {
        "email": f"e2e_test_{int(time.time())}@test.com",
        "password": "Test123456!",
        "full_name": "E2E Test User",
        "user_type": "buyer"
    }

    # Try to register
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 201 or response.status_code == 200:
            log_test("User Registration", "PASS", f"User created: {test_user['email']}", response.json())
        else:
            log_test("User Registration", "FAIL", f"Status: {response.status_code}", response.json())
            return None
    except Exception as e:
        log_error("User Registration Exception", str(e))
        return None

    # Try to login
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            },
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                log_test("User Login", "PASS", f"Token received", {"email": test_user["email"]})
                return {
                    "email": test_user["email"],
                    "token": token,
                    "user_id": data.get("user_id")
                }
            else:
                log_test("User Login", "FAIL", "No token in response", data)
                return None
        else:
            log_test("User Login", "FAIL", f"Status: {response.status_code}", response.json())
            return None
    except Exception as e:
        log_error("User Login Exception", str(e))
        return None

# ====================================================================================
# TEST 2: PRODUCT DISCOVERY AND CART
# ====================================================================================

def test_product_discovery_and_cart(auth_data: Dict):
    """Test product discovery and adding to cart"""
    print("=" * 80)
    print("TEST 2: PRODUCT DISCOVERY AND CART")
    print("=" * 80)

    headers = {
        "Authorization": f"Bearer {auth_data['token']}",
        "Content-Type": "application/json"
    }

    # Get available products
    try:
        response = requests.get(f"{BASE_URL}/api/v1/products/", params={"limit": 10})

        if response.status_code == 200:
            data = response.json()
            products = data.get("data", []) if isinstance(data, dict) else data

            if products and len(products) > 0:
                log_test("Product Discovery", "PASS", f"Found {len(products)} products", {"count": len(products)})

                # Select first product with stock
                selected_product = None
                for product in products:
                    if product.get("stock_disponible", 0) > 0:
                        selected_product = product
                        break

                if selected_product:
                    log_test("Product Selection", "PASS", f"Selected: {selected_product.get('name')}", {
                        "product_id": selected_product.get("id"),
                        "price": selected_product.get("precio_venta"),
                        "stock": selected_product.get("stock_disponible")
                    })
                    return [{"product_id": selected_product["id"], "quantity": 1}]
                else:
                    log_test("Product Selection", "FAIL", "No products with stock available")
                    return None
            else:
                log_test("Product Discovery", "FAIL", "No products found")
                return None
        else:
            log_error("Product Discovery Error", f"Status: {response.status_code}", response)
            return None
    except Exception as e:
        log_error("Product Discovery Exception", str(e))
        return None

# ====================================================================================
# TEST 3: CREATE ORDER
# ====================================================================================

def test_create_order(auth_data: Dict, cart_items: List[Dict]):
    """Test order creation with shipping info"""
    print("=" * 80)
    print("TEST 3: CREATE ORDER")
    print("=" * 80)

    headers = {
        "Authorization": f"Bearer {auth_data['token']}",
        "Content-Type": "application/json"
    }

    # Order data with CRITICAL shipping_state field
    order_data = {
        "items": cart_items,
        "shipping_name": "Juan E2E Test",
        "shipping_phone": "+57 300 1234567",
        "shipping_email": auth_data["email"],
        "shipping_address": "Calle 100 #45-67 Apto 302",
        "shipping_city": "Bogotá",
        "shipping_state": "Cundinamarca",  # CRITICAL FIELD
        "shipping_postal_code": "110111",
        "notes": "E2E Test Order - Please handle with care"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/orders/",
            json=order_data,
            headers=headers
        )

        if response.status_code in [200, 201]:
            data = response.json()
            order_info = data.get("data", data)

            # Validate shipping_state was included
            shipping_info = order_info.get("shipping_info", {})
            if "state" in shipping_info:
                log_test("Order Creation", "PASS", f"Order: {order_info.get('order_number')}", {
                    "order_id": order_info.get("id"),
                    "order_number": order_info.get("order_number"),
                    "total": order_info.get("total_amount"),
                    "shipping_state": shipping_info.get("state")
                })
                return order_info
            else:
                log_ux_issue(
                    "Missing shipping_state in response",
                    "Order created but shipping_state not in response - may cause frontend issues",
                    "HIGH"
                )
                return order_info
        elif response.status_code == 400:
            # Check if it's the shipping_state missing error
            error_data = response.json()
            error_detail = str(error_data.get("detail", ""))

            if "shipping_state" in error_detail.lower():
                log_error(
                    "CRITICAL: shipping_state validation error",
                    f"Backend requires shipping_state but frontend may not be sending it. Error: {error_detail}",
                    response
                )
            else:
                log_error("Order Creation Error", error_detail, response)
            return None
        else:
            log_error("Order Creation Error", f"Status: {response.status_code}", response)
            return None
    except Exception as e:
        log_error("Order Creation Exception", str(e))
        return None

# ====================================================================================
# TEST 4: PAYU CREDIT CARD PAYMENT
# ====================================================================================

def test_payu_credit_card_payment(auth_data: Dict, order_data: Dict):
    """Test PayU credit card payment flow"""
    print("=" * 80)
    print("TEST 4: PAYU CREDIT CARD PAYMENT")
    print("=" * 80)

    headers = {
        "Authorization": f"Bearer {auth_data['token']}",
        "Content-Type": "application/json"
    }

    # PayU Credit Card payment request
    payment_data = {
        "order_id": str(order_data["id"]),
        "amount": int(order_data["total_amount"] * 100),  # Convert to cents
        "currency": "COP",
        "payment_method": "CREDIT_CARD",
        "payer_email": auth_data["email"],
        "payer_full_name": "Juan E2E Test",
        "payer_phone": "+573001234567",
        # Test credit card (PayU test card)
        "card_number": "4111111111111111",
        "card_expiration_date": "2025/12",
        "card_security_code": "123",
        "card_holder_name": "JUAN TEST",
        "installments": 1,
        "response_url": f"{FRONTEND_URL}/payment-result"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/payments/process/payu",
            json=payment_data,
            headers=headers
        )

        if response.status_code in [200, 201]:
            data = response.json()
            log_test("PayU Credit Card Payment", "PASS", f"State: {data.get('state')}", {
                "transaction_id": data.get("transaction_id"),
                "state": data.get("state"),
                "message": data.get("message")
            })
            return data
        else:
            log_error("PayU Payment Error", f"Status: {response.status_code}", response)
            return None
    except Exception as e:
        log_error("PayU Payment Exception", str(e))
        return None

# ====================================================================================
# TEST 5: PSE PAYMENT
# ====================================================================================

def test_pse_payment(auth_data: Dict, order_data: Dict):
    """Test PSE bank transfer payment flow"""
    print("=" * 80)
    print("TEST 5: PSE PAYMENT")
    print("=" * 80)

    headers = {
        "Authorization": f"Bearer {auth_data['token']}",
        "Content-Type": "application/json"
    }

    # First, get available PSE banks
    try:
        response = requests.get(f"{BASE_URL}/api/v1/payments/methods")

        if response.status_code == 200:
            methods_data = response.json()
            pse_banks = methods_data.get("pse_banks", [])

            if pse_banks:
                log_test("PSE Banks Discovery", "PASS", f"Found {len(pse_banks)} banks", {
                    "count": len(pse_banks),
                    "first_bank": pse_banks[0] if pse_banks else None
                })
            else:
                log_ux_issue("No PSE Banks Available", "PSE enabled but no banks in list", "HIGH")
                return None
        else:
            log_error("Payment Methods Error", f"Status: {response.status_code}", response)
            return None
    except Exception as e:
        log_error("Payment Methods Exception", str(e))
        return None

    # PSE payment request
    payment_data = {
        "order_id": str(order_data["id"]),
        "amount": int(order_data["total_amount"] * 100),
        "currency": "COP",
        "payment_method": "PSE",
        "payer_email": auth_data["email"],
        "payer_full_name": "Juan E2E Test",
        "payer_phone": "+573001234567",
        # PSE specific fields
        "pse_bank_code": pse_banks[0]["financial_institution_code"] if pse_banks else "1007",
        "pse_user_type": "N",  # Natural person
        "pse_identification_type": "CC",  # Cédula de Ciudadanía
        "pse_identification_number": "1234567890",
        "response_url": f"{FRONTEND_URL}/payment-result"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/payments/process/payu",
            json=payment_data,
            headers=headers
        )

        if response.status_code in [200, 201]:
            data = response.json()

            # PSE requires redirect
            if data.get("payment_url"):
                log_test("PSE Payment", "PASS", "Redirect URL generated", {
                    "transaction_id": data.get("transaction_id"),
                    "state": data.get("state"),
                    "payment_url": data.get("payment_url")
                })
            else:
                log_ux_issue("PSE No Redirect URL", "PSE payment processed but no redirect URL", "HIGH")

            return data
        else:
            log_error("PSE Payment Error", f"Status: {response.status_code}", response)
            return None
    except Exception as e:
        log_error("PSE Payment Exception", str(e))
        return None

# ====================================================================================
# TEST 6: EFECTY CASH PAYMENT
# ====================================================================================

def test_efecty_payment(auth_data: Dict, order_data: Dict):
    """Test Efecty cash payment code generation"""
    print("=" * 80)
    print("TEST 6: EFECTY CASH PAYMENT")
    print("=" * 80)

    headers = {
        "Authorization": f"Bearer {auth_data['token']}",
        "Content-Type": "application/json"
    }

    # Efecty payment request
    payment_data = {
        "order_id": str(order_data["id"]),
        "amount": int(order_data["total_amount"] * 100),
        "customer_email": auth_data["email"],
        "customer_phone": "+573001234567",
        "expiration_hours": 72  # 3 days
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/payments/process/efecty",
            json=payment_data,
            headers=headers
        )

        if response.status_code in [200, 201]:
            data = response.json()

            # Validate Efecty response completeness
            required_fields = ["payment_code", "barcode_data", "instructions", "expires_at"]
            missing_fields = [f for f in required_fields if f not in data]

            if not missing_fields:
                log_test("Efecty Payment Code Generation", "PASS", f"Code: {data.get('payment_code')}", {
                    "payment_code": data.get("payment_code"),
                    "amount": data.get("amount"),
                    "expires_at": data.get("expires_at"),
                    "points_count": data.get("points_count")
                })

                # Check instructions quality
                instructions = data.get("instructions", "")
                if len(instructions) < 50:
                    log_ux_issue("Efecty Instructions Too Short", "Instructions may not be clear enough", "MEDIUM")

                return data
            else:
                log_error("Efecty Incomplete Response", f"Missing fields: {', '.join(missing_fields)}", response)
                return None
        else:
            log_error("Efecty Payment Error", f"Status: {response.status_code}", response)
            return None
    except Exception as e:
        log_error("Efecty Payment Exception", str(e))
        return None

# ====================================================================================
# TEST 7: ADMIN EFECTY CONFIRMATION
# ====================================================================================

def test_admin_efecty_confirmation(efecty_data: Dict):
    """Test admin Efecty payment confirmation flow"""
    print("=" * 80)
    print("TEST 7: ADMIN EFECTY CONFIRMATION")
    print("=" * 80)

    # Login as admin
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/admin-login",
            json={
                "email": "admin@mestocker.com",
                "password": "Admin123456"
            },
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            admin_data = response.json()
            admin_token = admin_data.get("access_token")

            if admin_token:
                log_test("Admin Login", "PASS", "Admin authenticated")
            else:
                log_error("Admin Login Error", "No token in admin response", response)
                return None
        else:
            log_error("Admin Login Error", f"Status: {response.status_code}", response)
            return None
    except Exception as e:
        log_error("Admin Login Exception", str(e))
        return None

    # Confirm Efecty payment
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }

    confirmation_data = {
        "payment_code": efecty_data.get("payment_code"),
        "paid_amount": efecty_data.get("amount"),
        "receipt_number": "EFEC-TEST-001"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/payments/efecty/confirm",
            json=confirmation_data,
            headers=headers
        )

        if response.status_code in [200, 201]:
            data = response.json()
            log_test("Admin Efecty Confirmation", "PASS", f"Order: {data.get('order_id')}", {
                "order_id": data.get("order_id"),
                "payment_code": data.get("payment_code"),
                "message": data.get("message")
            })
            return data
        else:
            log_error("Efecty Confirmation Error", f"Status: {response.status_code}", response)
            return None
    except Exception as e:
        log_error("Efecty Confirmation Exception", str(e))
        return None

# ====================================================================================
# MAIN TEST EXECUTION
# ====================================================================================

def generate_report():
    """Generate comprehensive test report"""
    print("\n" + "=" * 80)
    print("E2E TEST REPORT - CHECKOUT AND PAYMENT FLOWS")
    print("=" * 80)
    print(f"Generated: {datetime.now().isoformat()}")
    print()

    # Summary
    total_tests = len(test_results)
    passed = len([t for t in test_results if t.status == "PASS"])
    failed = len([t for t in test_results if t.status == "FAIL"])
    skipped = len([t for t in test_results if t.status == "SKIP"])

    print(f"SUMMARY:")
    print(f"  Total Tests: {total_tests}")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  ⏭️ Skipped: {skipped}")
    print()

    # Errors
    if errors_found:
        print(f"ERRORS FOUND: {len(errors_found)}")
        for i, error in enumerate(errors_found, 1):
            print(f"  {i}. {error['type']}")
            print(f"     {error['details']}")
            print()
    else:
        print("✅ No errors found!")
        print()

    # UX Issues
    if ux_issues:
        print(f"UX ISSUES: {len(ux_issues)}")
        for i, issue in enumerate(ux_issues, 1):
            severity_icon = "🔴" if issue["severity"] == "HIGH" else "🟡" if issue["severity"] == "MEDIUM" else "🟢"
            print(f"  {i}. {severity_icon} {issue['type']} ({issue['severity']})")
            print(f"     {issue['details']}")
            print()
    else:
        print("✅ No UX issues found!")
        print()

    # Detailed Results
    print("DETAILED TEST RESULTS:")
    print("-" * 80)
    for i, result in enumerate(test_results, 1):
        status_icon = "✅" if result.status == "PASS" else "❌" if result.status == "FAIL" else "⏭️"
        print(f"{i}. {status_icon} {result.test_name} - {result.status}")
        if result.details:
            print(f"   {result.details}")
        print()

    # Save report to file
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total_tests,
            "passed": passed,
            "failed": failed,
            "skipped": skipped
        },
        "tests": [t.to_dict() for t in test_results],
        "errors": errors_found,
        "ux_issues": ux_issues
    }

    report_file = f"/home/admin-jairo/MeStore/.workspace/departments/testing/e2e-testing-ai/reports/checkout_payment_e2e_report_{int(time.time())}.json"
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)

    print(f"📄 Full report saved to: {report_file}")
    print()

def main():
    """Main test execution"""
    print("\n" + "🚀" * 40)
    print("MESTORE E2E CHECKOUT AND PAYMENT TESTING")
    print("🚀" * 40)
    print()

    # Test 1: User Registration and Login
    auth_data = test_user_registration_and_login()
    if not auth_data:
        print("❌ Cannot proceed without authentication")
        generate_report()
        return

    # Test 2: Product Discovery and Cart
    cart_items = test_product_discovery_and_cart(auth_data)
    if not cart_items:
        print("❌ Cannot proceed without cart items")
        generate_report()
        return

    # Test 3: Create Order (this will be used for all payment methods)
    order_data = test_create_order(auth_data, cart_items)
    if not order_data:
        print("❌ Cannot proceed without order")
        generate_report()
        return

    # Test 4: PayU Credit Card Payment (using a separate order)
    order_data_2 = test_create_order(auth_data, cart_items)
    if order_data_2:
        test_payu_credit_card_payment(auth_data, order_data_2)

    # Test 5: PSE Payment (using another separate order)
    order_data_3 = test_create_order(auth_data, cart_items)
    if order_data_3:
        test_pse_payment(auth_data, order_data_3)

    # Test 6: Efecty Payment
    efecty_data = test_efecty_payment(auth_data, order_data)

    # Test 7: Admin Efecty Confirmation
    if efecty_data:
        test_admin_efecty_confirmation(efecty_data)

    # Generate final report
    generate_report()

    print("=" * 80)
    print("✅ E2E TESTING COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    main()
