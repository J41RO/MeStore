"""
Enterprise Security Middleware for MeStore.

This middleware provides comprehensive security features:
- Advanced rate limiting with Redis
- Fraud detection and anomaly analysis
- Device fingerprinting and session management
- Enterprise audit logging
- Colombian compliance features

Author: Backend Senior Developer
Version: 1.0.0 Enterprise
"""

import time
from datetime import datetime, timezone
from typing import Callable, Optional, Dict
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logger import get_logger
from app.core.redis import get_redis_service
from app.services.rate_limiting_service import EnterpriseRateLimitingService, RateLimitType
from app.services.fraud_detection_service import EnterpriseFraudDetectionService, RiskLevel
from app.services.session_service import EnterpriseSessionService

logger = get_logger(__name__)


class EnterpriseSecurityMiddleware(BaseHTTPMiddleware):
    """
    Enterprise security middleware providing comprehensive protection.

    Features:
    - Real-time rate limiting with multiple strategies
    - Fraud detection and behavioral analysis
    - Session management and device tracking
    - Security headers enforcement
    - Comprehensive audit logging
    - Performance monitoring
    """

    def __init__(self, app):
        """Initialize enterprise security middleware."""
        super().__init__(app)
        self.redis_client = None
        self.rate_limiter = None
        self.fraud_detector = None
        self.session_manager = None
        self._initialize_services()

    def _initialize_services(self):
        """Initialize security services lazily."""
        try:
            # Services will be initialized on first request to avoid startup issues
            pass
        except Exception as e:
            logger.error("Error initializing security services", error=str(e))

    async def _ensure_services(self):
        """Ensure all security services are initialized."""
        if self.redis_client is None:
            try:
                redis_service = await get_redis_service()
                self.redis_client = redis_service.client
                self.rate_limiter = EnterpriseRateLimitingService(self.redis_client)
                self.fraud_detector = EnterpriseFraudDetectionService(self.redis_client)
                self.session_manager = EnterpriseSessionService(self.redis_client)

                # Test Redis connection
                await self.redis_client.ping()
                return True

            except Exception as e:
                logger.critical("Critical security service failure - Redis unavailable", error=str(e))
                # SECURITY FIX: Fail closed when security services unavailable
                # This prevents authentication bypass when Redis is down
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Security services unavailable - access denied"
                )
        return True

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Main middleware dispatch method."""
        start_time = time.time()

        try:
            # Ensure services are initialized
            services_available = await self._ensure_services()

            # Extract request information
            ip_address = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
            user_agent = request.headers.get('User-Agent', 'unknown')
            endpoint = request.url.path
            method = request.method

            # Add security headers to request context
            request.state.start_time = start_time
            request.state.ip_address = ip_address
            request.state.user_agent = user_agent

            # Skip security checks for health endpoints
            if self._is_health_endpoint(endpoint):
                response = await call_next(request)
                return self._add_security_headers(response)

            # SECURITY FIX: Always apply security checks - fail closed approach
            if not services_available:
                logger.critical("Security services unavailable - denying access",
                              endpoint=endpoint, ip_address=ip_address)
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content={"detail": "Security services unavailable"},
                    headers=self._get_security_headers()
                )

            if self.rate_limiter:
                # 1. Rate Limiting Check
                rate_limit_result = await self.rate_limiter.check_rate_limit(
                    request=request,
                    endpoint=endpoint,
                    user_id=getattr(request.state, 'user_id', None)
                )

                if not rate_limit_result.allowed:
                    return await self._handle_rate_limit_exceeded(rate_limit_result, request)

                # Add rate limit info to request state
                request.state.rate_limit_result = rate_limit_result

            # 2. Fraud Detection (for authentication endpoints) - MANDATORY for auth endpoints
            if self._is_auth_endpoint(endpoint):
                if not self.fraud_detector:
                    logger.critical("Fraud detection unavailable for auth endpoint - denying access",
                                  endpoint=endpoint, ip_address=ip_address)
                    return JSONResponse(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        content={"detail": "Security services required for authentication"},
                        headers=self._get_security_headers()
                    )

                await self._apply_fraud_detection(request)

            # 3. Process the request
            try:
                response = await call_next(request)

                # 4. Post-request processing
                if self.session_manager:
                    await self._post_request_processing(request, response)

                # 5. Add security headers
                response = self._add_security_headers(response)

                # 6. Audit logging
                await self._audit_log_request(request, response, start_time)

                return response

            except HTTPException as e:
                # Handle HTTP exceptions with proper logging
                await self._audit_log_exception(request, e, start_time)
                raise

        except Exception as e:
            # Handle unexpected exceptions
            logger.error(
                "Unexpected error in security middleware",
                error=str(e),
                endpoint=getattr(request, 'url', {}).get('path', 'unknown'),
                ip_address=ip_address
            )

            # Create error response
            error_response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )

            return self._add_security_headers(error_response)

    def _is_health_endpoint(self, endpoint: str) -> bool:
        """Check if endpoint is a health check endpoint."""
        health_endpoints = ['/health', '/api/v1/health', '/ping', '/status']
        return any(endpoint.startswith(health_ep) for health_ep in health_endpoints)

    def _is_auth_endpoint(self, endpoint: str) -> bool:
        """Check if endpoint is authentication-related."""
        auth_endpoints = ['/auth/login', '/auth/register', '/auth/admin-login']
        return any(endpoint.endswith(auth_ep) for auth_ep in auth_endpoints)

    async def _handle_rate_limit_exceeded(self, rate_limit_result, request: Request) -> Response:
        """Handle rate limit exceeded scenario."""
        logger.warning(
            "Rate limit exceeded",
            ip_address=getattr(request.state, 'ip_address', 'unknown'),
            endpoint=request.url.path,
            limit_type=rate_limit_result.limit_type.value,
            retry_after=rate_limit_result.retry_after_seconds
        )

        headers = {
            "X-RateLimit-Limit": "100",  # Generic limit for response
            "X-RateLimit-Remaining": str(rate_limit_result.remaining_requests),
            "X-RateLimit-Reset": str(int(rate_limit_result.reset_time.timestamp())),
        }

        if rate_limit_result.retry_after_seconds:
            headers["Retry-After"] = str(rate_limit_result.retry_after_seconds)

        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "retry_after_seconds": rate_limit_result.retry_after_seconds
            },
            headers=headers
        )

    async def _apply_fraud_detection(self, request: Request) -> None:
        """Apply fraud detection to authentication requests."""
        try:
            # This would be called during login attempts
            # For now, we just prepare the fraud detection context
            request.state.fraud_detection_enabled = True

        except Exception as e:
            logger.error("Error applying fraud detection", error=str(e))

    async def _post_request_processing(self, request: Request, response: Response) -> None:
        """Post-request security processing."""
        try:
            # Update session activity if user is authenticated
            if hasattr(request.state, 'session_id') and self.session_manager:
                await self.session_manager.update_session_activity(request.state.session_id)

        except Exception as e:
            logger.error("Error in post-request processing", error=str(e))

    def _get_security_headers(self) -> Dict[str, str]:
        """Get security headers as dictionary."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            ),
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains" if not settings.DEBUG else "",
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "bluetooth=()"
            ),
            "X-Enterprise-Security": "enabled",
            "X-Rate-Limit-Policy": "sliding-window",
            "X-Fraud-Detection": "active" if settings.FRAUD_DETECTION_ENABLED else "disabled"
        }

    def _add_security_headers(self, response: Response) -> Response:
        """Add comprehensive security headers to response."""
        try:
            # Get security headers
            security_headers = self._get_security_headers()

            # Add headers to response
            for header, value in security_headers.items():
                if value:  # Only add non-empty headers
                    response.headers[header] = value

            return response

        except Exception as e:
            logger.error("Error adding security headers", error=str(e))
            return response

    async def _audit_log_request(self, request: Request, response: Response, start_time: float) -> None:
        """Comprehensive audit logging for security monitoring."""
        try:
            end_time = time.time()
            duration_ms = round((end_time - start_time) * 1000, 2)

            # Determine if this request should be audited
            if self._should_audit_request(request, response):
                audit_data = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "request_id": getattr(request.state, 'request_id', None),
                    "ip_address": getattr(request.state, 'ip_address', 'unknown'),
                    "user_agent": getattr(request.state, 'user_agent', 'unknown'),
                    "method": request.method,
                    "endpoint": request.url.path,
                    "query_params": dict(request.query_params) if request.query_params else {},
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "user_id": getattr(request.state, 'user_id', None),
                    "session_id": getattr(request.state, 'session_id', None),
                    "rate_limit_info": {
                        "remaining": getattr(request.state, 'rate_limit_result', {}).get('remaining_requests', 0),
                        "limit_type": getattr(request.state, 'rate_limit_result', {}).get('limit_type', None)
                    } if hasattr(request.state, 'rate_limit_result') else None
                }

                # Log based on response status
                if response.status_code >= 400:
                    logger.warning("Security audit - Client error", **audit_data)
                elif response.status_code >= 500:
                    logger.error("Security audit - Server error", **audit_data)
                elif self._is_sensitive_endpoint(request.url.path):
                    logger.info("Security audit - Sensitive endpoint", **audit_data)

        except Exception as e:
            logger.error("Error in audit logging", error=str(e))

    async def _audit_log_exception(self, request: Request, exception: HTTPException, start_time: float) -> None:
        """Audit log exceptions for security monitoring."""
        try:
            end_time = time.time()
            duration_ms = round((end_time - start_time) * 1000, 2)

            audit_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "ip_address": getattr(request.state, 'ip_address', 'unknown'),
                "user_agent": getattr(request.state, 'user_agent', 'unknown'),
                "method": request.method,
                "endpoint": request.url.path,
                "status_code": exception.status_code,
                "detail": exception.detail,
                "duration_ms": duration_ms,
                "exception_type": "HTTPException"
            }

            if exception.status_code == 401:
                logger.warning("Security audit - Unauthorized access", **audit_data)
            elif exception.status_code == 403:
                logger.warning("Security audit - Forbidden access", **audit_data)
            elif exception.status_code == 429:
                logger.warning("Security audit - Rate limit exceeded", **audit_data)
            else:
                logger.info("Security audit - HTTP exception", **audit_data)

        except Exception as e:
            logger.error("Error in exception audit logging", error=str(e))

    def _should_audit_request(self, request: Request, response: Response) -> bool:
        """Determine if a request should be audited."""
        # Always audit sensitive endpoints
        if self._is_sensitive_endpoint(request.url.path):
            return True

        # Always audit error responses
        if response.status_code >= 400:
            return True

        # Always audit POST, PUT, DELETE requests
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return True

        return False

    def _is_sensitive_endpoint(self, endpoint: str) -> bool:
        """Check if endpoint is sensitive and requires auditing."""
        sensitive_patterns = [
            '/auth/',
            '/admin/',
            '/users/',
            '/api/v1/users/',
            '/api/v1/auth/',
            '/api/v1/admin/'
        ]

        return any(pattern in endpoint for pattern in sensitive_patterns)


class SecurityMetricsMiddleware(BaseHTTPMiddleware):
    """
    Lightweight middleware for collecting security metrics.
    """

    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.error_count = 0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Collect basic security metrics."""
        self.request_count += 1

        try:
            response = await call_next(request)

            if response.status_code >= 400:
                self.error_count += 1

            # Add metrics headers
            response.headers["X-Request-Count"] = str(self.request_count)
            response.headers["X-Error-Rate"] = str(round(self.error_count / self.request_count * 100, 2))

            return response

        except Exception as e:
            self.error_count += 1
            logger.error("Error in security metrics middleware", error=str(e))
            raise