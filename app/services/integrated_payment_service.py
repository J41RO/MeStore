"""
Integrated Payment Service
==========================

Comprehensive payment processing service that integrates Wompi payment gateway
with order processing, fraud detection, and commission calculation.

This service orchestrates the complete payment flow:
- Order validation and preparation
- Fraud detection screening
- Wompi payment processing
- Transaction recording
- Commission calculation
- Order status updates
- Webhook handling

Author: System Architect AI
Date: 2025-09-17
Purpose: Complete integration of payment processing with business logic
"""

import asyncio
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status

# Import payment services
from app.services.payments.wompi_service import WompiService, WompiError
from app.services.payments.payu_service import get_payu_service
from app.services.payments.fraud_detection_service import FraudDetectionService
from app.services.payments.payment_commission_service import PaymentCommissionService
from app.services.payments.webhook_handler import WompiWebhookHandler

# Import models
from app.models.order import Order, OrderStatus, PaymentStatus, Transaction
from app.models.user import User
from app.models.product import Product
from app.models.commission import Commission

# Import core services
from app.core.config import settings
from app.services.audit_logging_service import AuditLoggingService

logger = logging.getLogger(__name__)


class PaymentProcessingError(Exception):
    """Payment processing specific error"""
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)


class IntegratedPaymentService:
    """
    Integrated payment service orchestrating complete payment flow.
    """

    def __init__(self, db: AsyncSession = None):
        self.wompi_service = WompiService()
        self.fraud_service = None  # Will be initialized with db when needed
        self.commission_service = None  # Will be initialized with db when needed
        self.webhook_handler = None  # Will be initialized with db when needed
        self.audit_service = AuditLoggingService

    def _ensure_services_initialized(self, db: AsyncSession):
        """Initialize services that require database session."""
        if self.fraud_service is None:
            self.fraud_service = FraudDetectionService(db)
        if self.commission_service is None:
            self.commission_service = PaymentCommissionService(db)
        if self.webhook_handler is None:
            self.webhook_handler = WompiWebhookHandler(db)

    async def create_payment_intent(
        self,
        amount: int,
        currency: str,
        description: Optional[str] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Create a payment intent for processing payments.

        Args:
            amount: Payment amount in cents
            currency: Currency code (e.g., COP)
            description: Payment description
            user_id: User making the payment

        Returns:
            Dict with payment intent data
        """
        try:
            logger.info(f"Creating payment intent for amount {amount} {currency}")

            # Generate payment intent ID and client secret
            payment_intent_id = f"pi_{uuid4().hex[:16]}"
            client_secret = f"pi_{uuid4().hex[:16]}_secret_{uuid4().hex[:16]}"

            # For now, return a mock payment intent
            # In production, this would call Wompi's API
            return {
                "payment_intent_id": payment_intent_id,
                "client_secret": client_secret,
                "amount": amount,
                "currency": currency,
                "status": "requires_payment_method"
            }

        except Exception as e:
            logger.error(f"Error creating payment intent: {str(e)}")
            raise PaymentProcessingError(
                message="Failed to create payment intent",
                error_code="INTENT_CREATION_FAILED",
                details={"error": str(e)}
            )

    async def confirm_payment(
        self,
        payment_intent_id: str,
        payment_method_id: str,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Confirm a payment intent with a payment method.

        Args:
            payment_intent_id: Payment intent ID to confirm
            payment_method_id: Payment method ID
            user_id: User confirming the payment

        Returns:
            Dict with payment confirmation results
        """
        try:
            logger.info(f"Confirming payment intent {payment_intent_id}")

            # For now, return a mock confirmation
            # In production, this would call Wompi's API to confirm the payment
            return {
                "status": "succeeded",
                "payment_intent_id": payment_intent_id,
                "amount": 250000  # Mock amount
            }

        except Exception as e:
            logger.error(f"Error confirming payment: {str(e)}")
            raise PaymentProcessingError(
                message="Failed to confirm payment",
                error_code="PAYMENT_CONFIRMATION_FAILED",
                details={"error": str(e)}
            )

    async def process_order_payment(
        self,
        order_id: int,
        payment_method: str,
        payment_data: Dict[str, Any],
        db: AsyncSession,
        user: User = None,
        ip_address: str = None
    ) -> Dict[str, Any]:
        """
        Process payment for an order with complete integration.

        Args:
            order_id: Order ID to process payment for
            payment_method: Payment method (credit_card, debit_card, etc.)
            payment_data: Payment method specific data
            db: Database session
            user: User making the payment
            ip_address: Client IP for fraud detection

        Returns:
            Dict with payment processing results
        """
        # Initialize services with database session
        self._ensure_services_initialized(db)

        transaction_id = str(uuid4())

        try:
            # Log payment attempt
            await self.audit_service.log_payment_attempt(
                order_id=order_id,
                user_id=user.id if user else None,
                amount=0,  # Will be updated
                method=payment_method,
                ip_address=ip_address
            )

            # 1. Validate and prepare order
            order = await self._validate_and_prepare_order(order_id, db)
            if not order:
                raise PaymentProcessingError(
                    f"Order {order_id} not found or cannot be processed",
                    "ORDER_NOT_FOUND"
                )

            # 2. Fraud detection screening
            fraud_result = await self._screen_for_fraud(
                order, payment_data, user, ip_address
            )

            if fraud_result.get("blocked", False):
                await self._handle_fraud_block(order, fraud_result, db)
                raise PaymentProcessingError(
                    "Transaction blocked by fraud detection",
                    "FRAUD_DETECTED",
                    fraud_result
                )

            # 3. Create transaction record
            transaction = await self._create_transaction_record(
                order, payment_method, transaction_id, db
            )

            # 4. Process payment with Wompi
            payment_result = await self._process_wompi_payment(
                order, payment_method, payment_data, transaction_id
            )

            # 5. Update transaction with Wompi response
            await self._update_transaction_status(
                transaction, payment_result, db
            )

            # 6. Calculate and record commissions
            if payment_result.get("status") == "approved":
                await self._calculate_commissions(order, transaction, db)

            # 7. Update order status
            await self._update_order_status(order, payment_result, db)

            # 8. Log successful payment
            await self.audit_service.log_payment_success(
                order_id=order_id,
                transaction_id=transaction_id,
                amount=float(order.total_amount),
                wompi_transaction_id=payment_result.get("transaction_id")
            )

            return {
                "success": True,
                "order_id": order_id,
                "transaction_id": transaction_id,
                "wompi_transaction_id": payment_result.get("transaction_id"),
                "status": payment_result.get("status"),
                "payment_url": payment_result.get("payment_url"),
                "fraud_score": fraud_result.get("risk_score", 0)
            }

        except PaymentProcessingError:
            # Re-raise payment errors
            raise
        except WompiError as e:
            # Handle Wompi specific errors
            await self.audit_service.log_payment_error(
                order_id=order_id,
                error=str(e),
                error_code=e.error_code
            )
            raise PaymentProcessingError(
                f"Payment gateway error: {e.message}",
                e.error_code,
                e.response_data
            )
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error in payment processing: {str(e)}")
            await self.audit_service.log_payment_error(
                order_id=order_id,
                error=str(e),
                error_code="INTERNAL_ERROR"
            )
            raise PaymentProcessingError(
                "Internal payment processing error",
                "INTERNAL_ERROR",
                {"original_error": str(e)}
            )

    async def handle_payment_webhook(
        self,
        webhook_data: Dict[str, Any],
        signature: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Handle payment webhook from Wompi.

        Args:
            webhook_data: Webhook payload
            signature: Webhook signature for verification
            db: Database session

        Returns:
            Dict with webhook processing results
        """
        try:
            # Verify webhook signature
            if not await self.webhook_handler.verify_signature(webhook_data, signature):
                raise PaymentProcessingError(
                    "Invalid webhook signature",
                    "INVALID_SIGNATURE"
                )

            # Process webhook
            result = await self.webhook_handler.handle_webhook(webhook_data, db)

            # Update order and transaction status
            if "transaction_id" in result:
                await self._update_from_webhook(result, db)

            return {
                "success": True,
                "processed": True,
                "transaction_id": result.get("transaction_id")
            }

        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            raise PaymentProcessingError(
                f"Webhook processing failed: {str(e)}",
                "WEBHOOK_ERROR"
            )

    async def get_payment_status(
        self,
        order_id: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get comprehensive payment status for an order.

        Args:
            order_id: Order ID
            db: Database session

        Returns:
            Dict with payment status information
        """
        try:
            # Get order with transaction data
            stmt = select(Order).where(Order.id == order_id)
            result = await db.execute(stmt)
            order = result.scalar_one_or_none()

            if not order:
                raise PaymentProcessingError(
                    f"Order {order_id} not found",
                    "ORDER_NOT_FOUND"
                )

            # Get latest transaction
            stmt = select(Transaction).where(
                Transaction.order_id == order_id
            ).order_by(Transaction.created_at.desc())
            result = await db.execute(stmt)
            transaction = result.scalar_one_or_none()

            # Get Wompi transaction status if available
            wompi_status = None
            if transaction and transaction.wompi_transaction_id:
                try:
                    wompi_status = await self.wompi_service.get_transaction_status(
                        transaction.wompi_transaction_id
                    )
                except Exception as e:
                    logger.warning(f"Failed to get Wompi status: {str(e)}")

            return {
                "order_id": order_id,
                "order_status": order.status.value,
                "payment_status": transaction.status.value if transaction else "none",
                "transaction_id": transaction.id if transaction else None,
                "wompi_transaction_id": transaction.wompi_transaction_id if transaction else None,
                "amount": float(order.total_amount),
                "wompi_status": wompi_status,
                "last_updated": transaction.updated_at.isoformat() if transaction else None
            }

        except PaymentProcessingError:
            raise
        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            raise PaymentProcessingError(
                f"Failed to get payment status: {str(e)}",
                "STATUS_ERROR"
            )

    async def _validate_and_prepare_order(
        self,
        order_id: int,
        db: AsyncSession
    ) -> Optional[Order]:
        """Validate order can be processed for payment"""
        stmt = select(Order).where(Order.id == order_id)
        result = await db.execute(stmt)
        order = result.scalar_one_or_none()

        if not order:
            return None

        # Check if order is in valid state for payment
        if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            logger.warning(f"Order {order_id} in invalid state for payment: {order.status}")
            return None

        return order

    async def _screen_for_fraud(
        self,
        order: Order,
        payment_data: Dict[str, Any],
        user: User,
        ip_address: str
    ) -> Dict[str, Any]:
        """Screen transaction for fraud"""
        transaction_data = {
            "order_id": order.id,
            "amount": float(order.total_amount),
            "user_id": user.id if user else None,
            "ip_address": ip_address,
            "payment_method": payment_data.get("method"),
            "card_bin": payment_data.get("card_bin"),
            "email": user.email if user else None
        }

        return await self.fraud_service.screen_transaction(transaction_data)

    async def _handle_fraud_block(
        self,
        order: Order,
        fraud_result: Dict[str, Any],
        db: AsyncSession
    ):
        """Handle blocked transaction due to fraud"""
        # Update order status
        stmt = update(Order).where(Order.id == order.id).values(
            status=OrderStatus.CANCELLED
        )
        await db.execute(stmt)
        await db.commit()

        # Log fraud event
        await self.audit_service.log_security_event(
            event_type="fraud_detection_block",
            order_id=order.id,
            details=fraud_result
        )

    async def _create_transaction_record(
        self,
        order: Order,
        payment_method: str,
        transaction_id: str,
        db: AsyncSession
    ) -> Transaction:
        """Create transaction record in database"""
        transaction = Transaction(
            id=transaction_id,
            order_id=order.id,
            amount=order.total_amount,
            payment_method=payment_method,
            status=PaymentStatus.PENDING,
            created_at=datetime.utcnow()
        )

        db.add(transaction)
        await db.commit()
        return transaction

    async def _process_wompi_payment(
        self,
        order: Order,
        payment_method: str,
        payment_data: Dict[str, Any],
        transaction_id: str
    ) -> Dict[str, Any]:
        """Process payment through Wompi gateway"""
        wompi_data = {
            "amount_in_cents": int(order.total_amount * 100),
            "currency": "COP",
            "customer_email": order.buyer.email if hasattr(order, "buyer") else None,
            "reference": f"order_{order.id}_{transaction_id}",
            "payment_method": payment_method,
            "payment_source_id": payment_data.get("payment_source_id"),
            "redirect_url": payment_data.get("redirect_url"),
            **payment_data
        }

        return await self.wompi_service.create_transaction(wompi_data)

    async def _update_transaction_status(
        self,
        transaction: Transaction,
        payment_result: Dict[str, Any],
        db: AsyncSession
    ):
        """Update transaction with Wompi response"""
        status_map = {
            "approved": PaymentStatus.APPROVED,
            "declined": PaymentStatus.DECLINED,
            "pending": PaymentStatus.PROCESSING,
            "error": PaymentStatus.ERROR
        }

        stmt = update(Transaction).where(Transaction.id == transaction.id).values(
            wompi_transaction_id=payment_result.get("transaction_id"),
            status=status_map.get(payment_result.get("status"), PaymentStatus.ERROR),
            wompi_response=payment_result,
            updated_at=datetime.utcnow()
        )
        await db.execute(stmt)
        await db.commit()

    async def _calculate_commissions(
        self,
        order: Order,
        transaction: Transaction,
        db: AsyncSession
    ):
        """Calculate and record commissions for approved payment"""
        try:
            await self.commission_service.calculate_order_commissions(
                order_id=order.id,
                transaction_id=transaction.id,
                db=db
            )
        except Exception as e:
            logger.error(f"Commission calculation failed: {str(e)}")
            # Don't fail the entire payment for commission errors

    async def _update_order_status(
        self,
        order: Order,
        payment_result: Dict[str, Any],
        db: AsyncSession
    ):
        """Update order status based on payment result"""
        status_map = {
            "approved": OrderStatus.CONFIRMED,
            "declined": OrderStatus.CANCELLED,
            "pending": OrderStatus.PENDING,
            "error": OrderStatus.PENDING
        }

        new_status = status_map.get(payment_result.get("status"), OrderStatus.PENDING)

        stmt = update(Order).where(Order.id == order.id).values(
            status=new_status,
            updated_at=datetime.utcnow()
        )
        await db.execute(stmt)
        await db.commit()

    async def _update_from_webhook(
        self,
        webhook_result: Dict[str, Any],
        db: AsyncSession
    ):
        """Update order and transaction from webhook data"""
        # Implementation depends on webhook_result structure
        # This would update order status based on final payment status
        pass

    async def get_payment_methods(self) -> List[Dict[str, Any]]:
        """Get available payment methods from Wompi"""
        try:
            return await self.wompi_service.get_payment_methods()
        except Exception as e:
            logger.error(f"Failed to get payment methods: {str(e)}")
            return []

    async def process_payment_with_fallback(
        self,
        order_id: str,
        amount: int,
        payment_method: str,
        payment_data: Dict[str, Any],
        db: AsyncSession,
        gateway_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process payment with automatic fallback to secondary gateway.

        This method implements intelligent gateway routing with automatic failover:
        1. Try primary/preferred gateway first
        2. If it fails, automatically fall back to secondary gateway
        3. Return error only if all gateways fail

        Args:
            order_id: Order ID to process payment for
            amount: Payment amount in cents
            payment_method: Payment method (credit_card, pse, etc.)
            payment_data: Payment method specific data
            db: Database session
            gateway_preference: Preferred gateway (wompi, payu) or None for auto-selection

        Returns:
            Dict with payment result including gateway used

        Raises:
            PaymentProcessingError: If all gateways fail
        """
        try:
            logger.info(
                f"Processing payment with fallback for order {order_id}, "
                f"method: {payment_method}, preference: {gateway_preference}"
            )

            # Determine gateway priority based on preference and configuration
            primary_gateway = gateway_preference or settings.PAYMENT_PRIMARY_GATEWAY
            gateways = self._get_gateway_priority(primary_gateway, payment_method)

            last_error = None

            # Try each gateway in priority order
            for gateway_name in gateways:
                try:
                    logger.info(f"Attempting payment via {gateway_name} gateway")

                    if gateway_name == "wompi":
                        result = await self._process_via_wompi(
                            order_id, amount, payment_method, payment_data, db
                        )
                    elif gateway_name == "payu":
                        result = await self._process_via_payu(
                            order_id, amount, payment_method, payment_data, db
                        )
                    else:
                        logger.warning(f"Unknown gateway: {gateway_name}, skipping")
                        continue

                    # If successful, return result
                    if result.get("success") or result.get("state") in ["APPROVED", "PENDING"]:
                        logger.info(f"Payment successful via {gateway_name}")
                        result["gateway_used"] = gateway_name
                        return result

                except WompiError as e:
                    last_error = e
                    logger.warning(
                        f"Gateway {gateway_name} failed: {e.message}. "
                        f"Attempting next gateway if available."
                    )
                    continue
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Gateway {gateway_name} error: {str(e)}. "
                        f"Attempting next gateway if available."
                    )
                    continue

            # All gateways failed
            error_message = f"All payment gateways failed. Last error: {str(last_error)}"
            logger.error(error_message)
            raise PaymentProcessingError(
                message="Payment processing failed across all gateways",
                error_code="ALL_GATEWAYS_FAILED",
                details={"last_error": str(last_error), "gateways_tried": gateways}
            )

        except PaymentProcessingError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in payment fallback: {str(e)}", exc_info=True)
            raise PaymentProcessingError(
                message="Unexpected payment processing error",
                error_code="PAYMENT_FALLBACK_ERROR",
                details={"error": str(e)}
            )

    def _get_gateway_priority(
        self,
        preferred_gateway: str,
        payment_method: str
    ) -> List[str]:
        """
        Determine gateway priority based on preference and payment method.

        Args:
            preferred_gateway: Preferred gateway (wompi, payu)
            payment_method: Payment method being used

        Returns:
            List of gateways in priority order
        """
        # Base priority
        if preferred_gateway == "wompi":
            gateways = ["wompi", "payu"]
        elif preferred_gateway == "payu":
            gateways = ["payu", "wompi"]
        else:
            # Default priority if not specified
            gateways = ["wompi", "payu"]

        # Method-specific adjustments
        # Some methods might work better with specific gateways
        if payment_method in ["nequi", "bancolombia_transfer"]:
            # These methods are Wompi-specific, only use Wompi
            gateways = ["wompi"]
        elif payment_method in ["baloto", "su_red"]:
            # These methods work better with PayU in Colombia
            if "payu" in gateways:
                gateways.remove("payu")
                gateways.insert(0, "payu")

        logger.debug(f"Gateway priority for {payment_method}: {gateways}")
        return gateways

    async def _process_via_wompi(
        self,
        order_id: str,
        amount: int,
        payment_method: str,
        payment_data: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Process payment via Wompi gateway"""
        try:
            # Use existing Wompi processing logic
            # This should use the wompi_service methods
            wompi_result = await self.wompi_service.create_transaction({
                "amount_in_cents": amount,
                "currency": "COP",
                "customer_email": payment_data.get("customer_email"),
                "payment_method": payment_method,
                "reference": f"ORDER-{order_id}",
                **payment_data
            })

            return {
                "success": wompi_result.get("status") == "APPROVED",
                "transaction_id": wompi_result.get("id"),
                "status": wompi_result.get("status"),
                "message": wompi_result.get("status_message"),
                "gateway": "wompi"
            }

        except Exception as e:
            logger.error(f"Wompi processing error: {str(e)}")
            raise

    async def _process_via_payu(
        self,
        order_id: str,
        amount: int,
        payment_method: str,
        payment_data: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Process payment via PayU gateway"""
        try:
            # Get order for reference
            from sqlalchemy import select
            stmt = select(Order).where(Order.id == order_id)
            result = await db.execute(stmt)
            order = result.scalar_one_or_none()

            if not order:
                raise PaymentProcessingError(
                    message="Order not found",
                    error_code="ORDER_NOT_FOUND"
                )

            # Build PayU transaction
            payu_transaction = {
                "merchant_id": settings.PAYU_MERCHANT_ID,
                "account_id": settings.PAYU_ACCOUNT_ID,
                "reference_code": f"ORDER-{order.order_number}",
                "description": f"MeStore Order {order.order_number}",
                "amount": amount,
                "currency": "COP",
                "payer": {
                    "email": payment_data.get("customer_email", payment_data.get("payer_email")),
                    "full_name": payment_data.get("customer_name", payment_data.get("payer_full_name")),
                    "phone": payment_data.get("customer_phone", payment_data.get("payer_phone"))
                },
                "payment_method": self._map_payment_method_to_payu(payment_method),
                **payment_data
            }

            payu_service = get_payu_service()
            payu_result = await payu_service.create_transaction(payu_transaction)

            return {
                "success": payu_result.get("state") in ["APPROVED", "PENDING"],
                "transaction_id": payu_result.get("transaction_id"),
                "state": payu_result.get("state"),
                "status": payu_result.get("state"),
                "message": payu_result.get("message"),
                "payment_url": payu_result.get("redirect_url"),
                "gateway": "payu"
            }

        except Exception as e:
            logger.error(f"PayU processing error: {str(e)}")
            raise

    def _map_payment_method_to_payu(self, method: str) -> str:
        """Map generic payment method to PayU-specific method"""
        method_map = {
            "credit_card": "CREDIT_CARD",
            "debit_card": "CREDIT_CARD",
            "pse": "PSE",
            "efecty": "EFECTY",
            "baloto": "BALOTO"
        }
        return method_map.get(method.lower(), "CREDIT_CARD")

    async def health_check(self) -> Dict[str, Any]:
        """Health check for integrated payment service"""
        health_status = {
            "service": "IntegratedPaymentService",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }

        # Check Wompi service
        try:
            wompi_health = await self.wompi_service.health_check()
            health_status["components"]["wompi"] = wompi_health
        except Exception as e:
            health_status["components"]["wompi"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Check fraud detection service
        try:
            fraud_health = await self.fraud_service.health_check()
            health_status["components"]["fraud_detection"] = fraud_health
        except Exception as e:
            health_status["components"]["fraud_detection"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Overall health
        all_healthy = all(
            comp.get("status") != "unhealthy"
            for comp in health_status["components"].values()
        )
        health_status["status"] = "healthy" if all_healthy else "degraded"

        return health_status


# Global instance for application use
integrated_payment_service = IntegratedPaymentService()