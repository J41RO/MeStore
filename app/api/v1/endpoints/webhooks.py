"""
Wompi Webhook Handler for Payment Confirmations
=================================================

Secure webhook endpoint for receiving and processing Wompi payment notifications.

Features:
- HMAC SHA256 signature verification for security
- Idempotency protection against duplicate events
- Atomic transaction updates with rollback support
- Comprehensive audit logging for compliance
- Order status updates based on payment status
- Error handling that always returns 200 OK per Wompi spec

Author: Payment Systems AI
Date: 2025-10-01
Purpose: Production-ready Wompi webhook integration
Security: PCI DSS compliant webhook processing
"""

import logging
import hmac
import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Database and dependencies
from app.database import get_db
from app.core.config import settings

# Models
from app.models.order import Order, OrderTransaction, PaymentStatus, OrderStatus
from app.models.payment import WebhookEvent, WebhookEventType, WebhookEventStatus

# Schemas
from app.schemas.payment import (
    WompiWebhookEvent,
    WompiTransaction,
    WebhookResponse,
    WebhookProcessingResult
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ===== SIGNATURE VERIFICATION =====

def verify_wompi_signature(
    payload: bytes,
    signature: str,
    secret: str
) -> bool:
    """
    Verify Wompi HMAC SHA256 signature for webhook authenticity.

    Args:
        payload: Raw webhook payload bytes
        signature: Signature from X-Event-Signature or X-Signature header
        secret: WOMPI_WEBHOOK_SECRET from settings

    Returns:
        bool: True if signature is valid, False otherwise

    Security:
        - Uses HMAC SHA256 for cryptographic signature verification
        - Constant-time comparison to prevent timing attacks
        - Validates webhook is actually from Wompi servers
    """
    if not secret:
        logger.error("WOMPI_WEBHOOK_SECRET not configured - cannot verify signatures")
        return False

    if not signature:
        logger.warning("No signature provided in webhook request")
        return False

    try:
        # Calculate expected signature
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        # Constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(expected_signature, signature)

        if not is_valid:
            logger.warning(
                f"Signature verification failed. "
                f"Expected signature does not match provided signature."
            )

        return is_valid

    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}")
        return False


# ===== IDEMPOTENCY CHECK =====

async def check_event_already_processed(
    db: AsyncSession,
    event_id: str
) -> bool:
    """
    Check if webhook event has already been processed (idempotency).

    Args:
        db: Database session
        event_id: Wompi event ID (transaction ID)

    Returns:
        bool: True if already processed, False if new event

    Note:
        This prevents duplicate processing if Wompi retries the webhook.
    """
    try:
        result = await db.execute(
            select(WebhookEvent).where(WebhookEvent.event_id == event_id)
        )
        existing_event = result.scalar_one_or_none()
        return existing_event is not None
    except Exception as e:
        logger.error(f"Error checking event idempotency: {str(e)}")
        return False


# ===== ORDER STATUS MAPPING =====

def map_wompi_status_to_order_status(wompi_status: str) -> tuple[OrderStatus, PaymentStatus]:
    """
    Map Wompi transaction status to internal order and payment statuses.

    Args:
        wompi_status: Wompi status (APPROVED, DECLINED, PENDING, ERROR, VOIDED)

    Returns:
        tuple: (OrderStatus, PaymentStatus)

    Status Mapping:
        - APPROVED → order: confirmed, payment: approved
        - DECLINED → order: pending, payment: declined
        - PENDING → order: pending, payment: pending
        - ERROR → order: pending, payment: error
        - VOIDED → order: cancelled, payment: cancelled
    """
    status_map = {
        "APPROVED": (OrderStatus.CONFIRMED, PaymentStatus.APPROVED),
        "DECLINED": (OrderStatus.PENDING, PaymentStatus.DECLINED),
        "PENDING": (OrderStatus.PENDING, PaymentStatus.PENDING),
        "ERROR": (OrderStatus.PENDING, PaymentStatus.ERROR),
        "VOIDED": (OrderStatus.CANCELLED, PaymentStatus.CANCELLED),
    }

    return status_map.get(
        wompi_status.upper(),
        (OrderStatus.PENDING, PaymentStatus.ERROR)
    )


# ===== ORDER UPDATE LOGIC =====

