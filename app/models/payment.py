from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum as PyEnum
from typing import Optional, Dict, Any
import uuid

class WebhookEventType(PyEnum):
    TRANSACTION_UPDATED = "transaction.updated"
    PAYMENT_CREATED = "payment.created"
    PAYMENT_UPDATED = "payment.updated"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_APPROVED = "payment.approved"
    PAYMENT_DECLINED = "payment.declined"
    PAYMENT_VOIDED = "payment.voided"
    PAYMENT_REFUNDED = "payment.refunded"

class WebhookEventStatus(PyEnum):
    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    IGNORED = "ignored"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_reference = Column(String(100), unique=True, nullable=False, index=True)
    transaction_id = Column(Integer, ForeignKey("order_transactions.id"), nullable=False)
    
    # Payment identification
    wompi_transaction_id = Column(String(200), nullable=True, index=True)
    wompi_payment_id = Column(String(200), nullable=True, index=True)
    
    # Amount and currency
    amount_in_cents = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False, default="COP")
    
    # Payment method details
    payment_method_type = Column(String(50), nullable=False)
    payment_method = Column(JSON, nullable=True)  # Full payment method object from Wompi
    
    # Customer information
    customer_email = Column(String(320), nullable=True)
    customer_data = Column(JSON, nullable=True)  # Customer info from Wompi
    
    # Payment status and lifecycle
    status = Column(String(50), nullable=False)
    status_message = Column(Text, nullable=True)
    
    # Gateway response data
    gateway_response = Column(JSON, nullable=True)  # Complete response from Wompi
    gateway_created_at = Column(DateTime(timezone=True), nullable=True)
    gateway_finalized_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    transaction = relationship("OrderTransaction", backref="payment")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, ref='{self.payment_reference}', status={self.status})>"

    @property
    def amount_in_currency(self):
        """Convert amount from cents to currency units"""
        return self.amount_in_cents / 100.0 if self.amount_in_cents else 0.0

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(100), unique=True, nullable=False, index=True)  # Wompi event ID
    transaction_id = Column(Integer, ForeignKey("order_transactions.id"), nullable=True)
    
    # Event details
    event_type = Column(Enum(WebhookEventType), nullable=False)
    event_status = Column(Enum(WebhookEventStatus), nullable=False, default=WebhookEventStatus.RECEIVED)
    
    # Webhook data
    raw_payload = Column(JSON, nullable=False)  # Complete webhook payload
    signature = Column(String(500), nullable=True)  # Webhook signature for validation
    signature_validated = Column(Boolean, default=False)
    
    # Processing details
    processed_at = Column(DateTime(timezone=True), nullable=True)
    processing_attempts = Column(Integer, default=0)
    processing_error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    gateway_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    transaction = relationship("OrderTransaction", back_populates="webhook_events")
    
    def __repr__(self):
        return f"<WebhookEvent(id={self.id}, type={self.event_type}, status={self.event_status})>"

class PaymentRefund(Base):
    __tablename__ = "payment_refunds"

    id = Column(Integer, primary_key=True, index=True)
    refund_reference = Column(String(100), unique=True, nullable=False, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("order_transactions.id"), nullable=False)
    
    # Refund details
    refund_amount_in_cents = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False, default="COP")
    reason = Column(Text, nullable=True)
    
    # Gateway details
    wompi_refund_id = Column(String(200), nullable=True, index=True)
    gateway_response = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(50), nullable=False)
    status_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    payment = relationship("Payment", backref="refunds")
    transaction = relationship("OrderTransaction", backref="refunds")
    
    def __repr__(self):
        return f"<PaymentRefund(id={self.id}, ref='{self.refund_reference}', status={self.status})>"

    @property
    def refund_amount_in_currency(self):
        """Convert refund amount from cents to currency units"""
        return self.refund_amount_in_cents / 100.0 if self.refund_amount_in_cents else 0.0

class PaymentIntent(Base):
    __tablename__ = "payment_intents"

    id = Column(Integer, primary_key=True, index=True)
    intent_reference = Column(String(100), unique=True, nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Intent details
    amount_in_cents = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False, default="COP")
    
    # Customer and billing
    customer_email = Column(String(320), nullable=False)
    billing_data = Column(JSON, nullable=True)  # Address and other billing info
    
    # Payment preferences
    payment_method_types = Column(JSON, nullable=True)  # Allowed payment methods
    redirect_url = Column(String(1000), nullable=True)
    
    # Wompi specific
    wompi_payment_link_id = Column(String(200), nullable=True, index=True)
    wompi_checkout_url = Column(String(1000), nullable=True)
    
    # Status and lifecycle  
    status = Column(String(50), nullable=False, default="created")
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    order = relationship("Order", backref="payment_intents")
    
    def __repr__(self):
        return f"<PaymentIntent(id={self.id}, ref='{self.intent_reference}', status={self.status})>"

    @property
    def amount_in_currency(self):
        """Convert amount from cents to currency units"""
        return self.amount_in_cents / 100.0 if self.amount_in_cents else 0.0

    @property
    def is_expired(self):
        """Check if payment intent has expired"""
        if not self.expires_at:
            return False
        return func.now() > self.expires_at