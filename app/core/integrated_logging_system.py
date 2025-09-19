"""
Integrated Logging System
=========================

Comprehensive logging and audit trail system that integrates:
- Security audit logging with threat detection
- Business event logging for compliance
- Performance logging with metrics correlation
- Error tracking with incident management
- User activity logging for analytics
- System health logging for monitoring

This system provides centralized logging with structured data, correlation IDs,
and integration with all Phase 2 components.

Author: System Architect AI
Date: 2025-09-17
Purpose: Unified logging and audit system for complete observability
"""

import asyncio
import json
import logging
import logging.handlers
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from uuid import uuid4
import traceback
import sys
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

# Import services for integration
from app.services.audit_logging_service import AuditLoggingService
from app.core.config import settings

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class LogLevel(Enum):
    """Log levels with numeric values"""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class LogCategory(Enum):
    """Log categories for organization"""
    SECURITY = "security"
    BUSINESS = "business"
    PERFORMANCE = "performance"
    SYSTEM = "system"
    USER_ACTIVITY = "user_activity"
    API = "api"
    DATABASE = "database"
    PAYMENT = "payment"
    AUTHENTICATION = "authentication"
    ERROR = "error"


@dataclass
class LogContext:
    """Structured log context"""
    correlation_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class StructuredLogEntry:
    """Structured log entry"""
    level: LogLevel
    category: LogCategory
    message: str
    context: LogContext
    data: Dict[str, Any] = None
    tags: List[str] = None
    duration_ms: Optional[float] = None
    error_details: Optional[str] = None
    business_impact: Optional[str] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.tags is None:
            self.tags = []


