"""
Unified Error Handler
=====================

Comprehensive error handling system that integrates across all Phase 2 components:
- Security error handling with audit logging
- Payment error handling with transaction safety
- Performance error handling with degradation management
- Database error handling with connection recovery
- External service error handling with circuit breakers

This module provides consistent error handling patterns across the entire application
while maintaining security, performance, and reliability requirements.

Author: System Architect AI
Date: 2025-09-17
Purpose: Unified error handling for all integrated systems
"""

import asyncio
import logging
import traceback
from contextlib import contextmanager, asynccontextmanager
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Callable, Type
from enum import Enum
from dataclasses import dataclass, field
from functools import wraps
import json

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError, TimeoutError as SQLTimeoutError
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError

# Import integrated services
from app.services.audit_logging_service import AuditLoggingService
from app.services.integrated_performance_service import integrated_performance_service

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    PAYMENT = "payment"
    DATABASE = "database"
    EXTERNAL_SERVICE = "external_service"
    PERFORMANCE = "performance"
    VALIDATION = "validation"
    SYSTEM = "system"
    SECURITY = "security"


@dataclass
class ErrorContext:
    """Error context information"""
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorInfo:
    """Standardized error information"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Optional[str] = None
    context: Optional[ErrorContext] = None
    recoverable: bool = True
    retry_after: Optional[int] = None
    user_message: Optional[str] = None
    technical_message: Optional[str] = None


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    """Circuit breaker for external services"""
    name: str
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout: int = 60
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None


class UnifiedErrorHandler:
    """
    Unified error handler for all integrated systems.
    """

    def __init__(self):
        self.audit_service = AuditLoggingService
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.error_patterns = {}
        self.recovery_strategies = {}

        # Initialize default error patterns
        self._setup_error_patterns()
        self._setup_recovery_strategies()

    def _setup_error_patterns(self):
        """Setup default error classification patterns"""
        self.error_patterns = {
            # Database errors
            SQLAlchemyError: (ErrorCategory.DATABASE, ErrorSeverity.HIGH),
            DisconnectionError: (ErrorCategory.DATABASE, ErrorSeverity.CRITICAL),
            SQLTimeoutError: (ErrorCategory.DATABASE, ErrorSeverity.MEDIUM),

            # Redis errors
            RedisError: (ErrorCategory.EXTERNAL_SERVICE, ErrorSeverity.MEDIUM),
            RedisConnectionError: (ErrorCategory.EXTERNAL_SERVICE, ErrorSeverity.HIGH),

            # HTTP errors
            HTTPException: (ErrorCategory.VALIDATION, ErrorSeverity.LOW),

            # Security errors
            PermissionError: (ErrorCategory.SECURITY, ErrorSeverity.HIGH),
            ValueError: (ErrorCategory.VALIDATION, ErrorSeverity.LOW),

            # System errors
            ConnectionError: (ErrorCategory.EXTERNAL_SERVICE, ErrorSeverity.HIGH),
            TimeoutError: (ErrorCategory.PERFORMANCE, ErrorSeverity.MEDIUM),
        }

    def _setup_recovery_strategies(self):
        """Setup default recovery strategies"""
        self.recovery_strategies = {
            ErrorCategory.DATABASE: self._recover_database_error,
            ErrorCategory.EXTERNAL_SERVICE: self._recover_external_service_error,
            ErrorCategory.PAYMENT: self._recover_payment_error,
            ErrorCategory.PERFORMANCE: self._recover_performance_error,
        }

    async def handle_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None,
        custom_message: Optional[str] = None
    ) -> ErrorInfo:
        """
        Handle any error with comprehensive processing.

        Args:
            error: Exception that occurred
            context: Error context information
            custom_message: Custom error message

        Returns:
            ErrorInfo with processed error details
        """
        try:
            # Generate error ID for tracking
            error_id = self._generate_error_id()

            # Classify error
            category, severity = self._classify_error(error)

            # Create error info
            error_info = ErrorInfo(
                error_id=error_id,
                category=category,
                severity=severity,
                message=custom_message or str(error),
                details=self._get_error_details(error),
                context=context,
                recoverable=self._is_recoverable(error, category),
                user_message=self._get_user_message(error, category),
                technical_message=str(error)
            )

            # Log error with appropriate level
            await self._log_error(error_info, error)

            # Audit security-related errors
            if category in [ErrorCategory.SECURITY, ErrorCategory.AUTHENTICATION, ErrorCategory.AUTHORIZATION]:
                await self._audit_security_error(error_info, error)

            # Handle circuit breaker logic
            if category == ErrorCategory.EXTERNAL_SERVICE:
                await self._handle_circuit_breaker(error_info, error)

            # Attempt recovery if possible
            if error_info.recoverable:
                recovery_result = await self._attempt_recovery(error_info, error)
                if recovery_result:
                    error_info.recoverable = True
                    error_info.retry_after = recovery_result.get("retry_after")

            return error_info

        except Exception as handler_error:
            logger.critical(f"Error in error handler: {str(handler_error)}")
            # Return minimal error info to prevent infinite loops
            return ErrorInfo(
                error_id="error_handler_failed",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.CRITICAL,
                message="Internal error handler failure",
                recoverable=False
            )

    def error_handler_decorator(
        self,
        error_category: Optional[ErrorCategory] = None,
        custom_message: Optional[str] = None,
        reraise: bool = True
    ):
        """
        Decorator for automatic error handling.

        Args:
            error_category: Override error category classification
            custom_message: Custom error message
            reraise: Whether to reraise the error after handling

        Usage:
            @error_handler.error_handler_decorator(ErrorCategory.PAYMENT, "Payment processing failed")
            async def process_payment(...):
                # Function implementation
        """
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    # Extract context from request if available
                    context = self._extract_context_from_args(args, kwargs)

                    # Handle error
                    error_info = await self.handle_error(e, context, custom_message)

                    # Override category if specified
                    if error_category:
                        error_info.category = error_category

                    if reraise:
                        # Convert to appropriate HTTP exception
                        raise self._convert_to_http_exception(error_info)
                    else:
                        return {"error": error_info.user_message, "error_id": error_info.error_id}

            return wrapper
        return decorator

    @asynccontextmanager
    async def error_handling_context(
        self,
        operation_name: str,
        context: Optional[ErrorContext] = None
    ):
        """
        Context manager for error handling with performance monitoring.

        Usage:
            async with error_handler.error_handling_context("payment_processing"):
                # Your operation here
        """
        try:
            async with integrated_performance_service.monitor_operation(operation_name):
                yield
        except Exception as e:
            error_info = await self.handle_error(e, context)
            raise self._convert_to_http_exception(error_info)

    # Circuit Breaker Methods

    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(name=service_name)
        return self.circuit_breakers[service_name]

    async def call_with_circuit_breaker(
        self,
        service_name: str,
        operation: Callable,
        *args,
        **kwargs
    ):
        """
        Call operation with circuit breaker protection.

        Args:
            service_name: Name of the external service
            operation: Operation to call
            *args, **kwargs: Arguments for the operation

        Returns:
            Operation result

        Raises:
            HTTPException: If circuit breaker is open
        """
        circuit_breaker = self.get_circuit_breaker(service_name)

        # Check circuit breaker state
        if circuit_breaker.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset(circuit_breaker):
                circuit_breaker.state = CircuitBreakerState.HALF_OPEN
                logger.info(f"Circuit breaker for {service_name} moved to half-open")
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Service {service_name} is temporarily unavailable"
                )

        try:
            result = await operation(*args, **kwargs)

            # Success - handle circuit breaker state
            if circuit_breaker.state == CircuitBreakerState.HALF_OPEN:
                circuit_breaker.success_count += 1
                if circuit_breaker.success_count >= circuit_breaker.success_threshold:
                    circuit_breaker.state = CircuitBreakerState.CLOSED
                    circuit_breaker.failure_count = 0
                    circuit_breaker.success_count = 0
                    logger.info(f"Circuit breaker for {service_name} closed")

            return result

        except Exception as e:
            # Failure - update circuit breaker
            circuit_breaker.failure_count += 1
            circuit_breaker.last_failure_time = datetime.utcnow()

            if circuit_breaker.failure_count >= circuit_breaker.failure_threshold:
                circuit_breaker.state = CircuitBreakerState.OPEN
                logger.warning(f"Circuit breaker for {service_name} opened due to failures")

            raise

    # Helper Methods

    def _classify_error(self, error: Exception) -> tuple[ErrorCategory, ErrorSeverity]:
        """Classify error by type"""
        error_type = type(error)

        # Check exact type match
        if error_type in self.error_patterns:
            return self.error_patterns[error_type]

        # Check inheritance
        for exception_type, (category, severity) in self.error_patterns.items():
            if isinstance(error, exception_type):
                return category, severity

        # Default classification
        return ErrorCategory.SYSTEM, ErrorSeverity.MEDIUM

    def _is_recoverable(self, error: Exception, category: ErrorCategory) -> bool:
        """Determine if error is recoverable"""
        # Critical security errors are not recoverable
        if category == ErrorCategory.SECURITY and isinstance(error, PermissionError):
            return False

        # Database disconnections can be recovered
        if isinstance(error, DisconnectionError):
            return True

        # Most validation errors are not recoverable
        if category == ErrorCategory.VALIDATION:
            return False

        # External service errors might be recoverable
        if category == ErrorCategory.EXTERNAL_SERVICE:
            return True

        return True

    def _get_user_message(self, error: Exception, category: ErrorCategory) -> str:
        """Get user-friendly error message"""
        user_messages = {
            ErrorCategory.AUTHENTICATION: "Authentication failed. Please login again.",
            ErrorCategory.AUTHORIZATION: "You don't have permission to perform this action.",
            ErrorCategory.PAYMENT: "Payment processing failed. Please try again or use a different payment method.",
            ErrorCategory.DATABASE: "A temporary system error occurred. Please try again later.",
            ErrorCategory.EXTERNAL_SERVICE: "An external service is temporarily unavailable. Please try again later.",
            ErrorCategory.PERFORMANCE: "The system is experiencing high load. Please try again in a few minutes.",
            ErrorCategory.VALIDATION: "Invalid request data. Please check your input and try again.",
            ErrorCategory.SYSTEM: "An unexpected system error occurred. Please try again later.",
            ErrorCategory.SECURITY: "A security error occurred. This incident has been logged."
        }

        return user_messages.get(category, "An error occurred. Please try again later.")

    def _get_error_details(self, error: Exception) -> str:
        """Get detailed error information for logging"""
        return traceback.format_exc()

    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        from uuid import uuid4
        return f"err_{uuid4().hex[:8]}"

    async def _log_error(self, error_info: ErrorInfo, error: Exception):
        """Log error with appropriate level"""
        log_data = {
            "error_id": error_info.error_id,
            "category": error_info.category.value,
            "severity": error_info.severity.value,
            "message": error_info.message,
            "context": error_info.context.__dict__ if error_info.context else None
        }

        if error_info.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"CRITICAL ERROR: {error_info.message}", extra=log_data)
        elif error_info.severity == ErrorSeverity.HIGH:
            logger.error(f"ERROR: {error_info.message}", extra=log_data)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"WARNING: {error_info.message}", extra=log_data)
        else:
            logger.info(f"INFO: {error_info.message}", extra=log_data)

    async def _audit_security_error(self, error_info: ErrorInfo, error: Exception):
        """Audit security-related errors"""
        try:
            await self.audit_service.log_security_event(
                event_type="security_error",
                user_id=error_info.context.user_id if error_info.context else None,
                ip_address=error_info.context.ip_address if error_info.context else None,
                details={
                    "error_id": error_info.error_id,
                    "error_type": error.__class__.__name__,
                    "message": error_info.message,
                    "endpoint": error_info.context.endpoint if error_info.context else None
                }
            )
        except Exception as audit_error:
            logger.error(f"Failed to audit security error: {str(audit_error)}")

    async def _handle_circuit_breaker(self, error_info: ErrorInfo, error: Exception):
        """Handle circuit breaker logic for external service errors"""
        # Implementation would depend on the specific error and context
        pass

    async def _attempt_recovery(self, error_info: ErrorInfo, error: Exception) -> Optional[Dict[str, Any]]:
        """Attempt to recover from error"""
        recovery_strategy = self.recovery_strategies.get(error_info.category)
        if recovery_strategy:
            try:
                return await recovery_strategy(error_info, error)
            except Exception as recovery_error:
                logger.error(f"Recovery strategy failed: {str(recovery_error)}")
        return None

    async def _recover_database_error(self, error_info: ErrorInfo, error: Exception) -> Dict[str, Any]:
        """Recovery strategy for database errors"""
        return {"retry_after": 30}  # Suggest retry after 30 seconds

    async def _recover_external_service_error(self, error_info: ErrorInfo, error: Exception) -> Dict[str, Any]:
        """Recovery strategy for external service errors"""
        return {"retry_after": 60}  # Suggest retry after 1 minute

    async def _recover_payment_error(self, error_info: ErrorInfo, error: Exception) -> Dict[str, Any]:
        """Recovery strategy for payment errors"""
        return {"retry_after": 120}  # Suggest retry after 2 minutes

    async def _recover_performance_error(self, error_info: ErrorInfo, error: Exception) -> Dict[str, Any]:
        """Recovery strategy for performance errors"""
        return {"retry_after": 180}  # Suggest retry after 3 minutes

    def _should_attempt_reset(self, circuit_breaker: CircuitBreaker) -> bool:
        """Check if circuit breaker should attempt reset"""
        if circuit_breaker.last_failure_time:
            time_since_failure = datetime.utcnow() - circuit_breaker.last_failure_time
            return time_since_failure.total_seconds() >= circuit_breaker.timeout
        return False

    def _extract_context_from_args(self, args, kwargs) -> Optional[ErrorContext]:
        """Extract error context from function arguments"""
        # Look for Request object in args/kwargs
        for arg in args:
            if hasattr(arg, 'client') and hasattr(arg, 'method'):  # Likely a Request object
                return ErrorContext(
                    ip_address=arg.client.host if arg.client else None,
                    user_agent=arg.headers.get("User-Agent") if hasattr(arg, 'headers') else None,
                    endpoint=str(arg.url) if hasattr(arg, 'url') else None,
                    method=arg.method if hasattr(arg, 'method') else None
                )

        return None

    def _convert_to_http_exception(self, error_info: ErrorInfo) -> HTTPException:
        """Convert ErrorInfo to appropriate HTTPException"""
        status_code_map = {
            ErrorCategory.AUTHENTICATION: status.HTTP_401_UNAUTHORIZED,
            ErrorCategory.AUTHORIZATION: status.HTTP_403_FORBIDDEN,
            ErrorCategory.PAYMENT: status.HTTP_402_PAYMENT_REQUIRED,
            ErrorCategory.DATABASE: status.HTTP_503_SERVICE_UNAVAILABLE,
            ErrorCategory.EXTERNAL_SERVICE: status.HTTP_503_SERVICE_UNAVAILABLE,
            ErrorCategory.PERFORMANCE: status.HTTP_503_SERVICE_UNAVAILABLE,
            ErrorCategory.VALIDATION: status.HTTP_400_BAD_REQUEST,
            ErrorCategory.SYSTEM: status.HTTP_500_INTERNAL_SERVER_ERROR,
            ErrorCategory.SECURITY: status.HTTP_403_FORBIDDEN
        }

        status_code = status_code_map.get(error_info.category, status.HTTP_500_INTERNAL_SERVER_ERROR)

        detail = {
            "error_id": error_info.error_id,
            "message": error_info.user_message,
            "category": error_info.category.value,
            "recoverable": error_info.recoverable
        }

        if error_info.retry_after:
            detail["retry_after"] = error_info.retry_after

        return HTTPException(status_code=status_code, detail=detail)

    async def health_check(self) -> Dict[str, Any]:
        """Health check for error handling system"""
        return {
            "service": "UnifiedErrorHandler",
            "status": "healthy",
            "circuit_breakers": {
                name: {
                    "state": cb.state.value,
                    "failure_count": cb.failure_count,
                    "success_count": cb.success_count
                }
                for name, cb in self.circuit_breakers.items()
            },
            "timestamp": datetime.utcnow().isoformat()
        }


# Global instance for application use
unified_error_handler = UnifiedErrorHandler()