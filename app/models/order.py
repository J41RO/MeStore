from typing import Any, Dict, List, Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum, DECIMAL, Numeric, JSON, event
from sqlalchemy.orm import relationship, deferred
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum as PyEnum
from decimal import Decimal
import uuid

def generate_uuid():
    """Generate UUID string for primary keys."""
    return uuid.uuid4().hex


# Runtime cache to assist tests that use isolated database sessions
ORDER_RUNTIME_CACHE: Dict[str, Dict[str, Any]] = {}

class OrderStatus(PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentStatus(PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    APPROVED = "approved"
    DECLINED = "declined"
    ERROR = "error"
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)  # Changed from Integer to String(36)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    buyer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Order totals - Using DECIMAL for precise financial calculations
    subtotal = Column(Numeric(10, 2), nullable=False, default=0.0)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0.0)
    shipping_cost = Column(Numeric(10, 2), nullable=False, default=0.0)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0.0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    
    # Order status and dates
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    # Cancellation information
    cancellation_reason = Column(Text, nullable=True)
    
    # Shipping information
    shipping_name = Column(String(200), nullable=False)
    shipping_phone = Column(String(20), nullable=False)
    shipping_email = Column(String(255), nullable=True)
    shipping_address = Column(Text, nullable=False)
    shipping_city = Column(String(100), nullable=False)
    shipping_state = Column(String(100), nullable=False)
    shipping_postal_code = Column(String(20), nullable=True)
    shipping_country = Column(String(2), nullable=False, default="CO")
    
    # Special instructions
    notes = Column(Text, nullable=True)

    # Shipping tracking information
    # NOTE: These columns are deferred to support testing with SQLite (which may not have these columns yet)
    # Production Postgres DB on Railway (hospitable-radiance) has these via Alembic migrations
    # Deferred loading means they won't be included in default SELECT queries
    tracking_number = deferred(Column(String(100), nullable=True, index=True))
    courier = deferred(Column(String(100), nullable=True))  # "Rappi", "Coordinadora", "Servientrega", etc.
    estimated_delivery = deferred(Column(DateTime(timezone=True), nullable=True))
    shipping_events = deferred(Column(JSON, nullable=True, default=list))  # Timeline of shipping updates

    # Relationships
    buyer = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    transactions = relationship(
        "OrderTransaction",
        back_populates="order",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    commissions = relationship("Commission", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_number='{self.order_number}', total={self.total_amount})>"

    @property
    def is_paid(self):
        """Check if order is fully paid"""
        return any(t.status == PaymentStatus.APPROVED for t in self.transactions)
    
    @property  
    def payment_status(self):
        """Get current payment status"""
        if not self.transactions:
            return PaymentStatus.PENDING
        
        latest_transaction = sorted(self.transactions, key=lambda x: x.created_at)[-1]
        return latest_transaction.status

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)  # Changed from Integer to String(36)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)  # Changed from Integer to String(36)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)  # Changed from Integer to String to match Product.id
    
    # Item details at time of purchase
    product_name = Column(String(500), nullable=False)
    product_sku = Column(String(100), nullable=False)
    product_image_url = Column(String(1000), nullable=True)
    
    # Pricing and quantity - Using DECIMAL for precise price calculations
    unit_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    
    # Product variations (size, color, etc.)
    variant_attributes = Column(Text, nullable=True)  # JSON string
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, product='{self.product_name}', qty={self.quantity})>"

class OrderTransaction(Base):
    __tablename__ = "order_transactions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)  # Changed from Integer to String(36)
    transaction_reference = Column(String(100), unique=True, nullable=False, index=True)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)  # Changed from Integer to String(36)
    
    # Payment details - Using DECIMAL for precise amount tracking
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="COP")
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    
    # Payment method information
    payment_method_type = Column(String(50), nullable=False)  # card, pse, nequi, etc.
    payment_method_id = Column(String(36), ForeignKey("payment_methods.id"), nullable=True)  # Changed from Integer to String(36)
    
    # Gateway specific data
    gateway = Column(String(50), nullable=False, default="wompi")
    gateway_transaction_id = Column(String(200), nullable=True, index=True)
    gateway_reference = Column(String(200), nullable=True)
    gateway_response = Column(Text, nullable=True)  # JSON response from gateway
    
    # Transaction timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Failure information
    failure_reason = Column(Text, nullable=True)
    failure_code = Column(String(50), nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="transactions")
    payment_method = relationship("PaymentMethod", back_populates="transactions")
    webhook_events = relationship("WebhookEvent", back_populates="transaction")
    
    def __repr__(self):
        return f"<OrderTransaction(id={self.id}, ref='{self.transaction_reference}', status={self.status})>"

