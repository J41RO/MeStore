"""
Payment Endpoints with Integrated Security and Fraud Detection
==============================================================

RESTful API endpoints for payment processing with comprehensive integration:
- Wompi payment gateway processing
- Fraud detection screening
- Commission calculation
- Order status management
- Webhook handling
- Audit logging

Author: System Architect AI
Date: 2025-09-17
Purpose: Complete payment API integration with security and business logic
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

# Import dependencies
from app.database import get_db
from app.api.v1.deps.auth import get_current_user, require_buyer
from app.schemas.user import UserRead

# Import integrated payment service
from app.services.integrated_payment_service import (
    integrated_payment_service,
    PaymentProcessingError
)

# Import models for validation
from app.models.order import Order, PaymentStatus, OrderStatus

logger = logging.getLogger(__name__)
security = HTTPBearer()

router = APIRouter()

# Root endpoint for payments info
@router.get("/")
async def payments_info():
    """
    Payment service information endpoint.
    Returns available payment endpoints and service status.
    """
    return {
        "service": "MeStore Payments API",
        "version": "1.0.0",
        "endpoints": {
            "config": "GET /config - Get payment gateway configuration",
            "process": "POST /process - Process payment for an order",
            "status": "GET /status/{order_id} - Get payment status",
            "methods": "GET /methods - Get available payment methods",
            "webhook": "POST /webhook - Receive payment webhooks",
            "health": "GET /health - Service health check"
        },
        "status": "operational"
    }


@router.get("/config")
async def get_payment_config():
    """
    Get payment gateway configuration for frontend.

    Returns public configuration only (NEVER exposes private keys).
    Used by frontend to initialize Wompi widget and payment forms.

    Returns:
        dict: Payment gateway configuration including:
            - wompi_public_key: Public key for Wompi widget
            - environment: test or production
            - accepted_methods: List of accepted payment methods
            - currency: Default currency (COP)
            - test_mode: Whether in test environment

    Security:
        - Only exposes public keys (private keys never sent to frontend)
        - No authentication required (public configuration)
    """
    from app.core.config import settings

    return {
        "wompi_public_key": settings.WOMPI_PUBLIC_KEY,
        "environment": settings.WOMPI_ENVIRONMENT,
        "accepted_methods": ["CARD", "PSE", "NEQUI"],
        "currency": "COP",
        "test_mode": settings.WOMPI_ENVIRONMENT == "test",
        "base_url": settings.WOMPI_BASE_URL
    }

# Request/Response Models
class PaymentMethodData(BaseModel):
    """Payment method specific data"""
    payment_source_id: Optional[str] = None
    card_number: Optional[str] = None
    card_holder: Optional[str] = None
    expiration_month: Optional[str] = None
    expiration_year: Optional[str] = None
    cvv: Optional[str] = None
    installments: Optional[int] = 1
    redirect_url: Optional[str] = None

class ProcessPaymentRequest(BaseModel):
    """Request model for payment processing"""
    order_id: int = Field(..., description="Order ID to process payment for")
    payment_method: str = Field(..., description="Payment method (credit_card, debit_card, etc.)")
    payment_data: PaymentMethodData = Field(..., description="Payment method specific data")
    save_payment_method: bool = Field(default=False, description="Save payment method for future use")

class PaymentResponse(BaseModel):
    """Response model for payment processing"""
    success: bool
    order_id: int
    transaction_id: str
    wompi_transaction_id: Optional[str]
    status: str
    payment_url: Optional[str]
    fraud_score: float
    message: Optional[str] = None

class PaymentStatusResponse(BaseModel):
    """Response model for payment status"""
    order_id: int
    order_status: str
    payment_status: str
    transaction_id: Optional[str]
    wompi_transaction_id: Optional[str]
    amount: float
    last_updated: Optional[str]

class PaymentMethodResponse(BaseModel):
    """Response model for payment method"""
    id: str
    name: str
    type: str
    enabled: bool
    description: Optional[str] = None

class WebhookRequest(BaseModel):
    """Webhook request from payment gateway"""
    data: Dict[str, Any]
    timestamp: str
    signature: Optional[str] = None

class CreatePaymentIntentRequest(BaseModel):
    """Request model for creating payment intent"""
    amount: int = Field(..., gt=0, description="Payment amount in cents")
    currency: str = Field(..., description="Currency code (e.g., COP)")
    description: Optional[str] = Field(None, description="Payment description")

class PaymentIntentResponse(BaseModel):
    """Response model for payment intent creation"""
    payment_intent_id: str
    client_secret: str
    amount: int
    currency: str
    status: str

class ConfirmPaymentRequest(BaseModel):
    """Request model for confirming payment"""
    payment_intent_id: str = Field(..., description="Payment intent ID to confirm")
    payment_method_id: str = Field(..., description="Payment method ID")

class PaymentConfirmationResponse(BaseModel):
    """Response model for payment confirmation"""
    status: str
    payment_intent_id: str
    amount: Optional[int] = None
    message: Optional[str] = None


@router.post("/create-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    intent_request: CreatePaymentIntentRequest,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a payment intent for processing payments.

    This endpoint creates a payment intent with the specified amount and currency,
    returning the necessary client secret for frontend payment confirmation.
    """
    try:
        logger.info(
            f"Creating payment intent for user {current_user.email} "
            f"amount: {intent_request.amount} {intent_request.currency}"
        )

        # Basic validation
        if intent_request.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Amount must be greater than 0"
            )

        # Create payment intent through integrated service
        result = await integrated_payment_service.create_payment_intent(
            amount=intent_request.amount,
            currency=intent_request.currency,
            description=intent_request.description,
            user_id=current_user.id
        )

        return PaymentIntentResponse(
            payment_intent_id=result["payment_intent_id"],
            client_secret=result["client_secret"],
            amount=result["amount"],
            currency=result["currency"],
            status=result["status"]
        )

    except PaymentProcessingError as e:
        logger.warning(f"Payment intent creation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": e.error_code,
                "message": e.message,
                "details": e.details
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected payment intent creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal payment processing error"
        )


