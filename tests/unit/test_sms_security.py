"""
Unit tests for SMS Security module - CRITICAL tests
Coverage target: 85-90%

This test suite focuses on critical security functions:
- Rate limiting (phone and IP)
- Phone number validation
- IP extraction from requests
- GDPR-compliant logging

Author: unit-testing-ai
Date: 2025-10-11
"""
import pytest
from unittest.mock import AsyncMock, Mock
from app.core.sms_security import (
    check_phone_rate_limit,
    check_ip_rate_limit,
    validate_phone_number,
    get_client_ip,
    log_sms_security_event
)


# ============================================================================
# CRITICAL TESTS: check_phone_rate_limit()
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.sms_security
async def test_check_phone_rate_limit_first_attempt(mock_redis_service):
    """First SMS attempt should be ALLOWED"""
    phone = "+573001234567"

    allowed, message = await check_phone_rate_limit(mock_redis_service, phone)

    assert allowed is True
    assert message == "OK"
    assert mock_redis_service._storage[f"sms_rate_limit:phone:{phone}"] == "1"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.sms_security
async def test_check_phone_rate_limit_third_attempt(mock_redis_service):
    """Third SMS attempt should be ALLOWED (limit is 3)"""
    phone = "+573001234567"
    key = f"sms_rate_limit:phone:{phone}"

    # Simulate 2 previous attempts
    mock_redis_service._storage[key] = "2"

    allowed, message = await check_phone_rate_limit(mock_redis_service, phone)

    assert allowed is True
    assert message == "OK"
    assert mock_redis_service._storage[key] == "3"  # Incremented


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.sms_security
async def test_check_phone_rate_limit_fourth_attempt_blocked(mock_redis_service):
    """
    Fourth SMS attempt should be BLOCKED (rate limit exceeded)

    ✅ BUG FIXED by security-backend-ai on 2025-10-12:
    Corrected logger.warning syntax to use extra={"key": value}
    Rate limiting now works correctly and blocks 4th attempt.
    """
    phone = "+573001234567"
    key = f"sms_rate_limit:phone:{phone}"

    # Simulate 3 previous attempts (limit reached)
    mock_redis_service._storage[key] = "3"

    allowed, message = await check_phone_rate_limit(mock_redis_service, phone)

    # ✅ CORRECTED: Rate limiting now works properly
    assert allowed is False
    assert "Demasiados intentos" in message
    assert "3 intentos" in message


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.sms_security
async def test_check_phone_rate_limit_redis_failure_fail_open(mock_redis_service):
    """CRITICAL: If Redis fails, should FAIL-OPEN (allow request)"""
    phone = "+573001234567"

    # Simulate Redis failure
    mock_redis_service.cache_get.side_effect = Exception("Redis connection lost")

    allowed, message = await check_phone_rate_limit(mock_redis_service, phone)

    assert allowed is True  # ⭐ FAIL-OPEN: Don't block users if Redis down
    assert message == "OK"


# ============================================================================
# CRITICAL TESTS: check_ip_rate_limit()
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.sms_security
async def test_check_ip_rate_limit_first_attempt(mock_redis_service):
    """First IP attempt should be ALLOWED"""
    ip = "203.0.113.1"

    allowed, message = await check_ip_rate_limit(mock_redis_service, ip)

    assert allowed is True
    assert message == "OK"
    assert mock_redis_service._storage[f"sms_rate_limit:ip:{ip}"] == "1"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.sms_security
async def test_check_ip_rate_limit_tenth_attempt(mock_redis_service):
    """Tenth IP attempt should be ALLOWED (limit is 10)"""
    ip = "203.0.113.1"
    key = f"sms_rate_limit:ip:{ip}"

    # Simulate 9 previous attempts
    mock_redis_service._storage[key] = "9"

    allowed, message = await check_ip_rate_limit(mock_redis_service, ip)

    assert allowed is True
    assert message == "OK"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.sms_security
