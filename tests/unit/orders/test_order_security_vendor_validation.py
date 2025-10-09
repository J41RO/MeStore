"""
PRIORITY 1: CRITICAL SECURITY TESTS - VENDOR Validation
=======================================================

TDD Phase: RED
Status: Tests expected to FAIL initially
Purpose: Ensure VENDOR users cannot create orders (403, not 500)

Background:
-----------
Vendors are sellers, NOT buyers. They should be blocked from creating orders
with a clear 403 Forbidden response, not a 500 Internal Server Error.

Reference:
----------
File: app/api/v1/endpoints/orders.py
Line: 96 - VENDOR validation exists but needs comprehensive testing
Fix applied: 2025-10-09 (Security patch)

Test Strategy:
--------------
1. Test VENDOR token → 403 Forbidden (CRITICAL)
2. Test clear error message for vendors
3. Test CUSTOMER/BUYER tokens → Allowed
4. Test ADMIN/SUPERUSER tokens → Allowed
5. Test multiple vendor attempts all rejected
6. Test vendor vs customer distinction is enforced

Expected RED Phase Behavior:
----------------------------
- Some tests MAY fail if validation logic incomplete
- Some tests MAY pass if code already exists
- Error codes might be wrong (500 instead of 403)
- Error messages might be unclear

Created: 2025-10-09
Squad: tdd-specialist
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from decimal import Decimal
from typing import Dict, Any

# Use fixtures from main conftest.py
# pytest_plugins removed - using auto-discovery


# ============================================================================
# VENDOR REJECTION TESTS - Core Security
# ============================================================================

@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.security
@pytest.mark.critical
@pytest.mark.asyncio
async def test_vendor_token_rejected_with_403(
    async_client: AsyncClient,
    auth_headers_vendor: Dict[str, str]
):
    """
    CRITICAL: Vendor token must be rejected with 403 Forbidden.

    Security Requirement:
    - Vendors are sellers, NOT buyers
    - Must return 403 (Forbidden), NOT 500 (Internal Server Error)
    - Must not process order at all

    Reference: orders.py line 96

    Expected RED Phase:
    - Test might PASS if security fix is complete
    - Test might FAIL if fix returns wrong status code
    - Test might FAIL if fix is missing
    """
    # Arrange: Create minimal valid order payload
    order_payload = {
        "items": [{"product_id": "test-product-123", "quantity": 2}],
        "shipping_name": "Test User",
        "shipping_phone": "3001234567",
        "shipping_address": "Test Address 123",
        "shipping_city": "Bogotá",
        "shipping_state": "Cundinamarca"
    }

    # Act: Attempt to create order with VENDOR token
    response = await async_client.post(
        "/api/v1/orders/",
        json=order_payload,
        headers=auth_headers_vendor
    )

    # Assert: Must be 403 Forbidden, not 500 or 201
    assert response.status_code == 403, (
        f"Expected 403 Forbidden for VENDOR, got {response.status_code}. "
        f"Vendors should not be able to create orders. "
        f"Response: {response.json() if response.status_code != 500 else response.text}"
    )

    # Assert: Response should have error detail
    response_data = response.json()
    # App uses custom error handler - check for error_message or detail
    assert "error_message" in response_data or "detail" in response_data, (
        f"Response missing error field. Got keys: {list(response_data.keys())}"
    )


@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.security
def test_vendor_receives_clear_error_message(
    client: TestClient,
    auth_headers_vendor: Dict[str, str],
    sample_product_data: Dict[str, Any]
):
    """
    Test that VENDOR receives clear, actionable error message.

    Requirements:
    - Error message must explain WHY vendor cannot create orders
    - Message should guide vendor to correct action
    - No stack traces or technical details exposed

    Expected RED Phase:
    - Test might FAIL if error message is generic
    - Test might FAIL if message not user-friendly
    """
    # Act
    response = client.post(
        "/api/v1/orders/",
        json=sample_product_data,
        headers=auth_headers_vendor
    )

    # Assert: Status must be 403
    assert response.status_code == 403

    # Assert: Error message must be clear and specific
    response_data = response.json()
    # App uses custom error handler - get error_message or detail
    error_detail = response_data.get("error_message", response_data.get("detail", "")).lower()

    # Check for key phrases
    assert "vendor" in error_detail, (
        f"Error message should mention 'vendor' to clarify who is blocked. Got: '{error_detail}'"
    )
    assert "cannot" in error_detail or "not allowed" in error_detail, (
        f"Error message should clearly state the prohibition. Got: '{error_detail}'"
    )
    assert "customer" in error_detail or "buyer" in error_detail, (
        f"Error message should explain who CAN create orders. Got: '{error_detail}'"
    )

    # Assert: No stack traces or technical errors exposed
    assert "traceback" not in error_detail, (
        "Error message should not expose stack traces"
    )
    assert "exception" not in error_detail, (
        "Error message should not expose internal exceptions"
    )


@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.security
def test_customer_token_allowed(
    client: TestClient,
    auth_headers_buyer: Dict[str, str],
    sample_product_data: Dict[str, Any]
):
    """
    Test that CUSTOMER token is allowed to create orders.

    Baseline Validation:
    - CUSTOMER user_type should be allowed
    - Should NOT return 403
    - Should proceed to order validation (may fail for other reasons)

    Expected RED Phase:
    - Test might PASS if customer logic exists
    - Test might FAIL with 400/404 due to missing products (acceptable)
    - Test should NOT fail with 403
    """
    # Act
    response = client.post(
        "/api/v1/orders/",
        json=sample_product_data,
        headers=auth_headers_buyer
    )

    # Assert: Should NOT be 403 (customer is allowed)
    assert response.status_code != 403, (
        f"CUSTOMER should be allowed to create orders, got 403. "
        f"Response: {response.json()}"
    )

    # Note: Test doesn't check for 201 because order might fail for other reasons
    # (missing products, insufficient stock, etc.) which is acceptable
    # The key assertion is: NOT 403


@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.security
def test_buyer_token_allowed(
    client: TestClient,
    sample_product_data: Dict[str, Any]
):
    """
    Test that BUYER token is allowed to create orders.

    Context: BUYER is another valid customer type

    Expected RED Phase:
    - Similar to customer test
    - Should NOT return 403
    """
    # Arrange: Create BUYER token
    from app.core.security import create_access_token

    buyer_user_data = {
        "sub": "test-buyer-123",
        "email": "buyer@test.com",
        "nombre": "Test Buyer",
        "user_type": "BUYER",
        "is_active": True,
        "is_verified": True
    }
    buyer_token = create_access_token(data=buyer_user_data)
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}

    # Act
    response = client.post(
        "/api/v1/orders/",
        json=sample_product_data,
        headers=buyer_headers
    )

    # Assert: Should NOT be 403
    assert response.status_code != 403, (
        f"BUYER should be allowed to create orders, got 403. "
        f"Response: {response.json()}"
    )


@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.security
def test_admin_token_allowed(
    client: TestClient,
    auth_headers_admin: Dict[str, str],
    sample_product_data: Dict[str, Any]
):
    """
    Test that ADMIN/SUPERUSER token is allowed to create orders.

    Business Rule:
    - Admins should be able to create orders (for customer support, testing)

    Expected RED Phase:
    - Should NOT return 403
    """
    # Act
    response = client.post(
        "/api/v1/orders/",
        json=sample_product_data,
        headers=auth_headers_admin
    )

    # Assert: Should NOT be 403
    assert response.status_code != 403, (
        f"ADMIN/SUPERUSER should be allowed to create orders, got 403. "
        f"Response: {response.json()}"
    )


@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.security
def test_multiple_vendor_attempts_all_rejected(
    client: TestClient,
    sample_product_data: Dict[str, Any]
):
    """
    Test that ALL vendor attempts are consistently rejected.

    Security Validation:
    - Multiple different vendor tokens
    - All should get 403
    - No inconsistency in enforcement

    Expected RED Phase:
    - Test might FAIL if validation is inconsistent
    - All attempts should be blocked equally
    """
    from app.core.security import create_access_token

    # Create 3 different vendor tokens
    vendor_tokens = []
    for i in range(3):
        vendor_data = {
            "sub": f"vendor-{i}",
            "email": f"vendor{i}@test.com",
            "nombre": f"Vendor {i}",
            "user_type": "VENDOR",
            "is_active": True,
            "is_verified": True
        }
        token = create_access_token(data=vendor_data)
        vendor_tokens.append(token)

    # Act: Try to create order with each vendor token
    results = []
    for token in vendor_tokens:
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            "/api/v1/orders/",
            json=sample_product_data,
            headers=headers
        )
        results.append({
            "status_code": response.status_code,
            "response": response.json() if response.status_code != 500 else response.text
        })

    # Assert: ALL must be 403
    for idx, result in enumerate(results):
        assert result["status_code"] == 403, (
            f"Vendor {idx} got status {result['status_code']}, expected 403. "
            f"All vendors must be consistently blocked. "
            f"Response: {result['response']}"
        )

    # Assert: All got same error treatment
    status_codes = [r["status_code"] for r in results]
    assert len(set(status_codes)) == 1, (
        f"Inconsistent handling of vendor attempts: {status_codes}. "
        f"All vendors should be treated identically."
    )


# ============================================================================
# EDGE CASES - Vendor Security
# ============================================================================

@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.security
def test_vendor_cannot_bypass_with_modified_payload(
    client: TestClient,
    auth_headers_vendor: Dict[str, str],
    sample_product_data: Dict[str, Any]
):
    """
    Test that VENDOR cannot bypass restriction by modifying request payload.

    Attack Scenario:
    - Vendor tries to add "user_type": "CUSTOMER" in payload
    - System must use JWT token data, NOT request payload

    Expected RED Phase:
    - Test might FAIL if server trusts client data
    - Should still return 403 based on JWT, not payload
    """
    # Arrange: Modify payload to claim customer type
    malicious_payload = sample_product_data.copy()
    malicious_payload["user_type"] = "CUSTOMER"  # Attempted bypass
    malicious_payload["buyer_type"] = "BUYER"    # Another attempt

    # Act
    response = client.post(
        "/api/v1/orders/",
        json=malicious_payload,
        headers=auth_headers_vendor  # Still vendor JWT
    )

    # Assert: Must still be 403 (JWT determines user type, not payload)
    assert response.status_code == 403, (
        f"VENDOR cannot bypass restriction by modifying payload. "
        f"Got status {response.status_code}. "
        f"System must validate based on JWT token, not request data."
    )


@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.security
def test_vendor_validation_case_insensitive(
    client: TestClient,
    sample_product_data: Dict[str, Any]
):
    """
    Test that vendor validation is case-insensitive.

    Security Edge Case:
    - "VENDOR", "vendor", "Vendor", "VeNdOr" should all be blocked
    - Prevent case-based bypass attempts

    Expected RED Phase:
    - Test might FAIL if validation is case-sensitive
    - All variations should be blocked
    """
    from app.core.security import create_access_token

    # Test different case variations
    case_variations = ["VENDOR", "vendor", "Vendor", "VeNdOr", "vEnDoR"]

    for user_type_variant in case_variations:
        # Create token with case variant
        vendor_data = {
            "sub": f"vendor-{user_type_variant}",
            "email": f"vendor_{user_type_variant}@test.com",
            "nombre": "Test Vendor",
            "user_type": user_type_variant,
            "is_active": True,
            "is_verified": True
        }
        token = create_access_token(data=vendor_data)
        headers = {"Authorization": f"Bearer {token}"}

        # Act
        response = client.post(
            "/api/v1/orders/",
            json=sample_product_data,
            headers=headers
        )

        # Assert
        assert response.status_code == 403, (
            f"user_type='{user_type_variant}' should be blocked. "
            f"Got status {response.status_code}. "
            f"Validation must be case-insensitive."
        )


# ============================================================================
# DOCUMENTATION & METADATA
# ============================================================================

"""
RED PHASE EXPECTED OUTCOMES:
=============================

