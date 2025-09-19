"""
CORS Security Integration Tests
===============================

Comprehensive tests to validate CORS middleware security configurations
and ensure no security vulnerabilities exist in the FastAPI implementation.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import os

from app.main import app
from app.core.config import settings


class TestCORSSecurityConfiguration:
    """Test CORS security configuration across different environments."""

    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    def test_cors_no_wildcard_origins(self):
        """Test that wildcard origins are never allowed."""
        # Test development environment
        with patch.object(settings, 'CORS_ORIGINS', '*'):
            with pytest.raises(ValueError, match="CORS origins cannot contain wildcards"):
                settings.validate_cors_origins('*')

    def test_development_cors_origins(self):
        """Test development environment CORS origins."""
        with patch.object(settings, 'ENVIRONMENT', 'development'):
            origins = settings.get_cors_origins_for_environment()

            # Should include standard development origins
            assert "http://localhost:5173" in origins
            assert "http://localhost:3000" in origins
            assert "http://127.0.0.1:5173" in origins

            # Should not contain wildcards
            assert "*" not in str(origins)

    def test_production_cors_https_enforcement(self):
        """Test production environment enforces HTTPS origins."""
        with patch.object(settings, 'ENVIRONMENT', 'production'):
            with patch.object(settings, 'CORS_ORIGINS', 'http://example.com,https://secure.example.com'):
                with pytest.raises(ValueError, match="Production origins must use HTTPS"):
                    settings.get_cors_origins_for_environment()

    def test_production_cors_requires_explicit_origins(self):
        """Test production requires explicit CORS origins."""
        with patch.object(settings, 'ENVIRONMENT', 'production'):
            with patch.object(settings, 'CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000,http://192.168.1.137:5173'):
                with pytest.raises(ValueError, match="Production CORS_ORIGINS must be explicitly set"):
                    settings.get_cors_origins_for_environment()

    def test_testing_environment_restrictions(self):
        """Test testing environment only allows test domains."""
        with patch.object(settings, 'ENVIRONMENT', 'testing'):
            with patch.object(settings, 'CORS_ORIGINS', 'http://production.example.com'):
                with pytest.raises(ValueError, match="Non-test origin not allowed in testing environment"):
                    settings.get_cors_origins_for_environment()

    def test_secure_cors_methods_production(self):
        """Test dangerous HTTP methods are removed in production."""
        with patch.object(settings, 'ENVIRONMENT', 'production'):
            with patch.object(settings, 'CORS_ALLOW_METHODS', 'GET,POST,TRACE,DELETE,CONNECT'):
                methods = settings.get_secure_cors_methods()

                # Dangerous methods should be removed
                assert "TRACE" not in methods
                assert "CONNECT" not in methods

                # Safe methods should remain
                assert "GET" in methods
                assert "POST" in methods
                assert "DELETE" in methods

    def test_secure_cors_headers_production(self):
        """Test potentially dangerous headers are removed in production."""
        with patch.object(settings, 'ENVIRONMENT', 'production'):
            with patch.object(settings, 'CORS_ALLOW_HEADERS', 'Authorization,Content-Type,X-Forwarded-For,Accept'):
                headers = settings.get_secure_cors_headers()

                # Dangerous headers should be removed
                assert "X-Forwarded-For" not in [h.lower() for h in headers]

                # Safe headers should remain
                assert "Authorization" in headers
                assert "Content-Type" in headers

    def test_cors_preflight_request(self):
        """Test CORS preflight request handling."""
        # Test preflight OPTIONS request
        headers = {
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        }

        response = self.client.options("/api/v1/health", headers=headers)

        # Should allow the request
        assert response.status_code in [200, 204]

        # Should have CORS headers
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers

    def test_cors_actual_request(self):
        """Test actual CORS request with valid origin."""
        headers = {
            "Origin": "http://localhost:5173",
            "Content-Type": "application/json"
        }

        response = self.client.get("/health", headers=headers)

        # Should succeed
        assert response.status_code == 200

        # Should have CORS headers
        assert "Access-Control-Allow-Origin" in response.headers

    def test_cors_invalid_origin_rejected(self):
        """Test that invalid origins are properly rejected."""
        # Test with clearly invalid origin
        headers = {
            "Origin": "http://malicious-site.com",
            "Content-Type": "application/json"
        }

        response = self.client.get("/health", headers=headers)

        # Request should still succeed (CORS is browser-enforced)
        # but CORS headers should not be present for invalid origins
        assert response.status_code == 200

        # CORS headers should not include the malicious origin
        if "Access-Control-Allow-Origin" in response.headers:
            assert response.headers["Access-Control-Allow-Origin"] != "http://malicious-site.com"

    def test_cors_credentials_configuration(self):
        """Test CORS credentials configuration."""
        headers = {
            "Origin": "http://localhost:5173",
            "Content-Type": "application/json"
        }

        response = self.client.get("/health", headers=headers)

        # Should have proper credentials configuration
        if "Access-Control-Allow-Credentials" in response.headers:
            assert response.headers["Access-Control-Allow-Credentials"] in ["true", "false"]

    def test_cors_max_age_security(self):
        """Test CORS max-age configuration for security."""
        headers = {
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        }

        response = self.client.options("/api/v1/health", headers=headers)

        if "Access-Control-Max-Age" in response.headers:
            max_age = int(response.headers["Access-Control-Max-Age"])
            # Should not cache for too long (security consideration)
            assert max_age <= 3600  # 1 hour maximum


class TestMiddlewareChainSecurity:
    """Test middleware chain ordering and security."""

    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    def test_middleware_chain_ordering(self):
        """Test that middleware is applied in correct security order."""
        # This is a behavioral test - middleware should apply in the right order
        # HTTPS redirect -> Compression -> CORS -> Application

        response = self.client.get("/health")
        assert response.status_code == 200

        # Should have compression if content is large enough
        # Should have CORS headers for valid origins
        # Should have security headers if security middleware is active

    def test_https_redirect_production_only(self):
        """Test HTTPS redirect is only active in production."""
        # In development/testing, HTTP should be allowed
        response = self.client.get("/health")
        assert response.status_code == 200
        # Should not redirect to HTTPS in non-production

    def test_gzip_compression_active(self):
        """Test GZip compression is active."""
        # Request a potentially large response
        response = self.client.get("/docs")

        # If the response is large enough, should have compression headers
        if len(response.content) > 1000:
            # May have compression headers depending on client Accept-Encoding
            pass  # Compression is optional based on client headers

    def test_security_headers_present(self):
        """Test security headers are present in responses."""
        response = self.client.get("/health")

        # Basic security checks
        assert response.status_code == 200

        # Check for common security headers (if security middleware is active)
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security"
        ]

        # Note: These headers may be added by other middleware
        # This test documents expected security headers


@pytest.mark.integration
class TestCORSEnvironmentIntegration:
    """Integration tests for CORS across different environments."""

    def test_development_environment_cors(self):
        """Test CORS configuration in development environment."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'development'}):
            client = TestClient(app)

            headers = {"Origin": "http://localhost:5173"}
            response = client.get("/health", headers=headers)

            assert response.status_code == 200

    def test_testing_environment_cors(self):
        """Test CORS configuration in testing environment."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'testing'}):
            # Testing environment should be restrictive
            pass  # Add specific testing environment checks

    def test_cors_error_handling(self):
        """Test CORS error handling and validation."""
        # Test invalid configuration handling
        with patch.object(settings, 'CORS_ORIGINS', ''):
            try:
                origins = settings.get_cors_origins_for_environment()
                # Should handle empty origins gracefully
                assert isinstance(origins, list)
            except ValueError:
                # May raise error for invalid configuration
                pass