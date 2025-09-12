from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Dict, Any, List, Optional
import logging
import json

from app.database import get_db
from app.models.user import User
from app.models.order import Order, Transaction, PaymentStatus
from app.models.payment import Payment, PaymentIntent, WebhookEvent
from app.services.payments.payment_processor import PaymentProcessor
from app.services.payments.webhook_handler import WebhookHandler
from app.services.payments.wompi_service import get_wompi_service
from app.core.auth import get_current_user
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class CardPaymentRequest(BaseModel):
    order_id: int
    card_number: str
    exp_month: str
    exp_year: str
    cvc: str
    card_holder: str
    installments: int = 1
    customer_phone: Optional[str] = None
    redirect_url: str

class PSEPaymentRequest(BaseModel):
    order_id: int
    user_type: str  # "0" for natural, "1" for juridical
    user_legal_id: str
    bank_code: str
    redirect_url: str

class PaymentResponse(BaseModel):
    transaction_id: int
    wompi_transaction_id: str
    status: str
    checkout_url: Optional[str] = None
    reference: str
    message: str

class PaymentStatusResponse(BaseModel):
    transaction_id: int
    reference: str
    status: str
    amount: float
    currency: str
    order_number: str
    created_at: str
    failure_reason: Optional[str] = None

class PSEBank(BaseModel):
    financial_institution_code: str
    financial_institution_name: str

class PaymentMethodsResponse(BaseModel):
    card_enabled: bool
    pse_enabled: bool
    pse_banks: List[PSEBank]
    wompi_public_key: str

