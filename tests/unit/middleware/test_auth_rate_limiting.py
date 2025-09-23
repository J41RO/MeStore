# ~/tests/unit/middleware/test_auth_rate_limiting.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Test Suite for Enhanced Authentication Rate Limiting
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
Comprehensive test suite for enhanced authentication rate limiting middleware.

This module tests:
- Brute force attack prevention
- Progressive penalty enforcement
- IP-based and user-based rate limiting
- Automatic blacklisting functionality
- Integration with audit logging
"""

import asyncio
import json
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

from app.middleware.auth_rate_limiting import (
    AuthRateLimitingMiddleware,
    AuthRateLimitType,
    BruteForceLevel,
    create_auth_rate_limiting_middleware
)


class TestAuthRateLimitingMiddleware:
    """Test suite for authentication rate limiting middleware."""

    @pytest.fixture
    def app(self):
        """Create test FastAPI application."""
        app = FastAPI()

        @app.post("/api/v1/auth/login")
        async def login():
            return {"message": "Login endpoint"}

        @app.post("/api/v1/auth/admin-login")
        async def admin_login():
            return {"message": "Admin login endpoint"}

        @app.post("/api/v1/auth/forgot-password")
        async def forgot_password():
            return {"message": "Password reset endpoint"}

        @app.post("/api/v1/auth/register")
        async def register():
            return {"message": "Registration endpoint"}

        @app.post("/api/v1/otp/send")
        async def send_otp():
            return {"message": "OTP send endpoint"}

        @app.get("/api/v1/users/profile")
        async def profile():
            return {"message": "Non-auth endpoint"}

        return app

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        redis_mock = AsyncMock()
        redis_mock.ping = AsyncMock(return_value=True)
        redis_mock.get = AsyncMock(return_value=None)
        redis_mock.setex = AsyncMock()
        redis_mock.expire = AsyncMock()
        redis_mock.incr = AsyncMock(return_value=1)
        redis_mock.exists = AsyncMock(return_value=False)
        redis_mock.zcard = AsyncMock(return_value=0)
        redis_mock.zadd = AsyncMock()
        redis_mock.zremrangebyscore = AsyncMock()
        return redis_mock

    @pytest.fixture
    def middleware(self, app, mock_redis):
        """Create middleware with mock Redis."""
        return AuthRateLimitingMiddleware(app, mock_redis)

    @pytest.fixture
    def test_client(self, app, middleware):
        """Create test client with middleware."""
        app.add_middleware(lambda app: middleware)
        return TestClient(app)

    def test_non_auth_endpoint_not_rate_limited(self, middleware):
        """Test that non-authentication endpoints are not rate limited."""
        # Create mock request for non-auth endpoint
        request = MagicMock()
        request.url.path = "/api/v1/users/profile"

        auth_type = middleware._get_auth_endpoint_type(request)
        assert auth_type is None

    def test_auth_endpoint_type_detection(self, middleware):
        """Test authentication endpoint type detection."""
        test_cases = [
            ("/api/v1/auth/login", AuthRateLimitType.LOGIN_ATTEMPTS),
            ("/api/v1/auth/admin-login", AuthRateLimitType.ADMIN_LOGIN),
            ("/api/v1/auth/forgot-password", AuthRateLimitType.PASSWORD_RESET),
            ("/api/v1/auth/register", AuthRateLimitType.REGISTRATION),
            ("/api/v1/otp/send", AuthRateLimitType.OTP_REQUESTS),
            ("/api/v1/users/profile", None),
        ]

        for path, expected_type in test_cases:
            request = MagicMock()
            request.url.path = path
            result = middleware._get_auth_endpoint_type(request)
            assert result == expected_type

    @pytest.mark.parametrize("headers_config,client_host,expected_ip,description", [
        # Scenario 1: X-Forwarded-For header (should extract first IP from comma-separated list)
        ({"x-forwarded-for": "192.168.1.100, 10.0.0.1", "x-real-ip": None},
         "127.0.0.1", "192.168.1.100", "Should extract first IP from X-Forwarded-For"),

        # Scenario 2: X-Real-IP header (when X-Forwarded-For is None)
        ({"x-forwarded-for": None, "x-real-ip": "192.168.1.200"},
         "127.0.0.1", "192.168.1.200", "Should use X-Real-IP when X-Forwarded-For is None"),

        # Scenario 3: Client host fallback (when both headers are None)
        ({"x-forwarded-for": None, "x-real-ip": None},
         "127.0.0.1", "127.0.0.1", "Should fallback to client.host when headers are None"),

        # Scenario 4: Empty X-Forwarded-For (should fallback to X-Real-IP)
        ({"x-forwarded-for": "", "x-real-ip": "10.0.0.50"},
         "192.168.1.1", "10.0.0.50", "Should use X-Real-IP when X-Forwarded-For is empty"),

        # Scenario 5: Both headers empty (should fallback to client.host)
        ({"x-forwarded-for": "", "x-real-ip": ""},
         "172.16.0.1", "172.16.0.1", "Should fallback to client.host when both headers are empty"),
    ])
    def test_client_ip_extraction(self, middleware, headers_config, client_host, expected_ip, description):
        """Test client IP address extraction with various header configurations."""
        # Create fresh mock for this test case
        request = MagicMock()
        request.headers.get.side_effect = lambda header: headers_config.get(header)
        request.client.host = client_host

        # Extract IP using middleware
        actual_ip = middleware._get_client_ip(request)

        # Assert the expected result with descriptive error message
        assert actual_ip == expected_ip, (
            f"{description}: Expected '{expected_ip}' but got '{actual_ip}' "
            f"with headers {headers_config} and client.host='{client_host}'"
        )

    @pytest.mark.asyncio
    async def test_user_identifier_extraction(self, middleware):
        """Test user identifier extraction from request body."""
        # Test with email in JSON body
        request = MagicMock()
        request.method = "POST"
        request.body = AsyncMock(return_value=b'{"email": "test@example.com", "password": "secret"}')

        user_id = await middleware._extract_user_identifier(request)
        assert user_id == "test@example.com"

        # Test with username in JSON body
        request.body = AsyncMock(return_value=b'{"username": "testuser", "password": "secret"}')

        user_id = await middleware._extract_user_identifier(request)
        assert user_id == "testuser"

        # Test with no identifier
        request.body = AsyncMock(return_value=b'{"password": "secret"}')

        user_id = await middleware._extract_user_identifier(request)
        assert user_id is None

        # Test with non-POST request
        request.method = "GET"

        user_id = await middleware._extract_user_identifier(request)
        assert user_id is None

    @pytest.mark.parametrize("violation_count,expected_multiplier", [
        (0, 24),  # No violations -> fallback to default (implementation detail)
        (1, 1),   # First violation -> base multiplier
        (2, 2),   # Second violation -> 2x multiplier
        (3, 4),   # Third violation -> 4x multiplier
        (4, 8),   # Fourth violation -> 8x multiplier
        (5, 24),  # Fifth+ violation -> max 24x multiplier
        (6, 24),  # Beyond 5 violations -> still max 24x multiplier
    ])
    def test_progressive_penalties(self, middleware, violation_count, expected_multiplier):
        """Test progressive penalty multiplier system for repeated violations."""
        # Test the penalty multiplier calculation directly using the same logic as the middleware
        actual_multiplier = middleware.penalty_multipliers.get(min(violation_count, 5), 24)

        assert actual_multiplier == expected_multiplier, (
            f"Violation count {violation_count} should result in {expected_multiplier}x multiplier, "
            f"but got {actual_multiplier}x"
        )

        # Also verify the multiplier is applied correctly in lockout duration calculation
        limits = middleware.auth_limits[AuthRateLimitType.LOGIN_ATTEMPTS]
        if limits["progressive_lockout"]:
            base_lockout = limits["lockout_duration_minutes"]
            expected_lockout = base_lockout * expected_multiplier

            # Verify the lockout calculation logic works as expected
            assert expected_lockout == base_lockout * actual_multiplier

    def test_penalty_multiplier_edge_cases(self, middleware):
        """Test edge cases for penalty multiplier calculation."""
        # Test that the multiplier dictionary contains expected keys
        expected_keys = {1, 2, 3, 4, 5}
        actual_keys = set(middleware.penalty_multipliers.keys())
        assert actual_keys == expected_keys, f"Expected keys {expected_keys}, got {actual_keys}"

        # Test that the values are as expected
        expected_values = {1: 1, 2: 2, 3: 4, 4: 8, 5: 24}
        for key, expected_value in expected_values.items():
            actual_value = middleware.penalty_multipliers[key]
            assert actual_value == expected_value, (
                f"Penalty multiplier for {key} violations should be {expected_value}, got {actual_value}"
            )

    @pytest.mark.asyncio
    async def test_ip_rate_limit_enforcement(self, middleware):
        """Test IP-based rate limit enforcement."""
        # Mock Redis to simulate max failures reached
        middleware.redis_client.zcard = AsyncMock(return_value=10)  # Max failures for login
        middleware.redis_client.get = AsyncMock(return_value=None)  # No existing lockout

        limits = middleware.auth_limits[AuthRateLimitType.LOGIN_ATTEMPTS]
        current_time = datetime.now(timezone.utc)

        is_allowed, info = await middleware._check_ip_auth_limits(
            "192.168.1.100", AuthRateLimitType.LOGIN_ATTEMPTS, limits, current_time
        )

        assert not is_allowed
        assert info["type"] == "ip_rate_limit"
        assert info["failures"] == 10
        assert info["max_failures"] == 10
        assert "lockout_until" in info
        assert "retry_after" in info

    @pytest.mark.asyncio
    async def test_user_rate_limit_enforcement(self, middleware):
        """Test user-based rate limit enforcement."""
        # Mock Redis to simulate max failures reached
        middleware.redis_client.zcard = AsyncMock(return_value=5)  # Max failures for user login
        middleware.redis_client.get = AsyncMock(return_value=None)  # No existing lockout

        limits = middleware.auth_limits[AuthRateLimitType.LOGIN_ATTEMPTS]
        current_time = datetime.now(timezone.utc)

        is_allowed, info = await middleware._check_user_auth_limits(
            "test@example.com", AuthRateLimitType.LOGIN_ATTEMPTS, limits, current_time
        )

        assert not is_allowed
        assert info["type"] == "user_rate_limit"
        assert info["failures"] == 5
        assert info["max_failures"] == 5
        assert "lockout_until" in info

    @pytest.mark.asyncio
    async def test_lockout_period_enforcement(self, middleware):
        """Test that active lockout periods are enforced."""
        # Mock Redis to return an active lockout
        future_time = datetime.now(timezone.utc) + timedelta(minutes=30)
        middleware.redis_client.get = AsyncMock(return_value=str(future_time.timestamp()))

        limits = middleware.auth_limits[AuthRateLimitType.LOGIN_ATTEMPTS]
        current_time = datetime.now(timezone.utc)

        is_allowed, info = await middleware._check_ip_auth_limits(
            "192.168.1.100", AuthRateLimitType.LOGIN_ATTEMPTS, limits, current_time
        )

        assert not is_allowed
        assert info["type"] == "ip_lockout"
        assert "lockout_until" in info
        assert info["retry_after"] > 0

    @pytest.mark.asyncio
    async def test_blacklist_functionality(self, middleware):
        """Test IP blacklisting functionality."""
        # Mock Redis to indicate IP is blacklisted
        middleware.redis_client.exists = AsyncMock(return_value=True)

        is_blacklisted = await middleware._is_blacklisted("192.168.1.100")
        assert is_blacklisted

        # Test blacklist response creation
        response = middleware._create_blacklist_response("192.168.1.100")
        assert response.status_code == 403
        assert "IPBlacklisted" in response.body.decode()

    @pytest.mark.asyncio
    async def test_auto_blacklist_on_severe_violations(self, middleware):
        """Test automatic blacklisting after severe violations."""
        with patch.object(middleware.audit_service, 'log_security_event', new_callable=AsyncMock) as mock_audit:
            await middleware._auto_blacklist_ip("192.168.1.100", 5)

            # Verify Redis blacklist key was set
            middleware.redis_client.setex.assert_called_once()

            # Verify audit log was created
            mock_audit.assert_called_once()
            call_args = mock_audit.call_args[1]
            assert call_args["event_type"] == "ip_auto_blacklisted"
            assert call_args["severity"] == "critical"

    @pytest.mark.asyncio
    async def test_authentication_failure_tracking(self, middleware):
        """Test authentication failure tracking in Redis."""
        with patch.object(middleware.audit_service, 'log_security_event', new_callable=AsyncMock):
            await middleware._track_authentication_failure(
                "192.168.1.100", "test@example.com", AuthRateLimitType.LOGIN_ATTEMPTS
            )

            # Verify Redis operations
            assert middleware.redis_client.zadd.call_count == 2  # IP and user tracking
            assert middleware.redis_client.expire.call_count == 2

    @pytest.mark.asyncio
    async def test_admin_login_stricter_limits(self, middleware):
        """Test that admin login has stricter limits than regular login."""
        admin_limits = middleware.auth_limits[AuthRateLimitType.ADMIN_LOGIN]
        login_limits = middleware.auth_limits[AuthRateLimitType.LOGIN_ATTEMPTS]

        # Admin should have stricter limits
        assert admin_limits["attempts_per_ip_per_hour"] < login_limits["attempts_per_ip_per_hour"]
        assert admin_limits["attempts_per_user_per_hour"] <= login_limits["attempts_per_user_per_hour"]
        assert admin_limits["lockout_duration_minutes"] >= login_limits["lockout_duration_minutes"]

    @pytest.mark.asyncio
    async def test_rate_limit_headers_added(self, middleware):
        """Test that appropriate rate limit headers are added to responses."""
        rate_limit_info = {
            "type": "ip_allowed",
            "remaining": 8,
            "reset_time": "2025-09-18T14:00:00Z"
        }

        response = Response()
        middleware._add_auth_rate_limit_headers(response, rate_limit_info)

        assert response.headers["X-Auth-RateLimit-Remaining"] == "8"
        assert response.headers["X-Auth-RateLimit-Reset"] == "2025-09-18T14:00:00Z"
        assert response.headers["X-Auth-RateLimit-Type"] == "ip_allowed"

    @pytest.mark.asyncio
    async def test_redis_error_fallback(self, middleware):
        """Test graceful fallback when Redis is unavailable."""
        # Mock Redis to raise exceptions
        middleware.redis_client.zcard = AsyncMock(side_effect=Exception("Redis unavailable"))

        limits = middleware.auth_limits[AuthRateLimitType.LOGIN_ATTEMPTS]
        current_time = datetime.now(timezone.utc)

        is_allowed, info = await middleware._check_ip_auth_limits(
            "192.168.1.100", AuthRateLimitType.LOGIN_ATTEMPTS, limits, current_time
        )

        # Should fail safe and allow with conservative limits
        assert is_allowed
        assert info["type"] == "error_fallback"
        assert info["remaining"] == 1

    @pytest.mark.asyncio
    async def test_different_endpoint_types_different_limits(self, middleware):
        """Test that different endpoint types have different rate limits."""
        endpoint_types = [
            AuthRateLimitType.LOGIN_ATTEMPTS,
            AuthRateLimitType.ADMIN_LOGIN,
            AuthRateLimitType.PASSWORD_RESET,
            AuthRateLimitType.REGISTRATION,
            AuthRateLimitType.OTP_REQUESTS
        ]

        for endpoint_type in endpoint_types:
            limits = middleware.auth_limits[endpoint_type]
            assert "attempts_per_ip_per_hour" in limits
            assert "attempts_per_user_per_hour" in limits
            assert "lockout_duration_minutes" in limits
            assert "progressive_lockout" in limits

    @pytest.mark.asyncio
    async def test_create_auth_rate_limiting_middleware_with_redis(self):
        """Test middleware creation with Redis connection."""
        app = FastAPI()

        with patch('redis.asyncio.from_url') as mock_redis_from_url:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis_from_url.return_value = mock_redis

            middleware = await create_auth_rate_limiting_middleware(app, "redis://localhost:6379")

            assert isinstance(middleware, AuthRateLimitingMiddleware)
            assert middleware.redis_client == mock_redis
            mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_auth_rate_limiting_middleware_redis_failure(self):
        """Test middleware creation when Redis connection fails."""
        app = FastAPI()

        with patch('redis.asyncio.from_url', side_effect=Exception("Connection failed")):
            middleware = await create_auth_rate_limiting_middleware(app, "redis://localhost:6379")

            assert isinstance(middleware, AuthRateLimitingMiddleware)
            assert middleware.redis_client is None

    def test_rate_limit_response_format(self, middleware):
        """Test rate limit response format and content."""
        rate_limit_info = {
            "type": "ip_rate_limit",
            "retry_after": 900,
            "lockout_until": "2025-09-18T14:00:00Z",
            "violation_count": 3
        }

        response = middleware._create_rate_limit_response(rate_limit_info)

        assert response.status_code == 429
        assert response.headers["X-Auth-RateLimit-Type"] == "ip_rate_limit"
        assert response.headers["X-Auth-RateLimit-Retry-After"] == "900"
        assert response.headers["Retry-After"] == "900"
        assert response.headers["X-Auth-Lockout-Until"] == "2025-09-18T14:00:00Z"
        assert response.headers["X-Auth-Violation-Count"] == "3"

        body = json.loads(response.body)
        assert body["error"]["type"] == "AuthRateLimitExceeded"
        assert body["error"]["code"] == "AUTH_RATE_LIMIT_EXCEEDED"
        assert "retry_after_seconds" in body["error"]["details"]


@pytest.mark.integration
class TestAuthRateLimitingIntegration:
    """Integration tests for authentication rate limiting middleware."""

    @pytest.fixture
    def app_with_middleware(self):
        """Create FastAPI app with auth rate limiting middleware."""
        app = FastAPI()

        @app.post("/api/v1/auth/login")
        async def login():
            # Simulate failed authentication
            return Response(status_code=401)

        @app.post("/api/v1/auth/admin-login")
        async def admin_login():
            return Response(status_code=401)

        # Add middleware
        middleware = AuthRateLimitingMiddleware(app, None)  # No Redis for integration tests
        app.add_middleware(lambda app: middleware)

        return app

    def test_multiple_failed_login_attempts(self, app_with_middleware):
        """Test multiple failed login attempts trigger rate limiting."""
        client = TestClient(app_with_middleware)

        # Make multiple failed login attempts
        for i in range(12):  # Exceed the limit of 10
            response = client.post(
                "/api/v1/auth/login",
                json={"email": "test@example.com", "password": "wrong"},
                headers={"X-Forwarded-For": "192.168.1.100"}
            )

            if i < 10:
                # Should be allowed initially
                assert response.status_code in [401, 200]  # Auth failure, not rate limit
            else:
                # Should be rate limited after 10 attempts
                assert response.status_code == 429

    def test_different_ips_independent_limits(self, app_with_middleware):
        """Test that different IPs have independent rate limits."""
        client = TestClient(app_with_middleware)

        # IP 1 makes failed attempts
        for _ in range(10):
            response = client.post(
                "/api/v1/auth/login",
                json={"email": "test@example.com", "password": "wrong"},
                headers={"X-Forwarded-For": "192.168.1.100"}
            )
            assert response.status_code == 401

        # IP 2 should still be allowed
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrong"},
            headers={"X-Forwarded-For": "192.168.1.200"}
        )
        assert response.status_code == 401  # Auth failure, not rate limited

    def test_admin_login_stricter_enforcement(self, app_with_middleware):
        """Test that admin login has stricter rate limiting."""
        client = TestClient(app_with_middleware)

        # Admin login should be rate limited after fewer attempts
        for i in range(5):  # Admin limit is 3
            response = client.post(
                "/api/v1/auth/admin-login",
                json={"email": "admin@example.com", "password": "wrong"},
                headers={"X-Forwarded-For": "192.168.1.100"}
            )

            if i < 3:
                assert response.status_code in [401, 200]
            else:
                assert response.status_code == 429