import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.order import Order, Transaction, PaymentMethod, PaymentStatus, OrderStatus
from app.models.payment import Payment, PaymentIntent, WebhookEvent, WebhookEventType, WebhookEventStatus
from app.models.user import User
from app.services.payments.wompi_service import get_wompi_service
from app.services.payments.fraud_detection_service import FraudDetectionService, FraudAction

logger = logging.getLogger(__name__)

class PaymentProcessor:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.wompi = get_wompi_service()
        self.fraud_detector = FraudDetectionService(db)

    async def create_payment_intent(
        self,
        order_id: int,
        customer_email: str,
        redirect_url: str,
        payment_method_types: Optional[List[str]] = None
    ) -> PaymentIntent:
        """Create a payment intent for an order"""
        try:
            # Get order details
            result = await self.db.execute(
                select(Order)
                .options(selectinload(Order.items))
                .where(Order.id == order_id)
            )
            order = result.scalar_one_or_none()
            
            if not order:
                raise ValueError(f"Order {order_id} not found")
                
            if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
                raise ValueError(f"Order {order_id} is not in a payable state")
            
            # Create payment intent record
            intent_reference = f"INTENT_{order_id}_{uuid.uuid4().hex[:8]}"
            
            payment_intent = PaymentIntent(
                intent_reference=intent_reference,
                order_id=order_id,
                amount_in_cents=self.wompi.amount_to_cents(order.total_amount),
                currency="COP",
                customer_email=customer_email,
                payment_method_types=payment_method_types or ["CARD", "PSE"],
                redirect_url=redirect_url,
                expires_at=datetime.utcnow() + timedelta(hours=24)  # 24 hour expiry
            )
            
            self.db.add(payment_intent)
            await self.db.commit()
            await self.db.refresh(payment_intent)
            
            return payment_intent
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating payment intent: {e}")
            raise

    async def process_card_payment(
        self,
        order_id: int,
        card_data: Dict[str, Any],
        customer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process credit/debit card payment"""
        try:
            # Get order
            result = await self.db.execute(
                select(Order)
                .options(selectinload(Order.buyer))
                .where(Order.id == order_id)
            )
            order = result.scalar_one_or_none()
            
            if not order:
                raise ValueError(f"Order {order_id} not found")
            
            # Create transaction record
            transaction_ref = self.wompi.generate_reference(order_id)
            transaction = Transaction(
                transaction_reference=transaction_ref,
                order_id=order_id,
                amount=order.total_amount,
                currency="COP",
                status=PaymentStatus.PENDING,
                payment_method_type="card",
                gateway="wompi"
            )
            
            self.db.add(transaction)
            await self.db.flush()  # Get transaction ID
            
            # Tokenize card
            async with self.wompi:
                token_response = await self.wompi.tokenize_card(card_data)
                card_token = token_response["data"]["id"]
                
                # Create payment source
                payment_source_data = {
                    "type": "CARD",
                    "token": card_token,
                    "customer_email": customer_data["email"],
                    "phone_number": customer_data.get("phone", ""),
                    "full_name": customer_data.get("full_name", "")
                }
                
                source_response = await self.wompi.create_payment_source(payment_source_data)
                payment_source_id = source_response["data"]["id"]
                
                # Create transaction
                transaction_data = {
                    "amount_in_cents": self.wompi.amount_to_cents(order.total_amount),
                    "currency": "COP",
                    "customer_email": customer_data["email"],
                    "payment_method": {
                        "type": "CARD",
                        "installments": card_data.get("installments", 1)
                    },
                    "reference": transaction_ref,
                    "redirect_url": customer_data.get("redirect_url", ""),
                    "payment_source_id": payment_source_id
                }
                
                wompi_response = await self.wompi.create_transaction(transaction_data)
                
                # Update transaction with Wompi response
                transaction.gateway_transaction_id = wompi_response["data"]["id"]
                transaction.gateway_response = wompi_response
                transaction.status = PaymentStatus.PROCESSING
                transaction.processed_at = datetime.utcnow()
                
                # Create payment record
                payment = Payment(
                    payment_reference=f"PAY_{transaction.id}_{uuid.uuid4().hex[:8]}",
                    transaction_id=transaction.id,
                    wompi_transaction_id=wompi_response["data"]["id"],
                    amount_in_cents=self.wompi.amount_to_cents(order.total_amount),
                    currency="COP",
                    payment_method_type="card",
                    payment_method=wompi_response["data"].get("payment_method", {}),
                    customer_email=customer_data["email"],
                    status=wompi_response["data"]["status"],
                    gateway_response=wompi_response
                )
                
                self.db.add(payment)
                await self.db.commit()
                
                return {
                    "transaction_id": transaction.id,
                    "wompi_transaction_id": wompi_response["data"]["id"],
                    "status": wompi_response["data"]["status"],
                    "checkout_url": wompi_response["data"].get("payment_link_url"),
                    "reference": transaction_ref
                }
                
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error processing card payment: {e}")
            raise

    async def process_pse_payment(
        self,
        order_id: int,
        pse_data: Dict[str, Any],
        customer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process PSE bank transfer payment"""
        try:
            # Get order
            result = await self.db.execute(
                select(Order).where(Order.id == order_id)
            )
            order = result.scalar_one_or_none()
            
            if not order:
                raise ValueError(f"Order {order_id} not found")
            
            # Create transaction record
            transaction_ref = self.wompi.generate_reference(order_id)
            transaction = Transaction(
                transaction_reference=transaction_ref,
                order_id=order_id,
                amount=order.total_amount,
                currency="COP",
                status=PaymentStatus.PENDING,
                payment_method_type="pse",
                gateway="wompi"
            )
            
            self.db.add(transaction)
            await self.db.flush()
            
            # Create PSE payment source
            async with self.wompi:
                payment_source_data = {
                    "type": "PSE",
                    "user_type": pse_data["user_type"],
                    "user_legal_id": pse_data["user_legal_id"],
                    "financial_institution_code": pse_data["bank_code"],
                    "payment_description": f"Pago orden #{order.order_number}",
                    "customer_email": customer_data["email"]
                }
                
                source_response = await self.wompi.create_payment_source(payment_source_data)
                payment_source_id = source_response["data"]["id"]
                
                # Create transaction
                transaction_data = {
                    "amount_in_cents": self.wompi.amount_to_cents(order.total_amount),
                    "currency": "COP",
                    "customer_email": customer_data["email"],
                    "payment_method": {
                        "type": "PSE"
                    },
                    "reference": transaction_ref,
                    "redirect_url": customer_data.get("redirect_url", ""),
                    "payment_source_id": payment_source_id
                }
                
                wompi_response = await self.wompi.create_transaction(transaction_data)
                
                # Update transaction
                transaction.gateway_transaction_id = wompi_response["data"]["id"]
                transaction.gateway_response = wompi_response
                transaction.status = PaymentStatus.PROCESSING
                transaction.processed_at = datetime.utcnow()
                
                # Create payment record
                payment = Payment(
                    payment_reference=f"PAY_{transaction.id}_{uuid.uuid4().hex[:8]}",
                    transaction_id=transaction.id,
                    wompi_transaction_id=wompi_response["data"]["id"],
                    amount_in_cents=self.wompi.amount_to_cents(order.total_amount),
                    currency="COP",
                    payment_method_type="pse",
                    payment_method=wompi_response["data"].get("payment_method", {}),
                    customer_email=customer_data["email"],
                    status=wompi_response["data"]["status"],
                    gateway_response=wompi_response
                )
                
                self.db.add(payment)
                await self.db.commit()
                
                return {
                    "transaction_id": transaction.id,
                    "wompi_transaction_id": wompi_response["data"]["id"],
                    "status": wompi_response["data"]["status"],
                    "checkout_url": wompi_response["data"].get("payment_link_url"),
                    "pse_redirect_url": source_response["data"].get("redirect_url"),
                    "reference": transaction_ref
                }
                
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error processing PSE payment: {e}")
            raise

    async def update_transaction_status(
        self,
        transaction_id: int,
        status: str,
        wompi_data: Optional[Dict[str, Any]] = None
    ) -> Transaction:
        """Update transaction status from webhook or manual check"""
        try:
            result = await self.db.execute(
                select(Transaction)
                .options(selectinload(Transaction.order))
                .where(Transaction.id == transaction_id)
            )
            transaction = result.scalar_one_or_none()
            
            if not transaction:
                raise ValueError(f"Transaction {transaction_id} not found")
            
            # Map Wompi status to our status
            status_mapping = {
                "APPROVED": PaymentStatus.APPROVED,
                "DECLINED": PaymentStatus.DECLINED,
                "PENDING": PaymentStatus.PENDING,
                "ERROR": PaymentStatus.ERROR,
                "VOIDED": PaymentStatus.CANCELLED
            }
            
            new_status = status_mapping.get(status, PaymentStatus.ERROR)
            transaction.status = new_status
            
            if wompi_data:
                transaction.gateway_response = wompi_data
                
            if new_status == PaymentStatus.APPROVED:
                transaction.confirmed_at = datetime.utcnow()
                # Update order status
                transaction.order.status = OrderStatus.CONFIRMED
                transaction.order.confirmed_at = datetime.utcnow()
                
            elif new_status in [PaymentStatus.DECLINED, PaymentStatus.ERROR]:
                transaction.failure_reason = wompi_data.get("status_message") if wompi_data else None
                transaction.failure_code = wompi_data.get("error", {}).get("type") if wompi_data else None
                
            await self.db.commit()
            await self.db.refresh(transaction)
            
            return transaction
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating transaction status: {e}")
            raise

    async def get_payment_status(self, transaction_reference: str) -> Dict[str, Any]:
        """Get current payment status"""
        try:
            result = await self.db.execute(
                select(Transaction)
                .options(selectinload(Transaction.order), selectinload(Transaction.payment))
                .where(Transaction.transaction_reference == transaction_reference)
            )
            transaction = result.scalar_one_or_none()
            
            if not transaction:
                raise ValueError(f"Transaction {transaction_reference} not found")
            
            return {
                "transaction_id": transaction.id,
                "reference": transaction.transaction_reference,
                "status": transaction.status.value,
                "amount": transaction.amount,
                "currency": transaction.currency,
                "order_number": transaction.order.order_number,
                "gateway_transaction_id": transaction.gateway_transaction_id,
                "created_at": transaction.created_at,
                "processed_at": transaction.processed_at,
                "confirmed_at": transaction.confirmed_at,
                "failure_reason": transaction.failure_reason
            }
            
        except Exception as e:
            logger.error(f"Error getting payment status: {e}")
            raise

    async def get_pse_banks(self) -> List[Dict[str, Any]]:
        """Get available PSE banks"""
        async with self.wompi:
            return await self.wompi.get_pse_banks()

    async def cancel_payment(self, transaction_id: int) -> bool:
        """Cancel/void a payment transaction"""
        try:
            result = await self.db.execute(
                select(Transaction).where(Transaction.id == transaction_id)
            )
            transaction = result.scalar_one_or_none()
            
            if not transaction or not transaction.gateway_transaction_id:
                return False
                
            if transaction.status not in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
                return False
                
            # Try to void with Wompi
            async with self.wompi:
                void_response = await self.wompi.void_transaction(transaction.gateway_transaction_id)
                
                if void_response.get("data", {}).get("status") == "VOIDED":
                    transaction.status = PaymentStatus.CANCELLED
                    await self.db.commit()
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling payment: {e}")
            return False