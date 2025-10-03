"""
PROPOSED FIX FOR RACE CONDITION IN WEBHOOKS
============================================

This file contains the complete proposed solution for BUG CRÍTICO #3.

DO NOT IMPLEMENT YET - This is for review only.

Author: SecurityBackendAI
Date: 2025-10-02
Status: AWAITING APPROVAL
"""

import logging
import hmac
import hashlib
import json
from typing import Dict, Any, Optional, Tuple, Set
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

# Database and dependencies
from app.database import get_db
from app.core.config import settings

# Models
from app.models.order import Order, OrderTransaction, PaymentStatus, OrderStatus
from app.models.payment import WebhookEvent, WebhookEventType, WebhookEventStatus

# Schemas
from app.schemas.payment import WompiWebhookEvent, WebhookResponse, WebhookProcessingResult


logger = logging.getLogger(__name__)
router = APIRouter()


# =====================================================
# NEW: ORDER STATE MACHINE
# =====================================================

class OrderStateMachine:
    """
    State machine para validar transiciones de orden.

    Previene transiciones inválidas causadas por webhooks desordenados.
    Por ejemplo, un webhook PENDING que llega después de uno APPROVED
    no debe poder regresar la orden a estado PENDING.
    """

    # Mapeo de transiciones válidas
    VALID_TRANSITIONS: Dict[OrderStatus, Set[OrderStatus]] = {
        OrderStatus.PENDING: {
            OrderStatus.CONFIRMED,
            OrderStatus.CANCELLED
        },
        OrderStatus.CONFIRMED: {
            OrderStatus.PROCESSING,
            OrderStatus.CANCELLED
        },
        OrderStatus.PROCESSING: {
            OrderStatus.SHIPPED,
            OrderStatus.CANCELLED
        },
        OrderStatus.SHIPPED: {
            OrderStatus.DELIVERED,
            OrderStatus.CANCELLED  # Cancelación excepcional después de envío
        },
        OrderStatus.DELIVERED: {
            OrderStatus.REFUNDED  # Solo refund después de entrega
        },
        OrderStatus.CANCELLED: set(),  # Estado terminal - no más transiciones
        OrderStatus.REFUNDED: set()    # Estado terminal - no más transiciones
    }

    @classmethod
    def is_valid_transition(
        cls,
        current_state: OrderStatus,
        new_state: OrderStatus
    ) -> bool:
        """
        Validate if state transition is allowed.

        Args:
            current_state: Current order status
            new_state: Proposed new status

        Returns:
            bool: True if transition is valid

        Examples:
            >>> OrderStateMachine.is_valid_transition(OrderStatus.PENDING, OrderStatus.CONFIRMED)
            True
            >>> OrderStateMachine.is_valid_transition(OrderStatus.CONFIRMED, OrderStatus.PENDING)
            False
            >>> OrderStateMachine.is_valid_transition(OrderStatus.CONFIRMED, OrderStatus.CONFIRMED)
            True  # Idempotent - same state always allowed
        """
        # Idempotent: Same state transition always allowed
        if current_state == new_state:
            return True

        # Check valid transitions map
        allowed_states = cls.VALID_TRANSITIONS.get(current_state, set())
        is_valid = new_state in allowed_states

        if not is_valid:
            logger.warning(
                f"Invalid state transition attempted: {current_state.value} → {new_state.value}",
                extra={
                    "current_state": current_state.value,
                    "attempted_state": new_state.value,
                    "allowed_states": [s.value for s in allowed_states]
                }
            )

        return is_valid

    @classmethod
    def get_allowed_transitions(
        cls,
        current_state: OrderStatus
    ) -> Set[OrderStatus]:
        """
        Get all allowed next states from current state.

        Args:
            current_state: Current order status

        Returns:
            Set of allowed next states
        """
        return cls.VALID_TRANSITIONS.get(current_state, set())

    @classmethod
    def is_terminal_state(cls, state: OrderStatus) -> bool:
        """
        Check if state is terminal (no further transitions allowed).

        Args:
            state: Order status to check

        Returns:
            bool: True if state is terminal
        """
        return len(cls.VALID_TRANSITIONS.get(state, set())) == 0


# =====================================================
# NEW: ATOMIC IDEMPOTENCY CHECK
# =====================================================

