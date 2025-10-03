"""
Efecty Cash Payment Service for Colombia
=========================================

Service for generating and managing cash payment codes for Efecty network.

Efecty is the largest cash payment network in Colombia with 20,000+ physical locations.
This service generates payment codes that customers can pay at any Efecty point.

Features:
- Payment code generation with expiration
- Payment verification and confirmation
- SMS/Email notifications with payment instructions
- Barcode generation for quick payment
- Location finder integration
- Payment timeout management

Author: Payment Systems AI
Date: 2025-10-01
Purpose: Efecty cash payment integration for unbanked population access
"""

import logging
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from decimal import Decimal
import hashlib
import uuid

logger = logging.getLogger(__name__)
payment_logger = logging.getLogger(f"{__name__}.payments")


class EfectyError(Exception):
    """Base exception for Efecty service errors"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class EfectyValidationError(EfectyError):
    """Validation-related errors"""
    pass


class EfectyConfig:
    """Efecty service configuration"""

    def __init__(self):
        from app.core.config import settings

        self.enabled = settings.EFECTY_ENABLED
        self.payment_timeout_hours = settings.EFECTY_PAYMENT_TIMEOUT_HOURS
        self.code_prefix = settings.EFECTY_CODE_PREFIX
        self.min_amount = settings.EFECTY_MIN_AMOUNT
        self.max_amount = settings.EFECTY_MAX_AMOUNT

        # Validate configuration
        self._validate_config()

    def _validate_config(self):
        """Validate configuration parameters"""
        if self.min_amount >= self.max_amount:
            raise ValueError("EFECTY_MIN_AMOUNT must be less than EFECTY_MAX_AMOUNT")

        if self.payment_timeout_hours <= 0:
            raise ValueError("EFECTY_PAYMENT_TIMEOUT_HOURS must be positive")

        if len(self.code_prefix) < 2 or len(self.code_prefix) > 5:
            raise ValueError("EFECTY_CODE_PREFIX must be 2-5 characters")


class EfectyService:
    """
    Efecty cash payment service for Colombia.

    Generates payment codes that customers can pay at any Efecty location.
    Ideal for customers without bank accounts or credit cards.

    Payment Flow:
    1. Customer selects "Efecty" as payment method
    2. System generates unique payment code with expiration
    3. Customer receives code via SMS/Email with instructions
    4. Customer goes to any Efecty location with code
    5. Customer pays cash and receives receipt
    6. System receives payment confirmation (manual or via webhook)
    7. Order is marked as paid and processed
    """

    def __init__(self):
        self.config = EfectyConfig()

        payment_logger.info(
            f"Efecty service initialized",
            extra={
                "enabled": self.config.enabled,
                "timeout_hours": self.config.payment_timeout_hours,
                "min_amount": self.config.min_amount,
                "max_amount": self.config.max_amount
            }
        )

    def generate_payment_code(
        self,
        order_id: int,
        amount: int,
        customer_email: str,
        customer_name: str,
        customer_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate Efecty payment code for an order.

        Args:
            order_id: Order identifier
            amount: Payment amount in COP (not cents)
            customer_email: Customer email for notifications
            customer_name: Customer full name
            customer_phone: Customer phone for SMS (optional)

        Returns:
            Dict with payment code details:
                - payment_code: Unique code for payment
                - barcode_data: Data for barcode generation
                - expiration_date: When code expires
                - amount: Payment amount
                - instructions: Payment instructions for customer

        Raises:
            EfectyValidationError: If validation fails
        """
        # Validate inputs
        if not self.config.enabled:
            raise EfectyError("Efecty payments are disabled", error_code="EFECTY_DISABLED")

        if amount < self.config.min_amount:
            raise EfectyValidationError(
                f"Amount {amount} COP is below minimum {self.config.min_amount} COP",
                error_code="AMOUNT_TOO_LOW"
            )

        if amount > self.config.max_amount:
            raise EfectyValidationError(
                f"Amount {amount} COP exceeds maximum {self.config.max_amount} COP",
                error_code="AMOUNT_TOO_HIGH"
            )

        if not customer_email or "@" not in customer_email:
            raise EfectyValidationError("Valid customer email is required", error_code="INVALID_EMAIL")

        if not customer_name or len(customer_name.strip()) < 3:
            raise EfectyValidationError("Valid customer name is required", error_code="INVALID_NAME")

        try:
            # Generate unique payment code
            # Format: PREFIX-ORDERID-RANDOM (e.g., MST-12345-A7B9C2)
            random_suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            payment_code = f"{self.config.code_prefix}-{order_id}-{random_suffix}"

            # Calculate expiration date
            expiration_date = datetime.utcnow() + timedelta(hours=self.config.payment_timeout_hours)

            # Generate barcode data (Code 128 compatible)
            # Barcode contains: payment_code + checksum
            checksum = self._generate_checksum(payment_code, amount)
            barcode_data = f"{payment_code}{checksum}"

            # Generate reference number for Efecty system
            reference_number = self._generate_reference_number(order_id)

            payment_logger.info(
                f"Generated Efecty payment code",
                extra={
                    "order_id": order_id,
                    "payment_code": payment_code,
                    "amount": amount,
                    "expiration_hours": self.config.payment_timeout_hours
                }
            )

            return {
                "payment_code": payment_code,
                "reference_number": reference_number,
                "barcode_data": barcode_data,
                "amount": amount,
                "currency": "COP",
                "expiration_date": expiration_date.isoformat(),
                "expiration_timestamp": int(expiration_date.timestamp()),
                "customer_name": customer_name,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
                "instructions": self._generate_instructions(payment_code, amount, expiration_date),
                "locations_info": self._get_locations_info(),
                "created_at": datetime.utcnow().isoformat()
            }

        except EfectyError:
            raise
        except Exception as e:
            logger.error(f"Error generating Efecty payment code: {e}")
            raise EfectyError(f"Failed to generate payment code: {e}", error_code="CODE_GENERATION_FAILED")

    def _generate_checksum(self, payment_code: str, amount: int) -> str:
        """
        Generate checksum for barcode validation.

        Uses SHA-256 hash of payment_code + amount, takes first 4 characters.

        Args:
            payment_code: Payment code
            amount: Payment amount

        Returns:
            str: 4-character checksum
        """
        data = f"{payment_code}{amount}".encode('utf-8')
        hash_object = hashlib.sha256(data)
        return hash_object.hexdigest()[:4].upper()

    def _generate_reference_number(self, order_id: int) -> str:
        """
        Generate reference number for Efecty system.

        Format: YYYYMMDD-ORDERID (e.g., 20251001-12345)

        Args:
            order_id: Order identifier

        Returns:
            str: Reference number
        """
        date_prefix = datetime.utcnow().strftime("%Y%m%d")
        return f"{date_prefix}-{order_id}"

    def _generate_instructions(self, payment_code: str, amount: int, expiration_date: datetime) -> Dict[str, Any]:
        """
        Generate payment instructions for customer.

        Args:
            payment_code: Generated payment code
            amount: Payment amount
            expiration_date: Code expiration date

        Returns:
            Dict with instructions in Spanish
        """
        # Format amount with thousands separators
        formatted_amount = f"{amount:,}".replace(",", ".")

        expiration_str = expiration_date.strftime("%d/%m/%Y a las %I:%M %p")

        return {
            "title": "Instrucciones de Pago en Efecty",
            "steps": [
                {
                    "step": 1,
                    "title": "Dirígete a cualquier punto Efecty",
                    "description": f"Tienes hasta el {expiration_str} para realizar el pago. Encuentra la ubicación más cercana en www.efecty.com.co"
                },
                {
                    "step": 2,
                    "title": "Presenta tu código de pago",
                    "description": f"Menciona al cajero que vas a pagar con el código: {payment_code}"
                },
                {
                    "step": 3,
                    "title": "Realiza el pago en efectivo",
                    "description": f"Paga exactamente ${formatted_amount} COP"
                },
                {
                    "step": 4,
                    "title": "Guarda tu comprobante",
                    "description": "Recibirás un comprobante de pago. Guárdalo como evidencia de tu transacción."
                },
                {
                    "step": 5,
                    "title": "Confirmación automática",
                    "description": "Tu pedido será procesado automáticamente una vez confirmemos el pago (puede tomar hasta 30 minutos)."
                }
            ],
            "payment_code": payment_code,
            "amount": formatted_amount,
            "currency": "COP",
            "expiration_date": expiration_str,
            "important_notes": [
                "El código expira automáticamente después de la fecha límite",
                "Solo se aceptan pagos en efectivo",
                "El monto debe ser exacto - Efecty no da cambio para este tipo de transacciones",
                "Conserva tu comprobante hasta recibir tu pedido"
            ]
        }

    def _get_locations_info(self) -> Dict[str, Any]:
        """
        Get information about Efecty locations.

        Returns:
            Dict with locations information
        """
        return {
            "total_locations": "20,000+",
            "coverage": "Todo Colombia",
            "finder_url": "https://www.efecty.com.co/puntos-de-atencion",
            "customer_service": "01 8000 413 338",
            "hours": "Lunes a Sábado: 8:00 AM - 6:00 PM. Domingos y festivos: algunos puntos abiertos",
            "major_cities": [
                "Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena",
                "Bucaramanga", "Pereira", "Cúcuta", "Ibagué", "Santa Marta"
            ]
        }

    def validate_payment_code(self, payment_code: str) -> Dict[str, Any]:
        """
        Validate format of payment code.

        Args:
            payment_code: Payment code to validate

        Returns:
            Dict with validation result
        """
        try:
            # Expected format: PREFIX-ORDERID-RANDOM
            parts = payment_code.split("-")

            if len(parts) != 3:
                return {
                    "valid": False,
                    "error": "Invalid payment code format. Expected: PREFIX-ORDERID-RANDOM"
                }

            prefix, order_id_str, random_suffix = parts

            if prefix != self.config.code_prefix:
                return {
                    "valid": False,
                    "error": f"Invalid prefix. Expected: {self.config.code_prefix}"
                }

            if not order_id_str.isdigit():
                return {
                    "valid": False,
                    "error": "Order ID must be numeric"
                }

            if len(random_suffix) != 6:
                return {
                    "valid": False,
                    "error": "Invalid random suffix length"
                }

            return {
                "valid": True,
                "prefix": prefix,
                "order_id": int(order_id_str),
                "random_suffix": random_suffix
            }

        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }

    def is_code_expired(self, created_at: datetime) -> bool:
        """
        Check if payment code has expired.

        Args:
            created_at: When code was created

        Returns:
            bool: True if expired
        """
        expiration_date = created_at + timedelta(hours=self.config.payment_timeout_hours)
        return datetime.utcnow() > expiration_date

    def get_payment_status(self, payment_code: str, created_at: datetime) -> Dict[str, Any]:
        """
        Get current status of payment code.

        Args:
            payment_code: Payment code to check
            created_at: When code was created

        Returns:
            Dict with status information
        """
        validation = self.validate_payment_code(payment_code)

        if not validation["valid"]:
            return {
                "status": "invalid",
                "message": validation["error"]
            }

        is_expired = self.is_code_expired(created_at)
        expiration_date = created_at + timedelta(hours=self.config.payment_timeout_hours)
        time_remaining = expiration_date - datetime.utcnow()

        if is_expired:
            return {
                "status": "expired",
                "message": "Payment code has expired",
                "expired_at": expiration_date.isoformat()
            }
        else:
            return {
                "status": "active",
                "message": "Payment code is active and awaiting payment",
                "expires_at": expiration_date.isoformat(),
                "hours_remaining": int(time_remaining.total_seconds() / 3600),
                "minutes_remaining": int(time_remaining.total_seconds() / 60)
            }

    def generate_payment_confirmation_data(
        self,
        payment_code: str,
        amount: int,
        paid_at: datetime,
        efecty_transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate payment confirmation data after Efecty payment is completed.

        This would typically be called when:
        1. Manual confirmation by admin
        2. Webhook from Efecty (if API integration exists)
        3. Automated reconciliation process

        Args:
            payment_code: Payment code that was paid
            amount: Amount paid
            paid_at: When payment was made
            efecty_transaction_id: Efecty's transaction ID (if available)

        Returns:
            Dict with confirmation data
        """
        validation = self.validate_payment_code(payment_code)

        if not validation["valid"]:
            raise EfectyValidationError(
                f"Invalid payment code: {validation['error']}",
                error_code="INVALID_CODE"
            )

        payment_logger.info(
            f"Efecty payment confirmed",
            extra={
                "payment_code": payment_code,
                "amount": amount,
                "order_id": validation.get("order_id"),
                "efecty_transaction_id": efecty_transaction_id
            }
        )

        return {
            "payment_code": payment_code,
            "order_id": validation["order_id"],
            "amount": amount,
            "currency": "COP",
            "paid_at": paid_at.isoformat(),
            "payment_method": "EFECTY",
            "efecty_transaction_id": efecty_transaction_id or f"EFY-{uuid.uuid4().hex[:12].upper()}",
            "status": "confirmed",
            "confirmation_id": f"CONF-{uuid.uuid4().hex[:16].upper()}",
            "confirmed_at": datetime.utcnow().isoformat()
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Health check for Efecty service.

        Returns:
            Dict with health status
        """
        health_result = {
            "service": "EfectyService",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }

        try:
            # Check configuration
            if not self.config.enabled:
                health_result["status"] = "disabled"
                health_result["checks"]["configuration"] = {
                    "status": "disabled",
                    "message": "Efecty payments are disabled in configuration"
                }
            else:
                health_result["checks"]["configuration"] = {
                    "status": "healthy",
                    "timeout_hours": self.config.payment_timeout_hours,
                    "min_amount": self.config.min_amount,
                    "max_amount": self.config.max_amount
                }

            # Test code generation
            try:
                test_code_data = self.generate_payment_code(
                    order_id=99999,
                    amount=50000,
                    customer_email="test@example.com",
                    customer_name="Test Customer"
                )

                health_result["checks"]["code_generation"] = {
                    "status": "healthy",
                    "test_code_format": test_code_data["payment_code"]
                }
            except Exception as e:
                health_result["status"] = "degraded"
                health_result["checks"]["code_generation"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }

            return health_result

        except Exception as e:
            health_result["status"] = "unhealthy"
            health_result["error"] = str(e)
            logger.error(f"Efecty health check failed: {e}")
            return health_result


# Singleton instance
_efecty_service = None


def get_efecty_service() -> EfectyService:
    """Get or create the Efecty service singleton"""
    global _efecty_service
    if _efecty_service is None:
        _efecty_service = EfectyService()
    return _efecty_service
