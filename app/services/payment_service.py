"""
Comprehensive Payment Service with Wompi Integration
===================================================

Production-ready payment service that integrates Wompi payment gateway
with fraud detection, caching, and comprehensive error handling.

Author: Backend Framework AI
Date: 2025-09-17
Purpose: Centralized payment processing with Wompi integration for FastAPI DI
"""

import asyncio
import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from uuid import UUID, uuid4

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

# Core imports
from app.core.config import settings
from app.models.transaction import Transaction, TransactionStatus, PaymentMethod
from app.models.order import Order
from app.models.user import User
from app.services.cache_service import CacheService
from app.services.fraud_detection_service import FraudDetectionService

logger = logging.getLogger(__name__)


class WompiConfig:
    """Wompi payment gateway configuration"""

    def __init__(self):
        self.public_key = settings.WOMPI_PUBLIC_KEY
        self.private_key = settings.WOMPI_PRIVATE_KEY
        self.environment = settings.WOMPI_ENVIRONMENT
        self.webhook_secret = settings.WOMPI_WEBHOOK_SECRET
        self.base_url = settings.WOMPI_BASE_URL

        # API endpoints
        self.endpoints = {
            "acceptance_token": "/merchants/{}",
            "payment_sources": "/payment_sources",
            "transactions": "/transactions",
            "payment_methods": "/payment_methods",
            "token_credit_card": "/tokens/cards",
            "token_nequi": "/tokens/nequi"
        }

    def get_merchant_id(self) -> str:
        """Extract merchant ID from public key"""
        # Wompi public keys format: pub_test_xxxxx or pub_prod_xxxxx
        return self.public_key.split('_')[-1] if self.public_key else ""

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production" and self.public_key.startswith("pub_prod_")