async def ensure_webhook_idempotency(
    db: AsyncSession,
    event_id: str,
    event_type: str,
    raw_payload: Dict[str, Any]
) -> Tuple[bool, Optional[WebhookEvent]]:
    """
    Ensure webhook is processed only once using atomic database insert.

    This function uses the UNIQUE constraint on WebhookEvent.event_id to
    guarantee atomicity at the database level. If two concurrent requests
    try to process the same event_id, one will succeed and one will get
    an IntegrityError.

    Args:
        db: Database session
        event_id: Unique webhook event ID (e.g., Wompi transaction ID)
        event_type: Type of webhook event
        raw_payload: Complete webhook payload

    Returns:
        Tuple[bool, Optional[WebhookEvent]]:
            (is_duplicate, existing_event_if_duplicate)

    Raises:
        Exception: If database operation fails for reasons other than duplicate

    Security Note:
        This is the PRIMARY defense against race conditions. The unique
        constraint on event_id ensures that even if two webhooks pass the
        initial check, only one can successfully insert into the database.
    """
    try:
        # Map string event type to enum
        event_type_enum = WebhookEventType.TRANSACTION_UPDATED
        if "payment.created" in event_type:
            event_type_enum = WebhookEventType.PAYMENT_CREATED
        elif "payment.approved" in event_type:
            event_type_enum = WebhookEventType.PAYMENT_APPROVED
        elif "payment.declined" in event_type:
            event_type_enum = WebhookEventType.PAYMENT_DECLINED
        elif "payment.failed" in event_type:
            event_type_enum = WebhookEventType.PAYMENT_FAILED

        # Create webhook event record FIRST (before processing)
        # The UNIQUE constraint on event_id will prevent duplicates
        webhook_event = WebhookEvent(
            event_id=event_id,  # UNIQUE constraint here
            event_type=event_type_enum,
            event_status=WebhookEventStatus.PROCESSING,  # Mark as processing
            raw_payload=raw_payload,
            created_at=datetime.utcnow()
        )

        db.add(webhook_event)

        try:
            # Attempt to flush (commit to DB)
            # This will raise IntegrityError if event_id already exists
            await db.flush()

            # SUCCESS: This is the first time processing this event
            logger.info(
                f"New webhook event {event_id} registered for processing",
                extra={"event_id": event_id, "event_type": event_type}
            )

            return False, None  # Not a duplicate

        except IntegrityError as e:
            # DUPLICATE DETECTED by database UNIQUE constraint
            await db.rollback()

            logger.info(
                f"Duplicate webhook event {event_id} detected by database constraint",
                extra={
                    "event_id": event_id,
                    "error": str(e)
                }
            )

            # Fetch the existing event to return details
            result = await db.execute(
                select(WebhookEvent).where(WebhookEvent.event_id == event_id)
            )
            existing = result.scalar_one()

            logger.info(
                f"Webhook {event_id} was originally processed at {existing.created_at}",
                extra={
                    "event_id": event_id,
                    "original_processed_at": existing.created_at.isoformat(),
                    "original_status": existing.event_status.value
                }
            )

            return True, existing  # Is duplicate, return existing

    except IntegrityError:
        # Already handled above
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            f"Error in idempotency check for event {event_id}: {str(e)}",
            exc_info=True
        )
        # FAIL-SECURE: Re-raise error to prevent processing
        # Better to fail than to process duplicate
        raise


# =====================================================
# IMPROVED: UPDATE ORDER WITH LOCKS AND VALIDATION
# =====================================================

