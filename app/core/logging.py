"""
GREEN PHASE: Minimal logging implementation for audit functionality

This module provides the minimal audit logging functionality required
to make the test_admin_audit_logging_requirements test pass.

TDD GREEN PHASE: Just enough code to make the test pass.
"""

import logging
from typing import Any, Dict
from datetime import datetime


class AuditLogger:
    """Minimal audit logger implementation for GREEN phase"""

    def __init__(self):
        self.logger = logging.getLogger("audit")

    def info(self, message: str, extra: Dict[str, Any] = None):
        """Log audit information"""
        self.logger.info(message, extra=extra)

    def warning(self, message: str, extra: Dict[str, Any] = None):
        """Log audit warnings"""
        self.logger.warning(message, extra=extra)

    def error(self, message: str, extra: Dict[str, Any] = None):
        """Log audit errors"""
        self.logger.error(message, extra=extra)

    def log_admin_action(self, user_id: str, action: str, endpoint: str, status_code: int = None):
        """Log admin actions for audit trail"""
        audit_data = {
            "user_id": user_id,
            "action": action,
            "endpoint": endpoint,
            "timestamp": datetime.utcnow().isoformat(),
            "status_code": status_code
        }
        self.info(f"Admin action: {action} on {endpoint}", extra=audit_data)


# Global audit logger instance
audit_logger = AuditLogger()

# Export logger for compatibility
logger = audit_logger