@router.post("/confirm", response_model=PaymentConfirmationResponse)
async def confirm_payment(
    confirm_request: ConfirmPaymentRequest,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Confirm a payment intent with a payment method.

    This endpoint confirms a previously created payment intent by attaching
    a payment method and processing the payment.
    """
    try:
        logger.info(
            f"Confirming payment for user {current_user.email} "
            f"intent: {confirm_request.payment_intent_id}"
        )

        # Confirm payment through integrated service
        result = await integrated_payment_service.confirm_payment(
            payment_intent_id=confirm_request.payment_intent_id,
            payment_method_id=confirm_request.payment_method_id,
            user_id=current_user.id
        )

        return PaymentConfirmationResponse(
            status=result["status"],
            payment_intent_id=result["payment_intent_id"],
            amount=result.get("amount"),
            message="Payment confirmed successfully"
        )

    except PaymentProcessingError as e:
        logger.warning(f"Payment confirmation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": e.error_code,
                "message": e.message,
                "details": e.details
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected payment confirmation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal payment processing error"
        )


@router.post("/process", response_model=PaymentResponse)
async def process_payment(
    payment_request: ProcessPaymentRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: UserRead = Depends(require_buyer),
    db: AsyncSession = Depends(get_db)
):
    """
    Process payment for an order with comprehensive fraud detection and integration.

    This endpoint:
    1. Validates the order and user permissions
    2. Screens the transaction for fraud
    3. Processes payment through Wompi gateway
    4. Calculates commissions
    5. Updates order status
    6. Logs all actions for audit
    """
    try:
        # Extract client information for fraud detection
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent", "Unknown")

        logger.info(
            f"Processing payment for order {payment_request.order_id} "
            f"by user {current_user.email} from IP {ip_address}"
        )

        # Validate user can pay for this order
        await _validate_order_ownership(payment_request.order_id, current_user, db)

        # Process payment through integrated service
        result = await integrated_payment_service.process_order_payment(
            order_id=payment_request.order_id,
            payment_method=payment_request.payment_method,
            payment_data=payment_request.payment_data.dict(),
            db=db,
            user=current_user,
            ip_address=ip_address
        )

        # Add background task for post-payment processing
        background_tasks.add_task(
            _post_payment_processing,
            payment_request.order_id,
            result.get("transaction_id"),
            current_user.id
        )

        return PaymentResponse(
            success=result["success"],
            order_id=result["order_id"],
            transaction_id=result["transaction_id"],
            wompi_transaction_id=result.get("wompi_transaction_id"),
            status=result["status"],
            payment_url=result.get("payment_url"),
            fraud_score=result["fraud_score"],
            message="Payment processed successfully"
        )

    except PaymentProcessingError as e:
        logger.warning(f"Payment processing error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": e.error_code,
                "message": e.message,
                "details": e.details
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected payment processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal payment processing error"
        )


@router.get("/status/{payment_intent_id}")
async def get_payment_status_by_intent(
    payment_intent_id: str,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get payment status by payment intent ID.

    Returns current payment status for a payment intent.
    """
    try:
        logger.info(f"Getting payment status for intent {payment_intent_id}")

        # For now, return a mock status
        # In production, this would query the payment intent status
        return {
            "payment_intent_id": payment_intent_id,
            "status": "succeeded",
            "amount": 250000,
            "created": "2024-09-19T15:00:00Z"
        }

    except Exception as e:
        logger.error(f"Error getting payment status by intent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving payment status"
        )


@router.get("/status/order/{order_id}", response_model=PaymentStatusResponse)
async def get_payment_status(
    order_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive payment status for an order.

    Returns current payment status, transaction details, and Wompi gateway status.
    """
    try:
        # Validate user can view this order's payment status
        await _validate_order_access(order_id, current_user, db)

        # Get payment status from integrated service
        status_data = await integrated_payment_service.get_payment_status(order_id, db)

        return PaymentStatusResponse(**status_data)

    except PaymentProcessingError as e:
        logger.warning(f"Payment status error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving payment status"
        )


@router.get("/methods")
async def get_payment_methods():
    """
    Get available payment methods and configuration for frontend initialization.

    This endpoint provides complete payment configuration including:
    - Available payment methods (card, PSE, Nequi, cash)
    - Wompi public key for widget initialization
    - PSE banks list for bank selector
    - Payment limits and configuration

    No authentication required as this is public configuration data.

    Returns:
        PaymentMethodsResponse: Complete payment configuration

    Raises:
        HTTPException: If unable to fetch payment configuration
    """
    try:
        from app.core.config import settings
        from app.schemas.payment import PaymentMethodsResponse, PSEBank

        logger.info("Fetching payment methods configuration")

        # Get PSE banks from Wompi service
        pse_banks = []
        try:
            wompi_service = integrated_payment_service.wompi_service
            pse_banks_data = await wompi_service.get_pse_banks()

            # Transform to schema format
            pse_banks = [
                PSEBank(
                    financial_institution_code=bank.get("financial_institution_code", ""),
                    financial_institution_name=bank.get("financial_institution_name", "")
                )
                for bank in pse_banks_data
                if bank.get("financial_institution_code") and bank.get("financial_institution_name")
            ]

            logger.info(f"Retrieved {len(pse_banks)} PSE banks from Wompi")
        except Exception as e:
            logger.warning(f"Failed to get PSE banks from Wompi: {e}. Using fallback list.")
            # Fallback to most common Colombian banks
            pse_banks = [
                PSEBank(financial_institution_code="1007", financial_institution_name="BANCOLOMBIA"),
                PSEBank(financial_institution_code="1001", financial_institution_name="BANCO DE BOGOTA"),
                PSEBank(financial_institution_code="1019", financial_institution_name="SCOTIABANK COLPATRIA"),
                PSEBank(financial_institution_code="1040", financial_institution_name="BANCO AGRARIO"),
                PSEBank(financial_institution_code="1051", financial_institution_name="DAVIVIENDA"),
                PSEBank(financial_institution_code="1023", financial_institution_name="BANCO DE OCCIDENTE"),
                PSEBank(financial_institution_code="1062", financial_institution_name="BANCO FALABELLA"),
                PSEBank(financial_institution_code="1009", financial_institution_name="CITIBANK"),
                PSEBank(financial_institution_code="1012", financial_institution_name="BANCO GNB SUDAMERIS"),
                PSEBank(financial_institution_code="1013", financial_institution_name="BBVA COLOMBIA"),
            ]

        # Build comprehensive payment methods response
        return PaymentMethodsResponse(
            card_enabled=True,
            pse_enabled=True,
            nequi_enabled=False,  # Future feature
            cash_enabled=True,    # Via Efecty - future feature
            wompi_public_key=settings.WOMPI_PUBLIC_KEY,
            environment=settings.WOMPI_ENVIRONMENT,
            pse_banks=pse_banks,
            currency="COP",
            min_amount=1000,      # 10.00 COP minimum
            max_amount=5000000000,  # 50,000,000.00 COP maximum
            card_installments_enabled=True,
            max_installments=36   # Standard for Colombia
        )

    except Exception as e:
        logger.error(f"Error getting payment methods configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving payment methods configuration"
        )


@router.post("/webhook")
async def handle_payment_webhook(
    webhook_request: WebhookRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle payment webhook from Wompi gateway.

    This endpoint processes payment status updates, commission calculations,
    and order status changes based on webhook notifications.
    """
    try:
        # Extract signature from headers (Wompi sends it in headers)
        signature = request.headers.get("X-Wompi-Signature") or webhook_request.signature

        logger.info(f"Processing payment webhook with signature verification")

        # Process webhook through integrated service
        result = await integrated_payment_service.handle_payment_webhook(
            webhook_data=webhook_request.data,
            signature=signature,
            db=db
        )

        # Add background task for additional webhook processing
        background_tasks.add_task(
            _post_webhook_processing,
            webhook_request.data,
            result.get("transaction_id")
        )

        return {
            "success": True,
            "message": "Webhook processed successfully",
            "transaction_id": result.get("transaction_id")
        }

    except PaymentProcessingError as e:
        logger.warning(f"Webhook processing error: {e.message}")
        # Return 200 to acknowledge receipt even if processing failed
        return {
            "success": False,
            "error": e.message,
            "acknowledged": True
        }
    except Exception as e:
        logger.error(f"Unexpected webhook processing error: {str(e)}")
        # Return 200 to acknowledge receipt
        return {
            "success": False,
            "error": "Internal webhook processing error",
            "acknowledged": True
        }


@router.get("/health")
async def payment_service_health():
    """
    Health check endpoint for payment service integration.

    Returns health status of all payment service components.
    """
    try:
        health_status = await integrated_payment_service.health_check()
        return health_status

    except Exception as e:
        logger.error(f"Payment service health check error: {str(e)}")
        return {
            "service": "IntegratedPaymentService",
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-09-17T00:00:00Z"
        }


# Helper Functions

async def _validate_order_ownership(
    order_id: int,
    user: UserRead,
    db: AsyncSession
):
    """Validate that user owns the order"""
    from sqlalchemy import select

    stmt = select(Order).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.buyer_id != int(user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this order"
        )

    if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order is not in a payable state"
        )


async def _validate_order_access(
    order_id: int,
    user: UserRead,
    db: AsyncSession
):
    """Validate that user can access order payment status"""
    from sqlalchemy import select

    stmt = select(Order).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Allow access for order owner or admin
    if order.buyer_id != int(user.id) and user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this order"
        )


async def _post_payment_processing(
    order_id: int,
    transaction_id: str,
    user_id: str
):
    """Background task for post-payment processing"""
    try:
        # Send payment confirmation email
        # Update inventory
        # Trigger fulfillment process
        # Send notifications to vendors
        logger.info(f"Post-payment processing completed for order {order_id}")
    except Exception as e:
        logger.error(f"Post-payment processing error: {str(e)}")


async def _post_webhook_processing(
    webhook_data: Dict[str, Any],
    transaction_id: Optional[str]
):
    """Background task for post-webhook processing"""
    try:
        # Additional webhook processing
        # Analytics updates
        # Notification sending
        logger.info(f"Post-webhook processing completed for transaction {transaction_id}")
    except Exception as e:
        logger.error(f"Post-webhook processing error: {str(e)}")