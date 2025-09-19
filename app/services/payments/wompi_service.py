import httpx
import hashlib
import hmac
import json
import logging
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from decimal import Decimal
import os
from pydantic import BaseModel
from functools import wraps
from contextlib import asynccontextmanager
from dataclasses import dataclass
import uuid

logger = logging.getLogger(__name__)

# Enhanced logging for payment security
payment_logger = logging.getLogger(f"{__name__}.payments")
security_logger = logging.getLogger(f"{__name__}.security")

@dataclass
class RetryConfig:
    """Configuration for retry logic"""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True

class WompiError(Exception):
    """Base exception for Wompi service errors"""
    def __init__(self, message: str, error_code: Optional[str] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.error_code = error_code
        self.response_data = response_data
        super().__init__(message)

class WompiNetworkError(WompiError):
    """Network-related errors"""
    pass

class WompiAuthenticationError(WompiError):
    """Authentication-related errors"""
    pass

class WompiValidationError(WompiError):
    """Validation-related errors"""
    pass

class WompiRateLimitError(WompiError):
    """Rate limiting errors"""
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        self.retry_after = retry_after
        super().__init__(message, **kwargs)

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
                except (httpx.TimeoutException, httpx.NetworkError, WompiNetworkError) as e:
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

                except WompiRateLimitError as e:
                    if e.retry_after and attempt < retry_config.max_attempts - 1:
                        logger.warning(f"Rate limited. Waiting {e.retry_after}s before retry")
                        await asyncio.sleep(e.retry_after)
                        continue
                    raise
                except (WompiAuthenticationError, WompiValidationError) as e:
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

class WompiConfig:
    """Enhanced Wompi configuration with security and performance settings"""

    def __init__(self):
        self.public_key = os.getenv("WOMPI_PUBLIC_KEY")
        self.private_key = os.getenv("WOMPI_PRIVATE_KEY")
        self.environment = os.getenv("WOMPI_ENVIRONMENT", "test")
        self.webhook_secret = os.getenv("WOMPI_WEBHOOK_SECRET")

        # Environment-specific URLs
        if self.environment == "production":
            self.base_url = os.getenv("WOMPI_BASE_URL", "https://production.wompi.co/v1")
        else:
            self.base_url = os.getenv("WOMPI_BASE_URL", "https://sandbox.wompi.co/v1")

        # Security settings
        self.webhook_tolerance = int(os.getenv("WOMPI_WEBHOOK_TOLERANCE", "300"))  # 5 minutes
        self.signature_algorithm = "sha256"

        # Performance settings
        self.timeout = float(os.getenv("WOMPI_TIMEOUT", "30.0"))
        self.max_retries = int(os.getenv("WOMPI_MAX_RETRIES", "3"))
        self.connection_pool_size = int(os.getenv("WOMPI_POOL_SIZE", "10"))

        # Rate limiting
        self.rate_limit_requests = int(os.getenv("WOMPI_RATE_LIMIT", "100"))
        self.rate_limit_window = int(os.getenv("WOMPI_RATE_WINDOW", "60"))

        # Allow missing keys in test environment
        is_test_env = (
            os.getenv("PYTEST_CURRENT_TEST") is not None or
            os.getenv("TESTING") == "1" or
            self.environment == "test"
        )

        if not self.public_key or not self.private_key:
            if is_test_env:
                # Use test defaults for testing
                self.public_key = self.public_key or "pub_test_default"
                self.private_key = self.private_key or "prv_test_default"
                self.webhook_secret = self.webhook_secret or "test_webhook_secret"
            else:
                raise ValueError("WOMPI_PUBLIC_KEY and WOMPI_PRIVATE_KEY must be set")

        # Validate configuration
        self._validate_config()

    def _validate_config(self):
        """Validate configuration parameters"""
        if self.environment not in ["test", "production"]:
            raise ValueError(f"Invalid environment: {self.environment}")

        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")

        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")

        # Validate key formats (basic check)
        if not self.public_key.startswith(("pub_", "pub_test_")):
            logger.warning("Public key format may be invalid")

        if not self.private_key.startswith(("prv_", "prv_test_")):
            logger.warning("Private key format may be invalid")

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

class PaymentSourceCard(BaseModel):
    type: str = "CARD"
    token: str
    installments: int = 1

class PaymentSourcePSE(BaseModel):
    type: str = "PSE"
    user_type: str  # "0" for natural person, "1" for juridical person
    user_legal_id: str
    financial_institution_code: str
    payment_description: str

class PaymentRequest(BaseModel):
    amount_in_cents: int
    currency: str = "COP"
    customer_email: str
    payment_method: Dict[str, Any]
    redirect_url: str
    reference: str
    payment_source_id: Optional[int] = None

class WompiService:
    """Enhanced Wompi service with security, monitoring, and resilience features"""

    def __init__(self):
        self.config = WompiConfig()
        self._request_count = 0
        self._rate_limit_window_start = time.time()
        self._circuit_breaker_failures = 0
        self._circuit_breaker_last_failure = 0
        self._circuit_breaker_threshold = 5
        self._circuit_breaker_timeout = 60  # seconds

        # Create HTTP client with enhanced configuration
        limits = httpx.Limits(
            max_keepalive_connections=self.config.connection_pool_size,
            max_connections=self.config.connection_pool_size * 2,
            keepalive_expiry=30.0
        )

        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Bearer {self.config.private_key}",
                "Content-Type": "application/json",
                "User-Agent": f"MeStore-Wompi-Client/1.0",
                "X-Request-ID": str(uuid.uuid4())
            },
            timeout=httpx.Timeout(self.config.timeout),
            limits=limits,
            verify=True  # Always verify SSL certificates
        )
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _generate_signature(self, data: str) -> str:
        """Generate HMAC signature for webhook validation"""
        if not self.config.webhook_secret:
            raise WompiAuthenticationError("Webhook secret not configured")

        try:
            return hmac.new(
                self.config.webhook_secret.encode('utf-8'),
                data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
        except Exception as e:
            security_logger.error(f"Failed to generate webhook signature: {e}")
            raise WompiError(f"Signature generation failed: {e}")

    def _check_rate_limit(self) -> None:
        """Check if request is within rate limits"""
        current_time = time.time()

        # Reset window if needed
        if current_time - self._rate_limit_window_start >= self.config.rate_limit_window:
            self._request_count = 0
            self._rate_limit_window_start = current_time

        if self._request_count >= self.config.rate_limit_requests:
            raise WompiRateLimitError(
                f"Rate limit exceeded: {self.config.rate_limit_requests} requests per {self.config.rate_limit_window}s",
                retry_after=int(self.config.rate_limit_window - (current_time - self._rate_limit_window_start))
            )

        self._request_count += 1

    def _check_circuit_breaker(self) -> None:
        """Check circuit breaker status"""
        current_time = time.time()

        # Reset circuit breaker if timeout has passed
        if (current_time - self._circuit_breaker_last_failure) > self._circuit_breaker_timeout:
            self._circuit_breaker_failures = 0

        if self._circuit_breaker_failures >= self._circuit_breaker_threshold:
            raise WompiNetworkError(
                f"Circuit breaker open: {self._circuit_breaker_failures} consecutive failures. "
                f"Will retry after {self._circuit_breaker_timeout}s"
            )

    def _record_failure(self) -> None:
        """Record a failure for circuit breaker"""
        self._circuit_breaker_failures += 1
        self._circuit_breaker_last_failure = time.time()

    def _record_success(self) -> None:
        """Record a success - reset circuit breaker"""
        self._circuit_breaker_failures = 0

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """Make HTTP request with monitoring and error handling"""
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Security and rate limiting checks
        self._check_rate_limit()
        self._check_circuit_breaker()

        # Prepare headers
        request_headers = self.client.headers.copy()
        if headers:
            request_headers.update(headers)
        request_headers["X-Request-ID"] = request_id

        payment_logger.info(
            f"Making {method} request to {endpoint}",
            extra={"request_id": request_id, "endpoint": endpoint}
        )

        try:
            response = await self.client.request(
                method=method,
                url=endpoint,
                headers=request_headers,
                **kwargs
            )

            # Log response metrics
            duration = time.time() - start_time
            payment_logger.info(
                f"Request completed: {response.status_code} in {duration:.3f}s",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "duration": duration
                }
            )

            # Handle different response codes
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                raise WompiRateLimitError(
                    "API rate limit exceeded",
                    retry_after=retry_after,
                    response_data=self._safe_json_decode(response)
                )
            elif response.status_code == 401:
                security_logger.error("Authentication failed", extra={"request_id": request_id})
                raise WompiAuthenticationError(
                    "Authentication failed - check API keys",
                    response_data=self._safe_json_decode(response)
                )
            elif response.status_code == 400:
                response_data = self._safe_json_decode(response)
                raise WompiValidationError(
                    f"Validation error: {response_data.get('error', {}).get('message', 'Unknown validation error')}",
                    response_data=response_data
                )
            elif response.status_code >= 500:
                self._record_failure()
                raise WompiNetworkError(
                    f"Server error: {response.status_code}",
                    response_data=self._safe_json_decode(response)
                )

            response.raise_for_status()
            self._record_success()
            return response

        except httpx.TimeoutException as e:
            self._record_failure()
            payment_logger.error(f"Request timeout: {e}", extra={"request_id": request_id})
            raise WompiNetworkError(f"Request timeout: {e}")
        except httpx.NetworkError as e:
            self._record_failure()
            payment_logger.error(f"Network error: {e}", extra={"request_id": request_id})
            raise WompiNetworkError(f"Network error: {e}")
        except (WompiError, httpx.HTTPStatusError) as e:
            # Re-raise Wompi errors and HTTP status errors
            raise
        except Exception as e:
            self._record_failure()
            payment_logger.error(f"Unexpected error: {e}", extra={"request_id": request_id})
            raise WompiError(f"Unexpected error: {e}")

    def _safe_json_decode(self, response: httpx.Response) -> Dict[str, Any]:
        """Safely decode JSON response"""
        try:
            return response.json()
        except (json.JSONDecodeError, ValueError):
            return {"raw_response": response.text}

    @retry_on_failure()
    async def get_acceptance_token(self) -> Dict[str, Any]:
        """Get merchant acceptance token required for payments"""
        try:
            response = await self._make_request(
                "GET",
                f"/merchants/{self.config.public_key}"
            )
            data = response.json()

            acceptance_data = data.get("data", {}).get("presigned_acceptance", {})
            if not acceptance_data.get("acceptance_token"):
                raise WompiValidationError("No acceptance token in response", response_data=data)

            payment_logger.info("Acceptance token retrieved successfully")
            return {
                "acceptance_token": acceptance_data.get("acceptance_token"),
                "permalink": acceptance_data.get("permalink")
            }
        except WompiError:
            raise
        except Exception as e:
            logger.error(f"Error getting acceptance token: {e}")
            raise WompiError(f"Failed to get acceptance token: {e}")

    @retry_on_failure()
    async def tokenize_card(self, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tokenize a credit/debit card with enhanced security"""
        # Validate required fields
        required_fields = ["number", "exp_month", "exp_year", "cvc", "card_holder"]
        missing_fields = [field for field in required_fields if not card_data.get(field)]
        if missing_fields:
            raise WompiValidationError(f"Missing required fields: {missing_fields}")

        # Sanitize and validate card data
        try:
            card_number = str(card_data["number"]).replace(" ", "").replace("-", "")
            if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
                raise WompiValidationError("Invalid card number format")

            exp_month = str(card_data["exp_month"]).zfill(2)
            exp_year = str(card_data["exp_year"])
            if len(exp_year) == 2:
                exp_year = "20" + exp_year

            if not (1 <= int(exp_month) <= 12):
                raise WompiValidationError("Invalid expiration month")

            if int(exp_year) < datetime.now().year:
                raise WompiValidationError("Card has expired")

            cvc = str(card_data["cvc"])
            if not cvc.isdigit() or len(cvc) < 3 or len(cvc) > 4:
                raise WompiValidationError("Invalid CVC format")

        except ValueError as e:
            raise WompiValidationError(f"Invalid card data: {e}")

        payload = {
            "number": card_number,
            "exp_month": exp_month,
            "exp_year": exp_year,
            "cvc": cvc,
            "card_holder": str(card_data["card_holder"]).strip()
        }

        # Use public key for tokenization
        headers = {
            "Authorization": f"Bearer {self.config.public_key}",
            "Content-Type": "application/json"
        }

        try:
            # Log tokenization attempt (without sensitive data)
            security_logger.info(
                "Card tokenization attempt",
                extra={
                    "card_last_4": card_number[-4:] if len(card_number) >= 4 else "****",
                    "exp_month": exp_month,
                    "exp_year": exp_year
                }
            )

            response = await self._make_request(
                "POST",
                "/tokens/cards",
                headers=headers,
                json=payload
            )

            data = response.json()

            # Validate response
            if not data.get("data", {}).get("id"):
                raise WompiValidationError("No token in tokenization response", response_data=data)

            security_logger.info(
                "Card tokenization successful",
                extra={"token_id": data["data"]["id"]}
            )

            return data

        except WompiError:
            raise
        except Exception as e:
            security_logger.error(f"Card tokenization failed: {e}")
            raise WompiError(f"Card tokenization failed: {e}")

    async def create_payment_source(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a payment source (card or PSE)"""
        try:
            acceptance_token = await self.get_acceptance_token()
            
            payload = {
                "type": payment_data["type"],
                "acceptance_token": acceptance_token["acceptance_token"],
                "customer_email": payment_data["customer_email"]
            }
            
            if payment_data["type"] == "CARD":
                payload.update({
                    "token": payment_data["token"],
                    "customer_data": {
                        "phone_number": payment_data.get("phone_number", ""),
                        "full_name": payment_data.get("full_name", "")
                    }
                })
            elif payment_data["type"] == "PSE":
                payload.update({
                    "user_type": payment_data["user_type"],
                    "user_legal_id": payment_data["user_legal_id"],
                    "financial_institution_code": payment_data["financial_institution_code"],
                    "payment_description": payment_data["payment_description"]
                })
            
            response = await self.client.post("/payment_sources", json=payload)
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Error creating payment source: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise Exception("Failed to create payment source")

    async def create_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a payment transaction"""
        try:
            payload = {
                "amount_in_cents": transaction_data["amount_in_cents"],
                "currency": transaction_data.get("currency", "COP"),
                "customer_email": transaction_data["customer_email"],
                "payment_method": transaction_data["payment_method"],
                "reference": transaction_data["reference"],
                "redirect_url": transaction_data["redirect_url"]
            }
            
            if "payment_source_id" in transaction_data:
                payload["payment_source_id"] = transaction_data["payment_source_id"]
                
            response = await self.client.post("/transactions", json=payload)
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Error creating transaction: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise Exception("Failed to create transaction")

    async def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction details"""
        try:
            response = await self.client.get(f"/transactions/{transaction_id}")
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Error getting transaction {transaction_id}: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise Exception("Failed to get transaction")

    async def get_pse_banks(self) -> List[Dict[str, Any]]:
        """Get available PSE banks"""
        try:
            response = await self.client.get("/pse/financial_institutions")
            response.raise_for_status()
            
            data = response.json()
            return data.get("data", [])
            
        except httpx.HTTPError as e:
            logger.error(f"Error getting PSE banks: {e}")
            return []

    def validate_webhook_signature(self, payload: str, signature: str, timestamp: Optional[int] = None) -> bool:
        """Validate webhook signature with enhanced security"""
        if not payload or not signature:
            security_logger.warning("Empty payload or signature in webhook validation")
            return False

        if not self.config.webhook_secret:
            security_logger.error("Webhook secret not configured")
            return False

        try:
            # Validate timestamp if provided (replay attack protection)
            if timestamp and self.config.webhook_tolerance > 0:
                current_time = int(time.time())
                if abs(current_time - timestamp) > self.config.webhook_tolerance:
                    security_logger.warning(
                        f"Webhook timestamp outside tolerance: {abs(current_time - timestamp)}s",
                        extra={"timestamp": timestamp, "current_time": current_time}
                    )
                    return False

            expected_signature = self._generate_signature(payload)

            # Support multiple signature formats
            signature_formats = [
                signature,  # Direct signature
                signature.replace("sha256=", ""),  # Remove prefix if present
                f"sha256={signature}" if not signature.startswith("sha256=") else signature  # Add prefix if missing
            ]

            for sig_format in signature_formats:
                if hmac.compare_digest(expected_signature, sig_format.replace("sha256=", "")):
                    security_logger.info("Webhook signature validation successful")
                    return True

            security_logger.warning(
                "Webhook signature validation failed",
                extra={"expected_length": len(expected_signature), "received_length": len(signature)}
            )
            return False

        except Exception as e:
            security_logger.error(f"Error validating webhook signature: {e}")
            return False

    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook event from Wompi"""
        try:
            event = payload.get("event")
            data = payload.get("data", {})
            
            if event == "transaction.updated":
                transaction_id = data.get("id")
                if transaction_id:
                    # Get full transaction details
                    transaction = await self.get_transaction(transaction_id)
                    return {
                        "event": event,
                        "transaction": transaction,
                        "processed": True
                    }
            
            return {
                "event": event,
                "data": data,
                "processed": False
            }
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            raise Exception("Webhook processing failed")

    async def void_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Void/cancel a transaction"""
        try:
            response = await self.client.post(f"/transactions/{transaction_id}/void")
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Error voiding transaction {transaction_id}: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise Exception("Failed to void transaction")

    def amount_to_cents(self, amount: float) -> int:
        """Convert amount to cents for Wompi"""
        return int(Decimal(str(amount)) * 100)

    def cents_to_amount(self, cents: int) -> float:
        """Convert cents to amount"""
        return float(Decimal(cents) / 100)

    def generate_reference(self, order_id: int) -> str:
        """Generate unique reference for transaction"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"ORDER_{order_id}_{timestamp}"

    @retry_on_failure()
    async def get_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get real-time transaction status from Wompi API.

        Args:
            transaction_id: Wompi transaction ID

        Returns:
            Dict containing transaction status details

        Raises:
            WompiValidationError: If transaction_id is invalid
            WompiNetworkError: If network/API error occurs
            WompiError: For other Wompi-related errors
        """
        if not transaction_id or not isinstance(transaction_id, str):
            raise WompiValidationError("Transaction ID must be a non-empty string")

        try:
            payment_logger.info(
                f"Fetching transaction status for ID: {transaction_id}",
                extra={"transaction_id": transaction_id}
            )

            response = await self._make_request(
                "GET",
                f"/transactions/{transaction_id}"
            )

            data = response.json()

            # Validate response structure
            if not data.get("data"):
                raise WompiValidationError(
                    f"Invalid response structure for transaction {transaction_id}",
                    response_data=data
                )

            transaction_data = data["data"]

            # Extract key status information
            status_info = {
                "transaction_id": transaction_id,
                "status": transaction_data.get("status"),
                "status_message": transaction_data.get("status_message"),
                "amount_in_cents": transaction_data.get("amount_in_cents"),
                "currency": transaction_data.get("currency"),
                "reference": transaction_data.get("reference"),
                "payment_method": transaction_data.get("payment_method", {}),
                "created_at": transaction_data.get("created_at"),
                "finalized_at": transaction_data.get("finalized_at"),
                "shipping_address": transaction_data.get("shipping_address"),
                "redirect_url": transaction_data.get("redirect_url"),
                "payment_source_id": transaction_data.get("payment_source_id"),
                "payment_link_id": transaction_data.get("payment_link_id"),
                "customer_email": transaction_data.get("customer_email"),
                "customer_data": transaction_data.get("customer_data", {}),
                "billing_data": transaction_data.get("billing_data", {}),
                "taxes": transaction_data.get("taxes", [])
            }

            payment_logger.info(
                f"Transaction status retrieved: {status_info['status']}",
                extra={
                    "transaction_id": transaction_id,
                    "status": status_info["status"],
                    "amount_cents": status_info["amount_in_cents"]
                }
            )

            return status_info

        except WompiError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting transaction status: {e}")
            raise WompiError(f"Failed to get transaction status: {e}")

    @retry_on_failure()
    async def get_payment_methods(self) -> List[Dict[str, Any]]:
        """
        Get available payment methods from Wompi API.

        Returns:
            List of available payment methods with details

        Raises:
            WompiNetworkError: If network/API error occurs
            WompiError: For other Wompi-related errors
        """
        try:
            payment_logger.info("Fetching available payment methods")

            # Get merchant info which contains payment methods
            response = await self._make_request(
                "GET",
                f"/merchants/{self.config.public_key}"
            )

            data = response.json()
            merchant_data = data.get("data", {})

            if not merchant_data:
                raise WompiValidationError("No merchant data in response", response_data=data)

            # Extract payment methods information
            payment_methods = []

            # Add card payment methods if available
            if merchant_data.get("payment_methods", {}).get("card"):
                card_processors = merchant_data["payment_methods"]["card"]
                for processor in card_processors:
                    payment_methods.append({
                        "type": "CARD",
                        "name": "Credit/Debit Card",
                        "processor": processor,
                        "description": f"Pay with credit or debit card via {processor}",
                        "supported_currencies": ["COP"],
                        "installments_available": True,
                        "max_installments": 36  # Standard for Colombia
                    })

            # Add PSE if available
            if merchant_data.get("payment_methods", {}).get("pse"):
                # Get PSE banks
                try:
                    pse_banks = await self.get_pse_banks()
                    payment_methods.append({
                        "type": "PSE",
                        "name": "PSE (Pagos Seguros en Línea)",
                        "description": "Bank transfer via PSE",
                        "supported_currencies": ["COP"],
                        "available_banks": pse_banks,
                        "requires_user_type": True,
                        "requires_legal_id": True
                    })
                except Exception as e:
                    logger.warning(f"Failed to get PSE banks: {e}")
                    payment_methods.append({
                        "type": "PSE",
                        "name": "PSE (Pagos Seguros en Línea)",
                        "description": "Bank transfer via PSE",
                        "supported_currencies": ["COP"],
                        "available_banks": [],
                        "requires_user_type": True,
                        "requires_legal_id": True
                    })

            # Add additional payment methods if configured
            other_methods = merchant_data.get("payment_methods", {})
            for method_type, method_config in other_methods.items():
                if method_type not in ["card", "pse"] and method_config:
                    payment_methods.append({
                        "type": method_type.upper(),
                        "name": method_type.replace("_", " ").title(),
                        "description": f"Pay with {method_type}",
                        "supported_currencies": ["COP"],
                        "configuration": method_config
                    })

            # If no specific payment methods found, add defaults
            if not payment_methods:
                payment_methods = [
                    {
                        "type": "CARD",
                        "name": "Credit/Debit Card",
                        "description": "Pay with credit or debit card",
                        "supported_currencies": ["COP"],
                        "installments_available": True
                    }
                ]

            payment_logger.info(
                f"Retrieved {len(payment_methods)} payment methods",
                extra={"method_types": [pm["type"] for pm in payment_methods]}
            )

            return payment_methods

        except WompiError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting payment methods: {e}")
            raise WompiError(f"Failed to get payment methods: {e}")

    @retry_on_failure()
    async def health_check(self) -> Dict[str, Any]:
        """
        Validate connectivity and configuration with Wompi API.

        Returns:
            Dict containing health check results

        Raises:
            WompiAuthenticationError: If authentication fails
            WompiNetworkError: If network connectivity fails
            WompiError: For other health check failures
        """
        health_result = {
            "service": "WompiService",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": self.config.environment,
            "checks": {}
        }

        try:
            # Check 1: API Connectivity and Authentication
            try:
                start_time = time.time()
                response = await self._make_request(
                    "GET",
                    f"/merchants/{self.config.public_key}"
                )
                connectivity_time = time.time() - start_time

                merchant_data = response.json().get("data", {})

                health_result["checks"]["connectivity"] = {
                    "status": "healthy",
                    "response_time_ms": round(connectivity_time * 1000, 2),
                    "api_version": response.headers.get("X-API-Version", "unknown")
                }

                health_result["checks"]["authentication"] = {
                    "status": "healthy",
                    "merchant_id": merchant_data.get("id"),
                    "merchant_name": merchant_data.get("name")
                }

            except WompiAuthenticationError as e:
                health_result["status"] = "unhealthy"
                health_result["checks"]["authentication"] = {
                    "status": "unhealthy",
                    "error": "Authentication failed - check API keys",
                    "details": str(e)
                }
                raise

            except (WompiNetworkError, httpx.TimeoutException, httpx.NetworkError) as e:
                health_result["status"] = "unhealthy"
                health_result["checks"]["connectivity"] = {
                    "status": "unhealthy",
                    "error": "Network connectivity failed",
                    "details": str(e)
                }
                raise

            # Check 2: Configuration Validation
            config_issues = []

            if not self.config.public_key or not self.config.public_key.startswith(("pub_", "pub_test_")):
                config_issues.append("Invalid public key format")

            if not self.config.private_key or not self.config.private_key.startswith(("prv_", "prv_test_")):
                config_issues.append("Invalid private key format")

            if self.config.environment not in ["test", "production"]:
                config_issues.append(f"Invalid environment: {self.config.environment}")

            if config_issues:
                health_result["status"] = "degraded"
                health_result["checks"]["configuration"] = {
                    "status": "unhealthy",
                    "issues": config_issues
                }
            else:
                health_result["checks"]["configuration"] = {
                    "status": "healthy",
                    "environment": self.config.environment,
                    "base_url": self.config.base_url
                }

            # Check 3: Payment Methods Availability
            try:
                payment_methods = await self.get_payment_methods()
                health_result["checks"]["payment_methods"] = {
                    "status": "healthy",
                    "available_methods": len(payment_methods),
                    "method_types": [pm["type"] for pm in payment_methods]
                }
            except Exception as e:
                health_result["status"] = "degraded"
                health_result["checks"]["payment_methods"] = {
                    "status": "unhealthy",
                    "error": "Failed to retrieve payment methods",
                    "details": str(e)
                }

            # Check 4: Rate Limiting Status
            health_result["checks"]["rate_limiting"] = {
                "status": "healthy",
                "current_requests": self._request_count,
                "window_remaining": max(0, self.config.rate_limit_window - (time.time() - self._rate_limit_window_start)),
                "limit": self.config.rate_limit_requests
            }

            # Check 5: Circuit Breaker Status
            if self._circuit_breaker_failures >= self._circuit_breaker_threshold:
                health_result["status"] = "unhealthy"
                health_result["checks"]["circuit_breaker"] = {
                    "status": "open",
                    "failure_count": self._circuit_breaker_failures,
                    "last_failure": self._circuit_breaker_last_failure
                }
            else:
                health_result["checks"]["circuit_breaker"] = {
                    "status": "closed",
                    "failure_count": self._circuit_breaker_failures
                }

            # Overall health summary
            unhealthy_checks = [
                check for check in health_result["checks"].values()
                if check.get("status") == "unhealthy"
            ]

            if unhealthy_checks:
                health_result["status"] = "unhealthy"
            elif any(check.get("status") == "degraded" for check in health_result["checks"].values()):
                health_result["status"] = "degraded"

            payment_logger.info(
                f"Health check completed: {health_result['status']}",
                extra={
                    "status": health_result["status"],
                    "checks_count": len(health_result["checks"]),
                    "environment": self.config.environment
                }
            )

            return health_result

        except WompiError:
            raise
        except Exception as e:
            health_result["status"] = "unhealthy"
            health_result["error"] = str(e)
            logger.error(f"Health check failed with unexpected error: {e}")
            raise WompiError(f"Health check failed: {e}")

# Singleton instance - lazy loading
_wompi_service = None

def get_wompi_service() -> WompiService:
    """Get or create the Wompi service singleton"""
    global _wompi_service
    if _wompi_service is None:
        _wompi_service = WompiService()
    return _wompi_service

# For backwards compatibility
wompi_service = None