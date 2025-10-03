"""
Test Admin Orders Endpoints

Validates the admin orders management API endpoints:
- GET /api/v1/admin/orders - List all orders with filtering
- GET /api/v1/admin/orders/{order_id} - Get order detail
- PATCH /api/v1/admin/orders/{order_id}/status - Update order status
- DELETE /api/v1/admin/orders/{order_id} - Cancel order
- GET /api/v1/admin/orders/stats/dashboard - Get order statistics

Security: All endpoints require SUPERUSER authentication
"""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from datetime import datetime

from app.main import app
from app.models.user import User, UserType
from app.models.order import Order, OrderItem, OrderStatus, OrderTransaction, PaymentStatus
from app.models.product import Product
from app.core.security import create_access_token


@pytest.fixture
async def superuser_token(async_session: AsyncSession):
    """Create a SUPERUSER and return auth token"""
    from app.core.security import hash_password

    user = User(
        email="admin_orders_test@test.com",
        nombre="Admin",
        apellido="Test",
        user_type=UserType.SUPERUSER,
        is_verified=True,
        is_active=True
    )
    # Hash password using async function
    user.password_hash = await hash_password("testpassword")
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    # Create access token
    token = create_access_token(
        data={
            "sub": user.id,
            "user_id": user.id,
            "email": user.email,
            "user_type": user.user_type.value
        }
    )

    return token


@pytest.fixture
async def sample_order(async_session: AsyncSession):
    """Create a sample order for testing"""
    from app.core.security import hash_password

    # Create buyer
    buyer = User(
        email="buyer_orders_test@test.com",
        nombre="Buyer",
        apellido="Test",
        user_type=UserType.BUYER,
        is_verified=True,
        is_active=True
    )
    buyer.password_hash = await hash_password("testpassword")
    async_session.add(buyer)
    await async_session.commit()
    await async_session.refresh(buyer)

    # Create vendor
    vendor = User(
        email="vendor_orders_test@test.com",
        nombre="Vendor",
        apellido="Test",
        user_type=UserType.VENDOR,
        is_verified=True,
        is_active=True
    )
    vendor.password_hash = await hash_password("testpassword")
    async_session.add(vendor)
    await async_session.commit()
    await async_session.refresh(vendor)

    # Create product
    product = Product(
        nombre="Test Product",
        descripcion="Test product for orders",
        precio=Decimal("100.00"),
        stock=10,
        vendor_id=vendor.id,
        category_id=1,
        is_active=True
    )
    async_session.add(product)
    await async_session.commit()
    await async_session.refresh(product)

    # Create order
    order = Order(
        order_number=f"TEST-{datetime.now().timestamp()}",
        buyer_id=buyer.id,
        subtotal=Decimal("100.00"),
        tax_amount=Decimal("0.00"),
        shipping_cost=Decimal("10.00"),
        discount_amount=Decimal("0.00"),
        total_amount=Decimal("110.00"),
        status=OrderStatus.PENDING,
        shipping_name="Test Buyer",
        shipping_phone="+573001234567",
        shipping_address="Calle 123 #45-67",
        shipping_city="Bogotá",
        shipping_state="Cundinamarca",
        shipping_country="CO"
    )
    async_session.add(order)
    await async_session.commit()
    await async_session.refresh(order)

    # Create order item
    item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_name=product.nombre,
        product_sku=f"SKU-{product.id}",
        unit_price=Decimal("100.00"),
        quantity=1,
        total_price=Decimal("100.00")
    )
    async_session.add(item)

    # Create transaction
    transaction = OrderTransaction(
        transaction_reference=f"TXN-{datetime.now().timestamp()}",
        order_id=order.id,
        amount=Decimal("110.00"),
        currency="COP",
        status=PaymentStatus.PENDING,
        payment_method_type="card",
        gateway="wompi"
    )
    async_session.add(transaction)

    await async_session.commit()
    await async_session.refresh(order)

    return order


@pytest.mark.asyncio
async def test_get_all_orders_requires_superuser():
    """Test that getting all orders requires SUPERUSER authentication"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/admin/orders")
        assert response.status_code == 401  # Unauthorized


@pytest.mark.asyncio
async def test_get_all_orders_success(superuser_token: str, sample_order: Order):
    """Test successfully getting all orders as SUPERUSER"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/admin/orders",
            headers={"Authorization": f"Bearer {superuser_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data
        assert "total" in data
        assert isinstance(data["orders"], list)


@pytest.mark.asyncio
async def test_get_all_orders_with_filters(superuser_token: str, sample_order: Order):
    """Test filtering orders by status"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/admin/orders?status=pending",
            headers={"Authorization": f"Bearer {superuser_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data


@pytest.mark.asyncio
async def test_get_order_detail_success(superuser_token: str, sample_order: Order):
    """Test successfully getting order detail"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/admin/orders/{sample_order.id}",
            headers={"Authorization": f"Bearer {superuser_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_order.id
        assert data["order_number"] == sample_order.order_number
        assert "buyer_email" in data
        assert "items" in data
        assert "transactions" in data


@pytest.mark.asyncio
async def test_get_order_detail_not_found(superuser_token: str):
    """Test getting detail for non-existent order"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/admin/orders/99999",
            headers={"Authorization": f"Bearer {superuser_token}"}
        )
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_order_status_success(superuser_token: str, sample_order: Order):
    """Test successfully updating order status"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.patch(
            f"/api/v1/admin/orders/{sample_order.id}/status",
            headers={"Authorization": f"Bearer {superuser_token}"},
            json={"status": "confirmed", "notes": "Admin confirmed order"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "confirmed"


@pytest.mark.asyncio
async def test_update_order_status_invalid_status(superuser_token: str, sample_order: Order):
    """Test updating order with invalid status"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.patch(
            f"/api/v1/admin/orders/{sample_order.id}/status",
            headers={"Authorization": f"Bearer {superuser_token}"},
            json={"status": "invalid_status"}
        )
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_cancel_order_success(superuser_token: str, sample_order: Order):
    """Test successfully cancelling an order"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete(
            f"/api/v1/admin/orders/{sample_order.id}",
            headers={"Authorization": f"Bearer {superuser_token}"},
            json={"reason": "Customer requested cancellation", "refund_requested": False}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data


@pytest.mark.asyncio
async def test_get_order_stats_success(superuser_token: str, sample_order: Order):
    """Test successfully getting order statistics"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/admin/orders/stats/dashboard",
            headers={"Authorization": f"Bearer {superuser_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_orders_today" in data
        assert "total_orders_week" in data
        assert "total_orders_month" in data
        assert "revenue_today" in data
        assert "orders_by_status" in data
        assert "top_buyers" in data


@pytest.mark.asyncio
async def test_admin_orders_pagination(superuser_token: str, sample_order: Order):
    """Test pagination parameters"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/admin/orders?skip=0&limit=10",
            headers={"Authorization": f"Bearer {superuser_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["skip"] == 0
        assert data["limit"] == 10


@pytest.mark.asyncio
async def test_admin_orders_search(superuser_token: str, sample_order: Order):
    """Test search functionality"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Search by order number
        response = await client.get(
            f"/api/v1/admin/orders?search={sample_order.order_number}",
            headers={"Authorization": f"Bearer {superuser_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["orders"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
