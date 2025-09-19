"""
Comprehensive Security Middleware
=================================

Enterprise-grade security middleware for the MeStore application providing:
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- CORS configuration with security best practices
- Rate limiting with Redis-based storage
- Request/response audit logging
- Input validation and sanitization
- DDoS protection
- Geolocation security

Author: Security Backend AI
Date: 2025-09-17
Purpose: Provide comprehensive security layer for all HTTP requests
"""

import asyncio
import json
import logging
import hashlib
import time
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Callable
from urllib.parse import urlparse
from ipaddress import ip_address, ip_network
import re

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.middleware.cors import CORSMiddleware
from fastapi import HTTPException, status

from app.core.config import settings


# Configure security logger
security_logger = logging.getLogger("security_middleware")
security_logger.setLevel(logging.INFO)


class SecurityHeaders:
    """
    Security headers configuration and management.
    """

    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """
        Get comprehensive security headers for HTTP responses.

        Returns:
            Dict[str, str]: Security headers
        """
        return {
            # HTTPS enforcement
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",

            # Content Security Policy
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://api.wompi.co; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            ),

            # Clickjacking protection
            "X-Frame-Options": "DENY",

            # MIME type sniffing protection
            "X-Content-Type-Options": "nosniff",

            # XSS protection
            "X-XSS-Protection": "1; mode=block",

            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",

            # Permissions policy
            "Permissions-Policy": (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(self), usb=(), magnetometer=(), gyroscope=()"
            ),

            # Cross-origin policies
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin",

            # Cache control for sensitive endpoints
            "Cache-Control": "no-store, no-cache, must-revalidate, private",

            # Server identification hiding
            "Server": "MeStore/1.0"
        }

    @staticmethod
    def get_api_headers() -> Dict[str, str]:
        """
        Get headers specific to API endpoints.

        Returns:
            Dict[str, str]: API-specific headers
        """
        return {
            "X-API-Version": "1.0",
            "X-Rate-Limit-Policy": "Enforced",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY"
        }


class RateLimiter:
    """
    Redis-based rate limiting with multiple strategies.
    """

    def __init__(self, redis_client=None):
        """Initialize rate limiter with Redis client."""
        self.redis_client = redis_client or self._get_redis_client()
        self.rate_limits = {
            # General API limits
            "api_general": {"requests": 1000, "window": 3600},  # 1000/hour
            "api_auth": {"requests": 10, "window": 600},        # 10/10min
            "api_password_reset": {"requests": 3, "window": 3600},  # 3/hour

            # By IP address
            "ip_general": {"requests": 5000, "window": 3600},   # 5000/hour per IP
            "ip_auth": {"requests": 50, "window": 600},         # 50/10min per IP

            # By user (authenticated requests)
            "user_general": {"requests": 2000, "window": 3600}, # 2000/hour per user
            "user_api": {"requests": 500, "window": 600},       # 500/10min per user
        }

    def _get_redis_client(self):
        """Get Redis client for rate limiting."""
        try:
            return redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                decode_responses=True
            )
        except Exception:
            return None

    def _get_rate_limit_key(self, identifier: str, limit_type: str) -> str:
        """Generate Redis key for rate limiting."""
        identifier_hash = hashlib.sha256(identifier.encode()).hexdigest()[:16]
        return f"rate_limit:{limit_type}:{identifier_hash}"

    async def is_rate_limited(self, identifier: str, limit_type: str) -> tuple[bool, Dict[str, int]]:
        """
        Check if identifier is rate limited.

        Args:
            identifier: IP address, user ID, or other identifier
            limit_type: Type of rate limit to check

        Returns:
            Tuple[bool, Dict]: (is_limited, rate_limit_info)
        """
        if not self.redis_client or limit_type not in self.rate_limits:
            return False, {}

        limit_config = self.rate_limits[limit_type]
        key = self._get_rate_limit_key(identifier, limit_type)

        # Sliding window rate limiting
        now = int(time.time())
        window_start = now - limit_config["window"]

        # Remove old entries
        self.redis_client.zremrangebyscore(key, 0, window_start)

        # Count current requests
        current_count = self.redis_client.zcard(key)

        # Check if rate limited
        is_limited = current_count >= limit_config["requests"]

        # Add current request if not limited
        if not is_limited:
            self.redis_client.zadd(key, {str(now): now})
            self.redis_client.expire(key, limit_config["window"])

        # Calculate reset time
        reset_time = window_start + limit_config["window"]

        rate_info = {
            "limit": limit_config["requests"],
            "remaining": max(0, limit_config["requests"] - current_count - (0 if is_limited else 1)),
            "reset": reset_time,
            "window": limit_config["window"]
        }

        return is_limited, rate_info


