"""
Enhanced JSON Logging Configuration for Production

This module provides structured JSON logging for production environments,
making logs easily parseable by log aggregation systems like ELK, Splunk, etc.

Features:
- Structured JSON output
- Correlation IDs for request tracing
- Performance metrics in logs
- PII-safe logging (hashes sensitive data)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
"""

import logging
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging

    Formats log records as JSON objects with consistent structure for easy parsing
    by log aggregation systems.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON

        Args:
            record: The log record to format

        Returns:
            JSON string representation of the log record
        """
        # Base log data
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'process': record.process,
        }

        # Add environment context
        log_data['environment'] = settings.ENVIRONMENT

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }

        # Add extra fields from record
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)

        # Add correlation ID if present (for request tracing)
        if hasattr(record, 'correlation_id'):
            log_data['correlation_id'] = record.correlation_id

        # Add performance metrics if present
        if hasattr(record, 'duration_ms'):
            log_data['performance'] = {
                'duration_ms': record.duration_ms
            }

        # Add user context if present (PII-safe)
        if hasattr(record, 'user_id'):
            log_data['user'] = {
                'id_hash': self._hash_pii(record.user_id) if record.user_id else None
            }

        # Add request context if present
        if hasattr(record, 'request_method'):
            log_data['request'] = {
                'method': record.request_method,
                'path': record.request_path,
                'ip_hash': self._hash_pii(record.client_ip) if hasattr(record, 'client_ip') else None
            }

        # Add SMS verification context if present
        if hasattr(record, 'sms_event'):
            log_data['sms'] = {
                'event': record.sms_event,
                'phone_hash': self._hash_pii(record.phone_number) if hasattr(record, 'phone_number') else None,
                'status': record.sms_status if hasattr(record, 'sms_status') else None
            }

        # Add security context if present
        if hasattr(record, 'security_event'):
            log_data['security'] = {
                'event': record.security_event,
                'severity': record.security_severity if hasattr(record, 'security_severity') else 'info',
                'action_taken': record.security_action if hasattr(record, 'security_action') else None
            }

        return json.dumps(log_data, default=str)

    def _hash_pii(self, value: str) -> str:
        """
        Hash PII data for privacy-safe logging

        Args:
            value: The value to hash

        Returns:
            SHA256 hash of the value (first 16 chars)
        """
        if not value:
            return None

        return hashlib.sha256(value.encode()).hexdigest()[:16]


class CorrelationLoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds correlation IDs to all log records

    This allows tracing a single request through multiple services/components.
    """

    def __init__(self, logger: logging.Logger, correlation_id: Optional[str] = None):
        super().__init__(logger, {})
        self.correlation_id = correlation_id or self._generate_correlation_id()

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Add correlation ID to extra fields"""
        if 'extra' not in kwargs:
            kwargs['extra'] = {}

        kwargs['extra']['correlation_id'] = self.correlation_id

        return msg, kwargs

    @staticmethod
    def _generate_correlation_id() -> str:
        """Generate a unique correlation ID"""
        import uuid
        return str(uuid.uuid4())


def setup_json_logging():
    """
    Configure JSON logging for production

    Should be called at application startup to configure the root logger
    with JSON formatting.
    """
    # Only use JSON logging in production
    if settings.ENVIRONMENT.lower() not in ['production', 'staging']:
        return

    # Create JSON formatter
    json_formatter = JSONFormatter()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove existing handlers
    root_logger.handlers = []

    # Add JSON handler for stdout
    json_handler = logging.StreamHandler()
    json_handler.setFormatter(json_formatter)
    root_logger.addHandler(json_handler)

    # Configure specific loggers
    for logger_name in ['app', 'uvicorn', 'fastapi']:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.propagate = True  # Propagate to root logger


def log_sms_event(
    logger: logging.Logger,
    event: str,
    phone_number: str,
    status: str,
    extra: Optional[Dict[str, Any]] = None
):
    """
    Log an SMS verification event with structured data

    Args:
        logger: The logger to use
        event: Event type (e.g., 'send', 'verify', 'rate_limit')
        phone_number: Phone number (will be hashed)
        status: Event status (e.g., 'success', 'error', 'blocked')
        extra: Additional context data
    """
    log_data = {
        'sms_event': event,
        'phone_number': phone_number,  # Will be hashed by formatter
        'sms_status': status
    }

    if extra:
        log_data.update(extra)

    logger.info(
        f"SMS {event}: {status}",
        extra={'extra_data': log_data}
    )


def log_security_event(
    logger: logging.Logger,
    event: str,
    severity: str = 'info',
    action: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None
):
    """
    Log a security event with structured data

    Args:
        logger: The logger to use
        event: Event type (e.g., 'rate_limit_hit', 'invalid_phone', 'brute_force')
        severity: Event severity ('info', 'warning', 'critical')
        action: Action taken (e.g., 'blocked', 'logged', 'alerted')
        extra: Additional context data
    """
    log_data = {
        'security_event': event,
        'security_severity': severity,
        'security_action': action
    }

    if extra:
        log_data.update(extra)

    # Map severity to log level
    level_map = {
        'info': logging.INFO,
        'warning': logging.WARNING,
        'critical': logging.CRITICAL
    }

    logger.log(
        level_map.get(severity, logging.INFO),
        f"Security event: {event}",
        extra={'extra_data': log_data}
    )


def log_performance(
    logger: logging.Logger,
    operation: str,
    duration_ms: float,
    extra: Optional[Dict[str, Any]] = None
):
    """
    Log performance metrics with structured data

    Args:
        logger: The logger to use
        operation: Operation name (e.g., 'sms_send', 'db_query')
        duration_ms: Duration in milliseconds
        extra: Additional context data
    """
    log_data = {
        'duration_ms': duration_ms
    }

    if extra:
        log_data.update(extra)

    logger.info(
        f"Performance: {operation} completed in {duration_ms:.2f}ms",
        extra={'extra_data': log_data}
    )


# Example usage in production:
"""
from app.core.monitoring.logging_config import (
    setup_json_logging,
    log_sms_event,
    log_security_event,
    log_performance
)

# At app startup:
setup_json_logging()

# In SMS verification code:
log_sms_event(
    logger,
    event='send',
    phone_number='+573001234567',
    status='success',
    extra={'country_code': '+57', 'channel': 'sms'}
)

# For security events:
log_security_event(
    logger,
    event='rate_limit_hit',
    severity='warning',
    action='blocked',
    extra={'ip': '192.168.1.1', 'limit_type': 'phone'}
)

# For performance tracking:
import time
start = time.time()
# ... operation ...
duration_ms = (time.time() - start) * 1000
log_performance(
    logger,
    operation='twilio_api_call',
    duration_ms=duration_ms,
    extra={'method': 'send_verification'}
)
"""