class WompiApiClient:
    """HTTP client for Wompi API communication"""

    def __init__(self, config: WompiConfig):
        self.config = config
        self.timeout = httpx.Timeout(30.0)

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        use_private_key: bool = False
    ) -> Dict[str, Any]:
        """Make authenticated request to Wompi API"""

        # Set authentication
        auth_headers = {}
        if use_private_key:
            auth_headers["Authorization"] = f"Bearer {self.config.private_key}"
        else:
            auth_headers["Authorization"] = f"Bearer {self.config.public_key}"

        # Merge headers
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **auth_headers,
            **(headers or {})
        }

        url = f"{self.config.base_url}{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=request_headers, params=data)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=request_headers, json=data)
                elif method.upper() == "PUT":
                    response = await client.put(url, headers=request_headers, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            logger.error(f"Wompi API timeout for {method} {endpoint}")
            raise Exception("Payment gateway timeout")
        except httpx.HTTPStatusError as e:
            logger.error(f"Wompi API error {e.response.status_code}: {e.response.text}")
            raise Exception(f"Payment gateway error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Wompi API communication error: {str(e)}")
            raise Exception("Payment gateway communication error")

    async def get_acceptance_token(self) -> str:
        """Get merchant acceptance token"""
        merchant_id = self.config.get_merchant_id()
        endpoint = self.config.endpoints["acceptance_token"].format(merchant_id)

        response = await self._make_request("GET", endpoint)
        return response["data"]["presigned_acceptance"]["acceptance_token"]

    async def create_payment_source(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create payment source (tokenize payment method)"""
        return await self._make_request(
            "POST",
            self.config.endpoints["payment_sources"],
            data=source_data,
            use_private_key=True
        )

    async def create_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create payment transaction"""
        return await self._make_request(
            "POST",
            self.config.endpoints["transactions"],
            data=transaction_data,
            use_private_key=True
        )

    async def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction status"""
        endpoint = f"{self.config.endpoints['transactions']}/{transaction_id}"
        return await self._make_request("GET", endpoint, use_private_key=True)


class PaymentService:
    """
    Comprehensive payment service with Wompi integration, fraud detection, and caching.
    """

    def __init__(self, cache_service: Optional[CacheService] = None, fraud_service: Optional[FraudDetectionService] = None):
        self.wompi_config = WompiConfig()
        self.wompi_client = WompiApiClient(self.wompi_config)
        self.cache_service = cache_service
        self.fraud_service = fraud_service

        # Payment configuration
        self.supported_currencies = ["COP"]
        self.min_amount = Decimal("1000")  # Minimum 1000 COP
        self.max_amount = Decimal("50000000")  # Maximum 50M COP

    async def validate_payment_request(
        self,
        amount: Decimal,
        currency: str,
        payment_method: str,
        user: User,
        order: Optional[Order] = None
    ) -> Dict[str, Any]:
        """
        Validate payment request with comprehensive checks.
        """
        validation_errors = []

        # Validate amount
        if amount < self.min_amount:
            validation_errors.append(f"Amount too low. Minimum: {self.min_amount} {currency}")

        if amount > self.max_amount:
            validation_errors.append(f"Amount too high. Maximum: {self.max_amount} {currency}")

        # Validate currency
        if currency not in self.supported_currencies:
            validation_errors.append(f"Unsupported currency: {currency}")

        # Validate payment method
        valid_methods = ["CARD", "NEQUI", "PSE", "BANCOLOMBIA_TRANSFER"]
        if payment_method not in valid_methods:
            validation_errors.append(f"Unsupported payment method: {payment_method}")

        # Validate user
        if not user.is_active:
            validation_errors.append("User account is not active")

        # Fraud detection if available
        if self.fraud_service:
            fraud_check = await self.fraud_service.check_payment_fraud(
                user_id=user.id,
                amount=amount,
                payment_method=payment_method,
                order=order
            )

            if fraud_check.get("is_fraudulent"):
                validation_errors.append(f"Payment blocked by fraud detection: {fraud_check.get('reason')}")

        return {
            "is_valid": len(validation_errors) == 0,
            "errors": validation_errors
        }

    async def create_payment_intent(
        self,
        db: AsyncSession,
        amount: Decimal,
        currency: str,
        payment_method: str,
        user: User,
        order: Optional[Order] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create payment intent with Wompi integration.
        """
        logger.info(f"Creating payment intent for user {user.id}, amount: {amount} {currency}")

        # Validate payment request
        validation = await self.validate_payment_request(amount, currency, payment_method, user, order)
        if not validation["is_valid"]:
            raise ValueError(f"Payment validation failed: {validation['errors']}")

        try:
            # Get acceptance token
            acceptance_token = await self.wompi_client.get_acceptance_token()

            # Create transaction record
            transaction = Transaction(
                id=uuid4(),
                amount=amount,
                currency=currency,
                status=TransactionStatus.PENDING,
                payment_method=PaymentMethod(payment_method),
                user_id=user.id,
                order_id=order.id if order else None,
                gateway_transaction_id=None,
                metadata=metadata or {},
                created_at=datetime.utcnow()
            )

            db.add(transaction)
            await db.commit()
            await db.refresh(transaction)

            # Prepare Wompi transaction data
            transaction_data = {
                "amount_in_cents": int(amount * 100),  # Convert to cents
                "currency": currency,
                "customer_email": user.email,
                "reference": f"MS-{transaction.id}",
                "acceptance_token": acceptance_token,
                "payment_method": {
                    "type": payment_method.lower(),
                    "installments": 1 if payment_method == "CARD" else None
                },
                "shipping_address": self._get_shipping_address(order) if order else None,
                "redirect_url": f"{settings.FRONTEND_URL}/payment/result"
            }

            # Create payment with Wompi
            wompi_response = await self.wompi_client.create_transaction(transaction_data)

            # Update transaction with gateway ID
            transaction.gateway_transaction_id = wompi_response["data"]["id"]
            transaction.gateway_response = wompi_response
            await db.commit()

            # Cache transaction for quick lookup
            if self.cache_service:
                await self.cache_service.set(
                    f"payment_intent:{transaction.id}",
                    {
                        "transaction_id": str(transaction.id),
                        "wompi_id": wompi_response["data"]["id"],
                        "status": transaction.status.value,
                        "amount": str(amount),
                        "currency": currency
                    },
                    ttl=3600  # 1 hour
                )

            logger.info(f"Payment intent created successfully: {transaction.id}")

            return {
                "transaction_id": str(transaction.id),
                "wompi_transaction_id": wompi_response["data"]["id"],
                "payment_url": wompi_response["data"]["payment_link_url"],
                "status": transaction.status.value,
                "amount": str(amount),
                "currency": currency,
                "reference": transaction_data["reference"]
            }

        except Exception as e:
            # Rollback transaction
            await db.rollback()
            logger.error(f"Error creating payment intent: {str(e)}")
            raise Exception(f"Failed to create payment intent: {str(e)}")

    async def process_webhook(
        self,
        db: AsyncSession,
        webhook_data: Dict[str, Any],
        signature: str
    ) -> Dict[str, Any]:
        """
        Process Wompi webhook with signature validation.
        """
        logger.info("Processing Wompi webhook")

        # Validate webhook signature
        if not self._validate_webhook_signature(webhook_data, signature):
            logger.warning("Invalid webhook signature")
            raise ValueError("Invalid webhook signature")

        try:
            event_type = webhook_data.get("event")
            transaction_data = webhook_data.get("data", {})
            wompi_transaction_id = transaction_data.get("id")

            if not wompi_transaction_id:
                raise ValueError("Missing transaction ID in webhook")

            # Find transaction by gateway ID
            stmt = select(Transaction).where(
                Transaction.gateway_transaction_id == wompi_transaction_id
            )
            result = await db.execute(stmt)
            transaction = result.scalar_one_or_none()

            if not transaction:
                logger.warning(f"Transaction not found for Wompi ID: {wompi_transaction_id}")
                return {"status": "ignored", "reason": "transaction_not_found"}

            # Process based on event type
            old_status = transaction.status

            if event_type == "transaction.updated":
                new_status = self._map_wompi_status(transaction_data.get("status"))
                transaction.status = new_status
                transaction.gateway_response = webhook_data
                transaction.updated_at = datetime.utcnow()

                # Update related order if exists
                if transaction.order_id and new_status == TransactionStatus.APPROVED:
                    await self._update_order_payment_status(db, transaction.order_id, "paid")

            await db.commit()

            # Update cache
            if self.cache_service:
                await self.cache_service.delete(f"payment_intent:{transaction.id}")

            # Log status change
            if old_status != transaction.status:
                logger.info(
                    f"Transaction {transaction.id} status changed: {old_status.value} -> {transaction.status.value}"
                )

            return {
                "status": "processed",
                "transaction_id": str(transaction.id),
                "old_status": old_status.value,
                "new_status": transaction.status.value
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"Error processing webhook: {str(e)}")
            raise Exception(f"Webhook processing failed: {str(e)}")

    async def get_payment_status(
        self,
        db: AsyncSession,
        transaction_id: UUID
    ) -> Dict[str, Any]:
        """
        Get current payment status with caching.
        """
        # Check cache first
        if self.cache_service:
            cached_status = await self.cache_service.get(f"payment_status:{transaction_id}")
            if cached_status:
                return cached_status

        # Get from database
        stmt = select(Transaction).where(Transaction.id == transaction_id)
        result = await db.execute(stmt)
        transaction = result.scalar_one_or_none()

        if not transaction:
            raise ValueError(f"Transaction not found: {transaction_id}")

        # Optionally sync with Wompi if needed
        if transaction.gateway_transaction_id and transaction.status == TransactionStatus.PENDING:
            try:
                wompi_data = await self.wompi_client.get_transaction(transaction.gateway_transaction_id)
                new_status = self._map_wompi_status(wompi_data["data"]["status"])

                if new_status != transaction.status:
                    transaction.status = new_status
                    transaction.updated_at = datetime.utcnow()
                    await db.commit()

            except Exception as e:
                logger.warning(f"Failed to sync with Wompi: {str(e)}")

        status_data = {
            "transaction_id": str(transaction.id),
            "status": transaction.status.value,
            "amount": str(transaction.amount),
            "currency": transaction.currency,
            "payment_method": transaction.payment_method.value,
            "created_at": transaction.created_at.isoformat(),
            "updated_at": transaction.updated_at.isoformat() if transaction.updated_at else None,
            "gateway_transaction_id": transaction.gateway_transaction_id
        }

        # Cache status
        if self.cache_service:
            await self.cache_service.set(
                f"payment_status:{transaction_id}",
                status_data,
                ttl=300  # 5 minutes
            )

        return status_data

    def _validate_webhook_signature(self, webhook_data: Dict[str, Any], signature: str) -> bool:
        """Validate Wompi webhook signature"""
        if not self.wompi_config.webhook_secret:
            logger.warning("Webhook secret not configured, skipping validation")
            return True

        # Create payload string
        payload = json.dumps(webhook_data, sort_keys=True, separators=(',', ':'))

        # Calculate expected signature
        expected_signature = hmac.new(
            self.wompi_config.webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def _map_wompi_status(self, wompi_status: str) -> TransactionStatus:
        """Map Wompi transaction status to internal status"""
        status_mapping = {
            "APPROVED": TransactionStatus.APPROVED,
            "PENDING": TransactionStatus.PENDING,
            "DECLINED": TransactionStatus.FAILED,
            "VOIDED": TransactionStatus.CANCELLED,
            "ERROR": TransactionStatus.FAILED
        }

        return status_mapping.get(wompi_status, TransactionStatus.PENDING)

    def _get_shipping_address(self, order: Order) -> Optional[Dict[str, str]]:
        """Extract shipping address from order"""
        if not order or not hasattr(order, 'shipping_address'):
            return None

        return {
            "address_line_1": getattr(order.shipping_address, 'address_line_1', ''),
            "address_line_2": getattr(order.shipping_address, 'address_line_2', ''),
            "country": getattr(order.shipping_address, 'country', 'CO'),
            "region": getattr(order.shipping_address, 'region', ''),
            "city": getattr(order.shipping_address, 'city', ''),
            "postal_code": getattr(order.shipping_address, 'postal_code', '')
        }

    async def _update_order_payment_status(self, db: AsyncSession, order_id: UUID, status: str):
        """Update order payment status"""
        stmt = update(Order).where(Order.id == order_id).values(
            payment_status=status,
            updated_at=datetime.utcnow()
        )
        await db.execute(stmt)

    async def get_payment_methods(self) -> List[Dict[str, Any]]:
        """Get available payment methods for Colombia"""
        if self.cache_service:
            cached_methods = await self.cache_service.get("payment_methods")
            if cached_methods:
                return cached_methods

        # Default payment methods for Colombia
        payment_methods = [
            {
                "type": "CARD",
                "name": "Tarjeta de Crédito/Débito",
                "description": "Visa, Mastercard, American Express",
                "fees": "2.9% + $900 COP",
                "min_amount": 1000,
                "max_amount": 50000000
            },
            {
                "type": "NEQUI",
                "name": "Nequi",
                "description": "Pago a través de la app Nequi",
                "fees": "1.9% + $900 COP",
                "min_amount": 1000,
                "max_amount": 2000000
            },
            {
                "type": "PSE",
                "name": "PSE",
                "description": "Pago a través de PSE",
                "fees": "$3.500 COP por transacción",
                "min_amount": 1600,
                "max_amount": 50000000
            }
        ]

        # Cache payment methods
        if self.cache_service:
            await self.cache_service.set("payment_methods", payment_methods, ttl=3600)

        return payment_methods


# Global payment service instance for dependency injection
_payment_service: Optional[PaymentService] = None


async def get_payment_service(
    cache_service: Optional[CacheService] = None,
    fraud_service: Optional[FraudDetectionService] = None
) -> PaymentService:
    """Dependency function to get payment service instance"""
    global _payment_service

    if _payment_service is None:
        _payment_service = PaymentService(cache_service, fraud_service)

    return _payment_service