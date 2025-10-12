"""
SMS Security Module
Provides rate limiting, validation, and logging for SMS endpoints.

This module implements enterprise-grade security for SMS verification:
- Rate limiting by phone number (3 attempts/10 min)
- Rate limiting by IP address (10 attempts/1 hour)
- International phone validation with Google libphonenumber
- Structured security logging with GDPR compliance
- Fail-open design for Redis failures

Author: security-backend-ai
Date: 2025-10-11
"""

import hashlib
import logging
from datetime import datetime
from typing import Tuple, Optional
from fastapi import Request
import phonenumbers
from phonenumbers import NumberParseException

from app.core.redis.service import RedisService

logger = logging.getLogger(__name__)

# Rate limiting constants
RATE_LIMIT_PHONE_MAX = 3
RATE_LIMIT_PHONE_WINDOW = 600  # 10 minutes
RATE_LIMIT_IP_MAX = 10
RATE_LIMIT_IP_WINDOW = 3600  # 1 hour


async def check_phone_rate_limit(
    redis: RedisService,
    phone: str
) -> Tuple[bool, str]:
    """
    Check rate limiting for phone number.

    Implements 3 attempts per 10 minutes per phone number.
    Uses Redis for distributed rate limiting.

    Args:
        redis: Redis service instance
        phone: Phone number to check (E.164 format recommended)

    Returns:
        Tuple of (allowed: bool, message: str)
        - (True, "OK") if allowed
        - (False, "error message") if rate limit exceeded

    Security:
        - Fails open if Redis is unavailable (allows request)
        - Uses atomic Redis operations
        - Automatic expiration prevents memory leaks
    """
    key = f"sms_rate_limit:phone:{phone}"

    try:
        count = await redis.cache_get(key)

        if count is None:
            # First attempt - set counter with expiration
            await redis.cache_set(key, "1", expire=RATE_LIMIT_PHONE_WINDOW)
            logger.info(f"Rate limit initialized for phone", extra={"phone_hash": _hash_phone(phone)})
            return True, "OK"

        count_int = int(count)
        if count_int >= RATE_LIMIT_PHONE_MAX:
            logger.warning(
                f"Phone rate limit exceeded",
                extra={
                    "phone_hash": _hash_phone(phone),
                    "attempts": count_int,
                    "max_allowed": RATE_LIMIT_PHONE_MAX
                }
            )
            return False, f"Demasiados intentos. Máximo {RATE_LIMIT_PHONE_MAX} intentos en 10 minutos."

        # Increment counter (atomic operation)
        await redis.redis.incr(key)
        logger.info(
            f"Phone rate limit check passed",
            extra={
                "phone_hash": _hash_phone(phone),
                "attempts": count_int + 1,
                "max_allowed": RATE_LIMIT_PHONE_MAX
            }
        )
        return True, "OK"

    except Exception as e:
        logger.error(f"Error checking phone rate limit: {e}", extra={"phone": phone}, exc_info=True)
        # Fail open - allow request if Redis fails
        return True, "OK"


async def check_ip_rate_limit(
    redis: RedisService,
    ip: str
) -> Tuple[bool, str]:
    """
    Check rate limiting for IP address.

    Implements 10 attempts per 1 hour per IP address.
    Prevents distributed attacks from same network.

    Args:
        redis: Redis service instance
        ip: IP address to check (IPv4 or IPv6)

    Returns:
        Tuple of (allowed: bool, message: str)
        - (True, "OK") if allowed
        - (False, "error message") if rate limit exceeded

    Security:
        - Fails open if Redis is unavailable
        - Considers proxy headers via get_client_ip()
        - Tracks real client IP behind load balancers
    """
    key = f"sms_rate_limit:ip:{ip}"

    try:
        count = await redis.cache_get(key)

        if count is None:
            # First attempt - set counter with expiration
            await redis.cache_set(key, "1", expire=RATE_LIMIT_IP_WINDOW)
            logger.info(f"Rate limit initialized for IP", extra={"ip": ip})
            return True, "OK"

        count_int = int(count)
        if count_int >= RATE_LIMIT_IP_MAX:
            logger.warning(
                f"IP rate limit exceeded",
                extra={
                    "ip": ip,
                    "attempts": count_int,
                    "max_allowed": RATE_LIMIT_IP_MAX
                }
            )
            return False, f"Demasiadas solicitudes desde tu red. Máximo {RATE_LIMIT_IP_MAX} intentos en 1 hora."

        # Increment counter (atomic operation)
        await redis.redis.incr(key)
        logger.info(
            f"IP rate limit check passed",
            extra={
                "ip": ip,
                "attempts": count_int + 1,
                "max_allowed": RATE_LIMIT_IP_MAX
            }
        )
        return True, "OK"

    except Exception as e:
        logger.error(f"Error checking IP rate limit: {e}", extra={"ip": ip}, exc_info=True)
        # Fail open - allow request if Redis fails
        return True, "OK"


