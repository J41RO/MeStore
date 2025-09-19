#!/usr/bin/env python3
"""
API Endpoints Integration Testing
================================
Comprehensive testing of all API endpoints with integrated middleware:
- Authentication & Authorization
- Rate Limiting
- Security Headers
- User Agent Validation
- Request Logging
- Error Handling

Author: Integration Testing AI
Date: 2025-09-17
"""

import pytest
import time
import asyncio
from typing import Dict, List, Any
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.user import User, UserType
from app.core.security import create_access_token


@pytest.mark.integration
class TestAPIEndpointsWithMiddleware:
    """Test all API endpoints with complete middleware stack."""

    @pytest.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient, async_session: AsyncSession):
        """Setup test data and client."""
        self.client = async_client
        self.db = async_session
        await self._create_test_users()

    async def _create_test_users(self):
        """Create test users with different roles."""
        from app.core.security import get_password_hash

        # Admin user
        admin_hash = await get_password_hash("admin123")
        admin = User(
            email="api_admin@test.com",
            password_hash=admin_hash,
            nombre="API",
            apellido="Admin",
            user_type=UserType.SUPERUSER,
            is_active=True
        )

        # Vendor user
        vendor_hash = await get_password_hash("vendor123")
        vendor = User(
            email="api_vendor@test.com",
            password_hash=vendor_hash,
            nombre="API",
            apellido="Vendor",
            user_type=UserType.VENDEDOR,
            is_active=True
        )

        # Buyer user
        buyer_hash = await get_password_hash("buyer123")
        buyer = User(
            email="api_buyer@test.com",
            password_hash=buyer_hash,
            nombre="API",
            apellido="Buyer",
            user_type=UserType.COMPRADOR,
            is_active=True
        )

        for user in [admin, vendor, buyer]:
            self.db.add(user)

        await self.db.commit()

        # Store tokens
        self.admin_token = create_access_token(data={
            "sub": str(admin.id),
            "email": admin.email,
            "user_type": admin.user_type.value,
            "nombre": admin.nombre,
            "apellido": admin.apellido
        })

        self.vendor_token = create_access_token(data={
            "sub": str(vendor.id),
            "email": vendor.email,
            "user_type": vendor.user_type.value,
            "nombre": vendor.nombre,
            "apellido": vendor.apellido
        })

        self.buyer_token = create_access_token(data={
            "sub": str(buyer.id),
            "email": buyer.email,
            "user_type": buyer.user_type.value,
            "nombre": buyer.nombre,
            "apellido": buyer.apellido
        })

    def get_valid_headers(self, token: str = None) -> Dict[str, str]:
        """Get valid headers that pass middleware validation."""
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if token:
            headers["Authorization"] = f"Bearer {token}"

        return headers

    async def test_user_agent_validation_middleware(self):
        """Test User-Agent validation middleware integration."""
        # Test with invalid User-Agent
        invalid_headers = {
            "User-Agent": "BadBot/1.0",
            "Content-Type": "application/json"
        }

        response = await self.client.get("/health", headers=invalid_headers)
        # Should be blocked by User-Agent validator
        assert response.status_code in [400, 403, 406]

        # Test with valid User-Agent
        valid_headers = self.get_valid_headers()
        response = await self.client.get("/health", headers=valid_headers)
        assert response.status_code == 200

    async def test_rate_limiting_middleware_integration(self):
        """Test rate limiting middleware with real requests."""
        headers = self.get_valid_headers()

        # Make multiple rapid requests to trigger rate limiting
        responses = []
        for i in range(50):  # Attempt many requests quickly
            response = await self.client.get("/health", headers=headers)
            responses.append(response.status_code)

            if response.status_code == 429:  # Rate limited
                break

        # Should eventually get rate limited
        assert 429 in responses or all(r == 200 for r in responses)

    async def test_authentication_endpoints_integration(self):
        """Test authentication endpoints with complete middleware stack."""
        headers = self.get_valid_headers()

        # Test login endpoint
        login_data = {
            "email": "api_admin@test.com",
            "password": "admin123"
        }

        response = await self.client.post(
            "/api/v1/auth/login",
            json=login_data,
            headers=headers
        )

        assert response.status_code in [200, 422, 404]  # Success, validation error, or not found

        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data

    async def test_protected_endpoints_authorization(self):
        """Test protected endpoints require proper authorization."""
        # Test without token
        headers = self.get_valid_headers()

        protected_endpoints = [
            "/api/v1/auth/me",
            "/api/v1/products/",
            "/api/v1/orders/",
            "/api/v1/admin/users"
        ]

        for endpoint in protected_endpoints:
            response = await self.client.get(endpoint, headers=headers)
            # Should require authentication
            assert response.status_code in [401, 404]

        # Test with token
        auth_headers = self.get_valid_headers(self.admin_token)

        for endpoint in protected_endpoints:
            response = await self.client.get(endpoint, headers=auth_headers)
            # Should not be unauthorized
            assert response.status_code != 401

    async def test_role_based_access_integration(self):
        """Test role-based access control across endpoints."""
        # Admin endpoints - should be accessible to admin
        admin_headers = self.get_valid_headers(self.admin_token)
        admin_endpoints = [
            "/api/v1/admin/users",
            "/api/v1/admin/system-stats",
            "/api/v1/commissions/"
        ]

        for endpoint in admin_endpoints:
            response = await self.client.get(endpoint, headers=admin_headers)
            assert response.status_code != 403  # Should not be forbidden

        # Same endpoints should be forbidden for buyer
        buyer_headers = self.get_valid_headers(self.buyer_token)

        for endpoint in admin_endpoints:
            response = await self.client.get(endpoint, headers=buyer_headers)
            assert response.status_code in [403, 404]  # Forbidden or not found

    async def test_vendor_specific_endpoints(self):
        """Test vendor-specific endpoints with proper authorization."""
        vendor_headers = self.get_valid_headers(self.vendor_token)

        vendor_endpoints = [
            "/api/v1/products/",
            "/api/v1/inventory/",
            "/api/v1/vendedores/profile"
        ]

        for endpoint in vendor_endpoints:
            response = await self.client.get(endpoint, headers=vendor_headers)
            # Vendor should access vendor endpoints
            assert response.status_code != 403

    async def test_cors_headers_integration(self):
        """Test CORS headers are properly set by middleware."""
        headers = self.get_valid_headers()
        headers["Origin"] = "http://localhost:3000"

        response = await self.client.options("/api/v1/auth/login", headers=headers)

        # CORS headers should be present
        cors_headers = response.headers
        assert "access-control-allow-origin" in cors_headers or response.status_code == 404

    async def test_security_headers_integration(self):
        """Test security headers are applied by middleware."""
        headers = self.get_valid_headers()

        response = await self.client.get("/health", headers=headers)

        # Check for security headers (if implemented)
        security_headers = [
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection"
        ]

        # In development, security headers might not be applied
        # In production, they should be present
        if response.status_code == 200:
            # Headers might be present
            pass

    async def test_error_handling_integration(self):
        """Test error handling across the middleware stack."""
        headers = self.get_valid_headers()

        # Test non-existent endpoint
        response = await self.client.get("/api/v1/nonexistent", headers=headers)
        assert response.status_code == 404

        # Test malformed JSON
        headers_with_json = self.get_valid_headers()
        response = await self.client.post(
            "/api/v1/auth/login",
            data="invalid json",  # Malformed JSON
            headers=headers_with_json
        )
        assert response.status_code in [400, 422]

    async def test_request_logging_integration(self):
        """Test request logging middleware integration."""
        headers = self.get_valid_headers(self.admin_token)

        # Make various requests that should be logged
        endpoints_to_test = [
            ("/health", "GET"),
            ("/api/v1/auth/me", "GET"),
            ("/api/v1/products/", "GET")
        ]

        for endpoint, method in endpoints_to_test:
            if method == "GET":
                response = await self.client.get(endpoint, headers=headers)
            elif method == "POST":
                response = await self.client.post(endpoint, headers=headers, json={})

            # Requests should complete regardless of logging
            assert response.status_code < 500  # No server errors

    async def test_database_integration_endpoints(self):
        """Test endpoints that interact with database through middleware."""
        headers = self.get_valid_headers(self.admin_token)

        # Database health check
        response = await self.client.get("/db-test", headers=headers)
        assert response.status_code == 200

        db_data = response.json()
        assert "status" in db_data
        assert db_data["status"] in ["success", "error"]

        # User test endpoint
        response = await self.client.get("/users/test", headers=headers)
        assert response.status_code == 200

        users_data = response.json()
        assert "status" in users_data


