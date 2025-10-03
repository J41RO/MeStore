"""
PayU Payment Gateway Service for Colombia
==========================================

Complete integration with PayU Latam payment gateway for Colombian payments.

Features:
- Credit/Debit card payments with installments
- PSE bank transfer support
- Cash payment methods (Efecty, Baloto, Su Red)
- Fraud detection integration
- Webhook handling with MD5 signature validation
- Multi-currency support (primarily COP)
- Comprehensive error handling and logging

Author: Payment Systems AI
Date: 2025-10-01
Purpose: PayU gateway integration for Colombian market
"""

import httpx
import hashlib
import hmac
import json
import logging
import asyncio
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from decimal import Decimal
from dataclasses import dataclass
from functools import wraps
import os

logger = logging.getLogger(__name__)
payment_logger = logging.getLogger(f"{__name__}.payments")
security_logger = logging.getLogger(f"{__name__}.security")


# ===== EXCEPTIONS =====

class PayUError(Exception):
    """Base exception for PayU service errors"""
    def __init__(self, message: str, error_code: Optional[str] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.error_code = error_code
        self.response_data = response_data
        super().__init__(message)


class PayUNetworkError(PayUError):
    """Network-related errors"""
    pass


class PayUAuthenticationError(PayUError):
    """Authentication-related errors"""
    pass


class PayUValidationError(PayUError):
    """Validation-related errors"""
    pass


class PayUTransactionError(PayUError):
    """Transaction processing errors"""
    pass


@dataclass
class RetryConfig:
    """Configuration for retry logic"""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


def retry_on_failure(retry_config: Optional[RetryConfig] = None):
    """Decorator for implementing retry logic with exponential backoff"""
    if retry_config is None:
        retry_config = RetryConfig()

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            delay = retry_config.initial_delay

            for attempt in range(retry_config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except (httpx.TimeoutException, httpx.NetworkError, PayUNetworkError) as e:
                    last_exception = e
                    if attempt == retry_config.max_attempts - 1:
                        logger.error(f"Final retry attempt failed for {func.__name__}: {e}")
                        break

                    # Calculate delay with jitter
                    actual_delay = delay
                    if retry_config.jitter:
                        import random
                        actual_delay *= (0.5 + random.random() * 0.5)

                    logger.warning(
                        f"Attempt {attempt + 1}/{retry_config.max_attempts} failed for {func.__name__}: {e}. "
                        f"Retrying in {actual_delay:.2f}s"
                    )

                    await asyncio.sleep(actual_delay)
                    delay = min(delay * retry_config.exponential_base, retry_config.max_delay)

                except (PayUAuthenticationError, PayUValidationError) as e:
                    # Don't retry authentication or validation errors
                    logger.error(f"Non-retryable error in {func.__name__}: {e}")
                    raise
                except Exception as e:
                    # Unknown error - don't retry
                    logger.error(f"Unknown error in {func.__name__}: {e}")
                    raise

            # All retries exhausted
            raise last_exception
        return wrapper
    return decorator


# ===== CONFIGURATION =====

class PayUConfig:
    """PayU configuration with security and performance settings"""

    def __init__(self):
        from app.core.config import settings

        # Get credentials based on environment
        creds = settings.get_payu_credentials()

        self.merchant_id = creds["merchant_id"]
        self.api_key = creds["api_key"]
        self.api_login = creds["api_login"]
        self.account_id = creds["account_id"]
        self.base_url = creds["base_url"]

        self.environment = os.getenv("PAYU_ENVIRONMENT", "test")
        self.timeout = float(os.getenv("PAYU_TIMEOUT", "30.0"))
        self.max_retries = int(os.getenv("PAYU_MAX_RETRIES", "3"))

        # Colombia-specific configuration
        self.country_code = "CO"
        self.currency = "COP"
        self.language = "es"

        # Validate configuration
        self._validate_config()

    def _validate_config(self):
        """Validate configuration parameters"""
        if not all([self.merchant_id, self.api_key, self.api_login, self.account_id]):
            raise ValueError("All PayU credentials must be set")

        if self.environment not in ["test", "production"]:
            raise ValueError(f"Invalid environment: {self.environment}")

        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production"

    @property
    def retry_config(self) -> RetryConfig:
        """Get retry configuration"""
        return RetryConfig(
            max_attempts=self.max_retries,
            initial_delay=1.0,
            max_delay=min(self.timeout / 2, 30.0),
            exponential_base=2.0,
            jitter=True
        )


# ===== MAIN SERVICE =====

class PayUService:
    """
    PayU Latam payment gateway service for Colombia.

    Supports:
    - Credit/Debit card payments (VISA, Mastercard, Amex, Diners)
    - PSE bank transfers
    - Cash payments (Efecty, Baloto, Su Red)
    - Installment plans (up to 36 months)
    - Fraud detection
    - Webhook notifications
    """

    def __init__(self):
        self.config = PayUConfig()

        # Create HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.config.timeout),
            verify=True,  # Always verify SSL
            headers={
                "Content-Type": "application/json; charset=UTF-8",
                "Accept": "application/json",
                "Content-Language": "es"
            }
        )

        payment_logger.info(
            f"PayU service initialized for {self.config.environment} environment",
            extra={"merchant_id": self.config.merchant_id, "country": self.config.country_code}
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _generate_signature(self, reference: str, amount: str, currency: str = "COP") -> str:
        """
        Generate MD5 signature for PayU requests.

        Formula: MD5(ApiKey~merchantId~referenceCode~amount~currency)

        Args:
            reference: Transaction reference code
            amount: Transaction amount (e.g., "50000.00")
            currency: Currency code (default: COP)

        Returns:
            str: MD5 hash signature
        """
        try:
            # PayU requires exact format with 1 decimal place for whole numbers, 2 for decimals
            amount_str = f"{float(amount):.1f}" if float(amount) == int(float(amount)) else f"{float(amount):.2f}"

            signature_string = f"{self.config.api_key}~{self.config.merchant_id}~{reference}~{amount_str}~{currency}"

            signature = hashlib.md5(signature_string.encode('utf-8')).hexdigest()

            security_logger.debug(
                f"Generated PayU signature",
                extra={"reference": reference, "amount": amount_str}
            )

            return signature

        except Exception as e:
            security_logger.error(f"Failed to generate PayU signature: {e}")
            raise PayUError(f"Signature generation failed: {e}")

    def validate_webhook_signature(self, payload: Dict[str, Any], received_signature: str) -> bool:
        """
        Validate webhook signature from PayU.

        PayU webhook signature formula:
        MD5(ApiKey~merchantId~referenceCode~new_value~currency~state_pol)

        Args:
            payload: Webhook payload data
            received_signature: Signature received from PayU

        Returns:
            bool: True if signature is valid
        """
        try:
            reference = payload.get("reference_sale")
            amount = payload.get("value")  # or "new_value" in some webhooks
            currency = payload.get("currency")
            state_pol = payload.get("state_pol")  # Payment state

            if not all([reference, amount, currency, state_pol]):
                security_logger.warning("Missing required fields in webhook for signature validation")
                return False

            # Format amount as PayU expects
            amount_str = f"{float(amount):.1f}" if float(amount) == int(float(amount)) else f"{float(amount):.2f}"

            signature_string = f"{self.config.api_key}~{self.config.merchant_id}~{reference}~{amount_str}~{currency}~{state_pol}"
            expected_signature = hashlib.md5(signature_string.encode('utf-8')).hexdigest()

            is_valid = hmac.compare_digest(expected_signature, received_signature)

            if is_valid:
                security_logger.info("PayU webhook signature validation successful")
            else:
                security_logger.warning(
                    "PayU webhook signature validation failed",
                    extra={"expected_length": len(expected_signature), "received_length": len(received_signature)}
                )

            return is_valid

        except Exception as e:
            security_logger.error(f"Error validating PayU webhook signature: {e}")
            return False

    @retry_on_failure()
    async def ping(self) -> Dict[str, Any]:
        """
        Test PayU API connectivity and credentials.

        Returns:
            Dict with ping result
        """
        try:
            payload = {
                "language": "es",
                "command": "PING",
                "merchant": {
                    "apiLogin": self.config.api_login,
                    "apiKey": self.config.api_key
                },
                "test": not self.config.is_production
            }

            response = await self.client.post(
                self.config.base_url,
                json=payload
            )

            response.raise_for_status()
            data = response.json()

            if data.get("code") == "SUCCESS":
                payment_logger.info("PayU ping successful")
                return {
                    "status": "success",
                    "message": "PayU API connection successful",
                    "environment": self.config.environment
                }
            else:
                raise PayUError(f"PayU ping failed: {data.get('error')}", error_code=data.get("code"))

        except httpx.HTTPError as e:
            raise PayUNetworkError(f"PayU ping network error: {e}")
        except Exception as e:
            raise PayUError(f"PayU ping error: {e}")

    @retry_on_failure()
    async def create_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a payment transaction with PayU.

        Args:
            transaction_data: Transaction details including:
                - amount_in_cents: int (amount in cents)
                - customer_email: str
                - payment_method: str (VISA, MASTERCARD, PSE, etc.)
                - reference: str (unique transaction reference)
                - description: str
                - customer_data: dict (name, document, phone)
                - payment_data: dict (card token or bank code for PSE)

        Returns:
            Dict with transaction result
        """
        try:
            # Convert amount from cents to decimal
            amount = Decimal(transaction_data["amount_in_cents"]) / 100

            reference = transaction_data["reference"]
            description = transaction_data.get("description", f"Order {reference}")

            # Generate signature
            signature = self._generate_signature(reference, str(amount), self.config.currency)

            # Build transaction payload
            payload = {
                "language": self.config.language,
                "command": "SUBMIT_TRANSACTION",
                "merchant": {
                    "apiKey": self.config.api_key,
                    "apiLogin": self.config.api_login
                },
                "transaction": {
                    "order": {
                        "accountId": self.config.account_id,
                        "referenceCode": reference,
                        "description": description,
                        "language": "es",
                        "signature": signature,
                        "notifyUrl": transaction_data.get("notify_url"),
                        "additionalValues": {
                            "TX_VALUE": {
                                "value": float(amount),
                                "currency": self.config.currency
                            }
                        },
                        "buyer": {
                            "merchantBuyerId": str(transaction_data.get("customer_id", "1")),
                            "fullName": transaction_data.get("customer_data", {}).get("full_name", ""),
                            "emailAddress": transaction_data["customer_email"],
                            "contactPhone": transaction_data.get("customer_data", {}).get("phone", ""),
                            "dniNumber": transaction_data.get("customer_data", {}).get("document", ""),
                            "shippingAddress": transaction_data.get("shipping_address", {})
                        }
                    },
                    "payer": {
                        "merchantPayerId": str(transaction_data.get("customer_id", "1")),
                        "fullName": transaction_data.get("customer_data", {}).get("full_name", ""),
                        "emailAddress": transaction_data["customer_email"],
                        "contactPhone": transaction_data.get("customer_data", {}).get("phone", ""),
                        "dniNumber": transaction_data.get("customer_data", {}).get("document", ""),
                        "billingAddress": transaction_data.get("billing_address", {})
                    },
                    "type": "AUTHORIZATION_AND_CAPTURE",
                    "paymentMethod": transaction_data["payment_method"],
                    "paymentCountry": self.config.country_code,
                    "deviceSessionId": transaction_data.get("device_session_id", str(uuid.uuid4())),
                    "ipAddress": transaction_data.get("ip_address", "127.0.0.1"),
                    "cookie": transaction_data.get("cookie", ""),
                    "userAgent": transaction_data.get("user_agent", "")
                },
                "test": not self.config.is_production
            }

            # Add payment-specific data
            payment_method = transaction_data["payment_method"]

            if payment_method in ["VISA", "MASTERCARD", "AMEX", "DINERS"]:
                # Card payment
                payment_data = transaction_data.get("payment_data", {})
                payload["transaction"]["creditCard"] = {
                    "number": payment_data.get("card_number"),
                    "securityCode": payment_data.get("cvv"),
                    "expirationDate": payment_data.get("expiration_date"),  # YYYY/MM
                    "name": payment_data.get("card_holder")
                }

                # Add installments if specified
                if payment_data.get("installments", 1) > 1:
                    payload["transaction"]["extraParameters"] = {
                        "INSTALLMENTS_NUMBER": payment_data.get("installments")
                    }

            elif payment_method == "PSE":
                # PSE bank transfer
                payment_data = transaction_data.get("payment_data", {})
                payload["transaction"]["extraParameters"] = {
                    "FINANCIAL_INSTITUTION_CODE": payment_data.get("bank_code"),
                    "USER_TYPE": payment_data.get("user_type", "N"),  # N=Natural, J=Juridical
                    "PSE_REFERENCE1": payment_data.get("pse_reference1", ""),
                    "PSE_REFERENCE2": payment_data.get("pse_reference2", ""),
                    "PSE_REFERENCE3": payment_data.get("pse_reference3", "")
                }

            # Make request
            payment_logger.info(
                f"Creating PayU transaction",
                extra={"reference": reference, "amount": float(amount), "payment_method": payment_method}
            )

            response = await self.client.post(
                self.config.base_url,
                json=payload
            )

            response.raise_for_status()
            data = response.json()

            # Parse response
            result = self._parse_transaction_response(data)

            payment_logger.info(
                f"PayU transaction created: {result['status']}",
                extra={"transaction_id": result.get("transaction_id"), "reference": reference}
            )

            return result

        except httpx.HTTPError as e:
            raise PayUNetworkError(f"PayU transaction network error: {e}")
        except PayUError:
            raise
        except Exception as e:
            raise PayUError(f"PayU transaction error: {e}")

    def _parse_transaction_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse PayU transaction response.

        PayU response structure:
        {
            "code": "SUCCESS" | "ERROR",
            "error": "...",
            "transactionResponse": {
                "state": "APPROVED" | "DECLINED" | "PENDING" | "ERROR",
                "paymentNetworkResponseCode": "...",
                "paymentNetworkResponseErrorMessage": "...",
                "trazabilityCode": "...",
                "authorizationCode": "...",
                "responseCode": "...",
                "responseMessage": "...",
                "orderId": "...",
                "transactionId": "...",
                "extraParameters": {...}
            }
        }

        Returns:
            Dict with normalized transaction result
        """
        if data.get("code") != "SUCCESS":
            error_message = data.get("error", "Unknown PayU error")
            raise PayUTransactionError(error_message, error_code=data.get("code"), response_data=data)

        tx_response = data.get("transactionResponse", {})
        state = tx_response.get("state", "ERROR")

        # Normalize status
        status_map = {
            "APPROVED": "approved",
            "DECLINED": "declined",
            "PENDING": "pending",
            "ERROR": "error",
            "EXPIRED": "expired"
        }

        return {
            "transaction_id": tx_response.get("transactionId"),
            "order_id": tx_response.get("orderId"),
            "status": status_map.get(state, "error"),
            "state": state,
            "response_code": tx_response.get("responseCode"),
            "response_message": tx_response.get("responseMessage"),
            "authorization_code": tx_response.get("authorizationCode"),
            "trazability_code": tx_response.get("trazabilityCode"),
            "payment_network_code": tx_response.get("paymentNetworkResponseCode"),
            "payment_network_message": tx_response.get("paymentNetworkResponseErrorMessage"),
            "extra_parameters": tx_response.get("extraParameters", {}),
            "pending_reason": tx_response.get("pendingReason"),
            "raw_response": data
        }

    @retry_on_failure()
    async def get_transaction_status(self, transaction_id: str = None, order_id: str = None) -> Dict[str, Any]:
        """
        Query transaction status from PayU.

        Args:
            transaction_id: PayU transaction ID
            order_id: PayU order ID

        Returns:
            Dict with transaction status details
        """
        if not transaction_id and not order_id:
            raise PayUValidationError("Either transaction_id or order_id must be provided")

        try:
            payload = {
                "language": self.config.language,
                "command": "ORDER_DETAIL_BY_REFERENCE_CODE" if not transaction_id else "TRANSACTION_RESPONSE_DETAIL",
                "merchant": {
                    "apiLogin": self.config.api_login,
                    "apiKey": self.config.api_key
                },
                "details": {
                    "transactionId": transaction_id if transaction_id else None,
                    "orderId": order_id if order_id else None
                },
                "test": not self.config.is_production
            }

            response = await self.client.post(
                self.config.base_url,
                json=payload
            )

            response.raise_for_status()
            data = response.json()

            if data.get("code") != "SUCCESS":
                raise PayUError(f"PayU status query failed: {data.get('error')}", error_code=data.get("code"))

            # Parse response - structure varies by query type
            result = data.get("result", {})

            return {
                "transaction_id": result.get("transactionId"),
                "order_id": result.get("orderId"),
                "reference": result.get("referenceCode"),
                "status": result.get("state"),
                "payment_method": result.get("paymentMethod"),
                "amount": result.get("amount"),
                "currency": result.get("currency"),
                "created_at": result.get("createdDate"),
                "updated_at": result.get("lastUpdateDate"),
                "raw_response": data
            }

        except httpx.HTTPError as e:
            raise PayUNetworkError(f"PayU status query network error: {e}")
        except PayUError:
            raise
        except Exception as e:
            raise PayUError(f"PayU status query error: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for PayU service.

        Returns:
            Dict with health status
        """
        health_result = {
            "service": "PayUService",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": self.config.environment,
            "checks": {}
        }

        try:
            # Test connectivity with ping
            start_time = time.time()
            ping_result = await self.ping()
            connectivity_time = time.time() - start_time

            health_result["checks"]["connectivity"] = {
                "status": "healthy" if ping_result["status"] == "success" else "unhealthy",
                "response_time_ms": round(connectivity_time * 1000, 2)
            }

            # Validate configuration
            config_issues = []

            if not self.config.merchant_id:
                config_issues.append("Merchant ID not configured")
            if not self.config.api_key:
                config_issues.append("API Key not configured")
            if not self.config.api_login:
                config_issues.append("API Login not configured")
            if not self.config.account_id:
                config_issues.append("Account ID not configured")

            if config_issues:
                health_result["status"] = "degraded"
                health_result["checks"]["configuration"] = {
                    "status": "unhealthy",
                    "issues": config_issues
                }
            else:
                health_result["checks"]["configuration"] = {
                    "status": "healthy",
                    "merchant_id": self.config.merchant_id,
                    "environment": self.config.environment
                }

            return health_result

        except Exception as e:
            health_result["status"] = "unhealthy"
            health_result["error"] = str(e)
            logger.error(f"PayU health check failed: {e}")
            return health_result

    def amount_to_cents(self, amount: float) -> int:
        """Convert amount to cents"""
        return int(Decimal(str(amount)) * 100)

    def cents_to_amount(self, cents: int) -> float:
        """Convert cents to amount"""
        return float(Decimal(cents) / 100)

    def generate_reference(self, order_id: int) -> str:
        """Generate unique reference for transaction"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"ORDER_{order_id}_{timestamp}"


# Singleton instance
_payu_service = None


def get_payu_service() -> PayUService:
    """Get or create the PayU service singleton"""
    global _payu_service
    if _payu_service is None:
        _payu_service = PayUService()
    return _payu_service
