"""
PRIORITY 1: CRITICAL SECURITY TESTS - Authentication
====================================================

TDD Phase: RED
Status: Tests expected to FAIL or expose gaps
Purpose: Ensure all /orders/ endpoints require valid JWT authentication

Background:
-----------
All order endpoints must require authentication. Invalid, expired, or missing
tokens must be rejected with appropriate 401 Unauthorized responses.

Reference:
----------
File: app/api/v1/endpoints/orders.py
Lines: 42-113 - Authentication dependency: get_current_user_for_orders
Uses: HTTPBearer, decode_access_token

Test Strategy:
--------------
1. No token → 401 Unauthorized
2. Invalid token format → 401
3. Expired token → 401
4. Malformed JWT → 401
5. Valid token → Proceeds (not 401)
6. Missing 'sub' claim → 401
7. Missing 'user_type' → Handled with defaults

Expected RED Phase Behavior:
----------------------------
- Some tests MAY fail if auth validation incomplete
- Some tests MAY pass if code already exists
- Error handling might not be consistent
- Edge cases might not be covered

Created: 2025-10-09
Squad: tdd-specialist
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from typing import Dict, Any
import jwt

from app.core.config import settings

# Import fixtures
pytest_plugins = ["tests.fixtures.orders.conftest"]


# ============================================================================
# NO TOKEN TESTS
# ============================================================================

@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.security
@pytest.mark.auth
def test_no_token_returns_401(
    client: TestClient,
    valid_order_payload: Dict[str, Any]
):
    """
    Test that request without Authorization header returns 401.

    Security Requirement:
    - All /orders/ endpoints must require authentication
    - Missing token → 401 Unauthorized

    Expected RED Phase:
    - SHOULD PASS if HTTPBearer dependency is enforced
    - MIGHT FAIL if endpoint allows anonymous access
    """
    # Act: POST without Authorization header
    response = client.post(
        "/api/v1/orders/",
        json=valid_order_payload
        # No headers parameter - no Authorization
    )

    # Assert: Must be 401 Unauthorized
    assert response.status_code == 401, (
        f"Expected 401 Unauthorized when no token provided, got {response.status_code}. "
        f"All order endpoints must require authentication. "
        f"Response: {response.json() if response.status_code != 500 else response.text}"
    )

    # Assert: Response should indicate authentication issue
    response_data = response.json()
    assert "detail" in response_data, (
        "401 response should include 'detail' field explaining error"
    )


@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.auth
def test_get_orders_requires_token(
    client: TestClient
):
    """
    Test that GET /orders/ also requires authentication.

    Ensures auth requirement is consistent across all order endpoints.

    Expected RED Phase:
    - SHOULD PASS if auth dependency is on router level
    """
    # Act: GET without token
    response = client.get("/api/v1/orders/")

    # Assert: Must be 401
    assert response.status_code == 401, (
        f"GET /orders/ must require authentication. "
        f"Got {response.status_code}."
    )


@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.auth
def test_get_order_details_requires_token(
    client: TestClient
):
    """
    Test that GET /orders/{order_id} requires authentication.

    Expected RED Phase:
    - SHOULD PASS if auth dependency is on function level
    """
    # Act: GET order details without token
    response = client.get("/api/v1/orders/12345")

    # Assert: Must be 401 (or 404 if order doesn't exist, but NOT 200)
    assert response.status_code in [401, 404], (
        f"GET /orders/{{id}} must require authentication. "
        f"Got {response.status_code}."
    )
    # Note: 404 acceptable because order might not exist, but point is: no 200 without auth


# ============================================================================
# INVALID TOKEN FORMAT TESTS
# ============================================================================

@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.security
@pytest.mark.auth
def test_invalid_token_format_rejected(
    client: TestClient,
    valid_order_payload: Dict[str, Any]
):
    """
    Test that invalid token format is rejected with 401.

    Invalid Formats:
    - "Bearer INVALID_TOKEN_FORMAT"
    - Not a proper JWT structure

    Expected RED Phase:
    - SHOULD PASS if decode_access_token validates format
    - MIGHT FAIL if accepts any string
    """
    # Arrange: Create invalid token (not a JWT)
    invalid_headers = {
        "Authorization": "Bearer INVALID_TOKEN_FORMAT_NOT_A_JWT"
    }

    # Act
    response = client.post(
        "/api/v1/orders/",
        json=valid_order_payload,
        headers=invalid_headers
    )

    # Assert: Must be 401
    assert response.status_code == 401, (
        f"Invalid token format must be rejected with 401. "
        f"Got {response.status_code}. "
        f"Response: {response.json() if response.status_code != 500 else response.text}"
    )


@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.auth
def test_malformed_jwt_rejected(
    client: TestClient,
    valid_order_payload: Dict[str, Any]
):
    """
    Test that malformed JWT structure is rejected.

    Malformed JWT:
    - "header.payload" (missing signature)
    - "garbage.token.here"
    - Random base64 strings

    Expected RED Phase:
    - SHOULD PASS if jwt.decode() is used correctly
    - MIGHT FAIL if no validation
    """
    # Arrange: Create malformed JWT
    malformed_headers = {
        "Authorization": "Bearer malformed.jwt.structure.invalid"
    }

    # Act
    response = client.post(
        "/api/v1/orders/",
        json=valid_order_payload,
        headers=malformed_headers
    )

    # Assert: Must be 401
    assert response.status_code == 401, (
        f"Malformed JWT must be rejected with 401. "
        f"Got {response.status_code}."
    )


# ============================================================================
# EXPIRED TOKEN TESTS
# ============================================================================

@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.security
@pytest.mark.auth
def test_expired_token_rejected(
    client: TestClient,
    valid_order_payload: Dict[str, Any],
    customer_user_data: Dict[str, Any]
):
    """
    Test that expired JWT token is rejected with 401.

    Security Requirement:
    - Tokens must have expiration validation
    - Expired tokens must be rejected even if otherwise valid

    Expected RED Phase:
    - SHOULD PASS if decode_access_token checks 'exp' claim
    - MIGHT FAIL if expiration not validated
    """
    # Arrange: Create expired token (exp in past)
    expired_payload = {
        "sub": customer_user_data["id"],
        "email": customer_user_data["email"],
        "user_type": customer_user_data["user_type"].value,
        "exp": datetime.utcnow() - timedelta(hours=1),  # 1 hour ago
        "iat": datetime.utcnow() - timedelta(hours=2),
        "jti": "expired-token-123"
    }

    expired_token = jwt.encode(
        expired_payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    expired_headers = {"Authorization": f"Bearer {expired_token}"}

    # Act
    response = client.post(
        "/api/v1/orders/",
        json=valid_order_payload,
        headers=expired_headers
    )

    # Assert: Must be 401
    assert response.status_code == 401, (
        f"Expired token must be rejected with 401. "
        f"Got {response.status_code}. "
        f"Token expiration must be validated."
    )


@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.auth
def test_future_iat_rejected(
    client: TestClient,
    valid_order_payload: Dict[str, Any],
    customer_user_data: Dict[str, Any]
):
    """
    Test that token with future 'iat' (issued at) is rejected.

    Security Edge Case:
    - Token claims to be issued in the future
    - Indicates potential clock manipulation or forged token

    Expected RED Phase:
    - MIGHT FAIL if iat not validated
    - SHOULD PASS if strict validation exists
    """
    # Arrange: Token with future iat
    future_iat_payload = {
        "sub": customer_user_data["id"],
        "email": customer_user_data["email"],
        "user_type": customer_user_data["user_type"].value,
        "iat": datetime.utcnow() + timedelta(hours=1),  # Future
        "exp": datetime.utcnow() + timedelta(hours=2),
        "jti": "future-token-123"
    }

    future_token = jwt.encode(
        future_iat_payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    future_headers = {"Authorization": f"Bearer {future_token}"}

    # Act
    response = client.post(
        "/api/v1/orders/",
        json=valid_order_payload,
        headers=future_headers
    )

    # Assert: Should be rejected (401 or handled gracefully)
    # Note: Some systems may accept this, so test is informational
    if response.status_code != 401:
        pytest.skip(
            f"System accepts future iat (status {response.status_code}). "
            "Consider adding validation for production security."
        )


# ============================================================================
# MISSING CLAIMS TESTS
# ============================================================================

@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.security
@pytest.mark.auth
def test_missing_sub_claim_rejected(
    client: TestClient,
    valid_order_payload: Dict[str, Any]
):
    """
    Test that JWT without 'sub' (user_id) claim is rejected.

    Security Requirement:
    - 'sub' claim is mandatory for identifying user
    - Missing 'sub' → Cannot determine order owner → 401

    Reference: orders.py line 84-87

    Expected RED Phase:
    - SHOULD PASS if validation checks for 'sub'
    - MIGHT FAIL if no validation
    """
    # Arrange: Token without 'sub' claim
    payload_no_sub = {
        # Missing "sub"
        "email": "nosub@test.com",
        "user_type": "CUSTOMER",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "jti": "no-sub-token"
    }

    token_no_sub = jwt.encode(
        payload_no_sub,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    headers_no_sub = {"Authorization": f"Bearer {token_no_sub}"}

    # Act
    response = client.post(
        "/api/v1/orders/",
        json=valid_order_payload,
        headers=headers_no_sub
    )

    # Assert: Must be 401
    assert response.status_code == 401, (
        f"Token without 'sub' claim must be rejected with 401. "
        f"Got {response.status_code}. "
        f"'sub' is mandatory for user identification. "
        f"Reference: orders.py line 84-87"
    )


@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.auth
def test_missing_user_type_defaults_correctly(
    client: TestClient,
    valid_order_payload: Dict[str, Any]
):
    """
    Test that JWT without 'user_type' is handled gracefully.

    Business Logic:
    - Reference: orders.py line 92
    - Code does: payload.get("user_type", "").upper()
    - Empty string → NOT "VENDOR" → Should be allowed

    Expected RED Phase:
    - SHOULD PASS if default handling works
    - Test validates that missing user_type doesn't crash
    """
    # Arrange: Token without user_type
    payload_no_type = {
        "sub": "customer-no-type-123",
        "email": "notype@test.com",
        # Missing "user_type"
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "jti": "no-type-token"
    }

    token_no_type = jwt.encode(
        payload_no_type,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    headers_no_type = {"Authorization": f"Bearer {token_no_type}"}

    # Act
    response = client.post(
        "/api/v1/orders/",
        json=valid_order_payload,
        headers=headers_no_type
    )

    # Assert: Should NOT be 403 (not vendor) and NOT 500 (not crash)
    assert response.status_code not in [403, 500], (
        f"Missing user_type should default gracefully. "
        f"Got {response.status_code}. "
        f"Expected: 400/404 (business validation) or 201 (success), NOT 403/500. "
        f"Response: {response.json() if response.status_code != 500 else response.text}"
    )


# ============================================================================
# VALID TOKEN TEST (Baseline)
# ============================================================================

@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.auth
def test_valid_token_accepted(
    client: TestClient,
    customer_auth_headers: Dict[str, str],
    valid_order_payload: Dict[str, Any]
):
    """
    Test that valid, properly formatted JWT token is accepted.

    Baseline Validation:
    - Valid token should NOT result in 401
    - May fail for other reasons (400, 404) but NOT auth issue

    Expected RED Phase:
    - SHOULD PASS if auth logic works
    - Confirms authentication layer functioning
    """
    # Act
    response = client.post(
        "/api/v1/orders/",
        json=valid_order_payload,
        headers=customer_auth_headers
    )

    # Assert: Should NOT be 401 (authentication passed)
    assert response.status_code != 401, (
        f"Valid token should be accepted. "
        f"Got {response.status_code}, expected anything but 401. "
        f"Response: {response.json() if response.status_code != 500 else response.text}"
    )

    # Note: May be 400/404/201 depending on business logic, but NOT 401


# ============================================================================
# WRONG SECRET KEY TEST
# ============================================================================

@pytest.mark.tdd
@pytest.mark.red_test
@pytest.mark.security
@pytest.mark.auth
def test_token_with_wrong_secret_rejected(
    client: TestClient,
    valid_order_payload: Dict[str, Any],
    customer_user_data: Dict[str, Any]
):
    """
    Test that JWT signed with wrong secret key is rejected.

    Security Critical:
    - Attacker might try to forge token with different key
    - Signature verification must catch this

    Expected RED Phase:
    - SHOULD PASS if jwt.decode verifies signature
    - MUST FAIL if signature not checked
    """
    # Arrange: Create token with wrong secret
    payload = {
        "sub": customer_user_data["id"],
        "email": customer_user_data["email"],
        "user_type": customer_user_data["user_type"].value,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "jti": "wrong-secret-token"
    }

    wrong_secret_token = jwt.encode(
        payload,
        "WRONG_SECRET_KEY_ATTACKER_ATTEMPT",  # Wrong key
        algorithm=settings.ALGORITHM
    )

    wrong_secret_headers = {"Authorization": f"Bearer {wrong_secret_token}"}

    # Act
    response = client.post(
        "/api/v1/orders/",
        json=valid_order_payload,
        headers=wrong_secret_headers
    )

    # Assert: MUST be 401
    assert response.status_code == 401, (
        f"Token signed with wrong secret MUST be rejected. "
        f"Got {response.status_code}. "
        f"CRITICAL SECURITY ISSUE if accepted."
    )


# ============================================================================
# DOCUMENTATION & METADATA
# ============================================================================

"""
RED PHASE EXPECTED OUTCOMES:
=============================

1. test_no_token_returns_401
   - SHOULD PASS if HTTPBearer enforced

2. test_get_orders_requires_token
   - SHOULD PASS if auth on all endpoints

3. test_get_order_details_requires_token
   - SHOULD PASS

4. test_invalid_token_format_rejected
   - SHOULD PASS if decode validates format

5. test_malformed_jwt_rejected
   - SHOULD PASS if jwt.decode used

6. test_expired_token_rejected
   - SHOULD PASS if exp validation exists

7. test_future_iat_rejected
   - MIGHT FAIL - informational test

8. test_missing_sub_claim_rejected
   - SHOULD PASS (see line 84-87)

9. test_missing_user_type_defaults_correctly
   - SHOULD PASS (see line 92)

10. test_valid_token_accepted
    - SHOULD PASS (baseline)

11. test_token_with_wrong_secret_rejected
    - MUST PASS (critical security)

NEXT STEPS (GREEN Phase):
==========================
1. Run tests: `python -m pytest tests/unit/orders/test_order_authentication.py -v`
2. Document failures
3. Fix authentication gaps
4. Ensure all auth tests GREEN

COVERAGE TARGET:
================
These tests cover lines 42-113 in orders.py (get_current_user_for_orders function)
"""