class IntegratedLoggingSystem:
    """
    Comprehensive logging system with audit trails and correlation.
    """

    def __init__(self):
        self.audit_service = AuditLoggingService
        self.correlation_store = {}  # Store correlation data
        self.loggers = {}  # Category-specific loggers

        # Initialize category-specific loggers
        self._setup_category_loggers()

        # Initialize log aggregation
        self._setup_log_aggregation()

    def _setup_category_loggers(self):
        """Setup specialized loggers for each category"""
        log_dir = Path(settings.LOG_DIR)
        log_dir.mkdir(exist_ok=True)

        for category in LogCategory:
            logger = logging.getLogger(f"mestore.{category.value}")
            logger.setLevel(getattr(logging, settings.LOG_LEVEL))

            # File handler with rotation
            file_handler = logging.handlers.RotatingFileHandler(
                log_dir / f"{category.value}.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )

            # JSON formatter for structured logs
            formatter = JsonFormatter()
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            self.loggers[category] = logger

    def _setup_log_aggregation(self):
        """Setup log aggregation and correlation"""
        # This could integrate with ELK stack, Prometheus, or other systems
        pass

    # Context Management

    def create_correlation_context(
        self,
        request: Optional[Request] = None,
        user_id: Optional[str] = None,
        operation: Optional[str] = None
    ) -> LogContext:
        """
        Create correlation context for request tracking.

        Args:
            request: FastAPI request object
            user_id: User ID if available
            operation: Operation name

        Returns:
            LogContext with correlation information
        """
        correlation_id = str(uuid4())

        context = LogContext(
            correlation_id=correlation_id,
            user_id=user_id,
            request_id=str(uuid4())
        )

        if request:
            context.ip_address = request.client.host if request.client else None
            context.user_agent = request.headers.get("User-Agent")
            context.endpoint = str(request.url.path)
            context.method = request.method

        # Store context for correlation
        self.correlation_store[correlation_id] = {
            "context": context,
            "operation": operation,
            "start_time": datetime.utcnow(),
            "events": []
        }

        return context

    def get_correlation_context(self, correlation_id: str) -> Optional[LogContext]:
        """Get correlation context by ID"""
        correlation_data = self.correlation_store.get(correlation_id)
        return correlation_data["context"] if correlation_data else None

    def add_correlation_event(
        self,
        correlation_id: str,
        event: str,
        data: Dict[str, Any] = None
    ):
        """Add event to correlation tracking"""
        if correlation_id in self.correlation_store:
            self.correlation_store[correlation_id]["events"].append({
                "event": event,
                "timestamp": datetime.utcnow(),
                "data": data or {}
            })

    # Structured Logging Methods

    async def log_structured(self, entry: StructuredLogEntry):
        """Log structured entry with correlation and audit"""
        try:
            # Get appropriate logger
            logger = self.loggers.get(entry.category, logging.getLogger())

            # Prepare log data
            log_data = {
                "level": entry.level.name,
                "category": entry.category.value,
                "message": entry.message,
                "correlation_id": entry.context.correlation_id,
                "timestamp": entry.context.timestamp.isoformat(),
                "context": asdict(entry.context),
                "data": entry.data,
                "tags": entry.tags
            }

            if entry.duration_ms is not None:
                log_data["duration_ms"] = entry.duration_ms

            if entry.error_details:
                log_data["error_details"] = entry.error_details

            if entry.business_impact:
                log_data["business_impact"] = entry.business_impact

            # Log with appropriate level
            if entry.level == LogLevel.DEBUG:
                logger.debug(entry.message, extra=log_data)
            elif entry.level == LogLevel.INFO:
                logger.info(entry.message, extra=log_data)
            elif entry.level == LogLevel.WARNING:
                logger.warning(entry.message, extra=log_data)
            elif entry.level == LogLevel.ERROR:
                logger.error(entry.message, extra=log_data)
            elif entry.level == LogLevel.CRITICAL:
                logger.critical(entry.message, extra=log_data)

            # Add to correlation events
            self.add_correlation_event(
                entry.context.correlation_id,
                f"{entry.category.value}_{entry.level.name.lower()}",
                log_data
            )

            # Audit critical events
            if entry.level in [LogLevel.ERROR, LogLevel.CRITICAL] or entry.category == LogCategory.SECURITY:
                await self._audit_critical_event(entry)

        except Exception as e:
            # Fallback logging to prevent loss of important events
            logging.getLogger().error(f"Failed to log structured entry: {str(e)}")

    # Business Event Logging

    async def log_business_event(
        self,
        event_type: str,
        message: str,
        context: LogContext,
        business_data: Dict[str, Any] = None,
        business_impact: str = None
    ):
        """Log business events for compliance and analytics"""
        entry = StructuredLogEntry(
            level=LogLevel.INFO,
            category=LogCategory.BUSINESS,
            message=f"BUSINESS_EVENT: {event_type} - {message}",
            context=context,
            data={
                "event_type": event_type,
                "business_data": business_data or {},
                "compliance_relevant": True
            },
            tags=["business_event", event_type],
            business_impact=business_impact
        )

        await self.log_structured(entry)

    async def log_user_activity(
        self,
        action: str,
        user_id: str,
        context: LogContext,
        details: Dict[str, Any] = None
    ):
        """Log user activities for analytics and security"""
        entry = StructuredLogEntry(
            level=LogLevel.INFO,
            category=LogCategory.USER_ACTIVITY,
            message=f"USER_ACTIVITY: {action} by user {user_id}",
            context=context,
            data={
                "action": action,
                "user_id": user_id,
                "details": details or {}
            },
            tags=["user_activity", action]
        )

        await self.log_structured(entry)

    # Security Event Logging

    async def log_security_event(
        self,
        event_type: str,
        message: str,
        context: LogContext,
        severity: str = "medium",
        threat_indicators: Dict[str, Any] = None
    ):
        """Log security events with threat analysis"""
        level_map = {
            "low": LogLevel.INFO,
            "medium": LogLevel.WARNING,
            "high": LogLevel.ERROR,
            "critical": LogLevel.CRITICAL
        }

        entry = StructuredLogEntry(
            level=level_map.get(severity, LogLevel.WARNING),
            category=LogCategory.SECURITY,
            message=f"SECURITY_EVENT: {event_type} - {message}",
            context=context,
            data={
                "event_type": event_type,
                "severity": severity,
                "threat_indicators": threat_indicators or {},
                "requires_investigation": severity in ["high", "critical"]
            },
            tags=["security_event", event_type, f"severity_{severity}"]
        )

        await self.log_structured(entry)

        # Also log through audit service for security events
        try:
            await self.audit_service.log_security_event(
                event_type=event_type,
                user_id=context.user_id,
                ip_address=context.ip_address,
                details={
                    "message": message,
                    "severity": severity,
                    "threat_indicators": threat_indicators
                }
            )
        except Exception as e:
            logging.getLogger().error(f"Failed to audit security event: {str(e)}")

    # Performance Event Logging

    async def log_performance_event(
        self,
        operation: str,
        duration_ms: float,
        context: LogContext,
        metrics: Dict[str, Any] = None,
        threshold_exceeded: bool = False
    ):
        """Log performance events with metrics"""
        level = LogLevel.WARNING if threshold_exceeded else LogLevel.INFO

        entry = StructuredLogEntry(
            level=level,
            category=LogCategory.PERFORMANCE,
            message=f"PERFORMANCE: {operation} completed in {duration_ms:.2f}ms",
            context=context,
            data={
                "operation": operation,
                "metrics": metrics or {},
                "threshold_exceeded": threshold_exceeded
            },
            tags=["performance", operation],
            duration_ms=duration_ms
        )

        await self.log_structured(entry)

    # Payment Event Logging

    async def log_payment_event(
        self,
        event_type: str,
        order_id: int,
        amount: float,
        context: LogContext,
        payment_data: Dict[str, Any] = None,
        success: bool = True
    ):
        """Log payment events for financial auditing"""
        level = LogLevel.INFO if success else LogLevel.ERROR

        entry = StructuredLogEntry(
            level=level,
            category=LogCategory.PAYMENT,
            message=f"PAYMENT: {event_type} for order {order_id} - Amount: ${amount:.2f}",
            context=context,
            data={
                "event_type": event_type,
                "order_id": order_id,
                "amount": amount,
                "success": success,
                "payment_data": payment_data or {},
                "financial_record": True
            },
            tags=["payment", event_type, "success" if success else "failure"],
            business_impact="financial" if success else "financial_loss"
        )

        await self.log_structured(entry)

    # API Event Logging

    async def log_api_event(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float,
        context: LogContext,
        request_size: int = 0,
        response_size: int = 0
    ):
        """Log API calls for monitoring and analytics"""
        level = LogLevel.ERROR if status_code >= 500 else LogLevel.INFO

        entry = StructuredLogEntry(
            level=level,
            category=LogCategory.API,
            message=f"API: {method} {endpoint} - {status_code} ({duration_ms:.2f}ms)",
            context=context,
            data={
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "request_size": request_size,
                "response_size": response_size,
                "success": status_code < 400
            },
            tags=["api", method.lower(), f"status_{status_code}"],
            duration_ms=duration_ms
        )

        await self.log_structured(entry)

    # Error Logging

    async def log_error(
        self,
        error: Exception,
        context: LogContext,
        operation: str = None,
        additional_data: Dict[str, Any] = None
    ):
        """Log errors with full context and stack trace"""
        entry = StructuredLogEntry(
            level=LogLevel.ERROR,
            category=LogCategory.ERROR,
            message=f"ERROR: {str(error)} in {operation or 'unknown operation'}",
            context=context,
            data={
                "error_type": error.__class__.__name__,
                "error_message": str(error),
                "operation": operation,
                "additional_data": additional_data or {}
            },
            tags=["error", error.__class__.__name__.lower()],
            error_details=traceback.format_exc()
        )

        await self.log_structured(entry)

    # System Event Logging

    async def log_system_event(
        self,
        event_type: str,
        message: str,
        context: LogContext,
        system_data: Dict[str, Any] = None,
        health_impact: str = None
    ):
        """Log system events for monitoring"""
        entry = StructuredLogEntry(
            level=LogLevel.INFO,
            category=LogCategory.SYSTEM,
            message=f"SYSTEM: {event_type} - {message}",
            context=context,
            data={
                "event_type": event_type,
                "system_data": system_data or {},
                "health_impact": health_impact
            },
            tags=["system", event_type]
        )

        await self.log_structured(entry)

    # Correlation and Analytics

    async def get_correlation_timeline(
        self,
        correlation_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get complete timeline for a correlation ID"""
        correlation_data = self.correlation_store.get(correlation_id)
        if not correlation_data:
            return None

        return {
            "correlation_id": correlation_id,
            "operation": correlation_data["operation"],
            "start_time": correlation_data["start_time"].isoformat(),
            "context": asdict(correlation_data["context"]),
            "events": correlation_data["events"],
            "duration_ms": (datetime.utcnow() - correlation_data["start_time"]).total_seconds() * 1000
        }

    async def cleanup_old_correlations(self, max_age_hours: int = 24):
        """Cleanup old correlation data to prevent memory leaks"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)

        to_remove = []
        for correlation_id, data in self.correlation_store.items():
            if data["start_time"] < cutoff_time:
                to_remove.append(correlation_id)

        for correlation_id in to_remove:
            del self.correlation_store[correlation_id]

        if to_remove:
            logging.getLogger().info(f"Cleaned up {len(to_remove)} old correlation entries")

    # Helper Methods

    async def _audit_critical_event(self, entry: StructuredLogEntry):
        """Audit critical events through audit service"""
        try:
            await self.audit_service.log_system_event(
                event_type=f"{entry.category.value}_critical",
                user_id=entry.context.user_id,
                ip_address=entry.context.ip_address,
                details={
                    "level": entry.level.name,
                    "message": entry.message,
                    "correlation_id": entry.context.correlation_id,
                    "data": entry.data
                }
            )
        except Exception as e:
            logging.getLogger().error(f"Failed to audit critical event: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """Health check for logging system"""
        return {
            "service": "IntegratedLoggingSystem",
            "status": "healthy",
            "active_correlations": len(self.correlation_store),
            "category_loggers": len(self.loggers),
            "timestamp": datetime.utcnow().isoformat()
        }


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }

        # Add extra data if present
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                              'filename', 'module', 'lineno', 'funcName', 'created',
                              'msecs', 'relativeCreated', 'thread', 'threadName',
                              'processName', 'process', 'exc_info', 'exc_text', 'stack_info']:
                    log_data[key] = value

        return json.dumps(log_data, default=str)


# Global instance for application use
integrated_logging_system = IntegratedLoggingSystem()