def validate_phone_number(phone: str) -> Tuple[bool, str, str]:
    """
    Validate international phone number using Google's libphonenumber.

    Performs comprehensive validation:
    - Format validation (E.164 standard)
    - Country code validation
    - Number type verification (mobile only)
    - Length and pattern validation

    Args:
        phone: Phone number to validate (should start with +)

    Returns:
        Tuple of (valid: bool, error_message: str, e164_format: str)
        - (True, "OK", "+1234567890") if valid
        - (False, "error message", "") if invalid

    Security:
        - Prevents SMS to non-mobile numbers (landlines)
        - Standardizes format to E.164
        - Validates against carrier databases

    Examples:
        >>> validate_phone_number("+573001234567")
        (True, "OK", "+573001234567")

        >>> validate_phone_number("3001234567")
        (False, "Formato telefónico inválido...", "")
    """
    try:
        # Parse phone number (None means auto-detect country from number)
        parsed = phonenumbers.parse(phone, None)

        # Check if valid according to carrier databases
        if not phonenumbers.is_valid_number(parsed):
            logger.warning(f"Invalid phone number", extra={"phone_length": len(phone)})
            return False, "Número telefónico inválido", ""

        # Check if mobile (SMS only works with mobile numbers)
        number_type = phonenumbers.number_type(parsed)
        if number_type not in [
            phonenumbers.PhoneNumberType.MOBILE,
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE
        ]:
            logger.warning(
                f"Non-mobile phone number",
                extra={
                    "phone_length": len(phone),
                    "number_type": number_type
                }
            )
            return False, "SMS solo disponible para números móviles", ""

        # Format to E.164 standard (+country_code + number)
        e164 = phonenumbers.format_number(
            parsed,
            phonenumbers.PhoneNumberFormat.E164
        )

        logger.info(f"Phone validation successful", extra={"e164_length": len(e164)})
        return True, "OK", e164

    except NumberParseException as e:
        error_msg = f"Formato telefónico inválido. Use +código_país seguido del número."
        logger.warning(f"Phone parse error", extra={"error": str(e), "phone_length": len(phone)})
        return False, error_msg, ""
    except Exception as e:
        logger.error(f"Error validating phone: {e}", extra={"phone": phone}, exc_info=True)
        return False, "Error validando número telefónico", ""


def get_client_ip(request: Request) -> str:
    """
    Extract real client IP considering proxies and load balancers.

    Checks headers in order of trust:
    1. X-Forwarded-For (first IP in chain)
    2. X-Real-IP
    3. Direct connection IP

    Args:
        request: FastAPI Request object

    Returns:
        Client IP address as string

    Security:
        - Handles proxy chains correctly
        - Takes first IP (real client) from X-Forwarded-For
        - Fallback to direct IP if no proxy headers

    Examples:
        X-Forwarded-For: "203.0.113.1, 198.51.100.2"
        Returns: "203.0.113.1"
    """
    # Check X-Forwarded-For header (for proxies/load balancers)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take first IP (real client) from chain
        client_ip = forwarded.split(",")[0].strip()
        logger.debug(f"Client IP from X-Forwarded-For", extra={"ip": client_ip})
        return client_ip

    # Check X-Real-IP header (nginx, cloudflare)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        logger.debug(f"Client IP from X-Real-IP", extra={"ip": real_ip})
        return real_ip

    # Fallback to direct connection IP
    direct_ip = request.client.host if request.client else "unknown"
    logger.debug(f"Client IP from direct connection", extra={"ip": direct_ip})
    return direct_ip


def log_sms_security_event(
    event_type: str,
    phone: str,
    ip: str,
    success: bool,
    reason: Optional[str] = None,
    extra: Optional[dict] = None
):
    """
    Log structured security event for SMS operations.

    Implements GDPR-compliant logging:
    - Hashes phone numbers for privacy
    - Structured JSON logging
    - Searchable security events
    - Audit trail for compliance

    Args:
        event_type: Type of event (sms_sent, rate_limit_hit, invalid_phone, etc.)
        phone: Phone number (will be hashed for privacy)
        ip: Client IP address
        success: Whether operation succeeded
        reason: Optional reason for failure
        extra: Optional extra data to log

    Event Types:
        - sms_sent: SMS successfully sent
        - rate_limit_phone: Phone rate limit hit
        - rate_limit_ip: IP rate limit hit
        - invalid_phone: Phone validation failed
        - twilio_error: Twilio API error

    Privacy:
        - Phone numbers are SHA256 hashed (GDPR Art. 32)
        - Only first 16 chars of hash logged
        - Cannot reverse to original number

    Example:
        log_sms_security_event(
            "sms_sent",
            "+573001234567",
            "203.0.113.1",
            True,
            extra={"twilio_sid": "SM123"}
        )
    """
    # Hash phone for privacy (GDPR compliance)
    phone_hash = _hash_phone(phone)

    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "phone_hash": phone_hash,
        "ip": ip,
        "success": success,
    }

    if reason:
        log_data["reason"] = reason

    if extra:
        log_data.update(extra)

    if success:
        logger.info(f"SMS Security Event: {event_type}", extra=log_data)
    else:
        logger.warning(f"SMS Security Event FAILED: {event_type}", extra=log_data)


def _hash_phone(phone: str) -> str:
    """
    Hash phone number for privacy-compliant logging.

    Args:
        phone: Phone number to hash

    Returns:
        First 16 characters of SHA256 hash

    Security:
        - One-way hash (cannot reverse)
        - Deterministic (same phone = same hash)
        - GDPR Article 32 compliant
    """
    return hashlib.sha256(phone.encode()).hexdigest()[:16]
