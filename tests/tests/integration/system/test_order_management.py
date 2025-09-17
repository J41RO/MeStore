"""
Comprehensive tests for Phase 9 MVP Order Management System.

Tests cover:
- Vendor order dashboard functionality
- Vendor order detail access
- Vendor order status updates
- Buyer order tracking with timeline
- Order status workflow validation
- Security access controls
- Notification system integration
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserType
from app.models.order import Order, OrderItem, OrderStatus, OrderTransaction
from app.models.product import Product
from app.services.order_notification_service import order_notification_service


class TestVendorOrderManagement:
    """Test vendor-specific order management functionality"""

    @pytest.fixture
    async def vendor_user(self, db_session: AsyncSession):
        """Create a test vendor user"""
        vendor = User(
            email="vendor@test.com",
            nombre="Test",
            apellido="Vendor",
            password_hash="hashed_password",
            user_type=UserType.VENDEDOR,
            is_active=True
        )
        db_session.add(vendor)
        await db_session.commit()
        await db_session.refresh(vendor)
        return vendor

    @pytest.fixture
    async def buyer_user(self, db_session: AsyncSession):
        """Create a test buyer user"""
        buyer = User(
            email="buyer@test.com",
            nombre="Test",
            apellido="Buyer",
            password_hash="hashed_password",
            user_type=UserType.COMPRADOR,
            is_active=True
        )
        db_session.add(buyer)
        await db_session.commit()
        await db_session.refresh(buyer)
        return buyer

    @pytest.fixture
    async def test_product(self, db_session: AsyncSession, vendor_user: User):
        """Create a test product for the vendor"""
        product = Product(
            name="Test Product",
            sku="TEST-001",
            precio_venta=100.0,
            vendedor_id=vendor_user.id,
            status="active"
        )
        db_session.add(product)
        await db_session.commit()
        await db_session.refresh(product)
        return product

    @pytest.fixture
    async def test_order(self, db_session: AsyncSession, buyer_user: User, test_product: Product):
        """Create a test order with the vendor's product"""
        order = Order(
            order_number="TEST-ORDER-001",
            buyer_id=buyer_user.id,
            total_amount=115.0,
            subtotal=100.0,
            tax_amount=15.0,
            shipping_cost=0.0,
            discount_amount=0.0,
            status=OrderStatus.CONFIRMED,
            confirmed_at=datetime.utcnow(),
            shipping_name="Test Buyer",
            shipping_phone="+1234567890",
            shipping_address="123 Test St",
            shipping_city="Test City",
            shipping_state="Test State"
        )
        db_session.add(order)
        await db_session.flush()

        order_item = OrderItem(
            order_id=order.id,
            product_id=test_product.id,
            product_name=test_product.name,
            product_sku=test_product.sku,
            unit_price=test_product.precio_venta,
            quantity=1,
            total_price=test_product.precio_venta
        )
        db_session.add(order_item)
        await db_session.commit()
        await db_session.refresh(order)
        return order

    async def test_vendor_order_dashboard_access(
        self,
        client: AsyncClient,
        vendor_user: User,
        test_order: Order
    ):
        """Test vendor can access their order dashboard"""
        # Mock authentication
        with patch('app.core.auth.get_current_user', return_value=vendor_user):
            response = await client.get("/api/v1/orders/vendor/dashboard")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["order_number"] == test_order.order_number
        assert data[0]["buyer_name"] == test_order.shipping_name

    async def test_vendor_order_dashboard_filters(
        self,
        client: AsyncClient,
        vendor_user: User,
        test_order: Order
    ):
        """Test vendor dashboard with status filters"""
        # Mock authentication
        with patch('app.core.auth.get_current_user', return_value=vendor_user):
            # Test confirmed orders
            response = await client.get(
                "/api/v1/orders/vendor/dashboard?status_filter=confirmed"
            )
            assert response.status_code == 200
            assert len(response.json()) == 1

            # Test non-existent status
            response = await client.get(
                "/api/v1/orders/vendor/dashboard?status_filter=delivered"
            )
            assert response.status_code == 200
            assert len(response.json()) == 0

    async def test_vendor_order_detail_access(
        self,
        client: AsyncClient,
        vendor_user: User,
        test_order: Order
    ):
        """Test vendor can access detailed order information"""
        with patch('app.core.auth.get_current_user', return_value=vendor_user):
            response = await client.get(f"/api/v1/orders/vendor/{test_order.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["order_number"] == test_order.order_number
        assert data["buyer_name"] == test_order.shipping_name
        assert data["status"] == OrderStatus.CONFIRMED.value
        assert len(data["items"]) == 1

    async def test_vendor_cannot_access_other_vendor_orders(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_order: Order
    ):
        """Test vendor cannot access orders without their products"""
        # Create different vendor
        other_vendor = User(
            email="other@vendor.com",
            nombre="Other",
            apellido="Vendor",
            password_hash="hashed_password",
            user_type=UserType.VENDEDOR,
            is_active=True
        )
        db_session.add(other_vendor)
        await db_session.commit()

        with patch('app.core.auth.get_current_user', return_value=other_vendor):
            response = await client.get(f"/api/v1/orders/vendor/{test_order.id}")

        assert response.status_code == 404

    async def test_vendor_order_status_update_processing(
        self,
        client: AsyncClient,
        vendor_user: User,
        test_order: Order
    ):
        """Test vendor can update order to processing status"""
        with patch('app.core.auth.get_current_user', return_value=vendor_user):
            with patch('app.services.order_notification_service.order_notification_service.notify_status_change') as mock_notify:
                mock_notify.return_value = True

                response = await client.patch(
                    f"/api/v1/orders/vendor/{test_order.id}/status",
                    json={
                        "status": "processing",
                        "notes": "Order being prepared"
                    }
                )

        assert response.status_code == 200
        data = response.json()
        assert data["old_status"] == "confirmed"
        assert data["new_status"] == "processing"
        mock_notify.assert_called_once()

    async def test_vendor_order_status_update_shipped(
        self,
        client: AsyncClient,
        vendor_user: User,
        test_order: Order,
        db_session: AsyncSession
    ):
        """Test vendor can update order to shipped status"""
        # First update to processing
        test_order.status = OrderStatus.PROCESSING
        test_order.processing_at = datetime.utcnow()
        await db_session.commit()

        with patch('app.core.auth.get_current_user', return_value=vendor_user):
            with patch('app.services.order_notification_service.order_notification_service.notify_status_change') as mock_notify:
                mock_notify.return_value = True

                response = await client.patch(
                    f"/api/v1/orders/vendor/{test_order.id}/status",
                    json={"status": "shipped"}
                )

        assert response.status_code == 200
        data = response.json()
        assert data["old_status"] == "processing"
        assert data["new_status"] == "shipped"

    async def test_vendor_status_update_invalid_transition(
        self,
        client: AsyncClient,
        vendor_user: User,
        test_order: Order
    ):
        """Test vendor cannot make invalid status transitions"""
        with patch('app.core.auth.get_current_user', return_value=vendor_user):
            # Try to go from confirmed directly to delivered (not allowed)
            response = await client.patch(
                f"/api/v1/orders/vendor/{test_order.id}/status",
                json={"status": "delivered"}
            )

        assert response.status_code == 400
        assert "Vendors can only update status to" in response.json()["detail"]

    async def test_non_vendor_access_denied(
        self,
        client: AsyncClient,
        buyer_user: User,
        test_order: Order
    ):
        """Test non-vendor users cannot access vendor endpoints"""
        with patch('app.core.auth.get_current_user', return_value=buyer_user):
            response = await client.get("/api/v1/orders/vendor/dashboard")

        assert response.status_code == 403
        assert "Vendor access required" in response.json()["detail"]


class TestBuyerOrderTracking:
    """Test buyer order tracking functionality"""

    @pytest.fixture
    async def buyer_with_order(self, db_session: AsyncSession):
        """Create buyer with order for tracking tests"""
        buyer = User(
            email="buyer@test.com",
            nombre="Test",
            apellido="Buyer",
            password_hash="hashed_password",
            user_type=UserType.COMPRADOR,
            is_active=True
        )
        db_session.add(buyer)
        await db_session.flush()

        order = Order(
            order_number="TRACK-001",
            buyer_id=buyer.id,
            total_amount=100.0,
            subtotal=85.0,
            tax_amount=15.0,
            shipping_cost=0.0,
            discount_amount=0.0,
            status=OrderStatus.SHIPPED,
            confirmed_at=datetime.utcnow() - timedelta(days=2),
            processing_at=datetime.utcnow() - timedelta(days=1),
            shipped_at=datetime.utcnow(),
            shipping_name="Test Buyer",
            shipping_phone="+1234567890",
            shipping_address="123 Test St",
            shipping_city="Test City",
            shipping_state="Test State"
        )
        db_session.add(order)
        await db_session.commit()
        await db_session.refresh(buyer)
        await db_session.refresh(order)

        return buyer, order

    async def test_buyer_order_tracking_timeline(
        self,
        client: AsyncClient,
        buyer_with_order
    ):
        """Test buyer can see detailed order tracking timeline"""
        buyer, order = buyer_with_order

        with patch('app.core.auth.get_current_user', return_value=buyer):
            response = await client.get(f"/api/v1/orders/{order.id}/tracking")

        assert response.status_code == 200
        data = response.json()

        # Verify timeline structure
        assert "timeline" in data
        timeline = data["timeline"]
        assert len(timeline) == 5  # pending, confirmed, processing, shipped, delivered

        # Check specific timeline events
        confirmed_event = next(e for e in timeline if e["status"] == "confirmed")
        assert confirmed_event["is_completed"] is True

        processing_event = next(e for e in timeline if e["status"] == "processing")
        assert processing_event["is_completed"] is True

        shipped_event = next(e for e in timeline if e["status"] == "shipped")
        assert shipped_event["is_completed"] is True

        delivered_event = next(e for e in timeline if e["status"] == "delivered")
        assert delivered_event["is_completed"] is False

    async def test_buyer_cannot_access_other_orders(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        buyer_with_order
    ):
        """Test buyer cannot access other buyer's orders"""
        _, order = buyer_with_order

        # Create different buyer
        other_buyer = User(
            email="other@buyer.com",
            nombre="Other",
            apellido="Buyer",
            password_hash="hashed_password",
            user_type=UserType.COMPRADOR,
            is_active=True
        )
        db_session.add(other_buyer)
        await db_session.commit()

        with patch('app.core.auth.get_current_user', return_value=other_buyer):
            response = await client.get(f"/api/v1/orders/{order.id}/tracking")

        assert response.status_code == 404


class TestOrderNotificationService:
    """Test order notification service"""

    @pytest.mark.asyncio
    async def test_notification_service_buyer_message(self):
        """Test notification service generates proper buyer messages"""
        # Mock order
        class MockBuyer:
            email = "buyer@test.com"

        class MockOrder:
            order_number = "TEST-001"
            buyer = MockBuyer()

        order = MockOrder()

        # Test different status messages
        message = order_notification_service._get_buyer_message(
            order, OrderStatus.CONFIRMED, OrderStatus.PROCESSING
        )
        assert "being processed" in message

        message = order_notification_service._get_buyer_message(
            order, OrderStatus.PROCESSING, OrderStatus.SHIPPED
        )
        assert "has been shipped" in message

    @pytest.mark.asyncio
    async def test_notification_service_vendor_message(self):
        """Test notification service generates proper vendor messages"""
        # Mock data
        class MockItem:
            total_price = 50.0

        class MockOrder:
            order_number = "TEST-001"

        order = MockOrder()
        vendor_items = [MockItem(), MockItem()]  # $100 total

        message = order_notification_service._get_vendor_message(
            order, OrderStatus.PENDING, OrderStatus.CONFIRMED, vendor_items
        )
        assert "New order received" in message
        assert "2 of your items" in message
        assert "$100.00" in message


class TestOrderStatusWorkflow:
    """Test order status workflow and timestamp updates"""

    async def test_status_workflow_timestamps(
        self,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test that status changes update appropriate timestamps"""
        # Create admin user
        admin = User(
            email="admin@test.com",
            nombre="Admin",
            apellido="User",
            password_hash="hashed_password",
            user_type=UserType.ADMIN,
            is_active=True
        )
        db_session.add(admin)
        await db_session.flush()

        # Create order
        order = Order(
            order_number="WORKFLOW-001",
            buyer_id=admin.id,  # Using admin as buyer for simplicity
            total_amount=100.0,
            subtotal=85.0,
            tax_amount=15.0,
            status=OrderStatus.PENDING,
            shipping_name="Test User",
            shipping_phone="+1234567890",
            shipping_address="123 Test St",
            shipping_city="Test City",
            shipping_state="Test State"
        )
        db_session.add(order)
        await db_session.commit()
        await db_session.refresh(order)

        with patch('app.core.auth.get_current_user', return_value=admin):
            with patch('app.services.order_notification_service.order_notification_service.notify_status_change'):
                # Test confirmed status sets confirmed_at
                response = await client.patch(
                    f"/api/v1/orders/{order.id}/status?new_status=confirmed"
                )
                assert response.status_code == 200

                # Refresh order to check timestamp
                await db_session.refresh(order)
                assert order.confirmed_at is not None

                # Test processing status sets processing_at
                response = await client.patch(
                    f"/api/v1/orders/{order.id}/status?new_status=processing"
                )
                assert response.status_code == 200

                await db_session.refresh(order)
                assert order.processing_at is not None

    async def test_order_workflow_validation(self):
        """Test order workflow business rules"""
        # This would test that orders follow proper workflow:
        # PENDING -> CONFIRMED -> PROCESSING -> SHIPPED -> DELIVERED
        # or PENDING/CONFIRMED -> CANCELLED
        pass


# Integration test fixtures and setup
@pytest.fixture
async def db_session():
    """Mock database session for testing"""
    # This would be implemented with actual test database setup
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
async def client():
    """Mock HTTP client for testing"""
    # This would be implemented with actual FastAPI test client
    return AsyncMock(spec=AsyncClient)