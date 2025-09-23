"""
GREEN PHASE: Minimal rate limiting implementation for admin endpoints

This module provides the minimal rate limiting functionality required
to make the test_admin_rate_limiting test pass.

TDD GREEN PHASE: Just enough code to make the test pass.
"""

import time
from typing import Dict, Any
from collections import defaultdict, deque
from datetime import datetime, timedelta
from fastapi import HTTPException, status


class SimpleRateLimiter:
    """Minimal in-memory rate limiter for GREEN phase"""

    def __init__(self):
        # Using in-memory storage for simplicity in GREEN phase
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.window_size = 60  # 60 seconds window
        self.max_requests = 10  # Maximum 10 requests per minute

    def check_rate_limit(self, identifier: str) -> bool:
        """
        Check if the request should be rate limited

        Returns:
            True if request is allowed, False if rate limited
        """
        now = time.time()
        window_start = now - self.window_size

        # Clean old requests outside the window
        user_requests = self.requests[identifier]
        while user_requests and user_requests[0] < window_start:
            user_requests.popleft()

        # Check if we've exceeded the limit
        if len(user_requests) >= self.max_requests:
            return False

        # Add current request
        user_requests.append(now)
        return True

    def get_rate_limit_status(self, identifier: str) -> Dict[str, Any]:
        """Get current rate limit status for an identifier"""
        now = time.time()
        window_start = now - self.window_size

        # Clean old requests
        user_requests = self.requests[identifier]
        while user_requests and user_requests[0] < window_start:
            user_requests.popleft()

        return {
            "requests_made": len(user_requests),
            "max_requests": self.max_requests,
            "window_size": self.window_size,
            "remaining": max(0, self.max_requests - len(user_requests))
        }


# Global rate limiter instance
rate_limiter = SimpleRateLimiter()


def check_admin_rate_limit(user_id: str) -> None:
    """
    Check rate limit for admin user and raise exception if exceeded

    This is the minimal implementation to make the test pass.
    """
    if not rate_limiter.check_rate_limit(f"admin_{user_id}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )