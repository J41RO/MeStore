"""
Payment Schemas for MeStore Payment System
==========================================

Comprehensive Pydantic schemas for payment processing, including:
- Payment method configuration and availability
- PSE bank information for Colombian bank transfers
- Payment intent creation and confirmation
- Transaction status and response models

Author: Payment Systems AI
Date: 2025-10-01
Purpose: Complete payment API schemas for Wompi integration
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# PSE Bank Information
class PSEBank(BaseModel):
    """Colombian PSE bank for online bank transfers"""
    financial_institution_code: str = Field(
        ...,
        description="Bank code for PSE transactions (e.g., '1007' for Bancolombia)"
    )
    financial_institution_name: str = Field(
        ...,
        description="Bank name in Spanish (e.g., 'BANCOLOMBIA')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "financial_institution_code": "1007",
                "financial_institution_name": "BANCOLOMBIA"
            }
        }


# Payment Methods Configuration
class PaymentMethodsResponse(BaseModel):
    """
    Complete payment methods configuration for frontend initialization.

    This response provides everything the frontend needs to:
    - Initialize Wompi payment widget
    - Display available payment methods
    - Configure PSE bank selector
    - Handle payment method specific requirements
    """
    # Payment method availability flags
    card_enabled: bool = Field(
        default=True,
        description="Credit/debit card payments available via Wompi"
    )
    pse_enabled: bool = Field(
        default=True,
        description="PSE bank transfer payments available"
    )
    nequi_enabled: bool = Field(
        default=False,
        description="Nequi digital wallet payments available (future feature)"
    )
    cash_enabled: bool = Field(
        default=True,
        description="Cash payments via Efecty network (future feature)"
    )

    # Wompi configuration for frontend
    wompi_public_key: str = Field(
        ...,
        description="Wompi public key for frontend widget initialization (NEVER expose private key)"
    )
    environment: str = Field(
        ...,
        description="Wompi environment: 'sandbox' for testing, 'production' for live transactions"
    )

    # PSE banks list for bank selector
    pse_banks: List[PSEBank] = Field(
        default_factory=list,
        description="Available Colombian banks for PSE transfers"
    )

    # Additional configuration
    currency: str = Field(
        default="COP",
        description="Default currency for all transactions (Colombian Pesos)"
    )
    min_amount: int = Field(
        default=1000,
        description="Minimum transaction amount in cents (10.00 COP)"
    )
    max_amount: int = Field(
        default=5000000000,
        description="Maximum transaction amount in cents (50,000,000.00 COP)"
    )

    # Card payment specific config
    card_installments_enabled: bool = Field(
        default=True,
        description="Whether card payments support installments"
    )
    max_installments: int = Field(
        default=36,
        description="Maximum installments available for card payments"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "card_enabled": True,
                "pse_enabled": True,
                "nequi_enabled": False,
                "cash_enabled": True,
                "wompi_public_key": "pub_test_xxxxxxxxxxxxxx",
                "environment": "sandbox",
                "pse_banks": [
                    {
                        "financial_institution_code": "1007",
                        "financial_institution_name": "BANCOLOMBIA"
                    },
                    {
                        "financial_institution_code": "1019",
                        "financial_institution_name": "SCOTIABANK COLPATRIA"
                    }
                ],
                "currency": "COP",
                "min_amount": 1000,
                "max_amount": 5000000000,
                "card_installments_enabled": True,
                "max_installments": 36
            }
        }


# Payment Intent Models (already exist in payments.py but included for completeness)
class CreatePaymentIntentRequest(BaseModel):
    """Request to create a payment intent"""
    amount: int = Field(..., gt=0, description="Payment amount in cents")
    currency: str = Field(default="COP", description="Currency code")
    description: Optional[str] = Field(None, description="Payment description")
    order_id: Optional[int] = Field(None, description="Associated order ID")


class PaymentIntentResponse(BaseModel):
    """Response after creating payment intent"""
    payment_intent_id: str = Field(..., description="Unique payment intent identifier")
    client_secret: str = Field(..., description="Client secret for frontend payment confirmation")
    amount: int = Field(..., description="Amount in cents")
    currency: str = Field(..., description="Currency code")
    status: str = Field(..., description="Payment intent status")


# Payment Confirmation Models
class ConfirmPaymentRequest(BaseModel):
    """Request to confirm a payment"""
    payment_intent_id: str = Field(..., description="Payment intent to confirm")
    payment_method_id: str = Field(..., description="Payment method identifier")


class PaymentConfirmationResponse(BaseModel):
    """Response after payment confirmation"""
    status: str = Field(..., description="Payment status (succeeded, failed, requires_action)")
    payment_intent_id: str = Field(..., description="Payment intent identifier")
    amount: Optional[int] = Field(None, description="Amount charged in cents")
    message: Optional[str] = Field(None, description="Human-readable message")


# Transaction Status Models
class PaymentStatusResponse(BaseModel):
    """Complete payment status for an order"""
    order_id: int = Field(..., description="Order identifier")
    order_status: str = Field(..., description="Order status (pending, confirmed, etc.)")
    payment_status: str = Field(..., description="Payment status (approved, declined, pending)")
    transaction_id: Optional[str] = Field(None, description="Internal transaction identifier")
    wompi_transaction_id: Optional[str] = Field(None, description="Wompi transaction identifier")
    amount: float = Field(..., description="Transaction amount")
    last_updated: Optional[str] = Field(None, description="Last status update timestamp")


# Payment Method Details (for individual method info)
class PaymentMethodDetail(BaseModel):
    """Detailed information about a specific payment method"""
    id: str = Field(..., description="Payment method identifier")
    type: str = Field(..., description="Method type (CARD, PSE, NEQUI, etc.)")
    name: str = Field(..., description="Human-readable method name")
    enabled: bool = Field(default=True, description="Whether method is currently available")
    description: Optional[str] = Field(None, description="Method description")
    logo_url: Optional[str] = Field(None, description="Payment method logo URL")
    processing_time: Optional[str] = Field(None, description="Expected processing time")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "card_visa",
                "type": "CARD",
                "name": "Visa Credit/Debit",
                "enabled": True,
                "description": "Pay with Visa card with up to 36 installments",
                "logo_url": "https://cdn.wompi.co/logos/visa.png",
                "processing_time": "immediate"
            }
        }


# Webhook Models for Wompi Integration
class WompiWebhookEvent(BaseModel):
    """
    Complete Wompi webhook event payload structure.

    Wompi sends this structure when transaction status changes.
    Documentation: https://docs.wompi.co/docs/en/eventos
    """
    event: str = Field(
        ...,
        description="Event type (e.g., 'transaction.updated')"
    )
    data: Dict[str, Any] = Field(
        ...,
        description="Transaction data object containing status, amount, reference, etc."
    )
    sent_at: datetime = Field(
        ...,
        description="ISO timestamp when Wompi sent the event"
    )
    timestamp: int = Field(
        ...,
        description="Unix timestamp of the event"
    )
    signature: Dict[str, Any] = Field(
        default_factory=dict,
        description="Signature information for verification"
    )
    environment: str = Field(
        ...,
        description="Wompi environment: 'test' or 'production'"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "event": "transaction.updated",
                "data": {
                    "id": "12345-1668624561-38705",
                    "amount_in_cents": 5000000,
                    "reference": "ORDER-2025-001",
                    "customer_email": "customer@example.com",
                    "currency": "COP",
                    "payment_method_type": "CARD",
                    "payment_method": {
                        "type": "CARD",
                        "extra": {
                            "name": "VISA-1234",
                            "brand": "VISA",
                            "last_four": "1234"
                        }
                    },
                    "status": "APPROVED",
                    "status_message": "Aprobada",
                    "shipping_address": None,
                    "redirect_url": "https://mestore.com/payment/success",
                    "payment_source_id": None,
                    "payment_link_id": None,
                    "created_at": "2025-10-01T10:30:00.000Z",
                    "finalized_at": "2025-10-01T10:30:45.000Z",
                    "taxes": []
                },
                "sent_at": "2025-10-01T10:30:50.000Z",
                "timestamp": 1696156250,
                "signature": {
                    "checksum": "abc123def456...",
                    "properties": ["id", "status", "amount_in_cents"]
                },
                "environment": "test"
            }
        }


class WompiTransaction(BaseModel):
    """
    Wompi transaction data from webhook.

    This is the structure inside the 'data' field of WompiWebhookEvent.
    """
    id: str = Field(..., description="Wompi transaction ID")
    amount_in_cents: int = Field(..., description="Transaction amount in cents")
    reference: str = Field(..., description="Merchant reference (order_number)")
    customer_email: str = Field(..., description="Customer email address")
    currency: str = Field(default="COP", description="Transaction currency")
    payment_method_type: str = Field(..., description="Payment method type (CARD, PSE, NEQUI)")
    payment_method: Optional[Dict[str, Any]] = Field(None, description="Payment method details")
    status: str = Field(..., description="Transaction status: APPROVED, DECLINED, PENDING, ERROR")
    status_message: Optional[str] = Field(None, description="Human-readable status message")
    created_at: str = Field(..., description="Transaction creation timestamp (ISO 8601)")
    finalized_at: Optional[str] = Field(None, description="Transaction finalization timestamp")
    redirect_url: Optional[str] = Field(None, description="Redirect URL after payment")
    payment_source_id: Optional[str] = Field(None, description="Payment source identifier")
    payment_link_id: Optional[str] = Field(None, description="Payment link identifier if applicable")
    shipping_address: Optional[Dict[str, Any]] = Field(None, description="Shipping address data")
    taxes: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Tax information")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "12345-1668624561-38705",
                "amount_in_cents": 5000000,
                "reference": "ORDER-2025-001",
                "customer_email": "customer@example.com",
                "currency": "COP",
                "payment_method_type": "CARD",
                "status": "APPROVED",
                "status_message": "Aprobada",
                "created_at": "2025-10-01T10:30:00.000Z",
                "finalized_at": "2025-10-01T10:30:45.000Z"
            }
        }


class WebhookProcessingResult(BaseModel):
    """Internal result of webhook processing"""
    success: bool = Field(..., description="Whether processing succeeded")
    event_id: str = Field(..., description="Webhook event ID")
    order_id: Optional[int] = Field(None, description="Associated order ID")
    transaction_id: Optional[str] = Field(None, description="Wompi transaction ID")
    status: str = Field(..., description="Processing status")
    message: Optional[str] = Field(None, description="Processing message or error")
    updated_order_status: Optional[str] = Field(None, description="New order status if updated")


class WebhookResponse(BaseModel):
    """
    Response to Wompi webhook request.

    CRITICAL: Always return 200 OK with this structure to prevent retry storms.
    Wompi retries failed webhooks exponentially, so we must acknowledge receipt.
    """
    status: str = Field(
        default="ok",
        description="Always 'ok' to acknowledge receipt"
    )
    message: Optional[str] = Field(
        default=None,
        description="Optional message (not read by Wompi)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok"
            }
        }