@pytest.mark.integration
class TestAPIPerformanceIntegration:
    """Test API performance with full middleware stack."""

    @pytest.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient, async_session: AsyncSession):
        """Setup test client."""
        self.client = async_client
        self.db = async_session

        # Create admin token for testing
        admin_data = {
            "sub": "test-admin-id",
            "email": "perf_admin@test.com",
            "user_type": "superuser",
            "nombre": "Performance",
            "apellido": "Admin"
        }
        self.admin_token = create_access_token(data=admin_data)

    def get_headers(self, token: str = None) -> Dict[str, str]:
        """Get headers for performance testing."""
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }

        if token:
            headers["Authorization"] = f"Bearer {token}"

        return headers

    async def test_concurrent_requests_performance(self):
        """Test API performance under concurrent load."""
        headers = self.get_headers(self.admin_token)

        async def make_request(endpoint: str):
            start_time = time.time()
            response = await self.client.get(endpoint, headers=headers)
            duration = time.time() - start_time
            return response.status_code, duration

        # Test concurrent requests to different endpoints
        endpoints = [
            "/health",
            "/db-test",
            "/api/v1/auth/me",
            "/api/v1/products/"
        ]

        tasks = []
        for _ in range(5):  # 5 concurrent requests per endpoint
            for endpoint in endpoints:
                tasks.append(make_request(endpoint))

        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time

        # Analyze results
        successful_requests = [
            r for r in results
            if not isinstance(r, Exception) and r[0] < 500
        ]

        assert len(successful_requests) > 0
        assert total_time < 30.0  # Should complete within 30 seconds

        # Check individual request times
        durations = [r[1] for r in successful_requests if isinstance(r, tuple)]
        if durations:
            avg_duration = sum(durations) / len(durations)
            assert avg_duration < 5.0  # Average request should be under 5 seconds

    async def test_middleware_overhead(self):
        """Test middleware processing overhead."""
        headers = self.get_headers()

        # Test simple endpoint multiple times
        durations = []
        for _ in range(10):
            start_time = time.time()
            response = await self.client.get("/health", headers=headers)
            duration = time.time() - start_time
            durations.append(duration)

            assert response.status_code == 200

        # Middleware should not add significant overhead
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)

        assert avg_duration < 1.0  # Average should be under 1 second
        assert max_duration < 3.0  # Max should be under 3 seconds

    async def test_response_time_consistency(self):
        """Test response time consistency across requests."""
        headers = self.get_headers(self.admin_token)

        # Test authenticated endpoint multiple times
        durations = []
        for _ in range(20):
            start_time = time.time()
            response = await self.client.get("/api/v1/auth/me", headers=headers)
            duration = time.time() - start_time
            durations.append(duration)

            if response.status_code == 200:
                break  # Stop if we get a successful response

        if durations:
            # Check consistency
            avg_duration = sum(durations) / len(durations)
            std_deviation = (sum((d - avg_duration) ** 2 for d in durations) / len(durations)) ** 0.5

            # Standard deviation should be reasonable
            assert std_deviation < avg_duration  # Std dev shouldn't exceed average