@router.post("/create-payment-intent")
async def create_payment_intent(
    order_id: int,
    redirect_url: str,
    payment_methods: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a payment intent for an order"""
    try:
        processor = PaymentProcessor(db)
        
        # Verify user owns the order
        result = await db.execute(
            select(Order).where(
                Order.id == order_id,
                Order.buyer_id == current_user.id
            )
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or access denied"
            )
        
        payment_intent = await processor.create_payment_intent(
            order_id=order_id,
            customer_email=current_user.email,
            redirect_url=redirect_url,
            payment_method_types=payment_methods
        )
        
        return {
            "intent_id": payment_intent.id,
            "intent_reference": payment_intent.intent_reference,
            "amount": payment_intent.amount_in_currency,
            "currency": payment_intent.currency,
            "expires_at": payment_intent.expires_at,
            "status": "created"
        }
        
    except Exception as e:
        logger.error(f"Error creating payment intent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment intent"
        )

@router.post("/card", response_model=PaymentResponse)
async def process_card_payment(
    payment_request: CardPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Process credit/debit card payment"""
    try:
        processor = PaymentProcessor(db)
        
        # Verify user owns the order
        result = await db.execute(
            select(Order).where(
                Order.id == payment_request.order_id,
                Order.buyer_id == current_user.id
            )
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or access denied"
            )
        
        # Prepare card data
        card_data = {
            "number": payment_request.card_number,
            "exp_month": payment_request.exp_month,
            "exp_year": payment_request.exp_year,
            "cvc": payment_request.cvc,
            "card_holder": payment_request.card_holder,
            "installments": payment_request.installments
        }
        
        # Prepare customer data
        customer_data = {
            "email": current_user.email,
            "full_name": current_user.full_name,
            "phone": payment_request.customer_phone or current_user.telefono or "",
            "redirect_url": payment_request.redirect_url
        }
        
        result = await processor.process_card_payment(
            order_id=payment_request.order_id,
            card_data=card_data,
            customer_data=customer_data
        )
        
        return PaymentResponse(
            transaction_id=result["transaction_id"],
            wompi_transaction_id=result["wompi_transaction_id"],
            status=result["status"],
            checkout_url=result.get("checkout_url"),
            reference=result["reference"],
            message="Card payment initiated successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing card payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment processing failed"
        )

@router.post("/pse", response_model=PaymentResponse)
async def process_pse_payment(
    payment_request: PSEPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Process PSE bank transfer payment"""
    try:
        processor = PaymentProcessor(db)
        
        # Verify user owns the order
        result = await db.execute(
            select(Order).where(
                Order.id == payment_request.order_id,
                Order.buyer_id == current_user.id
            )
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or access denied"
            )
        
        # Prepare PSE data
        pse_data = {
            "user_type": payment_request.user_type,
            "user_legal_id": payment_request.user_legal_id,
            "bank_code": payment_request.bank_code
        }
        
        # Prepare customer data
        customer_data = {
            "email": current_user.email,
            "full_name": current_user.full_name,
            "redirect_url": payment_request.redirect_url
        }
        
        result = await processor.process_pse_payment(
            order_id=payment_request.order_id,
            pse_data=pse_data,
            customer_data=customer_data
        )
        
        return PaymentResponse(
            transaction_id=result["transaction_id"],
            wompi_transaction_id=result["wompi_transaction_id"],
            status=result["status"],
            checkout_url=result.get("pse_redirect_url"),
            reference=result["reference"],
            message="PSE payment initiated successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing PSE payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PSE payment processing failed"
        )

@router.get("/status/{transaction_reference}", response_model=PaymentStatusResponse)
async def get_payment_status(
    transaction_reference: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payment status by transaction reference"""
    try:
        processor = PaymentProcessor(db)
        
        # Verify user has access to this transaction
        result = await db.execute(
            select(Transaction)
            .join(Order)
            .where(
                Transaction.transaction_reference == transaction_reference,
                Order.buyer_id == current_user.id
            )
        )
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found or access denied"
            )
        
        status_data = await processor.get_payment_status(transaction_reference)
        
        return PaymentStatusResponse(
            transaction_id=status_data["transaction_id"],
            reference=status_data["reference"],
            status=status_data["status"],
            amount=status_data["amount"],
            currency=status_data["currency"],
            order_number=status_data["order_number"],
            created_at=status_data["created_at"].isoformat() if status_data["created_at"] else "",
            failure_reason=status_data.get("failure_reason")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get payment status"
        )

@router.get("/methods", response_model=PaymentMethodsResponse)
async def get_payment_methods(db: AsyncSession = Depends(get_db)):
    """Get available payment methods and PSE banks"""
    try:
        processor = PaymentProcessor(db)
        pse_banks = await processor.get_pse_banks()
        
        wompi_service = get_wompi_service()
        
        return PaymentMethodsResponse(
            card_enabled=True,
            pse_enabled=True,
            pse_banks=[
                PSEBank(
                    financial_institution_code=bank["financial_institution_code"],
                    financial_institution_name=bank["financial_institution_name"]
                )
                for bank in pse_banks
            ],
            wompi_public_key=wompi_service.config.public_key
        )
        
    except Exception as e:
        logger.error(f"Error getting payment methods: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get payment methods"
        )

@router.post("/cancel/{transaction_id}")
async def cancel_payment(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a pending payment"""
    try:
        # Verify user has access to this transaction
        result = await db.execute(
            select(Transaction)
            .join(Order)
            .where(
                Transaction.id == transaction_id,
                Order.buyer_id == current_user.id
            )
        )
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found or access denied"
            )
        
        processor = PaymentProcessor(db)
        success = await processor.cancel_payment(transaction_id)
        
        return {
            "success": success,
            "message": "Payment cancelled successfully" if success else "Payment could not be cancelled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel payment"
        )

@router.post("/webhook")
async def wompi_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Handle Wompi webhook notifications"""
    try:
        # Get raw payload and signature
        payload = await request.body()
        signature = request.headers.get("X-Signature", "")
        
        if not signature:
            logger.warning("Webhook received without signature")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing signature"
            )
        
        # Parse JSON payload
        try:
            event_data = json.loads(payload.decode())
        except json.JSONDecodeError:
            logger.error("Invalid JSON in webhook payload")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        
        # Process webhook in background
        background_tasks.add_task(
            process_webhook_async,
            payload.decode(),
            signature,
            event_data,
            db
        )
        
        return {"message": "Webhook received", "status": "processing"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )

async def process_webhook_async(
    payload: str,
    signature: str,
    event_data: Dict[str, Any],
    db: AsyncSession
):
    """Process webhook asynchronously"""
    try:
        handler = WebhookHandler(db)
        result = await handler.process_webhook(payload, signature, event_data)
        
        if result.get("processed"):
            logger.info(f"Webhook processed successfully: {result}")
        else:
            logger.warning(f"Webhook processing failed: {result}")
            
    except Exception as e:
        logger.error(f"Error in background webhook processing: {e}")

# Admin endpoints (could be moved to separate router)
@router.get("/admin/transactions")
async def get_all_transactions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all transactions (admin only)"""
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        result = await db.execute(
            select(Transaction)
            .options(
                selectinload(Transaction.order),
                selectinload(Transaction.payment)
            )
            .offset(skip)
            .limit(limit)
        )
        transactions = result.scalars().all()
        
        return [
            {
                "id": t.id,
                "reference": t.transaction_reference,
                "order_number": t.order.order_number,
                "amount": t.amount,
                "status": t.status.value,
                "payment_method": t.payment_method_type,
                "created_at": t.created_at,
                "gateway_transaction_id": t.gateway_transaction_id
            }
            for t in transactions
        ]
        
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transactions"
        )

@router.post("/admin/retry-webhooks")
async def retry_failed_webhooks(
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retry failed webhook events (admin only)"""
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        handler = WebhookHandler(db)
        result = await handler.retry_failed_webhooks(limit)
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrying webhooks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retry webhooks"
        )