1. test_vendor_token_rejected_with_403
   - SHOULD PASS if security fix complete (line 96 applied)
   - SHOULD FAIL if returns 500 instead of 403

2. test_vendor_receives_clear_error_message
   - MIGHT FAIL if error message is generic
   - SHOULD PASS if fix includes detailed message

3. test_customer_token_allowed
   - MIGHT FAIL with 400/404 (acceptable - validation working)
   - SHOULD NOT fail with 403

4. test_buyer_token_allowed
   - Similar to customer test

5. test_admin_token_allowed
   - Similar to customer test

6. test_multiple_vendor_attempts_all_rejected
   - Tests consistency of enforcement
   - SHOULD PASS if fix is robust

7. test_vendor_cannot_bypass_with_modified_payload
   - Tests JWT validation vs payload data
   - SHOULD PASS if using JWT correctly

8. test_vendor_validation_case_insensitive
   - Tests case handling
   - SHOULD PASS if using .upper() (as per line 92)

NEXT STEPS (GREEN Phase):
==========================
1. Run tests: `python -m pytest tests/unit/orders/test_order_security_vendor_validation.py -v`
2. Document which tests PASS/FAIL
3. Fix failing tests one by one
4. Ensure all tests GREEN before moving to next priority

COVERAGE TARGET:
================
These tests cover lines 89-102 in orders.py (VENDOR validation block)
"""