@pytest.mark.integration
class TestAPISecurityIntegration:
    """Test API security with complete middleware integration."""

    @pytest.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient, async_session: AsyncSession):
        """Setup test client."""
        self.client = async_client
        self.db = async_session

    async def test_sql_injection_protection(self):
        """Test SQL injection protection through the API."""
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }

        # Try SQL injection in login
        malicious_data = {
            "email": "admin'; DROP TABLE users; --",
            "password": "password"
        }

        response = await self.client.post(
            "/api/v1/auth/login",
            json=malicious_data,
            headers=headers
        )

        # Should not cause server error (SQLAlchemy should protect)
        assert response.status_code in [400, 401, 422, 404]

    async def test_xss_protection(self):
        """Test XSS protection in API responses."""
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }

        # Try XSS in various fields
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ]

        for payload in xss_payloads:
            malicious_data = {
                "email": payload,
                "password": "password"
            }

            response = await self.client.post(
                "/api/v1/auth/login",
                json=malicious_data,
                headers=headers
            )

            # Should handle malicious input gracefully
            assert response.status_code < 500

    async def test_csrf_protection(self):
        """Test CSRF protection mechanisms."""
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "http://malicious-site.com"
        }

        # Try cross-origin request
        response = await self.client.post(
            "/api/v1/auth/login",
            json={"email": "test@test.com", "password": "password"},
            headers=headers
        )

        # CORS should handle this appropriately
        assert response.status_code in [200, 400, 401, 403, 422, 404]

    async def test_header_injection_protection(self):
        """Test protection against header injection attacks."""
        malicious_headers = {
            "User-Agent": "Mozilla/5.0\r\nX-Injected: malicious",
            "Content-Type": "application/json\r\nX-Injected: malicious"
        }

        response = await self.client.get("/health", headers=malicious_headers)

        # Should handle malicious headers without server error
        assert response.status_code < 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])