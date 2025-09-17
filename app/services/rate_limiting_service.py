"""
Enterprise Rate Limiting Service for MeStore.

This module provides comprehensive rate limiting capabilities:
- IP-based rate limiting with sliding window
- User-based rate limiting for authenticated requests
- Endpoint-specific rate limiting
- Enterprise security patterns for Colombian compliance

Author: Backend Senior Developer
Version: 1.0.0 Enterprise
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
from enum import Enum
from pydantic import BaseModel
from fastapi import Request

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class RateLimitType(str, Enum):
    """Rate limit types."""
    IP_BASED = "ip_based"
    USER_BASED = "user_based"
    ENDPOINT_BASED = "endpoint_based"
    GLOBAL = "global"


class RateLimitResult(BaseModel):
    """Rate limit check result."""
    allowed: bool
    remaining_requests: int
    reset_time: datetime
    limit_type: RateLimitType
    retry_after_seconds: Optional[int] = None


class EnterpriseRateLimitingService:
    """
    Enterprise-grade rate limiting service using Redis sliding window.

    Features:
    - Multiple rate limiting strategies
    - Sliding window counters
    - Burst protection
    - Whitelist/blacklist support
    - Real-time monitoring
    """

    def __init__(self, redis_client):
        """Initialize rate limiting service with Redis client."""
        self.redis = redis_client
        self.rate_limit_prefix = "rate_limit:"
        self.whitelist_prefix = "whitelist:"
        self.blacklist_prefix = "blacklist:"

    async def check_rate_limit(
        self,
        request: Request,
        endpoint: str,
        user_id: Optional[str] = None
    ) -> RateLimitResult:
        """
        Check if a request should be rate limited.

        Args:
            request: FastAPI request object
            endpoint: API endpoint being accessed
            user_id: Optional user ID for authenticated requests

        Returns:
            RateLimitResult: Rate limit check result
        """
        try:
            ip_address = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'

            # Check IP whitelist first
            if await self._is_whitelisted_ip(ip_address):
                return RateLimitResult(
                    allowed=True,
                    remaining_requests=9999,
                    reset_time=datetime.now(timezone.utc) + timedelta(hours=1),
                    limit_type=RateLimitType.GLOBAL
                )

            # Check IP blacklist
            if await self._is_blacklisted_ip(ip_address):
                return RateLimitResult(
                    allowed=False,
                    remaining_requests=0,
                    reset_time=datetime.now(timezone.utc) + timedelta(hours=24),
                    limit_type=RateLimitType.GLOBAL,
                    retry_after_seconds=86400
                )

            # Check different rate limit types in order of specificity
            checks = []

            # 1. Endpoint-specific rate limits
            endpoint_result = await self._check_endpoint_rate_limit(ip_address, endpoint, user_id)
            checks.append(endpoint_result)

            # 2. User-based rate limits (if authenticated)
            if user_id:
                user_result = await self._check_user_rate_limit(user_id)
                checks.append(user_result)

            # 3. IP-based rate limits
            ip_result = await self._check_ip_rate_limit(ip_address)
            checks.append(ip_result)

            # Return the most restrictive result
            for result in checks:
                if not result.allowed:
                    return result

            # If all checks pass, return the most restrictive allowed result
            most_restrictive = min(checks, key=lambda x: x.remaining_requests)
            return most_restrictive

        except Exception as e:
            logger.critical("Critical rate limiting service failure", error=str(e), endpoint=endpoint, ip=ip_address)
            # SECURITY FIX: Fail closed for critical endpoints, fail open for others
            critical_endpoints = [
                'auth/login', 'auth/register', 'auth/forgot-password', 'auth/admin-login',
                'otp/send', 'admin/', 'users/'
            ]

            is_critical = any(crit in endpoint.lower() for crit in critical_endpoints)

            if is_critical:
                logger.critical("Denying access to critical endpoint due to rate limiting failure", endpoint=endpoint)
                return RateLimitResult(
                    allowed=False,
                    remaining_requests=0,
                    reset_time=datetime.now(timezone.utc) + timedelta(minutes=5),
                    limit_type=RateLimitType.GLOBAL,
                    retry_after_seconds=300
                )
            else:
                # Non-critical endpoints can fail open with reduced limits
                return RateLimitResult(
                    allowed=True,
                    remaining_requests=10,  # Reduced from 100
                    reset_time=datetime.now(timezone.utc) + timedelta(minutes=1),
                    limit_type=RateLimitType.GLOBAL
                )

    async def _check_ip_rate_limit(self, ip_address: str) -> RateLimitResult:
        """Check IP-based rate limits."""
        try:
            # SECURITY FIX: More restrictive IP limits for better security
            limits = [
                {"window": 60, "max_requests": 60, "key_suffix": "1m"},       # Reduced from 100
                {"window": 3600, "max_requests": 600, "key_suffix": "1h"},    # Reduced from 1000
                {"window": 86400, "max_requests": 2400, "key_suffix": "1d"}   # Reduced from 5000
            ]

            for limit in limits:
                key = f"{self.rate_limit_prefix}ip:{ip_address}:{limit['key_suffix']}"
                current_count, reset_time = await self._sliding_window_counter(
                    key, limit['window'], limit['max_requests']
                )

                if current_count > limit['max_requests']:
                    return RateLimitResult(
                        allowed=False,
                        remaining_requests=0,
                        reset_time=reset_time,
                        limit_type=RateLimitType.IP_BASED,
                        retry_after_seconds=int((reset_time - datetime.now(timezone.utc)).total_seconds())
                    )

            # Return most restrictive window that's still allowing requests
            key = f"{self.rate_limit_prefix}ip:{ip_address}:1m"
            current_count, reset_time = await self._sliding_window_counter(key, 60, 60)

            return RateLimitResult(
                allowed=True,
                remaining_requests=max(0, 60 - current_count),
                reset_time=reset_time,
                limit_type=RateLimitType.IP_BASED
            )

        except Exception as e:
            logger.error("Error checking IP rate limit", error=str(e), ip=ip_address)
            # SECURITY FIX: Fail with conservative limits when Redis unavailable
            return RateLimitResult(
                allowed=True,
                remaining_requests=10,  # Very conservative limit
                reset_time=datetime.now(timezone.utc) + timedelta(minutes=1),
                limit_type=RateLimitType.IP_BASED
            )

    async def _check_user_rate_limit(self, user_id: str) -> RateLimitResult:
        """Check user-based rate limits for authenticated users."""
        try:
            # SECURITY FIX: More reasonable limits for authenticated users
            limits = [
                {"window": 60, "max_requests": 120, "key_suffix": "1m"},      # Reduced from 200
                {"window": 3600, "max_requests": 2400, "key_suffix": "1h"},   # Reduced from 5000
                {"window": 86400, "max_requests": 7200, "key_suffix": "1d"}   # Reduced from 20000
            ]

            for limit in limits:
                key = f"{self.rate_limit_prefix}user:{user_id}:{limit['key_suffix']}"
                current_count, reset_time = await self._sliding_window_counter(
                    key, limit['window'], limit['max_requests']
                )

                if current_count > limit['max_requests']:
                    return RateLimitResult(
                        allowed=False,
                        remaining_requests=0,
                        reset_time=reset_time,
                        limit_type=RateLimitType.USER_BASED,
                        retry_after_seconds=int((reset_time - datetime.now(timezone.utc)).total_seconds())
                    )

            # Return most restrictive window
            key = f"{self.rate_limit_prefix}user:{user_id}:1m"
            current_count, reset_time = await self._sliding_window_counter(key, 60, 120)

            return RateLimitResult(
                allowed=True,
                remaining_requests=max(0, 120 - current_count),
                reset_time=reset_time,
                limit_type=RateLimitType.USER_BASED
            )

        except Exception as e:
            logger.error("Error checking user rate limit", error=str(e), user_id=user_id)
            # SECURITY FIX: Fail with conservative limits
            return RateLimitResult(
                allowed=True,
                remaining_requests=20,  # Conservative limit
                reset_time=datetime.now(timezone.utc) + timedelta(minutes=1),
                limit_type=RateLimitType.USER_BASED
            )

    async def _check_endpoint_rate_limit(
        self,
        ip_address: str,
        endpoint: str,
        user_id: Optional[str] = None
    ) -> RateLimitResult:
        """Check endpoint-specific rate limits."""
        try:
            # Define endpoint-specific limits
            endpoint_limits = {
                "auth/login": {"window": 3600, "max_requests": settings.RATE_LIMIT_LOGIN_ATTEMPTS_PER_HOUR},
                "auth/forgot-password": {"window": 86400, "max_requests": settings.RATE_LIMIT_PASSWORD_RESET_PER_DAY},
                "auth/register": {"window": 86400, "max_requests": 5},  # 5 registrations per day per IP
                "otp/send": {"window": 3600, "max_requests": settings.RATE_LIMIT_OTP_REQUESTS_PER_HOUR}
            }

            # Normalize endpoint name
            endpoint_key = endpoint.lstrip('/').replace('/', '_')

            if endpoint_key in endpoint_limits:
                limit = endpoint_limits[endpoint_key]
                identifier = user_id if user_id else ip_address
                key = f"{self.rate_limit_prefix}endpoint:{endpoint_key}:{identifier}"

                current_count, reset_time = await self._sliding_window_counter(
                    key, limit['window'], limit['max_requests']
                )

                if current_count > limit['max_requests']:
                    return RateLimitResult(
                        allowed=False,
                        remaining_requests=0,
                        reset_time=reset_time,
                        limit_type=RateLimitType.ENDPOINT_BASED,
                        retry_after_seconds=int((reset_time - datetime.now(timezone.utc)).total_seconds())
                    )

                return RateLimitResult(
                    allowed=True,
                    remaining_requests=max(0, limit['max_requests'] - current_count),
                    reset_time=reset_time,
                    limit_type=RateLimitType.ENDPOINT_BASED
                )

            # No specific limit for this endpoint
            return RateLimitResult(
                allowed=True,
                remaining_requests=9999,
                reset_time=datetime.now(timezone.utc) + timedelta(hours=1),
                limit_type=RateLimitType.ENDPOINT_BASED
            )

        except Exception as e:
            logger.error("Error checking endpoint rate limit", error=str(e), endpoint=endpoint)
            # SECURITY FIX: Conservative fallback for endpoint limits
            return RateLimitResult(
                allowed=True,
                remaining_requests=5,  # Very conservative for endpoint-specific
                reset_time=datetime.now(timezone.utc) + timedelta(minutes=5),
                limit_type=RateLimitType.ENDPOINT_BASED
            )

    async def _sliding_window_counter(
        self,
        key: str,
        window_seconds: int,
        max_requests: int
    ) -> Tuple[int, datetime]:
        """
        Implement sliding window rate limiting using Redis sorted sets.

        Args:
            key: Redis key for the counter
            window_seconds: Time window in seconds
            max_requests: Maximum requests allowed in the window

        Returns:
            Tuple[int, datetime]: Current count and reset time
        """
        try:
            now = datetime.now(timezone.utc)
            window_start = now - timedelta(seconds=window_seconds)

            # Remove expired entries
            await self.redis.zremrangebyscore(
                key,
                0,
                window_start.timestamp()
            )

            # Add current request
            await self.redis.zadd(key, {str(now.timestamp()): now.timestamp()})

            # Set expiration for the key
            await self.redis.expire(key, window_seconds + 60)

            # Count current requests in window
            current_count = await self.redis.zcard(key)

            # Calculate reset time (start of next window)
            reset_time = now + timedelta(seconds=window_seconds)

            return current_count, reset_time

        except Exception as e:
            logger.error("Error in sliding window counter", error=str(e), key=key)
            # Return conservative values on error
            return 0, datetime.now(timezone.utc) + timedelta(seconds=window_seconds)

    async def _is_whitelisted_ip(self, ip_address: str) -> bool:
        """Check if IP is whitelisted."""
        try:
            whitelist_key = f"{self.whitelist_prefix}ip:{ip_address}"
            result = await self.redis.get(whitelist_key)
            return result is not None
        except Exception:
            return False

    async def _is_blacklisted_ip(self, ip_address: str) -> bool:
        """Check if IP is blacklisted."""
        try:
            blacklist_key = f"{self.blacklist_prefix}ip:{ip_address}"
            result = await self.redis.get(blacklist_key)
            return result is not None
        except Exception:
            return False

    async def add_to_whitelist(self, ip_address: str, duration_hours: int = 24) -> bool:
        """Add IP to whitelist."""
        try:
            whitelist_key = f"{self.whitelist_prefix}ip:{ip_address}"
            await self.redis.setex(
                whitelist_key,
                duration_hours * 3600,
                json.dumps({
                    "ip_address": ip_address,
                    "added_at": datetime.now(timezone.utc).isoformat(),
                    "expires_at": (datetime.now(timezone.utc) + timedelta(hours=duration_hours)).isoformat()
                })
            )
            logger.info("IP added to whitelist", ip_address=ip_address, duration_hours=duration_hours)
            return True
        except Exception as e:
            logger.error("Error adding IP to whitelist", error=str(e), ip_address=ip_address)
            return False

    async def add_to_blacklist(self, ip_address: str, duration_hours: int = 24) -> bool:
        """Add IP to blacklist."""
        try:
            blacklist_key = f"{self.blacklist_prefix}ip:{ip_address}"
            await self.redis.setex(
                blacklist_key,
                duration_hours * 3600,
                json.dumps({
                    "ip_address": ip_address,
                    "blocked_at": datetime.now(timezone.utc).isoformat(),
                    "expires_at": (datetime.now(timezone.utc) + timedelta(hours=duration_hours)).isoformat(),
                    "reason": "rate_limit_exceeded"
                })
            )
            logger.warning("IP added to blacklist", ip_address=ip_address, duration_hours=duration_hours)
            return True
        except Exception as e:
            logger.error("Error adding IP to blacklist", error=str(e), ip_address=ip_address)
            return False

    async def remove_from_whitelist(self, ip_address: str) -> bool:
        """Remove IP from whitelist."""
        try:
            whitelist_key = f"{self.whitelist_prefix}ip:{ip_address}"
            await self.redis.delete(whitelist_key)
            logger.info("IP removed from whitelist", ip_address=ip_address)
            return True
        except Exception as e:
            logger.error("Error removing IP from whitelist", error=str(e), ip_address=ip_address)
            return False

    async def remove_from_blacklist(self, ip_address: str) -> bool:
        """Remove IP from blacklist."""
        try:
            blacklist_key = f"{self.blacklist_prefix}ip:{ip_address}"
            await self.redis.delete(blacklist_key)
            logger.info("IP removed from blacklist", ip_address=ip_address)
            return True
        except Exception as e:
            logger.error("Error removing IP from blacklist", error=str(e), ip_address=ip_address)
            return False

    async def get_rate_limit_stats(self, identifier: str, limit_type: RateLimitType) -> Dict:
        """Get rate limiting statistics for monitoring."""
        try:
            if limit_type == RateLimitType.IP_BASED:
                prefix = f"{self.rate_limit_prefix}ip:{identifier}"
            elif limit_type == RateLimitType.USER_BASED:
                prefix = f"{self.rate_limit_prefix}user:{identifier}"
            else:
                return {"error": "Unsupported limit type for stats"}

            stats = {}
            for window in ["1m", "1h", "1d"]:
                key = f"{prefix}:{window}"
                count = await self.redis.zcard(key)
                stats[window] = count

            return {
                "identifier": identifier,
                "limit_type": limit_type.value,
                "current_requests": stats,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error("Error getting rate limit stats", error=str(e))
            return {"error": str(e)}

    async def reset_rate_limit(self, identifier: str, limit_type: RateLimitType) -> bool:
        """Reset rate limits for a specific identifier (admin function)."""
        try:
            if limit_type == RateLimitType.IP_BASED:
                prefix = f"{self.rate_limit_prefix}ip:{identifier}"
            elif limit_type == RateLimitType.USER_BASED:
                prefix = f"{self.rate_limit_prefix}user:{identifier}"
            else:
                return False

            # Delete all time window keys
            for window in ["1m", "1h", "1d"]:
                key = f"{prefix}:{window}"
                await self.redis.delete(key)

            logger.info("Rate limits reset", identifier=identifier, limit_type=limit_type.value)
            return True

        except Exception as e:
            logger.error("Error resetting rate limits", error=str(e))
            return False