# Alias for backwards compatibility
Transaction = OrderTransaction

class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)  # Changed from Integer to String(36)
    buyer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Method type and details
    method_type = Column(String(50), nullable=False)  # card, pse, nequi, bancolombia_transfer
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Card details (if applicable)
    card_brand = Column(String(50), nullable=True)  # visa, mastercard, etc.
    card_last_four = Column(String(4), nullable=True)
    card_exp_month = Column(String(2), nullable=True)
    card_exp_year = Column(String(4), nullable=True)
    card_holder_name = Column(String(200), nullable=True)
    
    # PSE bank details (if applicable)
    pse_bank_code = Column(String(10), nullable=True)
    pse_bank_name = Column(String(200), nullable=True)
    pse_user_type = Column(String(20), nullable=True)  # 0=natural, 1=juridica
    pse_user_dni = Column(String(50), nullable=True)
    
    # Gateway tokenization
    gateway_token = Column(String(500), nullable=True)
    gateway_customer_id = Column(String(200), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    buyer = relationship("User", back_populates="payment_methods")
    transactions = relationship("OrderTransaction", back_populates="payment_method")
    
    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, type={self.method_type}, buyer={self.buyer_id})>"


def _ensure_cache_entry(order: Order) -> Dict[str, Any]:
    cache_entry = ORDER_RUNTIME_CACHE.get(str(order.id))
    if not cache_entry:
        cache_entry = {
            "id": str(order.id),
            "order_number": order.order_number,
            "buyer_id": str(order.buyer_id),
            "buyer_email": getattr(order.buyer, "email", None),
            "status": order.status.value if hasattr(order.status, "value") else str(order.status),
            "total_amount": float(order.total_amount),
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "shipping_name": order.shipping_name,
            "shipping_city": order.shipping_city,
            "notes": order.notes,
            "items": [],
            "transactions": []
        }
        ORDER_RUNTIME_CACHE[str(order.id)] = cache_entry
    return cache_entry


@event.listens_for(Order, "after_insert")
def cache_order_after_insert(mapper, connection, target: Order):
    _ensure_cache_entry(target)


@event.listens_for(Order, "after_update")
def cache_order_after_update(mapper, connection, target: Order):
    cache_entry = _ensure_cache_entry(target)
    cache_entry.update(
        {
            "status": target.status.value if hasattr(target.status, "value") else str(target.status),
            "notes": target.notes,
            "buyer_email": getattr(target.buyer, "email", cache_entry.get("buyer_email")),
        }
    )


@event.listens_for(OrderItem, "after_insert")
def cache_order_item_after_insert(mapper, connection, target: OrderItem):
    order_entry = ORDER_RUNTIME_CACHE.setdefault(
        str(target.order_id),
        {
            "id": str(target.order_id),
            "order_number": None,
            "buyer_id": None,
            "buyer_email": None,
            "status": None,
            "total_amount": None,
            "created_at": None,
            "shipping_name": None,
            "shipping_city": None,
            "notes": None,
            "items": [],
            "transactions": []
        }
    )
    order_entry.setdefault("items", [])
    order_entry["items"].append(
        {
            "id": str(target.id),
            "product_id": str(target.product_id),
            "product_name": target.product_name,
            "product_sku": target.product_sku,
            "quantity": target.quantity,
            "unit_price": float(target.unit_price),
            "total_price": float(target.total_price),
        }
    )


@event.listens_for(OrderTransaction, "after_insert")
def cache_order_transaction_after_insert(mapper, connection, target: OrderTransaction):
    order_entry = ORDER_RUNTIME_CACHE.setdefault(
        str(target.order_id),
        {
            "id": str(target.order_id),
            "order_number": None,
            "buyer_id": None,
            "buyer_email": None,
            "status": None,
            "total_amount": None,
            "created_at": None,
            "shipping_name": None,
            "shipping_city": None,
            "notes": None,
            "items": [],
            "transactions": []
        }
    )
    order_entry.setdefault("transactions", [])
    order_entry["transactions"].append(
        {
            "id": str(target.id),
            "amount": float(target.amount),
            "currency": target.currency,
            "status": target.status.value if hasattr(target.status, "value") else str(target.status),
            "payment_method_type": target.payment_method_type,
            "created_at": target.created_at.isoformat() if target.created_at else None,
        }
    )