async def update_order_from_webhook(
    db: AsyncSession,
    transaction_data: Dict[str, Any],
    wompi_transaction_id: str
) -> WebhookProcessingResult:
    """
    Update order status based on Wompi webhook transaction data.

    IMPROVEMENTS FROM ORIGINAL:
    1. Uses .with_for_update() to acquire row-level lock on Order
    2. Validates state transitions using OrderStateMachine
    3. Checks if transaction already exists before creating
    4. Handles IntegrityError for duplicate transaction IDs
    5. Better error handling and logging

    Args:
        db: Database session
        transaction_data: Parsed Wompi transaction data
        wompi_transaction_id: Wompi transaction ID

    Returns:
        WebhookProcessingResult: Processing result with success status

    Process Flow:
        1. Acquire lock on order (with_for_update)
        2. Validate state transition
        3. Check for existing transaction
        4. Create or update transaction
        5. Update order status
        6. Commit atomically (releases lock)

    Concurrency Safety:
        The .with_for_update() lock ensures that only one webhook can
        modify this order at a time. Other webhooks will WAIT until
        the lock is released (on commit or rollback).
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

        # ✅ FIX #1: ACQUIRE ROW-LEVEL LOCK ON ORDER
        # This prevents concurrent webhooks from modifying the same order
        result = await db.execute(
            select(Order)
            .where(Order.order_number == order_reference)
            .options(selectinload(Order.transactions))
            .with_for_update()  # 🔒 LOCK ACQUIRED HERE
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

        # ✅ FIX #2: VALIDATE STATE TRANSITION
        if not OrderStateMachine.is_valid_transition(order.status, order_status):
            logger.warning(
                f"Invalid state transition blocked for order {order.id}: "
                f"{order.status.value} → {order_status.value}",
                extra={
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "current_status": order.status.value,
                    "attempted_status": order_status.value,
                    "wompi_transaction_id": wompi_transaction_id,
                    "wompi_status": wompi_status
                }
            )

            return WebhookProcessingResult(
                success=False,
                event_id=wompi_transaction_id,
                order_id=order.id,
                status="invalid_state_transition",
                message=f"Cannot transition order from {order.status.value} to {order_status.value}"
            )

        # ✅ FIX #3: CHECK FOR EXISTING TRANSACTION WITH LOCK
        # Search in already-loaded transactions (via selectinload)
        transaction = None
        for txn in order.transactions:
            if txn.gateway_transaction_id == wompi_transaction_id:
                transaction = txn
                break

        if transaction:
            # Transaction already exists - UPDATE it
            # Only update if status actually changed
            if transaction.status != payment_status:
                old_txn_status = transaction.status
                transaction.status = payment_status
                transaction.gateway_response = json.dumps(transaction_data)
                transaction.processed_at = datetime.utcnow()

                if status_message:
                    transaction.failure_reason = (
                        status_message if payment_status != PaymentStatus.APPROVED else None
                    )

                logger.info(
                    f"Updated existing transaction {transaction.id}: "
                    f"{old_txn_status.value} → {payment_status.value}",
                    extra={
                        "transaction_id": transaction.id,
                        "order_id": order.id,
                        "old_status": old_txn_status.value,
                        "new_status": payment_status.value
                    }
                )
            else:
                # Status hasn't changed - idempotent update
                logger.info(
                    f"Transaction {transaction.id} already in correct state: {payment_status.value}",
                    extra={
                        "transaction_id": transaction.id,
                        "status": payment_status.value,
                        "message": "Idempotent webhook - no changes needed"
                    }
                )

                # Still return success - this is normal for retried webhooks
                return WebhookProcessingResult(
                    success=True,
                    event_id=wompi_transaction_id,
                    order_id=order.id,
                    transaction_id=str(transaction.id),
                    status="already_processed",
                    message="Transaction already in target state (idempotent)",
                    updated_order_status=order.status.value
                )
        else:
            # ✅ FIX #4: CREATE NEW TRANSACTION
            # If we get IntegrityError here, it means another concurrent webhook
            # created this transaction between our check and now
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

            logger.info(
                f"Created new transaction for order {order.id}",
                extra={
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "payment_status": payment_status.value,
                    "gateway_transaction_id": wompi_transaction_id
                }
            )

        # Update order status (if transition is valid, which we already checked)
        old_order_status = order.status
        order.status = order_status
        order.updated_at = datetime.utcnow()

        # Update confirmed_at timestamp if payment approved and not already set
        if payment_status == PaymentStatus.APPROVED and not order.confirmed_at:
            order.confirmed_at = datetime.utcnow()
            logger.info(
                f"Order {order.id} confirmed at {order.confirmed_at}",
                extra={
                    "order_id": order.id,
                    "confirmed_at": order.confirmed_at.isoformat()
                }
            )

        # ✅ COMMIT TRANSACTION - LOCK RELEASED HERE
        await db.commit()
        await db.refresh(order)

        logger.info(
            f"Order {order.id} updated successfully: "
            f"{old_order_status.value} → {order_status.value}, "
            f"Payment: {payment_status.value}, "
            f"Wompi TXN: {wompi_transaction_id}",
            extra={
                "order_id": order.id,
                "old_status": old_order_status.value,
                "new_status": order_status.value,
                "payment_status": payment_status.value,
                "gateway_transaction_id": wompi_transaction_id
            }
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

    except IntegrityError as e:
        # Duplicate transaction creation detected
        await db.rollback()
        logger.warning(
            f"Integrity error updating order (possible concurrent webhook): {str(e)}",
            extra={
                "wompi_transaction_id": wompi_transaction_id,
                "error": str(e)
            }
        )

        return WebhookProcessingResult(
            success=False,
            event_id=wompi_transaction_id,
            status="duplicate_transaction",
            message="Transaction already exists (concurrent webhook detected)"
        )

    except Exception as e:
        await db.rollback()
        logger.error(
            f"Error updating order from webhook: {str(e)}",
            exc_info=True,
            extra={
                "wompi_transaction_id": wompi_transaction_id,
                "order_reference": transaction_data.get("reference")
            }
        )

        return WebhookProcessingResult(
            success=False,
            event_id=wompi_transaction_id,
            status="error",
            message=f"Database error: {str(e)}"
        )


# =====================================================
# SIGNATURE VERIFICATION (unchanged from original)
# =====================================================

def verify_wompi_signature(
    payload: bytes,
    signature: str,
    secret: str
) -> bool:
    """Verify Wompi HMAC SHA256 signature for webhook authenticity."""
    if not secret or not signature:
        return False

    try:
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        is_valid = hmac.compare_digest(expected_signature, signature)

        if not is_valid:
            logger.warning("Signature verification failed")

        return is_valid

    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}")
        return False


# =====================================================
# STATUS MAPPING (unchanged from original)
# =====================================================

def map_wompi_status_to_order_status(wompi_status: str) -> tuple[OrderStatus, PaymentStatus]:
    """Map Wompi transaction status to internal order and payment statuses."""
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


# =====================================================
# IMPROVED: WEBHOOK ENDPOINT
# =====================================================

@router.post("/wompi", response_model=WebhookResponse, status_code=status.HTTP_200_OK)
async def wompi_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> WebhookResponse:
    """
    Handle Wompi payment webhook notifications with race condition protection.

    IMPROVEMENTS FROM ORIGINAL:
    1. Atomic idempotency check BEFORE processing
    2. Updates webhook event status after processing
    3. Better error handling and logging
    4. Always returns 200 OK per Wompi spec

    Security Features:
    - HMAC SHA256 signature verification
    - Atomic idempotency protection (database UNIQUE constraint)
    - Row-level locking on order updates
    - State transition validation
    - Comprehensive audit logging

    Process Flow:
        1. Verify signature
        2. Parse payload
        3. Atomic idempotency check (insert WebhookEvent)
        4. If not duplicate: process webhook with locks
        5. Update webhook event status
        6. Always return 200 OK
    """
    # Get raw body for signature verification
    body = await request.body()
    body_str = body.decode('utf-8')

    # Get signature from headers
    signature = request.headers.get("X-Event-Signature") or request.headers.get("X-Signature")

    logger.info(
        f"Received Wompi webhook",
        extra={"signature_present": signature is not None}
    )

    # ✅ STEP 1: VERIFY SIGNATURE
    signature_valid = False
    if settings.WOMPI_WEBHOOK_SECRET:
        signature_valid = verify_wompi_signature(body, signature, settings.WOMPI_WEBHOOK_SECRET)

        if not signature_valid:
            logger.warning("Wompi webhook signature verification failed")
            # Still return 200 OK per Wompi spec
            return WebhookResponse(status="ok")
    else:
        logger.warning("WOMPI_WEBHOOK_SECRET not configured - skipping signature verification")
        signature_valid = True  # Allow if not configured (development only)

    # ✅ STEP 2: PARSE PAYLOAD
    try:
        payload_dict = json.loads(body_str)
        event_data = WompiWebhookEvent(**payload_dict)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook payload: {str(e)}")
        return WebhookResponse(status="ok")
    except Exception as e:
        logger.error(f"Error parsing webhook payload: {str(e)}")
        return WebhookResponse(status="ok")

    transaction_data = event_data.data
    wompi_transaction_id = transaction_data.get("id", "unknown")

    logger.info(
        f"Processing Wompi webhook",
        extra={
            "event_type": event_data.event,
            "transaction_id": wompi_transaction_id,
            "status": transaction_data.get('status')
        }
    )

    # ✅ STEP 3: ATOMIC IDEMPOTENCY CHECK
    try:
        is_duplicate, existing_event = await ensure_webhook_idempotency(
            db=db,
            event_id=wompi_transaction_id,
            event_type=event_data.event,
            raw_payload=payload_dict
        )

        if is_duplicate:
            logger.info(
                f"Duplicate webhook {wompi_transaction_id} detected - skipping processing",
                extra={
                    "event_id": wompi_transaction_id,
                    "original_processed_at": existing_event.created_at.isoformat(),
                    "original_status": existing_event.event_status.value
                }
            )
            # ✅ Return 200 OK - no further processing needed
            return WebhookResponse(status="ok")

    except Exception as e:
        logger.error(
            f"Idempotency check failed for webhook {wompi_transaction_id}: {str(e)}",
            exc_info=True
        )
        # ✅ FAIL-SECURE: Don't process if we can't verify idempotency
        return WebhookResponse(status="ok")

    # ✅ STEP 4: PROCESS WEBHOOK (with locks and validation)
    try:
        processing_result = await update_order_from_webhook(
            db=db,
            transaction_data=transaction_data,
            wompi_transaction_id=wompi_transaction_id
        )

        # ✅ STEP 5: UPDATE WEBHOOK EVENT STATUS
        await db.execute(
            update(WebhookEvent)
            .where(WebhookEvent.event_id == wompi_transaction_id)
            .values(
                event_status=(
                    WebhookEventStatus.PROCESSED if processing_result.success
                    else WebhookEventStatus.FAILED
                ),
                processed_at=datetime.utcnow(),
                processing_error=(
                    None if processing_result.success
                    else processing_result.message
                ),
                signature=signature,
                signature_validated=signature_valid
            )
        )
        await db.commit()

        # ✅ STEP 6: LOG RESULT
        if processing_result.success:
            logger.info(
                f"Webhook processed successfully",
                extra={
                    "event_id": wompi_transaction_id,
                    "order_id": processing_result.order_id,
                    "status": processing_result.updated_order_status
                }
            )
        else:
            logger.error(
                f"Webhook processing failed",
                extra={
                    "event_id": wompi_transaction_id,
                    "status": processing_result.status,
                    "message": processing_result.message
                }
            )

    except Exception as e:
        logger.error(
            f"Unexpected error processing webhook {wompi_transaction_id}: {str(e)}",
            exc_info=True
        )
        # Update webhook event to FAILED status
        try:
            await db.execute(
                update(WebhookEvent)
                .where(WebhookEvent.event_id == wompi_transaction_id)
                .values(
                    event_status=WebhookEventStatus.FAILED,
                    processing_error=str(e)
                )
            )
            await db.commit()
        except:
            pass  # Don't fail webhook response if audit update fails

    # ✅ ALWAYS RETURN 200 OK PER WOMPI SPECIFICATION
    return WebhookResponse(status="ok")


# =====================================================
# SUMMARY OF CHANGES
# =====================================================

"""
KEY IMPROVEMENTS TO PREVENT RACE CONDITIONS:

1. OrderStateMachine:
   - Validates state transitions
   - Prevents webhooks from moving orders backward
   - Example: CONFIRMED order cannot go back to PENDING

2. ensure_webhook_idempotency():
   - Uses database UNIQUE constraint for atomicity
   - Inserts webhook event BEFORE processing
   - If two webhooks arrive simultaneously, DB constraint ensures only one succeeds

3. update_order_from_webhook() with locks:
   - Uses .with_for_update() to lock order row
   - Other webhooks WAIT until lock is released
   - Validates state transition before updating
   - Checks for existing transaction before creating

4. Improved error handling:
   - Catches IntegrityError for duplicate transactions
   - Logs all operations for audit trail
   - Always returns 200 OK per gateway spec

CONCURRENCY FLOW:
    Webhook #1                          Webhook #2
    ----------                          ----------
    Insert event (SUCCESS)              Insert event (FAILS - duplicate)
    Lock order                          Return 200 OK (duplicate)
    Validate transition
    Update order
    Commit (release lock)
    Return 200 OK

RESULT: Only Webhook #1 processes. Webhook #2 detected as duplicate.
"""
