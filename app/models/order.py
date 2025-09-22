from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum as PyEnum
from decimal import Decimal
from typing import Optional
import uuid

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

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    buyer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Order totals
    subtotal = Column(Float, nullable=False, default=0.0)
    tax_amount = Column(Float, nullable=False, default=0.0)
    shipping_cost = Column(Float, nullable=False, default=0.0)
    discount_amount = Column(Float, nullable=False, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    # Order status and dates
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
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
    
    # Relationships
    buyer = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    transactions = relationship("OrderTransaction", back_populates="order")
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

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Item details at time of purchase
    product_name = Column(String(500), nullable=False)
    product_sku = Column(String(100), nullable=False)
    product_image_url = Column(String(1000), nullable=True)
    
    # Pricing and quantity
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    
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

    id = Column(Integer, primary_key=True, index=True)
    transaction_reference = Column(String(100), unique=True, nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="COP")
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    
    # Payment method information
    payment_method_type = Column(String(50), nullable=False)  # card, pse, nequi, etc.
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=True)
    
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

    id = Column(Integer, primary_key=True, index=True)
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