"""
Monitoring module for MeStore SMS Verification System

This module provides comprehensive production monitoring including:
- Prometheus metrics for SMS verification performance
- Custom metrics for business KPIs
- Error tracking and alerting
- Twilio integration health monitoring
"""

from .metrics import (
    # SMS Metrics
    sms_send_requests,
    sms_send_duration,
    sms_rate_limit_hits,
    sms_verification_attempts,

    # Twilio Metrics
    twilio_api_calls,
    twilio_api_errors,
    twilio_cost_usd,

    # Redis Metrics
    redis_rate_limit_checks,
    redis_errors,

    # Registration Flow Metrics
    registration_flow_events,
    registration_duration,

    # Helper functions
    track_sms_send,
    track_sms_verification,
    track_twilio_api_call,
    track_redis_operation,
    track_registration_event
)

__all__ = [
    'sms_send_requests',
    'sms_send_duration',
    'sms_rate_limit_hits',
    'sms_verification_attempts',
    'twilio_api_calls',
    'twilio_api_errors',
    'twilio_cost_usd',
    'redis_rate_limit_checks',
    'redis_errors',
    'registration_flow_events',
    'registration_duration',
    'track_sms_send',
    'track_sms_verification',
    'track_twilio_api_call',
    'track_redis_operation',
    'track_registration_event',
]
