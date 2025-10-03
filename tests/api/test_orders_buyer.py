"""
TDD Tests for Buyer Dashboard Order Endpoints
RED-GREEN-REFACTOR methodology

Tests for:
- GET /api/v1/orders/{order_id}/tracking - Get order tracking information
- PATCH /api/v1/orders/{order_id}/cancel - Cancel order with refund
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from decimal import Decimal
import uuid

from app.models.order import Order, OrderItem, OrderStatus
from app.models.user import User, UserType
from app.models.product import Product


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
async def test_user(async_session: AsyncSession):
    """Create test buyer user."""
    user = User(
        id=str(uuid.uuid4()),
        email="testbuyer@example.com",
        password_hash="$2b$12$test.hash.for.testing",
        nombre="John",
        apellido="Doe",
        user_type=UserType.BUYER,
        is_active=True
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture
async def second_user(async_session: AsyncSession):
    """Create second buyer user for ownership tests."""
    user = User(
        id=str(uuid.uuid4()),
        email="jane@example.com",
        password_hash="$2b$12$test.hash.for.testing",
        nombre="Jane",
        apellido="Smith",
        user_type=UserType.BUYER,
        is_active=True
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User):
    """Create authorization headers with mock token."""
    # Using mock token for testing - orders endpoint handles test scenario
    return {"Authorization": "Bearer mock-token"}


@pytest.fixture
async def test_order(async_session: AsyncSession, test_user: User):
    """Create test order for user."""
    order = Order(
        order_number="ORD-20251003-TEST001",
        buyer_id=test_user.id,
        subtotal=150000.0,
        tax_amount=28500.0,
        shipping_cost=15000.0,
        discount_amount=0.0,
        total_amount=193500.0,
        status=OrderStatus.PENDING,
        shipping_name="John Doe",
        shipping_phone="+57 300 1234567",
        shipping_address="Calle 123 #45-67",
        shipping_city="Bogotá",
        shipping_state="Cundinamarca",
        shipping_country="CO"
    )
    async_session.add(order)
    await async_session.commit()
    await async_session.refresh(order)
    return order


# ============================================================================
# RED PHASE TESTS - These should FAIL initially
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.tdd
@pytest.mark.red_test
async def test_get_order_tracking_unauthorized(async_client: AsyncClient):
    """
    RED TEST: Get tracking without authentication should return 401

    Expected behavior:
    - Endpoint exists
    - Returns 401 for unauthenticated requests
    """
    response = await async_client.get("/api/v1/orders/1/tracking")
    assert response.status_code in [401, 403]  # Either is acceptable for unauthenticated
    assert "error_message" in response.json() or "detail" in response.json()


@pytest.mark.asyncio
@pytest.mark.tdd
@pytest.mark.red_test
async def test_get_order_tracking_not_found(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """
    RED TEST: Get tracking for non-existent order should return 404

    Expected behavior:
    - Authenticated request
    - Order doesn't exist
    - Returns 404 Not Found
    """
    response = await async_client.get(
        "/api/v1/orders/999999/tracking",
        headers=auth_headers
    )
    assert response.status_code == 404
    assert "not found" in response.json().get("error_message", response.json().get("detail", "")).lower()


@pytest.mark.asyncio
@pytest.mark.tdd
@pytest.mark.red_test
async def test_get_order_tracking_forbidden_not_owner(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_user: User,
    second_user: User,
    test_order: Order,
    auth_headers: dict
):
    """
    RED TEST: Get tracking for another user's order should return 403

    Expected behavior:
    - Order exists but belongs to different user
    - Returns 403 Forbidden
    """
    # Create order for second_user
    order = Order(
        order_number="ORD-20251003-TEST002",
        buyer_id=second_user.id,
        subtotal=100000.0,
        tax_amount=19000.0,
        shipping_cost=15000.0,
        discount_amount=0.0,
        total_amount=134000.0,
        status=OrderStatus.PROCESSING,
        shipping_name="Jane Doe",
        shipping_phone="+57 300 9876543",
        shipping_address="Calle 456 #78-90",
        shipping_city="Medellín",
        shipping_state="Antioquia",
        shipping_country="CO"
    )
    async_session.add(order)
    await async_session.commit()
    await async_session.refresh(order)

    # Try to access with test_user's token (should fail)
    response = await async_client.get(
        f"/api/v1/orders/{order.id}/tracking",
        headers=auth_headers
    )
    assert response.status_code == 403
    assert "not authorized" in response.json().get("error_message", response.json().get("detail", "")).lower() or "forbidden" in response.json().get("error_message", response.json().get("detail", "")).lower()


@pytest.mark.asyncio
@pytest.mark.tdd
@pytest.mark.red_test
async def test_get_order_tracking_success(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """
    RED TEST: Get tracking for own order should return tracking information

    Expected behavior:
    - Order exists and belongs to current user
    - Returns 200 with tracking details
    - Includes: order_id, order_number, status, courier, tracking_number, etc.
    """
    # Create order with tracking info
    order = Order(
        order_number="ORD-20251003-TRACK01",
        buyer_id=test_user.id,
        subtotal=200000.0,
        tax_amount=38000.0,
        shipping_cost=0.0,  # Free shipping
        discount_amount=0.0,
        total_amount=238000.0,
        status=OrderStatus.SHIPPED,
        shipping_name="John Doe",
        shipping_phone="+57 300 1234567",
        shipping_address="Calle 123 #45-67",
        shipping_city="Bogotá",
        shipping_state="Cundinamarca",
        shipping_country="CO"
    )
    async_session.add(order)
    await async_session.commit()
    await async_session.refresh(order)

    response = await async_client.get(
        f"/api/v1/orders/{order.id}/tracking",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Validate response structure
    assert "order_id" in data
    assert "order_number" in data
    assert "status" in data
    assert data["order_number"] == "ORD-20251003-TRACK01"
    assert data["status"] == OrderStatus.SHIPPED.value


# ============================================================================
# ORDER CANCELLATION TESTS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.tdd
@pytest.mark.red_test
async def test_cancel_order_unauthorized(async_client: AsyncClient):
    """
    RED TEST: Cancel order without authentication should return 401
    """
    response = await async_client.patch(
        "/api/v1/orders/1/cancel",
        json={"reason": "Changed my mind", "refund_requested": True}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.tdd
@pytest.mark.red_test
async def test_cancel_order_not_found(
    async_client: AsyncClient,
    auth_headers: dict
):
    """
    RED TEST: Cancel non-existent order should return 404
    """
    response = await async_client.patch(
        "/api/v1/orders/999999/cancel",
        json={"reason": "Test cancellation", "refund_requested": True},
        headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.tdd
@pytest.mark.red_test
async def test_cancel_order_forbidden_not_owner(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_user: User,
    second_user: User,
    auth_headers: dict
):
    """
    RED TEST: Cancel another user's order should return 403
    """
    # Create order for second_user
    order = Order(
        order_number="ORD-20251003-CANCEL01",
        buyer_id=second_user.id,
        subtotal=100000.0,
        tax_amount=19000.0,
        shipping_cost=15000.0,
        discount_amount=0.0,
        total_amount=134000.0,
        status=OrderStatus.PENDING,
        shipping_name="Jane Doe",
        shipping_phone="+57 300 9876543",
        shipping_address="Calle 456 #78-90",
        shipping_city="Medellín",
        shipping_state="Antioquia",
        shipping_country="CO"
    )
    async_session.add(order)
    await async_session.commit()
    await async_session.refresh(order)

    response = await async_client.patch(
        f"/api/v1/orders/{order.id}/cancel",
        json={"reason": "Unauthorized cancel attempt", "refund_requested": True},
        headers=auth_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
@pytest.mark.tdd
@pytest.mark.red_test
async def test_cancel_order_invalid_status_already_shipped(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """
    RED TEST: Cannot cancel order that is already shipped

    Expected behavior:
    - Order status is SHIPPED
    - Returns 400 Bad Request
    - Error message indicates order cannot be cancelled
    """
    order = Order(
        order_number="ORD-20251003-SHIPPED01",
        buyer_id=test_user.id,
        subtotal=150000.0,
        tax_amount=28500.0,
        shipping_cost=15000.0,
        discount_amount=0.0,
        total_amount=193500.0,
        status=OrderStatus.SHIPPED,
        shipping_name="John Doe",
        shipping_phone="+57 300 1234567",
        shipping_address="Calle 123 #45-67",
        shipping_city="Bogotá",
        shipping_state="Cundinamarca",
        shipping_country="CO"
    )
    async_session.add(order)
    await async_session.commit()
    await async_session.refresh(order)

    response = await async_client.patch(
        f"/api/v1/orders/{order.id}/cancel",
        json={"reason": "Changed mind", "refund_requested": True},
        headers=auth_headers
    )

    assert response.status_code == 400
    assert "cannot be cancelled" in response.json().get("error_message", response.json().get("detail", "")).lower() or "already shipped" in response.json().get("error_message", response.json().get("detail", "")).lower()


@pytest.mark.asyncio
@pytest.mark.tdd
@pytest.mark.red_test
async def test_cancel_order_invalid_status_already_cancelled(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """
    RED TEST: Cannot cancel order that is already cancelled
    """
    order = Order(
        order_number="ORD-20251003-CANCELLED01",
        buyer_id=test_user.id,
        subtotal=100000.0,
        tax_amount=19000.0,
        shipping_cost=15000.0,
        discount_amount=0.0,
        total_amount=134000.0,
        status=OrderStatus.CANCELLED,
        shipping_name="John Doe",
        shipping_phone="+57 300 1234567",
        shipping_address="Calle 123 #45-67",
        shipping_city="Bogotá",
        shipping_state="Cundinamarca",
        shipping_country="CO"
    )
    async_session.add(order)
    await async_session.commit()
    await async_session.refresh(order)

    response = await async_client.patch(
        f"/api/v1/orders/{order.id}/cancel",
        json={"reason": "Double cancel attempt", "refund_requested": True},
        headers=auth_headers
    )

    assert response.status_code == 400
    assert "already cancelled" in response.json().get("error_message", response.json().get("detail", "")).lower()


@pytest.mark.asyncio
@pytest.mark.tdd
@pytest.mark.red_test
async def test_cancel_order_success_pending_status(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """
    RED TEST: Successfully cancel order with PENDING status

    Expected behavior:
    - Order status is PENDING
    - Returns 200 OK
    - Order status changed to CANCELLED
    - Cancellation reason recorded
    - Refund initiated
    """
    order = Order(
        order_number="ORD-20251003-TOCANCEL01",
        buyer_id=test_user.id,
        subtotal=120000.0,
        tax_amount=22800.0,
        shipping_cost=15000.0,
        discount_amount=0.0,
        total_amount=157800.0,
        status=OrderStatus.PENDING,
        shipping_name="John Doe",
        shipping_phone="+57 300 1234567",
        shipping_address="Calle 123 #45-67",
        shipping_city="Bogotá",
        shipping_state="Cundinamarca",
        shipping_country="CO"
    )
    async_session.add(order)
    await async_session.commit()
    await async_session.refresh(order)

    response = await async_client.patch(
        f"/api/v1/orders/{order.id}/cancel",
        json={
            "reason": "Changed my mind about purchase",
            "refund_requested": True
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Validate response structure
    assert "order_id" in data
    assert "status" in data
    assert "cancelled_at" in data
    assert "cancellation_reason" in data
    assert "refund_status" in data

    # Validate status change
    assert data["status"] == OrderStatus.CANCELLED.value
    assert data["cancellation_reason"] == "Changed my mind about purchase"
    assert data["refund_status"] in ["pending", "processing"]


@pytest.mark.asyncio
@pytest.mark.tdd
@pytest.mark.red_test
async def test_cancel_order_success_processing_status(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """
    RED TEST: Successfully cancel order with PROCESSING status

    Expected behavior:
    - Order status is PROCESSING
    - Returns 200 OK
    - Order cancelled successfully
    """
    order = Order(
        order_number="ORD-20251003-TOCANCEL02",
        buyer_id=test_user.id,
        subtotal=180000.0,
        tax_amount=34200.0,
        shipping_cost=15000.0,
        discount_amount=0.0,
        total_amount=229200.0,
        status=OrderStatus.PROCESSING,
        shipping_name="John Doe",
        shipping_phone="+57 300 1234567",
        shipping_address="Calle 123 #45-67",
        shipping_city="Bogotá",
        shipping_state="Cundinamarca",
        shipping_country="CO"
    )
    async_session.add(order)
    await async_session.commit()
    await async_session.refresh(order)

    response = await async_client.patch(
        f"/api/v1/orders/{order.id}/cancel",
        json={
            "reason": "Order taking too long to process",
            "refund_requested": True
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == OrderStatus.CANCELLED.value


@pytest.mark.asyncio
@pytest.mark.tdd
@pytest.mark.red_test
async def test_cancel_order_missing_reason(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """
    RED TEST: Cancel order without reason should return 422 validation error
    """
    order = Order(
        order_number="ORD-20251003-NOREASON",
        buyer_id=test_user.id,
        subtotal=100000.0,
        tax_amount=19000.0,
        shipping_cost=15000.0,
        discount_amount=0.0,
        total_amount=134000.0,
        status=OrderStatus.PENDING,
        shipping_name="John Doe",
        shipping_phone="+57 300 1234567",
        shipping_address="Calle 123 #45-67",
        shipping_city="Bogotá",
        shipping_state="Cundinamarca",
        shipping_country="CO"
    )
    async_session.add(order)
    await async_session.commit()
    await async_session.refresh(order)

    response = await async_client.patch(
        f"/api/v1/orders/{order.id}/cancel",
        json={"refund_requested": True},  # Missing reason
        headers=auth_headers
    )

    assert response.status_code == 422  # Pydantic validation error
