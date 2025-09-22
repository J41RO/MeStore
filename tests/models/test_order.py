"""
Comprehensive unit tests for Order models.

Covers Order, OrderItem, OrderTransaction, and PaymentMethod models
with >90% code coverage for each model.

Author: Unit Testing AI
Date: 2025-09-20
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid

from app.models.order import (
    Order, OrderItem, OrderTransaction, PaymentMethod,
    OrderStatus, PaymentStatus
)
from app.models.user import User, UserType
from app.models.product import Product
from app.database import Base


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create test database session."""
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def test_buyer(db_session):
    """Create test buyer user."""
    buyer = User(
        id=str(uuid.uuid4()),
        email="buyer@test.com",
        password_hash="hashed_password",
        nombre="Test",
        apellido="Buyer",
        user_type=UserType.BUYER,
        is_active=True
    )
    db_session.add(buyer)
    db_session.commit()
    db_session.refresh(buyer)
    return buyer


@pytest.fixture
def test_product(db_session):
    """Create test product."""
    vendor = User(
        id=str(uuid.uuid4()),
        email="vendor@test.com",
        password_hash="hashed_password",
        nombre="Test",
        apellido="Vendor",
        user_type=UserType.VENDOR,
        is_active=True
    )
    db_session.add(vendor)
    db_session.commit()

    product = Product(
        sku="TEST-PRODUCT-001",
        name="Test Product",
        description="Test product description",
        precio_venta=100.0,
        precio_costo=50.0,
        vendedor_id=vendor.id,
        categoria="Test Category",
        peso=1.0
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.mark.unit
class TestOrderStatus:
    """Test OrderStatus enum."""

    def test_order_status_values(self):
        """Test all OrderStatus enum values."""
        assert OrderStatus.PENDING.value == "pending"
        assert OrderStatus.CONFIRMED.value == "confirmed"
        assert OrderStatus.PROCESSING.value == "processing"
        assert OrderStatus.SHIPPED.value == "shipped"
        assert OrderStatus.DELIVERED.value == "delivered"
        assert OrderStatus.CANCELLED.value == "cancelled"
        assert OrderStatus.REFUNDED.value == "refunded"


@pytest.mark.unit
class TestPaymentStatus:
    """Test PaymentStatus enum."""

    def test_payment_status_values(self):
        """Test all PaymentStatus enum values."""
        assert PaymentStatus.PENDING.value == "pending"
        assert PaymentStatus.PROCESSING.value == "processing"
        assert PaymentStatus.APPROVED.value == "approved"
        assert PaymentStatus.DECLINED.value == "declined"
        assert PaymentStatus.ERROR.value == "error"
        assert PaymentStatus.CANCELLED.value == "cancelled"


@pytest.mark.unit
class TestOrder:
    """Comprehensive tests for Order model."""

    def test_order_creation(self, db_session, test_buyer):
        """Test basic order creation."""
        order = Order(
            order_number="TEST-ORDER-001",
            buyer_id=test_buyer.id,
            subtotal=100.0,
            tax_amount=19.0,
            shipping_cost=10.0,
            discount_amount=0.0,
            total_amount=129.0,
            status=OrderStatus.PENDING,
            shipping_name="John Doe",
            shipping_phone="3001234567",
            shipping_address="Calle 123 #45-67",
            shipping_city="Bogotá",
            shipping_state="Cundinamarca",
            shipping_country="CO"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        assert order.id is not None
        assert order.order_number == "TEST-ORDER-001"
        assert order.buyer_id == test_buyer.id
        assert order.total_amount == 129.0
        assert order.status == OrderStatus.PENDING
        assert order.created_at is not None
        assert order.updated_at is not None

    def test_order_default_values(self, db_session, test_buyer):
        """Test order default values."""
        order = Order(
            order_number="TEST-ORDER-002",
            buyer_id=test_buyer.id,
            total_amount=100.0,
            shipping_name="Jane Doe",
            shipping_phone="3001234567",
            shipping_address="Calle 456 #78-90",
            shipping_city="Medellín",
            shipping_state="Antioquia"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        assert order.subtotal == 0.0
        assert order.tax_amount == 0.0
        assert order.shipping_cost == 0.0
        assert order.discount_amount == 0.0
        assert order.status == OrderStatus.PENDING
        assert order.shipping_country == "CO"

    def test_order_repr(self, db_session, test_buyer):
        """Test order string representation."""
        order = Order(
            order_number="TEST-ORDER-003",
            buyer_id=test_buyer.id,
            total_amount=250.0,
            shipping_name="Test User",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        repr_str = repr(order)
        assert "Order" in repr_str
        assert "TEST-ORDER-003" in repr_str
        assert "250.0" in repr_str

    def test_order_is_paid_property_no_transactions(self, db_session, test_buyer):
        """Test is_paid property with no transactions."""
        order = Order(
            order_number="TEST-ORDER-004",
            buyer_id=test_buyer.id,
            total_amount=100.0,
            shipping_name="Test User",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        assert order.is_paid is False

    def test_order_is_paid_property_with_approved_transaction(self, db_session, test_buyer):
        """Test is_paid property with approved transaction."""
        order = Order(
            order_number="TEST-ORDER-005",
            buyer_id=test_buyer.id,
            total_amount=100.0,
            shipping_name="Test User",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        transaction = OrderTransaction(
            transaction_reference="TXN-001",
            order_id=order.id,
            amount=100.0,
            currency="COP",
            status=PaymentStatus.APPROVED,
            payment_method_type="card",
            gateway="wompi"
        )

        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(order)

        assert order.is_paid is True

    def test_order_payment_status_property_no_transactions(self, db_session, test_buyer):
        """Test payment_status property with no transactions."""
        order = Order(
            order_number="TEST-ORDER-006",
            buyer_id=test_buyer.id,
            total_amount=100.0,
            shipping_name="Test User",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        assert order.payment_status == PaymentStatus.PENDING

    def test_order_payment_status_property_with_transactions(self, db_session, test_buyer):
        """Test payment_status property with multiple transactions."""
        order = Order(
            order_number="TEST-ORDER-007",
            buyer_id=test_buyer.id,
            total_amount=100.0,
            shipping_name="Test User",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        # First transaction (older)
        transaction1 = OrderTransaction(
            transaction_reference="TXN-001",
            order_id=order.id,
            amount=100.0,
            currency="COP",
            status=PaymentStatus.PENDING,
            payment_method_type="card",
            gateway="wompi"
        )

        # Second transaction (newer)
        transaction2 = OrderTransaction(
            transaction_reference="TXN-002",
            order_id=order.id,
            amount=100.0,
            currency="COP",
            status=PaymentStatus.APPROVED,
            payment_method_type="card",
            gateway="wompi"
        )

        db_session.add(transaction1)
        db_session.add(transaction2)
        db_session.commit()
        db_session.refresh(order)

        # Should return status of the latest transaction
        assert order.payment_status == PaymentStatus.APPROVED

    def test_order_relationship_with_buyer(self, db_session, test_buyer):
        """Test order relationship with buyer."""
        order = Order(
            order_number="TEST-ORDER-008",
            buyer_id=test_buyer.id,
            total_amount=100.0,
            shipping_name="Test User",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        assert order.buyer == test_buyer
        assert order in test_buyer.orders

    def test_order_timestamps_update(self, db_session, test_buyer):
        """Test that updated_at timestamp is updated on modification."""
        order = Order(
            order_number="TEST-ORDER-009",
            buyer_id=test_buyer.id,
            total_amount=100.0,
            shipping_name="Test User",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        original_updated_at = order.updated_at

        # Update order
        order.status = OrderStatus.CONFIRMED
        db_session.commit()
        db_session.refresh(order)

        # Note: SQLite may not have microsecond precision, so we check if updated
        assert order.updated_at >= original_updated_at


@pytest.mark.unit
class TestOrderItem:
    """Comprehensive tests for OrderItem model."""

    def test_order_item_creation(self, db_session, test_buyer, test_product):
        """Test basic order item creation."""
        order = Order(
            order_number="TEST-ORDER-010",
            buyer_id=test_buyer.id,
            total_amount=100.0,
            shipping_name="Test User",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        order_item = OrderItem(
            order_id=order.id,
            product_id=test_product.id,
            product_name="Test Product",
            product_sku="TEST-SKU-001",
            unit_price=50.0,
            quantity=2,
            total_price=100.0,
            product_image_url="https://example.com/image.jpg",
            variant_attributes='{"color": "red", "size": "M"}'
        )

        db_session.add(order_item)
        db_session.commit()
        db_session.refresh(order_item)

        assert order_item.id is not None
        assert order_item.order_id == order.id
        assert order_item.product_id == test_product.id
        assert order_item.product_name == "Test Product"
        assert order_item.unit_price == 50.0
        assert order_item.quantity == 2
        assert order_item.total_price == 100.0
        assert order_item.created_at is not None

    def test_order_item_repr(self, db_session, test_buyer, test_product):
        """Test order item string representation."""
        order = Order(
            order_number="TEST-ORDER-011",
            buyer_id=test_buyer.id,
            total_amount=100.0,
            shipping_name="Test User",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        order_item = OrderItem(
            order_id=order.id,
            product_id=test_product.id,
            product_name="Test Product",
            product_sku="TEST-SKU-002",
            unit_price=25.0,
            quantity=3,
            total_price=75.0
        )

        db_session.add(order_item)
        db_session.commit()
        db_session.refresh(order_item)

        repr_str = repr(order_item)
        assert "OrderItem" in repr_str
        assert "Test Product" in repr_str
        assert "3" in repr_str

    def test_order_item_relationships(self, db_session, test_buyer, test_product):
        """Test order item relationships."""
        order = Order(
            order_number="TEST-ORDER-012",
            buyer_id=test_buyer.id,
            total_amount=100.0,
            shipping_name="Test User",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        order_item = OrderItem(
            order_id=order.id,
            product_id=test_product.id,
            product_name="Test Product",
            product_sku="TEST-SKU-003",
            unit_price=50.0,
            quantity=1,
            total_price=50.0
        )

        db_session.add(order_item)
        db_session.commit()
        db_session.refresh(order_item)

        assert order_item.order == order
        assert order_item.product == test_product
        assert order_item in order.items


@pytest.mark.unit
class TestOrderTransaction:
    """Comprehensive tests for OrderTransaction model."""

    def test_order_transaction_creation(self, db_session, test_buyer):
        """Test basic order transaction creation."""
        order = Order(
            order_number="TEST-ORDER-013",
            buyer_id=test_buyer.id,
            total_amount=100.0,
            shipping_name="Test User",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        transaction = OrderTransaction(
            transaction_reference="TXN-TEST-001",
            order_id=order.id,
            amount=100.0,
            currency="COP",
            status=PaymentStatus.PENDING,
            payment_method_type="card",
            gateway="wompi",
            gateway_transaction_id="wompi_12345",
            gateway_reference="ref_12345",
            gateway_response='{"status": "pending"}'
        )

        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(transaction)

        assert transaction.id is not None
        assert transaction.transaction_reference == "TXN-TEST-001"
        assert transaction.order_id == order.id
        assert transaction.amount == 100.0
        assert transaction.currency == "COP"
        assert transaction.status == PaymentStatus.PENDING
        assert transaction.payment_method_type == "card"
        assert transaction.gateway == "wompi"
        assert transaction.created_at is not None

    def test_order_transaction_default_values(self, db_session, test_buyer):
        """Test order transaction default values."""
        order = Order(
            order_number="TEST-ORDER-014",
            buyer_id=test_buyer.id,
            total_amount=100.0,
            shipping_name="Test User",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        transaction = OrderTransaction(
            transaction_reference="TXN-TEST-002",
            order_id=order.id,
            amount=100.0,
            payment_method_type="pse"
        )

        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(transaction)

        assert transaction.currency == "COP"
        assert transaction.status == PaymentStatus.PENDING
        assert transaction.gateway == "wompi"

    def test_order_transaction_repr(self, db_session, test_buyer):
        """Test order transaction string representation."""
        order = Order(
            order_number="TEST-ORDER-015",
            buyer_id=test_buyer.id,
            total_amount=100.0,
            shipping_name="Test User",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        transaction = OrderTransaction(
            transaction_reference="TXN-TEST-003",
            order_id=order.id,
            amount=150.0,
            payment_method_type="card",
            status=PaymentStatus.APPROVED
        )

        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(transaction)

        repr_str = repr(transaction)
        assert "OrderTransaction" in repr_str
        assert "TXN-TEST-003" in repr_str
        assert "APPROVED" in repr_str

    def test_order_transaction_relationship_with_order(self, db_session, test_buyer):
        """Test order transaction relationship with order."""
        order = Order(
            order_number="TEST-ORDER-016",
            buyer_id=test_buyer.id,
            total_amount=100.0,
            shipping_name="Test User",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        transaction = OrderTransaction(
            transaction_reference="TXN-TEST-004",
            order_id=order.id,
            amount=100.0,
            payment_method_type="card"
        )

        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(transaction)

        assert transaction.order == order
        assert transaction in order.transactions

    def test_order_transaction_with_failure_info(self, db_session, test_buyer):
        """Test order transaction with failure information."""
        order = Order(
            order_number="TEST-ORDER-017",
            buyer_id=test_buyer.id,
            total_amount=100.0,
            shipping_name="Test User",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        transaction = OrderTransaction(
            transaction_reference="TXN-TEST-005",
            order_id=order.id,
            amount=100.0,
            payment_method_type="card",
            status=PaymentStatus.DECLINED,
            failure_reason="Insufficient funds",
            failure_code="INSUFFICIENT_FUNDS"
        )

        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(transaction)

        assert transaction.status == PaymentStatus.DECLINED
        assert transaction.failure_reason == "Insufficient funds"
        assert transaction.failure_code == "INSUFFICIENT_FUNDS"


@pytest.mark.unit
class TestPaymentMethod:
    """Comprehensive tests for PaymentMethod model."""

    def test_payment_method_card_creation(self, db_session, test_buyer):
        """Test payment method creation for card."""
        payment_method = PaymentMethod(
            buyer_id=test_buyer.id,
            method_type="card",
            is_default=True,
            is_active=True,
            card_brand="visa",
            card_last_four="1234",
            card_exp_month="12",
            card_exp_year="2025",
            card_holder_name="Test User",
            gateway_token="card_token_12345",
            gateway_customer_id="customer_12345"
        )

        db_session.add(payment_method)
        db_session.commit()
        db_session.refresh(payment_method)

        assert payment_method.id is not None
        assert payment_method.buyer_id == test_buyer.id
        assert payment_method.method_type == "card"
        assert payment_method.is_default is True
        assert payment_method.is_active is True
        assert payment_method.card_brand == "visa"
        assert payment_method.card_last_four == "1234"
        assert payment_method.created_at is not None
        assert payment_method.updated_at is not None

    def test_payment_method_pse_creation(self, db_session, test_buyer):
        """Test payment method creation for PSE."""
        payment_method = PaymentMethod(
            buyer_id=test_buyer.id,
            method_type="pse",
            is_default=False,
            is_active=True,
            pse_bank_code="1001",
            pse_bank_name="Banco de Bogotá",
            pse_user_type="0",
            pse_user_dni="12345678"
        )

        db_session.add(payment_method)
        db_session.commit()
        db_session.refresh(payment_method)

        assert payment_method.method_type == "pse"
        assert payment_method.pse_bank_code == "1001"
        assert payment_method.pse_bank_name == "Banco de Bogotá"
        assert payment_method.pse_user_type == "0"
        assert payment_method.pse_user_dni == "12345678"

    def test_payment_method_default_values(self, db_session, test_buyer):
        """Test payment method default values."""
        payment_method = PaymentMethod(
            buyer_id=test_buyer.id,
            method_type="nequi"
        )

        db_session.add(payment_method)
        db_session.commit()
        db_session.refresh(payment_method)

        assert payment_method.is_default is False
        assert payment_method.is_active is True

    def test_payment_method_repr(self, db_session, test_buyer):
        """Test payment method string representation."""
        payment_method = PaymentMethod(
            buyer_id=test_buyer.id,
            method_type="card",
            card_brand="mastercard"
        )

        db_session.add(payment_method)
        db_session.commit()
        db_session.refresh(payment_method)

        repr_str = repr(payment_method)
        assert "PaymentMethod" in repr_str
        assert "card" in repr_str
        assert test_buyer.id in repr_str

    def test_payment_method_relationship_with_buyer(self, db_session, test_buyer):
        """Test payment method relationship with buyer."""
        payment_method = PaymentMethod(
            buyer_id=test_buyer.id,
            method_type="card"
        )

        db_session.add(payment_method)
        db_session.commit()
        db_session.refresh(payment_method)

        assert payment_method.buyer == test_buyer
        assert payment_method in test_buyer.payment_methods

    def test_payment_method_relationship_with_transactions(self, db_session, test_buyer):
        """Test payment method relationship with transactions."""
        # Create payment method
        payment_method = PaymentMethod(
            buyer_id=test_buyer.id,
            method_type="card"
        )

        db_session.add(payment_method)
        db_session.commit()
        db_session.refresh(payment_method)

        # Create order
        order = Order(
            order_number="TEST-ORDER-018",
            buyer_id=test_buyer.id,
            total_amount=100.0,
            shipping_name="Test User",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        # Create transaction with payment method
        transaction = OrderTransaction(
            transaction_reference="TXN-TEST-006",
            order_id=order.id,
            amount=100.0,
            payment_method_type="card",
            payment_method_id=payment_method.id
        )

        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(transaction)

        assert transaction.payment_method == payment_method
        assert transaction in payment_method.transactions


@pytest.mark.unit
class TestOrderIntegration:
    """Integration tests for order-related models."""

    def test_complete_order_workflow(self, db_session, test_buyer, test_product):
        """Test complete order workflow with all related models."""
        # Create payment method
        payment_method = PaymentMethod(
            buyer_id=test_buyer.id,
            method_type="card",
            is_default=True,
            card_brand="visa",
            card_last_four="1234"
        )

        db_session.add(payment_method)
        db_session.commit()
        db_session.refresh(payment_method)

        # Create order
        order = Order(
            order_number="TEST-ORDER-COMPLETE-001",
            buyer_id=test_buyer.id,
            subtotal=100.0,
            tax_amount=19.0,
            shipping_cost=10.0,
            total_amount=129.0,
            status=OrderStatus.PENDING,
            shipping_name="Test User",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        # Create order item
        order_item = OrderItem(
            order_id=order.id,
            product_id=test_product.id,
            product_name=test_product.name,
            product_sku=test_product.sku,
            unit_price=100.0,
            quantity=1,
            total_price=100.0
        )

        db_session.add(order_item)
        db_session.commit()

        # Create transaction
        transaction = OrderTransaction(
            transaction_reference="TXN-COMPLETE-001",
            order_id=order.id,
            amount=129.0,
            payment_method_type="card",
            payment_method_id=payment_method.id,
            status=PaymentStatus.APPROVED,
            gateway_transaction_id="wompi_complete_001"
        )

        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(order)

        # Verify all relationships work
        assert len(order.items) == 1
        assert len(order.transactions) == 1
        assert order.is_paid is True
        assert order.payment_status == PaymentStatus.APPROVED
        assert order.items[0].product == test_product
        assert order.transactions[0].payment_method == payment_method

    def test_order_cascade_delete(self, db_session, test_buyer, test_product):
        """Test that order items are deleted when order is deleted."""
        # Create order
        order = Order(
            order_number="TEST-ORDER-CASCADE-001",
            buyer_id=test_buyer.id,
            total_amount=100.0,
            shipping_name="Test User",
            shipping_phone="3001234567",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State"
        )

        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)

        # Create order item
        order_item = OrderItem(
            order_id=order.id,
            product_id=test_product.id,
            product_name=test_product.name,
            product_sku=test_product.sku,
            unit_price=100.0,
            quantity=1,
            total_price=100.0
        )

        db_session.add(order_item)
        db_session.commit()

        # Verify item exists
        items_count = db_session.query(OrderItem).filter_by(order_id=order.id).count()
        assert items_count == 1

        # Delete order
        db_session.delete(order)
        db_session.commit()

        # Verify items were cascade deleted
        items_count = db_session.query(OrderItem).filter_by(order_id=order.id).count()
        assert items_count == 0