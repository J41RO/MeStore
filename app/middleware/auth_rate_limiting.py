# ~/app/middleware/auth_rate_limiting.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Enhanced Authentication Rate Limiting Middleware
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Archivo: auth_rate_limiting.py
# Ruta: ~/app/middleware/auth_rate_limiting.py
# Autor: API Architect AI
# Fecha de Creación: 2025-09-18
# Versión: 1.0.0
# Propósito: Enhanced rate limiting specifically for authentication endpoints
#
# Características:
# - Brute force attack prevention for login endpoints
# - Adaptive rate limiting based on failed attempts
# - IP-based and user-based rate limiting
# - Progressive penalties for repeated failures
# - Integration with existing Redis infrastructure
#
# ---------------------------------------------------------------------------------------------

"""
Enhanced authentication rate limiting middleware for FastAPI.

This module provides specialized rate limiting for authentication endpoints:
- Brute force attack prevention
- Progressive penalties for failed login attempts
- IP-based and credential-based rate limiting
- Integration with audit logging system
- Automatic blacklisting for suspicious activity
"""

import asyncio
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
from enum import Enum

import redis.asyncio as redis
from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logger import get_logger
from app.services.audit_logging_service import EnterpriseAuditLoggingService

logger = get_logger(__name__)


class AuthRateLimitType(str, Enum):
    """Authentication rate limit types."""
    LOGIN_ATTEMPTS = "login_attempts"
    PASSWORD_RESET = "password_reset"
    REGISTRATION = "registration"
    OTP_REQUESTS = "otp_requests"
    ADMIN_LOGIN = "admin_login"


class BruteForceLevel(str, Enum):
    """Brute force attack severity levels."""
    NORMAL = "normal"
    SUSPICIOUS = "suspicious"
    SEVERE = "severe"
    CRITICAL = "critical"


class AuthRateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Enhanced rate limiting middleware specifically for authentication endpoints.

    Features:
    - Progressive penalties for failed attempts
    - IP-based and credential-based tracking
    - Automatic blacklisting for suspicious activity
    - Integration with audit logging
    - Configurable limits per endpoint type
    """

    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client
        self.audit_service = EnterpriseAuditLoggingService()

        # Authentication endpoint rate limits (per hour unless specified)
        self.auth_limits = {
            AuthRateLimitType.LOGIN_ATTEMPTS: {
                "attempts_per_ip_per_hour": 10,
                "attempts_per_user_per_hour": 5,
                "lockout_duration_minutes": 15,
                "progressive_lockout": True
            },
            AuthRateLimitType.ADMIN_LOGIN: {
                "attempts_per_ip_per_hour": 3,
                "attempts_per_user_per_hour": 3,
                "lockout_duration_minutes": 30,
                "progressive_lockout": True
            },
            AuthRateLimitType.PASSWORD_RESET: {
                "attempts_per_ip_per_hour": 3,
                "attempts_per_user_per_hour": 2,
                "lockout_duration_minutes": 60,
                "progressive_lockout": False
            },
            AuthRateLimitType.REGISTRATION: {
                "attempts_per_ip_per_hour": 5,
                "attempts_per_user_per_hour": 1,
                "lockout_duration_minutes": 120,
                "progressive_lockout": False
            },
            AuthRateLimitType.OTP_REQUESTS: {
                "attempts_per_ip_per_hour": 10,
                "attempts_per_user_per_hour": 5,
                "lockout_duration_minutes": 10,
                "progressive_lockout": True
            }
        }

        # Progressive penalty multipliers
        self.penalty_multipliers = {
            1: 1,    # First violation: base penalty
            2: 2,    # Second violation: 2x penalty
            3: 4,    # Third violation: 4x penalty
            4: 8,    # Fourth violation: 8x penalty
            5: 24,   # Fifth+ violation: 24x penalty (max)
        }

        # Authentication endpoint patterns
        self.auth_endpoints = {
            "/api/v1/auth/login": AuthRateLimitType.LOGIN_ATTEMPTS,
            "/api/v1/auth/admin-login": AuthRateLimitType.ADMIN_LOGIN,
            "/api/v1/auth/forgot-password": AuthRateLimitType.PASSWORD_RESET,
            "/api/v1/auth/reset-password": AuthRateLimitType.PASSWORD_RESET,
            "/api/v1/auth/register": AuthRateLimitType.REGISTRATION,
            "/api/v1/otp/send": AuthRateLimitType.OTP_REQUESTS,
            "/api/v1/otp/verify": AuthRateLimitType.OTP_REQUESTS,
        }

    async def dispatch(self, request: Request, call_next):
        """Process request with enhanced authentication rate limiting."""
        try:
            # Check if this is an authentication endpoint
            auth_type = self._get_auth_endpoint_type(request)
            if not auth_type:
                return await call_next(request)

            # Get client information
            client_ip = self._get_client_ip(request)
            user_identifier = await self._extract_user_identifier(request)

            # Check for existing blacklist
            if await self._is_blacklisted(client_ip):
                return self._create_blacklist_response(client_ip)

            # Check rate limits
            is_allowed, rate_limit_info = await self._check_auth_rate_limits(
                client_ip, user_identifier, auth_type
            )

            if not is_allowed:
                await self._log_rate_limit_violation(
                    client_ip, user_identifier, auth_type, rate_limit_info
                )
                return self._create_rate_limit_response(rate_limit_info)

            # Process the request
            response = await call_next(request)

            # Check if authentication failed and update failure tracking
            if response.status_code in [401, 403]:
                await self._track_authentication_failure(
                    client_ip, user_identifier, auth_type
                )

            # Add rate limit headers
            self._add_auth_rate_limit_headers(response, rate_limit_info)

            return response

        except Exception as e:
            logger.error(f"Auth rate limiting error: {e}")
            # Log the error but don't block legitimate requests
            await self.audit_service.log_security_event(
                event_type="auth_rate_limit_error",
                details={"error": str(e), "endpoint": str(request.url)},
                severity="medium",
                ip_address=self._get_client_ip(request)
            )
            return await call_next(request)

    def _get_auth_endpoint_type(self, request: Request) -> Optional[AuthRateLimitType]:
        """Determine if this is an authentication endpoint and get its type."""
        path = str(request.url.path)
        return self.auth_endpoints.get(path)

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address with proxy support."""
        # Check for forwarded headers (proxy/load balancer)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        return str(request.client.host) if request.client else "unknown"

    async def _extract_user_identifier(self, request: Request) -> Optional[str]:
        """Extract user identifier from request body (email/username)."""
        try:
            # Only extract for POST requests with JSON body
            if request.method != "POST":
                return None

            # Try to read the request body
            body = await request.body()
            if not body:
                return None

            # Parse JSON to extract email or username
            try:
                data = json.loads(body)
                return data.get("email") or data.get("username")
            except json.JSONDecodeError:
                return None

        except Exception:
            return None

    async def _check_auth_rate_limits(
        self,
        client_ip: str,
        user_identifier: Optional[str],
        auth_type: AuthRateLimitType
    ) -> Tuple[bool, Dict]:
        """Check authentication rate limits for both IP and user."""
        limits = self.auth_limits[auth_type]
        current_time = datetime.now(timezone.utc)

        # Check IP-based rate limits
        ip_allowed, ip_info = await self._check_ip_auth_limits(
            client_ip, auth_type, limits, current_time
        )

        # Check user-based rate limits if user identifier is available
        user_allowed, user_info = True, {}
        if user_identifier:
            user_allowed, user_info = await self._check_user_auth_limits(
                user_identifier, auth_type, limits, current_time
            )

        # Return the most restrictive result
        if not ip_allowed:
            return False, ip_info
        elif not user_allowed:
            return False, user_info
        else:
            # Both allowed, return the more restrictive info
            return True, ip_info if ip_info.get("remaining", 999) < user_info.get("remaining", 999) else user_info

    async def _check_ip_auth_limits(
        self,
        client_ip: str,
        auth_type: AuthRateLimitType,
        limits: Dict,
        current_time: datetime
    ) -> Tuple[bool, Dict]:
        """Check IP-based authentication rate limits."""
        try:
            # Get current failure count and violation history
            failure_key = f"auth_failures:ip:{client_ip}:{auth_type.value}"
            violation_key = f"auth_violations:ip:{client_ip}:{auth_type.value}"

            current_failures = await self._get_current_failures(failure_key, current_time)
            violation_count = await self._get_violation_count(violation_key)

            # Calculate progressive penalty
            base_lockout = limits["lockout_duration_minutes"]
            if limits["progressive_lockout"]:
                penalty_multiplier = self.penalty_multipliers.get(min(violation_count, 5), 24)
                actual_lockout = base_lockout * penalty_multiplier
            else:
                actual_lockout = base_lockout

            # Check if currently in lockout period
            lockout_key = f"auth_lockout:ip:{client_ip}:{auth_type.value}"
            lockout_until = await self._get_lockout_expiry(lockout_key)

            if lockout_until and current_time < lockout_until:
                return False, {
                    "type": "ip_lockout",
                    "ip": client_ip,
                    "lockout_until": lockout_until.isoformat(),
                    "retry_after": int((lockout_until - current_time).total_seconds()),
                    "violation_count": violation_count
                }

            # Check if current failures exceed limit
            max_failures = limits["attempts_per_ip_per_hour"]
            if current_failures >= max_failures:
                # Trigger lockout
                lockout_until = current_time + timedelta(minutes=actual_lockout)
                await self._set_lockout(lockout_key, lockout_until)
                await self._increment_violation_count(violation_key)

                return False, {
                    "type": "ip_rate_limit",
                    "ip": client_ip,
                    "failures": current_failures,
                    "max_failures": max_failures,
                    "lockout_until": lockout_until.isoformat(),
                    "retry_after": int(actual_lockout * 60),
                    "violation_count": violation_count + 1
                }

            return True, {
                "type": "ip_allowed",
                "ip": client_ip,
                "failures": current_failures,
                "remaining": max_failures - current_failures,
                "reset_time": (current_time + timedelta(hours=1)).isoformat()
            }

        except Exception as e:
            logger.error(f"Error checking IP auth limits: {e}")
            # Fail safe - allow with conservative limits
            return True, {"type": "error_fallback", "remaining": 1}

    async def _check_user_auth_limits(
        self,
        user_identifier: str,
        auth_type: AuthRateLimitType,
        limits: Dict,
        current_time: datetime
    ) -> Tuple[bool, Dict]:
        """Check user-based authentication rate limits."""
        try:
            # Similar to IP checking but for user identifier
            failure_key = f"auth_failures:user:{user_identifier}:{auth_type.value}"
            violation_key = f"auth_violations:user:{user_identifier}:{auth_type.value}"

            current_failures = await self._get_current_failures(failure_key, current_time)
            violation_count = await self._get_violation_count(violation_key)

            # Calculate progressive penalty
            base_lockout = limits["lockout_duration_minutes"]
            if limits["progressive_lockout"]:
                penalty_multiplier = self.penalty_multipliers.get(min(violation_count, 5), 24)
                actual_lockout = base_lockout * penalty_multiplier
            else:
                actual_lockout = base_lockout

            # Check if currently in lockout period
            lockout_key = f"auth_lockout:user:{user_identifier}:{auth_type.value}"
            lockout_until = await self._get_lockout_expiry(lockout_key)

            if lockout_until and current_time < lockout_until:
                return False, {
                    "type": "user_lockout",
                    "user": user_identifier,
                    "lockout_until": lockout_until.isoformat(),
                    "retry_after": int((lockout_until - current_time).total_seconds()),
                    "violation_count": violation_count
                }

            # Check if current failures exceed limit
            max_failures = limits["attempts_per_user_per_hour"]
            if current_failures >= max_failures:
                # Trigger lockout
                lockout_until = current_time + timedelta(minutes=actual_lockout)
                await self._set_lockout(lockout_key, lockout_until)
                await self._increment_violation_count(violation_key)

                return False, {
                    "type": "user_rate_limit",
                    "user": user_identifier,
                    "failures": current_failures,
                    "max_failures": max_failures,
                    "lockout_until": lockout_until.isoformat(),
                    "retry_after": int(actual_lockout * 60),
                    "violation_count": violation_count + 1
                }

            return True, {
                "type": "user_allowed",
                "user": user_identifier,
                "failures": current_failures,
                "remaining": max_failures - current_failures,
                "reset_time": (current_time + timedelta(hours=1)).isoformat()
            }

        except Exception as e:
            logger.error(f"Error checking user auth limits: {e}")
            # Fail safe - allow with conservative limits
            return True, {"type": "error_fallback", "remaining": 1}

    async def _get_current_failures(self, key: str, current_time: datetime) -> int:
        """Get current failure count within the time window."""
        if not self.redis_client:
            return 0

        try:
            # Use sliding window of 1 hour
            window_start = current_time - timedelta(hours=1)

            # Remove expired entries
            await self.redis_client.zremrangebyscore(
                key,
                0,
                window_start.timestamp()
            )

            # Count current entries
            return await self.redis_client.zcard(key)

        except Exception as e:
            logger.error(f"Error getting current failures: {e}")
            return 0

    async def _get_violation_count(self, key: str) -> int:
        """Get total violation count for progressive penalties."""
        if not self.redis_client:
            return 0

        try:
            count = await self.redis_client.get(key)
            return int(count) if count else 0
        except Exception:
            return 0

    async def _get_lockout_expiry(self, key: str) -> Optional[datetime]:
        """Get lockout expiry time."""
        if not self.redis_client:
            return None

        try:
            timestamp = await self.redis_client.get(key)
            if timestamp:
                return datetime.fromtimestamp(float(timestamp), tz=timezone.utc)
            return None
        except Exception:
            return None

    async def _set_lockout(self, key: str, until: datetime):
        """Set lockout period."""
        if not self.redis_client:
            return

        try:
            # Set lockout with expiry
            duration_seconds = int((until - datetime.now(timezone.utc)).total_seconds())
            await self.redis_client.setex(
                key,
                duration_seconds,
                until.timestamp()
            )
        except Exception as e:
            logger.error(f"Error setting lockout: {e}")

    async def _increment_violation_count(self, key: str):
        """Increment violation count for progressive penalties."""
        if not self.redis_client:
            return

        try:
            # Increment and set expiry of 24 hours
            await self.redis_client.incr(key)
            await self.redis_client.expire(key, 86400)
        except Exception as e:
            logger.error(f"Error incrementing violation count: {e}")

    async def _track_authentication_failure(
        self,
        client_ip: str,
        user_identifier: Optional[str],
        auth_type: AuthRateLimitType
    ):
        """Track authentication failure for rate limiting."""
        if not self.redis_client:
            return

        try:
            current_time = datetime.now(timezone.utc)
            timestamp = current_time.timestamp()

            # Track IP-based failure
            ip_key = f"auth_failures:ip:{client_ip}:{auth_type.value}"
            await self.redis_client.zadd(ip_key, {str(timestamp): timestamp})
            await self.redis_client.expire(ip_key, 3600)  # 1 hour expiry

            # Track user-based failure if available
            if user_identifier:
                user_key = f"auth_failures:user:{user_identifier}:{auth_type.value}"
                await self.redis_client.zadd(user_key, {str(timestamp): timestamp})
                await self.redis_client.expire(user_key, 3600)  # 1 hour expiry

            # Log security event
            await self.audit_service.log_security_event(
                event_type="authentication_failure",
                details={
                    "auth_type": auth_type.value,
                    "ip": client_ip,
                    "user": user_identifier,
                    "timestamp": current_time.isoformat()
                },
                severity="medium",
                ip_address=client_ip,
                user_id=user_identifier
            )

        except Exception as e:
            logger.error(f"Error tracking authentication failure: {e}")

    async def _is_blacklisted(self, client_ip: str) -> bool:
        """Check if IP is in the blacklist."""
        if not self.redis_client:
            return False

        try:
            blacklist_key = f"auth_blacklist:ip:{client_ip}"
            return await self.redis_client.exists(blacklist_key)
        except Exception:
            return False

    async def _log_rate_limit_violation(
        self,
        client_ip: str,
        user_identifier: Optional[str],
        auth_type: AuthRateLimitType,
        rate_limit_info: Dict
    ):
        """Log rate limit violation for security monitoring."""
        try:
            await self.audit_service.log_security_event(
                event_type="auth_rate_limit_exceeded",
                details={
                    "auth_type": auth_type.value,
                    "ip": client_ip,
                    "user": user_identifier,
                    "rate_limit_info": rate_limit_info
                },
                severity="high",
                ip_address=client_ip,
                user_id=user_identifier
            )

            # Auto-blacklist for severe violations
            violation_count = rate_limit_info.get("violation_count", 0)
            if violation_count >= 5:  # 5+ violations = auto blacklist
                await self._auto_blacklist_ip(client_ip, violation_count)

        except Exception as e:
            logger.error(f"Error logging rate limit violation: {e}")

    async def _auto_blacklist_ip(self, client_ip: str, violation_count: int):
        """Automatically blacklist IP for severe violations."""
        if not self.redis_client:
            return

        try:
            blacklist_key = f"auth_blacklist:ip:{client_ip}"
            blacklist_duration = 86400 * min(violation_count, 7)  # 1-7 days based on violations

            await self.redis_client.setex(
                blacklist_key,
                blacklist_duration,
                json.dumps({
                    "blacklisted_at": datetime.now(timezone.utc).isoformat(),
                    "violation_count": violation_count,
                    "duration_seconds": blacklist_duration,
                    "reason": "excessive_auth_failures"
                })
            )

            await self.audit_service.log_security_event(
                event_type="ip_auto_blacklisted",
                details={
                    "ip": client_ip,
                    "violation_count": violation_count,
                    "duration_days": blacklist_duration // 86400
                },
                severity="critical",
                ip_address=client_ip
            )

            logger.warning(f"Auto-blacklisted IP {client_ip} for {blacklist_duration//86400} days due to {violation_count} violations")

        except Exception as e:
            logger.error(f"Error auto-blacklisting IP: {e}")

    def _create_rate_limit_response(self, rate_limit_info: Dict) -> Response:
        """Create rate limit exceeded response."""
        retry_after = rate_limit_info.get("retry_after", 900)  # Default 15 minutes

        headers = {
            "X-Auth-RateLimit-Type": rate_limit_info.get("type", "unknown"),
            "X-Auth-RateLimit-Retry-After": str(retry_after),
            "Retry-After": str(retry_after)
        }

        # Add specific headers based on limit type
        if "lockout_until" in rate_limit_info:
            headers["X-Auth-Lockout-Until"] = rate_limit_info["lockout_until"]

        if "violation_count" in rate_limit_info:
            headers["X-Auth-Violation-Count"] = str(rate_limit_info["violation_count"])

        content = {
            "error": {
                "type": "AuthRateLimitExceeded",
                "code": "AUTH_RATE_LIMIT_EXCEEDED",
                "message": "Authentication rate limit exceeded. Please try again later.",
                "details": {
                    "limit_type": rate_limit_info.get("type"),
                    "retry_after_seconds": retry_after,
                    "lockout_until": rate_limit_info.get("lockout_until")
                }
            }
        }

        return Response(
            content=json.dumps(content),
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            headers=headers,
            media_type="application/json"
        )

    def _create_blacklist_response(self, client_ip: str) -> Response:
        """Create blacklist response."""
        content = {
            "error": {
                "type": "IPBlacklisted",
                "code": "IP_BLACKLISTED",
                "message": "Your IP address has been temporarily blocked due to suspicious activity.",
                "details": {
                    "ip": client_ip,
                    "contact": "Please contact support if you believe this is an error."
                }
            }
        }

        return Response(
            content=json.dumps(content),
            status_code=status.HTTP_403_FORBIDDEN,
            headers={"X-Blacklist-Status": "blocked"},
            media_type="application/json"
        )

    def _add_auth_rate_limit_headers(self, response: Response, rate_limit_info: Dict):
        """Add authentication rate limit headers to response."""
        if rate_limit_info.get("remaining") is not None:
            response.headers["X-Auth-RateLimit-Remaining"] = str(rate_limit_info["remaining"])

        if rate_limit_info.get("reset_time"):
            response.headers["X-Auth-RateLimit-Reset"] = rate_limit_info["reset_time"]

        response.headers["X-Auth-RateLimit-Type"] = rate_limit_info.get("type", "unknown")


# Utility function to create auth rate limiting middleware
async def create_auth_rate_limiting_middleware(app, redis_url: Optional[str] = None):
    """Create authentication rate limiting middleware with Redis backend."""
    redis_client = None

    if redis_url:
        try:
            redis_client = redis.from_url(redis_url)
            # Test connection
            await redis_client.ping()
            logger.info("Auth rate limiting middleware connected to Redis")
        except Exception as e:
            logger.warning(f"Redis connection failed for auth rate limiting, using fallback: {e}")
            redis_client = None

    return AuthRateLimitingMiddleware(app, redis_client)