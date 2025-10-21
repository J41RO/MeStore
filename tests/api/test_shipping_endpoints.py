"""
Test shipping endpoints functionality
"""
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from app.main import app
from app.models.order import Order, OrderStatus
from app.models.user import User, UserType
from sqlalchemy import select
from app.core.security import get_password_hash
from app.core.types import generate_uuid


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
async def test_assign_shipping_success(async_db_session, test_confirmed_order, auth_headers_admin, async_client):
    """Test successful shipping assignment"""
    from sqlalchemy.orm import undefer
    client = async_client

    # Assign shipping
    response = await client.post(
        f"/api/v1/shipping/orders/{test_confirmed_order.id}/shipping",
        json={
            "courier": "Rappi",
            "estimated_days": 3
        },
        headers=auth_headers_admin
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response
    assert "tracking_number" in data
    assert data["tracking_number"].startswith("SHIP-")
    assert data["courier"] == "Rappi"
    assert data["order_status"] == "shipped"
    assert "estimated_delivery" in data

    # Verify order updated in DB - Must undefer deferred columns in async context
    result = await async_db_session.execute(
        select(Order)
        .where(Order.id == test_confirmed_order.id)
        .options(
            undefer(Order.tracking_number),
            undefer(Order.courier),
            undefer(Order.estimated_delivery),
            undefer(Order.shipping_events)
        )
    )
    order = result.scalar_one()

    assert order.tracking_number is not None
    assert order.courier == "Rappi"
    assert order.status == OrderStatus.SHIPPED
    assert order.estimated_delivery is not None
    assert order.shipping_events is not None
    assert len(order.shipping_events) == 1  # Initial event


@pytest.mark.asyncio
async def test_assign_shipping_already_assigned(async_db_session, test_shipped_order, auth_headers_admin, async_client):
    """Test cannot assign shipping twice"""
    client = async_client

    # Try to assign shipping to already shipped order
    response = await client.post(
        f"/api/v1/shipping/orders/{test_shipped_order.id}/shipping",
        json={
            "courier": "Coordinadora",
            "estimated_days": 2
        },
        headers=auth_headers_admin
    )

    assert response.status_code == 400
    assert "already assigned" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_shipping_location_success(async_db_session, test_shipped_order, auth_headers_admin, async_client):
    """Test successful location update"""
    from sqlalchemy.orm import undefer
    client = async_client

    # Update location
    response = await client.patch(
        f"/api/v1/shipping/orders/{test_shipped_order.id}/shipping/location",
        json={
            "current_location": "Bogotá - Centro de distribución",
            "status": "at_warehouse",
            "description": "Paquete en bodega"
        },
        headers=auth_headers_admin
    )

    assert response.status_code == 200
    data = response.json()

    assert data["current_location"] == "Bogotá - Centro de distribución"
    assert data["status"] == "at_warehouse"
    assert data["total_events"] > 1  # Should have initial + new event

    # Verify order updated in DB - Must undefer deferred columns in async context
    result = await async_db_session.execute(
        select(Order)
        .where(Order.id == test_shipped_order.id)
        .options(
            undefer(Order.tracking_number),
            undefer(Order.courier),
            undefer(Order.estimated_delivery),
            undefer(Order.shipping_events)
        )
    )
    order = result.scalar_one()

    assert len(order.shipping_events) > 1
    latest_event = order.shipping_events[-1]
    assert latest_event["location"] == "Bogotá - Centro de distribución"
    assert latest_event["status"] == "at_warehouse"


@pytest.mark.asyncio
async def test_update_shipping_delivered(async_db_session, test_shipped_order, auth_headers_admin, async_client):
    """Test marking as delivered updates order status"""
    from sqlalchemy.orm import undefer
    client = async_client

    # Mark as delivered
    response = await client.patch(
        f"/api/v1/shipping/orders/{test_shipped_order.id}/shipping/location",
        json={
            "current_location": "Dirección de entrega",
            "status": "delivered",
            "description": "Paquete entregado exitosamente"
        },
        headers=auth_headers_admin
    )

    assert response.status_code == 200
    data = response.json()
    assert data["order_status"] == "delivered"

    # Verify order status updated - Must undefer deferred columns in async context
    result = await async_db_session.execute(
        select(Order)
        .where(Order.id == test_shipped_order.id)
        .options(
            undefer(Order.tracking_number),
            undefer(Order.courier),
            undefer(Order.estimated_delivery),
            undefer(Order.shipping_events)
        )
    )
    order = result.scalar_one()

    assert order.status == OrderStatus.DELIVERED
    assert order.delivered_at is not None


@pytest.mark.asyncio
async def test_get_shipping_tracking_authenticated(async_db_session, test_buyer_user, test_shipped_order, auth_headers_buyer, async_client):
    """Test buyer can view their own order tracking"""
    from sqlalchemy.orm import undefer
    client = async_client

    # Reload order with deferred columns to avoid lazy loading
    result = await async_db_session.execute(
        select(Order)
        .where(Order.id == test_shipped_order.id)
        .options(
            undefer(Order.tracking_number),
            undefer(Order.courier),
            undefer(Order.estimated_delivery),
            undefer(Order.shipping_events)
        )
    )
    order = result.scalar_one()

    # Get tracking
    response = await client.get(
        f"/api/v1/shipping/orders/{order.id}/shipping/tracking",
        headers=auth_headers_buyer
    )

    assert response.status_code == 200
    data = response.json()

    assert data["order_number"] == order.order_number
    assert data["shipping_info"]["tracking_number"] == order.tracking_number
    assert data["shipping_info"]["courier"] == order.courier
    assert len(data["shipping_info"]["shipping_events"]) > 0


@pytest.mark.asyncio
async def test_get_shipping_tracking_forbidden(async_db_session, test_buyer_user, test_shipped_order_other_buyer, auth_headers_buyer, async_client):
    """Test buyer cannot view other buyer's order"""
    client = async_client

    # Try to get tracking of another buyer's order
    response = await client.get(
        f"/api/v1/shipping/orders/{test_shipped_order_other_buyer.id}/shipping/tracking",
        headers=auth_headers_buyer
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_track_by_tracking_number_public(async_db_session, test_shipped_order, async_client):
    """Test public tracking by tracking number (no auth)"""
    from sqlalchemy.orm import undefer
    client = async_client

    # Reload order with deferred columns to avoid lazy loading
    result = await async_db_session.execute(
        select(Order)
        .where(Order.id == test_shipped_order.id)
        .options(
            undefer(Order.tracking_number),
            undefer(Order.courier),
            undefer(Order.estimated_delivery),
            undefer(Order.shipping_events)
        )
    )
    order = result.scalar_one()

    # Get tracking without authentication
    response = await client.get(
        f"/api/v1/shipping/tracking/{order.tracking_number}"
    )

    assert response.status_code == 200
    data = response.json()

    assert data["order_number"] == order.order_number
    assert data["shipping_info"]["tracking_number"] == order.tracking_number

    # Verify sensitive info is hidden (partial address only)
    assert data["shipping_city"] == order.shipping_city
    assert data["shipping_state"] == order.shipping_state


# Fixtures

@pytest_asyncio.fixture
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


@pytest_asyncio.fixture
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


@pytest_asyncio.fixture
async def test_buyer_user_other(async_db_session):
    """Create another buyer user for testing access control"""
    buyer = User(
        id=generate_uuid(),
        email="other_buyer@example.com",
        password_hash=await get_password_hash("testpass123"),
        nombre="Other Buyer",
        apellido="User",
        user_type=UserType.BUYER,
        is_active=True
    )
    async_db_session.add(buyer)
    await async_db_session.commit()
    await async_db_session.refresh(buyer)
    return buyer


@pytest_asyncio.fixture
async def test_shipped_order_other_buyer(async_db_session, test_buyer_user_other):
    """Create a shipped order for another buyer"""
    order = Order(
        order_number="ORD-TEST-003",
        buyer_id=test_buyer_user_other.id,
        status=OrderStatus.SHIPPED,
        total_amount=200000,
        shipping_address="Test Address 789",
        shipping_city="Cali",
        shipping_state="Valle del Cauca",
        shipping_name="Other Buyer",
        shipping_phone="0987654321",
        tracking_number="SHIP-20251003000001-TESTBBBB",
        courier="Coordinadora",
        estimated_delivery=datetime.now() + timedelta(days=3),
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
