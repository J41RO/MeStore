"""
Test shipping endpoints functionality
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.main import app
from app.models.order import Order, OrderStatus
from app.models.user import User
from sqlalchemy import select


@pytest.mark.asyncio
async def test_generate_tracking_number():
    """Test tracking number generation"""
    from app.api.v1.endpoints.shipping import generate_tracking_number

    tracking = generate_tracking_number()

    # Should start with SHIP-
    assert tracking.startswith("SHIP-")

    # Should have format SHIP-TIMESTAMP-RANDOM
    parts = tracking.split("-")
    assert len(parts) == 3
    assert parts[0] == "SHIP"
    assert len(parts[1]) == 14  # YYYYMMDDHHMMSS
    assert len(parts[2]) == 8   # 4 bytes hex = 8 chars


@pytest.mark.asyncio
async def test_assign_shipping_success(async_db_session, test_admin_user, test_confirmed_order):
    """Test successful shipping assignment"""
    client = TestClient(app)

    # Login as admin
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_admin_user.email,
            "password": "testpassword123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Assign shipping
    response = client.post(
        f"/api/v1/shipping/orders/{test_confirmed_order.id}/shipping",
        json={
            "courier": "Rappi",
            "estimated_days": 3
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response
    assert "tracking_number" in data
    assert data["tracking_number"].startswith("SHIP-")
    assert data["courier"] == "Rappi"
    assert data["order_status"] == "shipped"
    assert "estimated_delivery" in data

    # Verify order updated in DB
    result = await async_db_session.execute(
        select(Order).where(Order.id == test_confirmed_order.id)
    )
    order = result.scalar_one()

    assert order.tracking_number is not None
    assert order.courier == "Rappi"
    assert order.status == OrderStatus.SHIPPED
    assert order.estimated_delivery is not None
    assert order.shipping_events is not None
    assert len(order.shipping_events) == 1  # Initial event


@pytest.mark.asyncio
async def test_assign_shipping_already_assigned(async_db_session, test_admin_user, test_shipped_order):
    """Test cannot assign shipping twice"""
    client = TestClient(app)

    # Login as admin
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_admin_user.email,
            "password": "testpassword123"
        }
    )
    token = login_response.json()["access_token"]

    # Try to assign shipping to already shipped order
    response = client.post(
        f"/api/v1/shipping/orders/{test_shipped_order.id}/shipping",
        json={
            "courier": "Coordinadora",
            "estimated_days": 2
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert "already assigned" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_shipping_location_success(async_db_session, test_admin_user, test_shipped_order):
    """Test successful location update"""
    client = TestClient(app)

    # Login as admin
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_admin_user.email,
            "password": "testpassword123"
        }
    )
    token = login_response.json()["access_token"]

    # Update location
    response = client.patch(
        f"/api/v1/shipping/orders/{test_shipped_order.id}/shipping/location",
        json={
            "current_location": "Bogotá - Centro de distribución",
            "status": "at_warehouse",
            "description": "Paquete en bodega"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["current_location"] == "Bogotá - Centro de distribución"
    assert data["status"] == "at_warehouse"
    assert data["total_events"] > 1  # Should have initial + new event

    # Verify order updated in DB
    result = await async_db_session.execute(
        select(Order).where(Order.id == test_shipped_order.id)
    )
    order = result.scalar_one()

    assert len(order.shipping_events) > 1
    latest_event = order.shipping_events[-1]
    assert latest_event["location"] == "Bogotá - Centro de distribución"
    assert latest_event["status"] == "at_warehouse"


@pytest.mark.asyncio
async def test_update_shipping_delivered(async_db_session, test_admin_user, test_shipped_order):
    """Test marking as delivered updates order status"""
    client = TestClient(app)

    # Login as admin
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_admin_user.email,
            "password": "testpassword123"
        }
    )
    token = login_response.json()["access_token"]

    # Mark as delivered
    response = client.patch(
        f"/api/v1/shipping/orders/{test_shipped_order.id}/shipping/location",
        json={
            "current_location": "Dirección de entrega",
            "status": "delivered",
            "description": "Paquete entregado exitosamente"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["order_status"] == "delivered"

    # Verify order status updated
    result = await async_db_session.execute(
        select(Order).where(Order.id == test_shipped_order.id)
    )
    order = result.scalar_one()

    assert order.status == OrderStatus.DELIVERED
    assert order.delivered_at is not None


@pytest.mark.asyncio
async def test_get_shipping_tracking_authenticated(async_db_session, test_buyer_user, test_shipped_order):
    """Test buyer can view their own order tracking"""
    client = TestClient(app)

    # Login as buyer (owner of order)
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_buyer_user.email,
            "password": "buyerpassword123"
        }
    )
    token = login_response.json()["access_token"]

    # Get tracking
    response = client.get(
        f"/api/v1/shipping/orders/{test_shipped_order.id}/shipping/tracking",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["order_number"] == test_shipped_order.order_number
    assert data["shipping_info"]["tracking_number"] == test_shipped_order.tracking_number
    assert data["shipping_info"]["courier"] == test_shipped_order.courier
    assert len(data["shipping_info"]["shipping_events"]) > 0


@pytest.mark.asyncio
async def test_get_shipping_tracking_forbidden(async_db_session, test_buyer_user, test_shipped_order_other_buyer):
    """Test buyer cannot view other buyer's order"""
    client = TestClient(app)

    # Login as buyer
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_buyer_user.email,
            "password": "buyerpassword123"
        }
    )
    token = login_response.json()["access_token"]

    # Try to get tracking of another buyer's order
    response = client.get(
        f"/api/v1/shipping/orders/{test_shipped_order_other_buyer.id}/shipping/tracking",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_track_by_tracking_number_public(async_db_session, test_shipped_order):
    """Test public tracking by tracking number (no auth)"""
    client = TestClient(app)

    # Get tracking without authentication
    response = client.get(
        f"/api/v1/shipping/tracking/{test_shipped_order.tracking_number}"
    )

    assert response.status_code == 200
    data = response.json()

    assert data["order_number"] == test_shipped_order.order_number
    assert data["shipping_info"]["tracking_number"] == test_shipped_order.tracking_number

    # Verify sensitive info is hidden (partial address only)
    assert data["shipping_city"] == test_shipped_order.shipping_city
    assert data["shipping_state"] == test_shipped_order.shipping_state


# Fixtures

@pytest.fixture
async def test_confirmed_order(async_db_session, test_buyer_user):
    """Create a confirmed order for testing"""
    order = Order(
        order_number="ORD-TEST-001",
        buyer_id=test_buyer_user.id,
        status=OrderStatus.CONFIRMED,
        total_amount=100000,
        shipping_address="Test Address 123",
        shipping_city="Bogotá",
        shipping_state="Cundinamarca",
        shipping_name="Test Buyer",
        shipping_phone="1234567890"
    )
    async_db_session.add(order)
    await async_db_session.commit()
    await async_db_session.refresh(order)
    return order


@pytest.fixture
async def test_shipped_order(async_db_session, test_buyer_user):
    """Create a shipped order with tracking"""
    order = Order(
        order_number="ORD-TEST-002",
        buyer_id=test_buyer_user.id,
        status=OrderStatus.SHIPPED,
        total_amount=150000,
        shipping_address="Test Address 456",
        shipping_city="Medellín",
        shipping_state="Antioquia",
        shipping_name="Test Buyer",
        shipping_phone="1234567890",
        tracking_number="SHIP-20251003000000-TESTAAAA",
        courier="Rappi",
        estimated_delivery=datetime.now() + timedelta(days=2),
        shipping_events=[
            {
                "timestamp": datetime.now().isoformat(),
                "status": "in_transit",
                "location": "Origin warehouse",
                "description": "Package picked up"
            }
        ]
    )
    async_db_session.add(order)
    await async_db_session.commit()
    await async_db_session.refresh(order)
    return order


@pytest.fixture
async def test_buyer_user(async_db_session):
    """Create test buyer user"""
    from app.core.security import get_password_hash

    user = User(
        email="testbuyer@example.com",
        hashed_password=get_password_hash("buyerpassword123"),
        full_name="Test Buyer",
        is_active=True,
        is_superuser=False
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    return user