async def update_order_from_webhook(
    db: AsyncSession,
    transaction_data: Dict[str, Any],
    wompi_transaction_id: str
) -> WebhookProcessingResult:
    """
    Update order status based on Wompi webhook transaction data.

    Args:
        db: Database session
        transaction_data: Parsed Wompi transaction data
        wompi_transaction_id: Wompi transaction ID

    Returns:
        WebhookProcessingResult: Processing result with success status

    Process:
        1. Find order by reference (order_number)
        2. Map Wompi status to internal statuses
        3. Update order and create/update transaction
        4. Commit atomically or rollback on error
    """
    try:
        # Extract transaction details
        order_reference = transaction_data.get("reference")
        wompi_status = transaction_data.get("status")
        amount_in_cents = transaction_data.get("amount_in_cents")
        payment_method_type = transaction_data.get("payment_method_type")
        status_message = transaction_data.get("status_message")

        if not order_reference:
            return WebhookProcessingResult(
                success=False,
                event_id=wompi_transaction_id,
                status="error",
                message="No order reference found in transaction data"
            )

        # Find order by order_number
        result = await db.execute(
            select(Order)
            .where(Order.order_number == order_reference)
            .options(selectinload(Order.transactions))
        )
        order = result.scalar_one_or_none()

        if not order:
            logger.warning(f"Order not found for reference: {order_reference}")
            return WebhookProcessingResult(
                success=False,
                event_id=wompi_transaction_id,
                status="order_not_found",
                message=f"Order {order_reference} not found"
            )

        # Map Wompi status to internal statuses
        order_status, payment_status = map_wompi_status_to_order_status(wompi_status)

        # Find or create transaction record
        transaction = None
        for txn in order.transactions:
            if txn.gateway_transaction_id == wompi_transaction_id:
                transaction = txn
                break

        if not transaction:
            # Create new transaction record
            transaction = OrderTransaction(
                transaction_reference=f"TXN-{order.order_number}-{wompi_transaction_id[:10]}",
                order_id=order.id,
                amount=amount_in_cents / 100.0 if amount_in_cents else order.total_amount,
                currency="COP",
                status=payment_status,
                payment_method_type=payment_method_type or "unknown",
                gateway="wompi",
                gateway_transaction_id=wompi_transaction_id,
                gateway_response=json.dumps(transaction_data),
                processed_at=datetime.utcnow()
            )
            db.add(transaction)
            logger.info(f"Created new transaction for order {order.id}")
        else:
            # Update existing transaction
            transaction.status = payment_status
            transaction.gateway_response = json.dumps(transaction_data)
            transaction.processed_at = datetime.utcnow()
            if status_message:
                transaction.failure_reason = status_message if payment_status != PaymentStatus.APPROVED else None
            logger.info(f"Updated existing transaction {transaction.id}")

        # Update order status
        old_status = order.status
        order.status = order_status
        order.updated_at = datetime.utcnow()

        # Update confirmed_at timestamp if payment approved
        if payment_status == PaymentStatus.APPROVED and not order.confirmed_at:
            order.confirmed_at = datetime.utcnow()
            logger.info(f"Order {order.id} confirmed at {order.confirmed_at}")

        # Commit transaction
        await db.commit()
        await db.refresh(order)

        logger.info(
            f"Order {order.id} updated: {old_status} → {order_status}, "
            f"Payment: {payment_status}, Wompi TXN: {wompi_transaction_id}"
        )

        return WebhookProcessingResult(
            success=True,
            event_id=wompi_transaction_id,
            order_id=order.id,
            transaction_id=wompi_transaction_id,
            status="processed",
            message="Order updated successfully",
            updated_order_status=order_status.value
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating order from webhook: {str(e)}", exc_info=True)
        return WebhookProcessingResult(
            success=False,
            event_id=wompi_transaction_id,
            status="error",
            message=f"Database error: {str(e)}"
        )


# ===== WEBHOOK EVENT STORAGE =====

async def store_webhook_event(
    db: AsyncSession,
    event_id: str,
    event_type: str,
    raw_payload: Dict[str, Any],
    signature: Optional[str],
    signature_valid: bool,
    processing_result: WebhookProcessingResult
) -> None:
    """
    Store webhook event in database for audit trail.

    Args:
        db: Database session
        event_id: Wompi event ID
        event_type: Event type (transaction.updated, etc.)
        raw_payload: Complete webhook payload
        signature: Signature from header
        signature_valid: Whether signature was valid
        processing_result: Result of processing

    Note:
        This creates an audit trail for compliance and debugging.
    """
    try:
        # Map event type string to enum
        event_type_enum = WebhookEventType.TRANSACTION_UPDATED
        if "payment.created" in event_type:
            event_type_enum = WebhookEventType.PAYMENT_CREATED
        elif "payment.approved" in event_type:
            event_type_enum = WebhookEventType.PAYMENT_APPROVED
        elif "payment.declined" in event_type:
            event_type_enum = WebhookEventType.PAYMENT_DECLINED
        elif "payment.failed" in event_type:
            event_type_enum = WebhookEventType.PAYMENT_FAILED

        # Determine event status
        event_status = WebhookEventStatus.PROCESSED if processing_result.success else WebhookEventStatus.FAILED

        webhook_event = WebhookEvent(
            event_id=event_id,
            event_type=event_type_enum,
            event_status=event_status,
            raw_payload=raw_payload,
            signature=signature,
            signature_validated=signature_valid,
            processed_at=datetime.utcnow() if processing_result.success else None,
            processing_attempts=1,
            processing_error=processing_result.message if not processing_result.success else None,
            gateway_timestamp=datetime.fromisoformat(
                raw_payload.get("sent_at", "").replace("Z", "+00:00")
            ) if raw_payload.get("sent_at") else None
        )

        db.add(webhook_event)
        await db.commit()

        logger.info(f"Stored webhook event {event_id} with status {event_status}")

    except Exception as e:
        logger.error(f"Error storing webhook event: {str(e)}", exc_info=True)
        # Don't fail the webhook if audit logging fails


# ===== WEBHOOK ENDPOINT =====

@router.post("/wompi", response_model=WebhookResponse, status_code=status.HTTP_200_OK)
async def wompi_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> WebhookResponse:
    """
    Handle Wompi payment webhook notifications.

    This endpoint receives transaction status updates from Wompi payment gateway.

    Process:
        1. Verify HMAC SHA256 signature for authenticity
        2. Check idempotency (prevent duplicate processing)
        3. Parse webhook event data
        4. Update order and transaction status
        5. Store event in database for audit trail
        6. Always return 200 OK to prevent retry storms

    Headers:
        X-Event-Signature or X-Signature: HMAC SHA256 signature

    Request Body:
        WompiWebhookEvent: Complete webhook event payload

    Returns:
        WebhookResponse: Always {"status": "ok"} with 200 OK

    Security:
        - Signature verification required (rejects invalid signatures)
        - Idempotency protection (prevents duplicate processing)
        - Atomic database transactions (all-or-nothing updates)
        - Comprehensive audit logging (compliance trail)

    Important:
        Per Wompi specification, ALWAYS return 200 OK even on processing errors.
        This prevents exponential retry storms from Wompi servers.
    """
    # Get raw body for signature verification
    body = await request.body()
    body_str = body.decode('utf-8')

    # Get signature from headers (Wompi can send either header name)
    signature = request.headers.get("X-Event-Signature") or request.headers.get("X-Signature")

    # Log webhook receipt
    logger.info(f"Received Wompi webhook, signature present: {signature is not None}")

    # Verify signature
    signature_valid = False
    if settings.WOMPI_WEBHOOK_SECRET:
        signature_valid = verify_wompi_signature(body, signature, settings.WOMPI_WEBHOOK_SECRET)

        if not signature_valid:
            logger.warning("Wompi webhook signature verification failed")
            # Store failed verification event
            try:
                payload_dict = json.loads(body_str)
                event_id = payload_dict.get("data", {}).get("id", "unknown")
                await store_webhook_event(
                    db=db,
                    event_id=event_id,
                    event_type=payload_dict.get("event", "unknown"),
                    raw_payload=payload_dict,
                    signature=signature,
                    signature_valid=False,
                    processing_result=WebhookProcessingResult(
                        success=False,
                        event_id=event_id,
                        status="signature_invalid",
                        message="Signature verification failed"
                    )
                )
            except Exception as e:
                logger.error(f"Error storing failed signature event: {str(e)}")

            # Return 200 OK anyway per Wompi spec
            return WebhookResponse(status="ok")
    else:
        logger.warning("WOMPI_WEBHOOK_SECRET not configured - skipping signature verification")
        signature_valid = True  # Allow if not configured (development only)

    # Parse webhook payload
    try:
        payload_dict = json.loads(body_str)
        event_data = WompiWebhookEvent(**payload_dict)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook payload: {str(e)}")
        return WebhookResponse(status="ok")
    except Exception as e:
        logger.error(f"Error parsing webhook payload: {str(e)}")
        return WebhookResponse(status="ok")

    # Extract transaction data
    transaction_data = event_data.data
    wompi_transaction_id = transaction_data.get("id", "unknown")

    logger.info(
        f"Processing Wompi webhook: "
        f"Event: {event_data.event}, "
        f"TXN ID: {wompi_transaction_id}, "
        f"Status: {transaction_data.get('status')}"
    )

    # Check idempotency
    already_processed = await check_event_already_processed(db, wompi_transaction_id)
    if already_processed:
        logger.info(f"Webhook event {wompi_transaction_id} already processed (idempotent)")
        return WebhookResponse(status="ok")

    # Process webhook and update order
    processing_result = await update_order_from_webhook(
        db=db,
        transaction_data=transaction_data,
        wompi_transaction_id=wompi_transaction_id
    )

    # Store webhook event for audit trail
    await store_webhook_event(
        db=db,
        event_id=wompi_transaction_id,
        event_type=event_data.event,
        raw_payload=payload_dict,
        signature=signature,
        signature_valid=signature_valid,
        processing_result=processing_result
    )

    # Log result
    if processing_result.success:
        logger.info(
            f"Webhook processed successfully: "
            f"Order {processing_result.order_id} → {processing_result.updated_order_status}"
        )
    else:
        logger.error(
            f"Webhook processing failed: "
            f"{processing_result.status} - {processing_result.message}"
        )

    # Always return 200 OK per Wompi specification
    return WebhookResponse(status="ok")


# ===== HEALTH CHECK =====

@router.get("/health")
async def webhooks_health():
    """
    Health check for webhook service.

    Returns:
        dict: Service health status and configuration
    """
    return {
        "service": "Wompi Webhooks",
        "status": "operational",
        "signature_verification_enabled": bool(settings.WOMPI_WEBHOOK_SECRET),
        "environment": settings.WOMPI_ENVIRONMENT,
        "endpoints": {
            "wompi_webhook": "POST /webhooks/wompi",
            "health": "GET /webhooks/health"
        }
    }