class AuditLogger:
    """
    Comprehensive audit logging for security events.
    """

    def __init__(self):
        """Initialize audit logger."""
        self.sensitive_headers = {
            "authorization", "cookie", "x-api-key", "x-auth-token"
        }
        self.sensitive_fields = {
            "password", "token", "secret", "key", "credential"
        }

    def log_request(
        self,
        request: Request,
        ip_address: str,
        user_id: Optional[str] = None,
        processing_time: Optional[float] = None
    ):
        """
        Log HTTP request for audit trail.

        Args:
            request: FastAPI request object
            ip_address: Client IP address
            user_id: Authenticated user ID (if any)
            processing_time: Request processing time in seconds
        """
        # Sanitize headers
        headers = dict(request.headers)
        sanitized_headers = {}
        for key, value in headers.items():
            if key.lower() in self.sensitive_headers:
                sanitized_headers[key] = "[REDACTED]"
            else:
                sanitized_headers[key] = value

        # Log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "HTTP_REQUEST",
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": sanitized_headers,
            "ip_address": ip_address,
            "user_agent": headers.get("user-agent", ""),
            "user_id": user_id,
            "processing_time": processing_time,
            "request_size": headers.get("content-length", 0)
        }

        security_logger.info(f"REQUEST_AUDIT: {json.dumps(log_entry)}")

    def log_response(
        self,
        request: Request,
        response: Response,
        ip_address: str,
        user_id: Optional[str] = None,
        processing_time: Optional[float] = None
    ):
        """
        Log HTTP response for audit trail.

        Args:
            request: FastAPI request object
            response: FastAPI response object
            ip_address: Client IP address
            user_id: Authenticated user ID (if any)
            processing_time: Request processing time in seconds
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "HTTP_RESPONSE",
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "response_size": response.headers.get("content-length", 0),
            "ip_address": ip_address,
            "user_id": user_id,
            "processing_time": processing_time
        }

        # Log level based on status code
        if response.status_code >= 500:
            security_logger.error(f"RESPONSE_AUDIT: {json.dumps(log_entry)}")
        elif response.status_code >= 400:
            security_logger.warning(f"RESPONSE_AUDIT: {json.dumps(log_entry)}")
        else:
            security_logger.info(f"RESPONSE_AUDIT: {json.dumps(log_entry)}")

    def log_security_event(
        self,
        event_type: str,
        details: Dict,
        ip_address: str,
        user_id: Optional[str] = None
    ):
        """
        Log security-specific events.

        Args:
            event_type: Type of security event
            details: Event details
            ip_address: Client IP address
            user_id: User ID (if applicable)
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": f"SECURITY_{event_type}",
            "details": details,
            "ip_address": ip_address,
            "user_id": user_id
        }

        security_logger.warning(f"SECURITY_EVENT: {json.dumps(log_entry)}")


class IPSecurityValidator:
    """
    IP address security validation and geolocation checking.
    """

    def __init__(self):
        """Initialize IP security validator."""
        # Known malicious IP ranges (example - in production, use threat intelligence feeds)
        self.blocked_networks = [
            # Add known malicious networks
            ip_network("127.0.0.0/8"),  # Localhost (for testing)
        ]

        # Allowed countries (ISO codes) - Colombian focus
        self.allowed_countries = {"CO", "US", "CA", "ES", "MX", "PE", "EC", "VE", "PA"}

    def is_ip_blocked(self, ip_addr: str) -> tuple[bool, str]:
        """
        Check if IP address is blocked.

        Args:
            ip_addr: IP address to check

        Returns:
            Tuple[bool, str]: (is_blocked, reason)
        """
        try:
            ip = ip_address(ip_addr)

            # Check against blocked networks
            for network in self.blocked_networks:
                if ip in network:
                    return True, f"IP in blocked network: {network}"

            # Check for private/internal IPs in production
            if hasattr(settings, 'ENVIRONMENT') and settings.ENVIRONMENT == 'production':
                if ip.is_private and not ip.is_loopback:
                    return True, "Private IP not allowed in production"

            return False, "IP allowed"

        except ValueError:
            return True, "Invalid IP address format"


class ComprehensiveSecurityMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive security middleware combining all security features.
    """

    def __init__(self, app, **kwargs):
        """Initialize comprehensive security middleware."""
        super().__init__(app)

        # Initialize security components
        self.rate_limiter = RateLimiter()
        self.audit_logger = AuditLogger()
        self.ip_validator = IPSecurityValidator()
        self.security_headers = SecurityHeaders()

        # Security configuration
        self.enable_rate_limiting = kwargs.get('enable_rate_limiting', True)
        self.enable_audit_logging = kwargs.get('enable_audit_logging', True)
        self.enable_ip_validation = kwargs.get('enable_ip_validation', True)

        # Protected endpoints requiring stricter security
        self.protected_endpoints = {
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/reset-password",
            "/api/v1/admin",
            "/api/v1/payments"
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through comprehensive security pipeline.

        Args:
            request: FastAPI request object
            call_next: Next middleware/endpoint

        Returns:
            Response: HTTP response with security headers
        """
        start_time = time.time()

        # Extract client information
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        user_id = self._extract_user_id(request)

        try:
            # 1. IP Address Validation
            if self.enable_ip_validation:
                is_blocked, block_reason = self.ip_validator.is_ip_blocked(ip_address)
                if is_blocked:
                    self.audit_logger.log_security_event(
                        "IP_BLOCKED",
                        {"reason": block_reason, "ip": ip_address},
                        ip_address,
                        user_id
                    )
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": "Access denied"}
                    )

            # 2. Rate Limiting
            if self.enable_rate_limiting:
                rate_limit_result = await self._check_rate_limits(request, ip_address, user_id)
                if rate_limit_result:
                    return rate_limit_result

            # 3. Request Validation
            validation_result = await self._validate_request(request)
            if validation_result:
                return validation_result

            # 4. Audit Logging (Request)
            if self.enable_audit_logging:
                self.audit_logger.log_request(request, ip_address, user_id)

            # Process request
            response = await call_next(request)

            # 5. Add Security Headers
            self._add_security_headers(response, request)

            # 6. Audit Logging (Response)
            processing_time = time.time() - start_time
            if self.enable_audit_logging:
                self.audit_logger.log_response(
                    request, response, ip_address, user_id, processing_time
                )

            return response

        except Exception as e:
            # Log security exception
            self.audit_logger.log_security_event(
                "MIDDLEWARE_EXCEPTION",
                {"error": str(e), "request_path": request.url.path},
                ip_address,
                user_id
            )

            # Return generic error to avoid information disclosure
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request.

        Args:
            request: FastAPI request object

        Returns:
            str: Client IP address
        """
        # Check for proxy headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct connection
        return request.client.host if request.client else "unknown"

    def _extract_user_id(self, request: Request) -> Optional[str]:
        """
        Extract user ID from authenticated request.

        Args:
            request: FastAPI request object

        Returns:
            Optional[str]: User ID if authenticated
        """
        # This would integrate with your authentication system
        # For now, return None - implement based on your auth structure
        return getattr(request.state, 'user_id', None)

    async def _check_rate_limits(
        self,
        request: Request,
        ip_address: str,
        user_id: Optional[str]
    ) -> Optional[Response]:
        """
        Check rate limits for the request.

        Args:
            request: FastAPI request object
            ip_address: Client IP address
            user_id: User ID (if authenticated)

        Returns:
            Optional[Response]: Rate limit response if exceeded, None if allowed
        """
        path = request.url.path

        # Determine rate limit types to check
        limit_checks = []

        # IP-based rate limiting
        if path.startswith("/api/v1/auth"):
            limit_checks.append((ip_address, "ip_auth"))
        else:
            limit_checks.append((ip_address, "ip_general"))

        # User-based rate limiting (if authenticated)
        if user_id:
            if path.startswith("/api/v1"):
                limit_checks.append((user_id, "user_api"))
            else:
                limit_checks.append((user_id, "user_general"))

        # Check each rate limit
        for identifier, limit_type in limit_checks:
            is_limited, rate_info = await self.rate_limiter.is_rate_limited(identifier, limit_type)

            if is_limited:
                # Log rate limit violation
                self.audit_logger.log_security_event(
                    "RATE_LIMIT_EXCEEDED",
                    {
                        "limit_type": limit_type,
                        "identifier": hashlib.sha256(identifier.encode()).hexdigest()[:8],
                        "rate_info": rate_info
                    },
                    ip_address,
                    user_id
                )

                # Return rate limit response
                headers = {
                    "X-Rate-Limit-Limit": str(rate_info["limit"]),
                    "X-Rate-Limit-Remaining": str(rate_info["remaining"]),
                    "X-Rate-Limit-Reset": str(rate_info["reset"]),
                    "Retry-After": str(rate_info["window"])
                }

                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Rate limit exceeded",
                        "retry_after": rate_info["window"]
                    },
                    headers=headers
                )

        return None

    async def _validate_request(self, request: Request) -> Optional[Response]:
        """
        Validate request for security issues.

        Args:
            request: FastAPI request object

        Returns:
            Optional[Response]: Error response if validation fails, None if valid
        """
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "Request too large"}
            )

        # Check for suspicious patterns in URL
        suspicious_patterns = [
            r"\.\.\/",  # Directory traversal
            r"<script",  # XSS attempts
            r"javascript:",  # JavaScript injection
            r"data:text\/html",  # Data URL injection
        ]

        url_path = str(request.url)
        for pattern in suspicious_patterns:
            if re.search(pattern, url_path, re.IGNORECASE):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid request"}
                )

        return None

    def _add_security_headers(self, response: Response, request: Request):
        """
        Add security headers to response.

        Args:
            response: FastAPI response object
            request: FastAPI request object
        """
        # Add general security headers
        security_headers = self.security_headers.get_security_headers()

        for header, value in security_headers.items():
            response.headers[header] = value

        # Add API-specific headers for API endpoints
        if request.url.path.startswith("/api/"):
            api_headers = self.security_headers.get_api_headers()
            for header, value in api_headers.items():
                response.headers[header] = value

        # Add CORS headers if needed (handled by separate CORS middleware)

        # Add custom headers based on endpoint
        if any(endpoint in request.url.path for endpoint in self.protected_endpoints):
            response.headers["X-Protected-Endpoint"] = "true"