import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.order import Transaction
from app.models.payment import WebhookEvent, WebhookEventType, WebhookEventStatus, Payment
from app.services.payments.wompi_service import WompiService
from app.services.payments.payment_processor import PaymentProcessor

logger = logging.getLogger(__name__)

class WebhookHandler:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.wompi = WompiService()
        self.payment_processor = PaymentProcessor(db)

    async def process_webhook(
        self, 
        payload: str, 
        signature: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process incoming webhook from Wompi"""
        try:
            # Validate signature
            if not self.wompi.validate_webhook_signature(payload, signature):
                logger.warning("Invalid webhook signature received")
                return {"error": "Invalid signature", "processed": False}
            
            # Parse event data
            event_type = event_data.get("event")
            data = event_data.get("data", {})
            timestamp = event_data.get("timestamp")
            event_id = event_data.get("id", f"evt_{datetime.utcnow().timestamp()}")
            
            # Check if we've already processed this event
            existing_event = await self.db.execute(
                select(WebhookEvent).where(WebhookEvent.event_id == event_id)
            )
            if existing_event.scalar_one_or_none():
                logger.info(f"Event {event_id} already processed")
                return {"message": "Event already processed", "processed": True}
            
            # Create webhook event record
            webhook_event = WebhookEvent(
                event_id=event_id,
                event_type=self._map_event_type(event_type),
                event_status=WebhookEventStatus.RECEIVED,
                raw_payload=event_data,
                signature=signature,
                signature_validated=True,
                gateway_timestamp=datetime.fromtimestamp(timestamp) if timestamp else None
            )
            
            self.db.add(webhook_event)
            await self.db.flush()  # Get the ID
            
            # Process the event
            result = await self._process_event(webhook_event, event_type, data)
            
            # Update webhook event status
            webhook_event.event_status = WebhookEventStatus.PROCESSED if result["processed"] else WebhookEventStatus.FAILED
            webhook_event.processed_at = datetime.utcnow()
            webhook_event.processing_attempts += 1
            
            if not result["processed"] and "error" in result:
                webhook_event.processing_error = result["error"]
            
            await self.db.commit()
            
            return result
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error processing webhook: {e}")
            return {"error": str(e), "processed": False}

    def _map_event_type(self, event_type: str) -> WebhookEventType:
        """Map Wompi event type to our enum"""
        mapping = {
            "transaction.updated": WebhookEventType.TRANSACTION_UPDATED,
            "payment.created": WebhookEventType.PAYMENT_CREATED,
            "payment.updated": WebhookEventType.PAYMENT_UPDATED,
            "payment.failed": WebhookEventType.PAYMENT_FAILED,
            "payment.approved": WebhookEventType.PAYMENT_APPROVED,
            "payment.declined": WebhookEventType.PAYMENT_DECLINED,
            "payment.voided": WebhookEventType.PAYMENT_VOIDED,
            "payment.refunded": WebhookEventType.PAYMENT_REFUNDED
        }
        
        return mapping.get(event_type, WebhookEventType.TRANSACTION_UPDATED)

    async def _process_event(
        self, 
        webhook_event: WebhookEvent, 
        event_type: str, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process specific event type"""
        try:
            if event_type == "transaction.updated":
                return await self._handle_transaction_updated(webhook_event, data)
            elif event_type in ["payment.created", "payment.updated"]:
                return await self._handle_payment_updated(webhook_event, data)
            elif event_type == "payment.approved":
                return await self._handle_payment_approved(webhook_event, data)
            elif event_type == "payment.declined":
                return await self._handle_payment_declined(webhook_event, data)
            elif event_type == "payment.failed":
                return await self._handle_payment_failed(webhook_event, data)
            elif event_type == "payment.voided":
                return await self._handle_payment_voided(webhook_event, data)
            elif event_type == "payment.refunded":
                return await self._handle_payment_refunded(webhook_event, data)
            else:
                logger.warning(f"Unknown event type: {event_type}")
                return {"message": f"Unknown event type: {event_type}", "processed": False}
                
        except Exception as e:
            logger.error(f"Error processing event {event_type}: {e}")
            return {"error": str(e), "processed": False}

    async def _handle_transaction_updated(
        self, 
        webhook_event: WebhookEvent, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle transaction status update"""
        try:
            transaction_id = data.get("id")
            status = data.get("status")
            reference = data.get("reference")
            
            if not transaction_id or not status:
                return {"error": "Missing transaction ID or status", "processed": False}
            
            # Find our transaction by Wompi transaction ID
            result = await self.db.execute(
                select(Transaction)
                .options(selectinload(Transaction.order))
                .where(Transaction.gateway_transaction_id == transaction_id)
            )
            transaction = result.scalar_one_or_none()
            
            if not transaction:
                # Try to find by reference
                result = await self.db.execute(
                    select(Transaction)
                    .options(selectinload(Transaction.order))
                    .where(Transaction.transaction_reference == reference)
                )
                transaction = result.scalar_one_or_none()
                
            if not transaction:
                logger.warning(f"Transaction not found for Wompi ID {transaction_id}")
                return {"error": "Transaction not found", "processed": False}
            
            # Link webhook event to transaction
            webhook_event.transaction_id = transaction.id
            
            # Update transaction status
            updated_transaction = await self.payment_processor.update_transaction_status(
                transaction.id, 
                status, 
                data
            )
            
            logger.info(f"Updated transaction {transaction.id} status to {status}")
            
            return {
                "message": "Transaction updated successfully",
                "transaction_id": transaction.id,
                "new_status": status,
                "processed": True
            }
            
        except Exception as e:
            logger.error(f"Error handling transaction update: {e}")
            return {"error": str(e), "processed": False}

    async def _handle_payment_updated(
        self, 
        webhook_event: WebhookEvent, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle payment creation or update"""
        try:
            payment_id = data.get("id")
            status = data.get("status")
            amount_in_cents = data.get("amount_in_cents")
            reference = data.get("reference")
            
            # Find or create payment record
            result = await self.db.execute(
                select(Payment).where(Payment.wompi_payment_id == payment_id)
            )
            payment = result.scalar_one_or_none()
            
            if payment:
                # Update existing payment
                payment.status = status
                payment.gateway_response = data
                payment.updated_at = datetime.utcnow()
            else:
                # Find associated transaction
                result = await self.db.execute(
                    select(Transaction).where(Transaction.transaction_reference == reference)
                )
                transaction = result.scalar_one_or_none()
                
                if transaction:
                    # Create new payment record
                    payment = Payment(
                        payment_reference=f"PAY_{payment_id}",
                        transaction_id=transaction.id,
                        wompi_payment_id=payment_id,
                        amount_in_cents=amount_in_cents or 0,
                        currency="COP",
                        payment_method_type=data.get("payment_method", {}).get("type", "unknown"),
                        payment_method=data.get("payment_method", {}),
                        status=status,
                        gateway_response=data
                    )
                    self.db.add(payment)
                    webhook_event.transaction_id = transaction.id
            
            return {"message": "Payment updated successfully", "processed": True}
            
        except Exception as e:
            logger.error(f"Error handling payment update: {e}")
            return {"error": str(e), "processed": False}

    async def _handle_payment_approved(
        self, 
        webhook_event: WebhookEvent, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle payment approval"""
        return await self._handle_transaction_updated(webhook_event, data)

    async def _handle_payment_declined(
        self, 
        webhook_event: WebhookEvent, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle payment decline"""
        return await self._handle_transaction_updated(webhook_event, data)

    async def _handle_payment_failed(
        self, 
        webhook_event: WebhookEvent, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle payment failure"""
        return await self._handle_transaction_updated(webhook_event, data)

    async def _handle_payment_voided(
        self, 
        webhook_event: WebhookEvent, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle payment void/cancellation"""
        return await self._handle_transaction_updated(webhook_event, data)

    async def _handle_payment_refunded(
        self, 
        webhook_event: WebhookEvent, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle payment refund"""
        try:
            # This would involve creating refund records and updating order status
            # For now, just update the transaction status
            return await self._handle_transaction_updated(webhook_event, data)
            
        except Exception as e:
            logger.error(f"Error handling payment refund: {e}")
            return {"error": str(e), "processed": False}

    async def retry_failed_webhooks(self, limit: int = 100) -> Dict[str, Any]:
        """Retry failed webhook events"""
        try:
            # Get failed events that haven't been retried too many times
            result = await self.db.execute(
                select(WebhookEvent)
                .where(
                    WebhookEvent.event_status == WebhookEventStatus.FAILED,
                    WebhookEvent.processing_attempts < 3
                )
                .limit(limit)
            )
            failed_events = result.scalars().all()
            
            processed_count = 0
            for event in failed_events:
                try:
                    # Retry processing
                    result = await self._process_event(
                        event,
                        event.event_type.value,
                        event.raw_payload.get("data", {})
                    )
                    
                    # Update status
                    event.event_status = WebhookEventStatus.PROCESSED if result["processed"] else WebhookEventStatus.FAILED
                    event.processing_attempts += 1
                    event.processed_at = datetime.utcnow()
                    
                    if result["processed"]:
                        processed_count += 1
                        
                except Exception as e:
                    logger.error(f"Error retrying webhook {event.id}: {e}")
                    event.processing_attempts += 1
            
            await self.db.commit()
            
            return {
                "total_events": len(failed_events),
                "processed_successfully": processed_count,
                "message": f"Retried {len(failed_events)} events, {processed_count} successful"
            }
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error retrying failed webhooks: {e}")
            return {"error": str(e)}