async def test_check_ip_rate_limit_eleventh_attempt_blocked(mock_redis_service):
    """
    Eleventh IP attempt should be BLOCKED

    ✅ BUG FIXED by security-backend-ai on 2025-10-12:
    Corrected logger.warning syntax to use extra={"ip": value}
    IP rate limiting now works correctly and blocks 11th attempt.
    """
    ip = "203.0.113.1"
    key = f"sms_rate_limit:ip:{ip}"

    # Simulate 10 previous attempts (limit reached)
    mock_redis_service._storage[key] = "10"

    allowed, message = await check_ip_rate_limit(mock_redis_service, ip)

    # ✅ CORRECTED: IP rate limiting now works properly
    assert allowed is False
    assert "Demasiadas solicitudes" in message
    assert "10 intentos" in message


# ============================================================================
# HIGH PRIORITY TESTS: validate_phone_number()
# ============================================================================

@pytest.mark.unit
@pytest.mark.sms_security
@pytest.mark.parametrize("phone,expected_valid", [
    # ✅ BUG FIXED by security-backend-ai on 2025-10-12:
    # All logger calls now use extra={"key": value} syntax
    # Phone validation now works correctly

    # Valid phones (NOW WORKING):
    ("+573001234567", True),   # Valid Colombian mobile
    ("+17379771943", True),    # Valid US mobile
    ("+5491112345678", True),  # Valid Argentina mobile

    # Invalid phones (work correctly):
    ("3001234567", False),     # Missing country code
    ("+123", False),           # Too short
    ("+5712345678", False),    # Colombian landline (not mobile)
])
def test_validate_phone_number_various_formats(phone, expected_valid):
    """
    Test phone validation with various international formats

    ✅ CRITICAL BUG FIXED: All logging syntax corrected
    FIX: Changed logger.xxx(..., key=value) to logger.xxx(..., extra={"key": value})
    IMPACT: Complete restoration of SMS security features
    SEVERITY: RESOLVED - Rate limiting and validation fully functional
    """
    valid, error_msg, e164 = validate_phone_number(phone)

    assert valid == expected_valid
    if expected_valid:
        assert e164.startswith("+")
        assert error_msg == "OK"
    else:
        assert error_msg != "OK"
        assert e164 == ""


# ============================================================================
# MEDIUM PRIORITY TESTS: get_client_ip()
# ============================================================================

@pytest.mark.unit
@pytest.mark.sms_security
def test_get_client_ip_from_x_forwarded_for(mock_request):
    """Extract real IP from X-Forwarded-For header"""
    mock_request.headers = {"X-Forwarded-For": "198.51.100.1, 203.0.113.1"}

    ip = get_client_ip(mock_request)

    assert ip == "198.51.100.1"  # First IP in chain (real client)


@pytest.mark.unit
@pytest.mark.sms_security
def test_get_client_ip_direct_connection(mock_request):
    """Fallback to direct connection IP if no headers"""
    mock_request.headers = {}
    mock_request.client.host = "203.0.113.1"

    ip = get_client_ip(mock_request)

    assert ip == "203.0.113.1"


# ============================================================================
# MEDIUM PRIORITY TESTS: log_sms_security_event()
# ============================================================================

@pytest.mark.unit
@pytest.mark.sms_security
def test_log_sms_security_event_phone_hashing_gdpr(caplog):
    """CRITICAL: Phone must be hashed (GDPR Art. 32)"""
    import hashlib
    import logging
    caplog.set_level(logging.INFO)

    phone = "+573001234567"
    expected_hash = hashlib.sha256(phone.encode()).hexdigest()[:16]

    log_sms_security_event("sms_sent", phone, "203.0.113.1", True)

    # Phone original NO debe estar en logs
    log_text = caplog.text
    assert phone not in log_text

    # Hash SÍ debe estar (verificar en extra data o en texto)
    # El hash puede estar en el texto del log o en los records extra
    assert expected_hash in log_text or any(
        expected_hash in str(record.__dict__.get("phone_hash", ""))
        for record in caplog.records
    )
