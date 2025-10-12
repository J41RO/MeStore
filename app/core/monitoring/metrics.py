"""
Prometheus metrics for SMS verification system

This module defines all Prometheus metrics for monitoring the SMS verification
flow in production, including performance, error tracking, cost monitoring, and
business metrics.
"""

from prometheus_client import Counter, Histogram, Gauge, Summary
from typing import Literal
import time
from contextlib import contextmanager
from app.core.logger import get_logger

logger = get_logger(__name__)

# ============================================================================
# SMS SENDING METRICS
# ============================================================================

sms_send_requests = Counter(
    'sms_send_requests_total',
    'Total SMS send requests',
    ['status', 'country_code']
    # status: 'success', 'invalid', 'rate_limited', 'error'
    # country_code: first 3 digits of E.164 (e.g. '+57', '+1')
)

sms_send_duration = Histogram(
    'sms_send_duration_seconds',
    'SMS send request duration in seconds',
    buckets=[0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
)

sms_send_success_rate = Gauge(
    'sms_send_success_rate',
    'Current SMS send success rate (last 5 minutes)',
    # Calculated in alerts or dashboards from counters
)

sms_rate_limit_hits = Counter(
    'sms_rate_limit_hits_total',
    'SMS rate limit violations',
    ['limit_type']  # 'phone' or 'ip'
)

sms_invalid_phone = Counter(
    'sms_invalid_phone_total',
    'Invalid phone number attempts',
    ['reason']  # 'invalid_format', 'unsupported_country', 'invalid_e164'
)

# ============================================================================
# SMS VERIFICATION METRICS
# ============================================================================

sms_verification_attempts = Counter(
    'sms_verification_attempts_total',
    'SMS verification code attempts',
    ['status']  # 'success', 'invalid_code', 'expired', 'max_attempts'
)

sms_verification_success_rate = Gauge(
    'sms_verification_success_rate',
    'Current SMS verification success rate',
)

# ============================================================================
# TWILIO INTEGRATION METRICS
# ============================================================================

twilio_api_calls = Counter(
    'twilio_api_calls_total',
    'Twilio API calls',
    ['method', 'status_code']
    # method: 'send_verification', 'check_verification'
    # status_code: HTTP status or 'success'
)

twilio_api_errors = Counter(
    'twilio_api_errors_total',
    'Twilio API errors',
    ['error_code']  # Twilio error codes: 20003, 21211, etc.
)

twilio_api_latency = Histogram(
    'twilio_api_latency_seconds',
    'Twilio API latency in seconds',
    ['method'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

twilio_cost_usd = Counter(
    'twilio_cost_usd_total',
    'Accumulated Twilio costs in USD',
    # Each SMS ~ $0.0075 USD
)

# ============================================================================
# REDIS RATE LIMITING METRICS
# ============================================================================

redis_rate_limit_checks = Counter(
    'redis_rate_limit_checks_total',
    'Redis rate limit check operations',
    ['operation', 'result']
    # operation: 'phone', 'ip'
    # result: 'allowed', 'blocked'
)

redis_connection_errors = Counter(
    'redis_connection_errors_total',
    'Redis connection errors',
    ['operation']  # 'get', 'set', 'incr'
)

redis_failover_events = Counter(
    'redis_failover_events_total',
    'Redis failover events (fell back to allow)',
)

redis_response_time = Histogram(
    'redis_response_time_seconds',
    'Redis operation response time',
    ['operation'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
)

redis_errors = Counter(
    'redis_errors_total',
    'Redis operation errors (consolidated)',
    ['operation']
)

# ============================================================================
# USER REGISTRATION FLOW METRICS
# ============================================================================

registration_flow_events = Counter(
    'registration_flow_events_total',
    'Registration flow events',
    ['event', 'user_type']
    # event: 'started', 'email_sent', 'sms_sent', 'email_verified',
    #        'phone_verified', 'completed', 'abandoned_step_N'
    # user_type: 'BUYER', 'VENDOR'
)

registration_duration = Histogram(
    'registration_duration_seconds',
    'Time to complete full registration flow',
    ['user_type'],
    buckets=[30, 60, 120, 300, 600, 1800, 3600]  # 30s to 1 hour
)

registration_abandonment = Counter(
    'registration_abandonment_total',
    'Registration abandonment by step',
    ['step', 'user_type']
    # step: 'email_verification', 'phone_verification', 'profile_completion'
)

# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

endpoint_response_time = Histogram(
    'endpoint_response_time_seconds',
    'Endpoint response time',
    ['endpoint', 'method', 'status'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

# ============================================================================
# HELPER FUNCTIONS FOR EASY METRIC TRACKING
# ============================================================================

@contextmanager
def track_sms_send(country_code: str = 'unknown'):
    """
    Context manager to track SMS send performance

    Usage:
        with track_sms_send(country_code='+57'):
            result = await sms_service.send_verification_code(phone)
            if result['success']:
                sms_send_requests.labels(status='success', country_code='+57').inc()
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        sms_send_duration.observe(duration)


def track_sms_verification(status: Literal['success', 'invalid_code', 'expired', 'max_attempts']):
    """Track SMS verification attempt"""
    sms_verification_attempts.labels(status=status).inc()


def track_twilio_api_call(method: str, status_code: str, latency: float = None):
    """Track Twilio API call"""
    twilio_api_calls.labels(method=method, status_code=status_code).inc()

    if latency is not None:
        twilio_api_latency.labels(method=method).observe(latency)


def track_twilio_error(error_code: str):
    """Track Twilio error"""
    twilio_api_errors.labels(error_code=error_code).inc()


def track_twilio_cost(cost_usd: float):
    """Track Twilio cost (approximate)"""
    twilio_cost_usd.inc(cost_usd)


def track_redis_operation(operation: str, success: bool, latency: float = None):
    """Track Redis operation"""
    result = 'allowed' if success else 'blocked'
    redis_rate_limit_checks.labels(operation=operation, result=result).inc()

    if latency is not None:
        redis_response_time.labels(operation=operation).observe(latency)


def track_redis_error(operation: str):
    """Track Redis error"""
    redis_errors.labels(operation=operation).inc()


def track_registration_event(event: str, user_type: str):
    """Track registration flow event"""
    registration_flow_events.labels(event=event, user_type=user_type).inc()


def track_endpoint_performance(endpoint: str, method: str, status: int, duration: float):
    """Track endpoint performance"""
    endpoint_response_time.labels(
        endpoint=endpoint,
        method=method,
        status=str(status)
    ).observe(duration)


# ============================================================================
# METRIC EXPORT HELPERS
# ============================================================================

def get_all_metrics():
    """Get all registered metrics for debugging"""
    from prometheus_client import REGISTRY
    return list(REGISTRY._collector_to_names.keys())


def reset_metrics():
    """Reset all metrics (for testing only)"""
    logger.warning("⚠️ Resetting all Prometheus metrics - TESTING ONLY")
    # Note: Prometheus metrics cannot be truly reset in production
    # This is for development/testing purposes only
