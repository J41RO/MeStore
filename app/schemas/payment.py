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


# Webhook Models
class WebhookRequest(BaseModel):
    """Webhook notification from Wompi"""
    data: Dict[str, Any] = Field(..., description="Webhook payload data")
    timestamp: str = Field(..., description="Webhook timestamp")
    signature: Optional[str] = Field(None, description="Webhook signature for verification")


class WebhookResponse(BaseModel):
    """Response after processing webhook"""
    success: bool = Field(..., description="Whether webhook was processed successfully")
    message: Optional[str] = Field(None, description="Processing message")
    transaction_id: Optional[str] = Field(None, description="Associated transaction ID")
