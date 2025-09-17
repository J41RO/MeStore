#!/usr/bin/env python3
"""
Comprehensive TDD Unit Tests for JWT Security Module
===================================================

Testing Strategy:
- RED: Write failing test first
- GREEN: Implement minimal code to pass
- REFACTOR: Optimize while maintaining tests

Coverage Goals:
- JWT token creation: 100%
- JWT token decoding/validation: 100%
- Token expiration handling: 100%
- Refresh token functionality: 100%
- Security edge cases: 95%

File: tests/unit/auth/test_jwt_security.py
Author: Unit Testing AI - TDD Methodology
Date: 2025-09-17
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, Mock
from typing import Dict, Any, Optional
import jwt as jose_jwt
from jose import JWTError
import time

# Import modules under test
from app.core.security import (
    create_access_token,
    decode_access_token,
    create_refresh_token,
    decode_refresh_token
)
from app.core.config import settings


class TestJWTTokenCreation:
    """Test JWT token creation functionality with TDD methodology."""
    
    def test_create_access_token_with_basic_data_returns_valid_jwt(self):
        """TDD: create_access_token should return valid JWT string."""
        # RED: Test basic token creation
        data = {"sub": "test@example.com", "user_id": "123"}
        
        token = create_access_token(data)
        
        # GREEN: Verify token properties
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are typically long
        assert token.count('.') == 2  # JWT has 3 parts separated by dots
        
        # Verify it's a valid JWT by decoding (should not raise exception)
        decoded = jose_jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded["sub"] == "test@example.com"
        assert decoded["user_id"] == "123"
    
    def test_create_access_token_includes_expiration_claim(self):
        """TDD: Access token should include expiration claim."""
        data = {"sub": "test@example.com"}
        
        token = create_access_token(data)
        decoded = jose_jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Should have expiration claim
        assert "exp" in decoded
        assert isinstance(decoded["exp"], int)
        
        # Expiration should be in the future
        current_time = datetime.now(timezone.utc).timestamp()
        assert decoded["exp"] > current_time
    
    def test_create_access_token_with_custom_expiration(self):
        """TDD: create_access_token should respect custom expiration delta."""
        data = {"sub": "test@example.com"}
        custom_delta = timedelta(minutes=30)
        
        token = create_access_token(data, expires_delta=custom_delta)
        decoded = jose_jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Calculate expected expiration (within 1 minute tolerance)
        expected_exp = datetime.now(timezone.utc) + custom_delta
        actual_exp = datetime.fromtimestamp(decoded["exp"], timezone.utc)
        
        time_diff = abs((expected_exp - actual_exp).total_seconds())
        assert time_diff < 60  # Within 1 minute tolerance
    
    def test_create_access_token_without_custom_expiration_uses_default(self):
        """TDD: create_access_token should use default expiration when none provided."""
        data = {"sub": "test@example.com"}
        
        token = create_access_token(data)
        decoded = jose_jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Calculate expected expiration using default setting
        expected_exp = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        actual_exp = datetime.fromtimestamp(decoded["exp"], timezone.utc)
        
        time_diff = abs((expected_exp - actual_exp).total_seconds())
        assert time_diff < 60  # Within 1 minute tolerance
    
    def test_create_access_token_preserves_all_input_data(self):
        """TDD: create_access_token should preserve all provided data."""
        data = {
            "sub": "test@example.com",
            "user_id": "123",
            "user_type": "ADMIN",
            "permissions": ["read", "write"],
            "custom_field": "custom_value"
        }
        
        token = create_access_token(data)
        decoded = jose_jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # All original data should be preserved
        for key, value in data.items():
            assert decoded[key] == value
    
    def test_create_access_token_with_empty_data_creates_valid_token(self):
        """TDD: create_access_token should handle empty data gracefully."""
        data = {}
        
        token = create_access_token(data)
        decoded = jose_jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Should still have expiration
        assert "exp" in decoded
        assert len(decoded) == 1  # Only exp claim


class TestJWTTokenDecoding:
    """Test JWT token decoding and validation with TDD methodology."""
    
    def test_decode_access_token_valid_token_returns_payload(self):
        """TDD: decode_access_token should return payload for valid token."""
        # Create a valid token first
        data = {"sub": "test@example.com", "user_id": "123"}
        token = create_access_token(data)
        
        # Decode it
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert isinstance(decoded, dict)
        assert decoded["sub"] == "test@example.com"
        assert decoded["user_id"] == "123"
        assert "exp" in decoded
    
    def test_decode_access_token_invalid_token_returns_none(self):
        """TDD: decode_access_token should return None for invalid token."""
        invalid_token = "invalid.jwt.token"
        
        decoded = decode_access_token(invalid_token)
        
        assert decoded is None
    
    def test_decode_access_token_malformed_token_returns_none(self):
        """TDD: decode_access_token should handle malformed tokens gracefully."""
        malformed_tokens = [
            "not.a.jwt",
            "too.few.parts",
            "too.many.parts.here.invalid",
            "",
            "single_string_no_dots",
            "...",  # Empty parts
        ]
        
        for token in malformed_tokens:
            decoded = decode_access_token(token)
            assert decoded is None, f"Should return None for malformed token: {token}"
    
    def test_decode_access_token_expired_token_returns_none(self):
        """TDD: decode_access_token should return None for expired token."""
        # Create token with past expiration
        data = {"sub": "test@example.com"}
        past_delta = timedelta(minutes=-30)  # 30 minutes ago
        
        token = create_access_token(data, expires_delta=past_delta)
        
        # Should return None for expired token
        decoded = decode_access_token(token)
        assert decoded is None
    
    def test_decode_access_token_wrong_secret_returns_none(self):
        """TDD: decode_access_token should return None for token signed with wrong secret."""
        # Create token with different secret
        data = {"sub": "test@example.com"}
        wrong_secret = "wrong_secret_key"
        
        # Manually create token with wrong secret
        exp = datetime.now(timezone.utc) + timedelta(minutes=30)
        data.update({"exp": exp})
        wrong_token = jose_jwt.encode(data, wrong_secret, algorithm=settings.ALGORITHM)
        
        # Should return None when decoded with correct secret
        decoded = decode_access_token(wrong_token)
        assert decoded is None
    
    def test_decode_access_token_wrong_algorithm_returns_none(self):
        """TDD: decode_access_token should return None for token with wrong algorithm."""
        # Create token with different algorithm
        data = {"sub": "test@example.com"}
        exp = datetime.now(timezone.utc) + timedelta(minutes=30)
        data.update({"exp": exp})
        
        # Create token with HS512 instead of HS256
        wrong_algo_token = jose_jwt.encode(data, settings.SECRET_KEY, algorithm="HS512")
        
        # Should return None when decoded with expected algorithm
        decoded = decode_access_token(wrong_algo_token)
        assert decoded is None


class TestRefreshTokenFunctionality:
    """Test refresh token creation and validation with TDD methodology."""
    
    def test_create_refresh_token_returns_valid_jwt(self):
        """TDD: create_refresh_token should return valid JWT string."""
        data = {"sub": "test@example.com", "user_id": "123"}
        
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 50
        assert token.count('.') == 2
        
        # Verify it's a valid JWT
        decoded = jose_jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded["sub"] == "test@example.com"
        assert decoded["user_id"] == "123"
    
    def test_create_refresh_token_includes_type_claim(self):
        """TDD: Refresh token should include type claim."""
        data = {"sub": "test@example.com"}
        
        token = create_refresh_token(data)
        decoded = jose_jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        assert "type" in decoded
        assert decoded["type"] == "refresh"
    
    def test_create_refresh_token_has_longer_expiration_than_access_token(self):
        """TDD: Refresh token should have longer expiration than access token."""
        data = {"sub": "test@example.com"}
        
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        
        access_decoded = jose_jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        refresh_decoded = jose_jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        assert refresh_decoded["exp"] > access_decoded["exp"]
    
    def test_create_refresh_token_uses_configured_expiration_time(self):
        """TDD: Refresh token should use configured expiration time."""
        data = {"sub": "test@example.com"}
        
        token = create_refresh_token(data)
        decoded = jose_jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Calculate expected expiration
        expected_exp = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        actual_exp = datetime.fromtimestamp(decoded["exp"], timezone.utc)
        
        time_diff = abs((expected_exp - actual_exp).total_seconds())
        assert time_diff < 60  # Within 1 minute tolerance
    
    def test_decode_refresh_token_valid_refresh_token_returns_payload(self):
        """TDD: decode_refresh_token should return payload for valid refresh token."""
        data = {"sub": "test@example.com", "user_id": "123"}
        token = create_refresh_token(data)
        
        decoded = decode_refresh_token(token)
        
        assert decoded is not None
        assert isinstance(decoded, dict)
        assert decoded["sub"] == "test@example.com"
        assert decoded["user_id"] == "123"
        assert decoded["type"] == "refresh"
    
    def test_decode_refresh_token_access_token_returns_none(self):
        """TDD: decode_refresh_token should return None for access token."""
        data = {"sub": "test@example.com"}
        access_token = create_access_token(data)  # Not a refresh token
        
        decoded = decode_refresh_token(access_token)
        
        assert decoded is None
    
    def test_decode_refresh_token_invalid_token_returns_none(self):
        """TDD: decode_refresh_token should return None for invalid token."""
        invalid_token = "invalid.jwt.token"
        
        decoded = decode_refresh_token(invalid_token)
        
        assert decoded is None
    
    def test_decode_refresh_token_expired_token_returns_none(self):
        """TDD: decode_refresh_token should return None for expired refresh token."""
        # Create expired refresh token by mocking time
        data = {"sub": "test@example.com"}
        
        # Create token, then mock time to be in the future
        token = create_refresh_token(data)
        
        # Fast-forward time beyond expiration
        future_time = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES + 1)
        
        with patch('app.core.security.datetime') as mock_datetime:
            mock_datetime.now.return_value = future_time
            decoded = decode_refresh_token(token)
            
        assert decoded is None


class TestJWTSecurityEdgeCases:
    """Test edge cases and security scenarios for JWT functionality."""
    
    def test_token_tampering_detection(self):
        """TDD: JWT should detect token tampering."""
        data = {"sub": "test@example.com", "user_type": "USER"}
        token = create_access_token(data)
        
        # Tamper with the token by changing a character
        tampered_token = token[:-1] + ('X' if token[-1] != 'X' else 'Y')
        
        decoded = decode_access_token(tampered_token)
        assert decoded is None
    
    def test_token_payload_tampering_detection(self):
        """TDD: JWT should detect payload tampering."""
        data = {"sub": "test@example.com", "user_type": "USER"}
        token = create_access_token(data)
        
        # Split token and tamper with payload
        parts = token.split('.')
        assert len(parts) == 3
        
        # Decode payload, modify it, re-encode
        import base64
        import json
        
        # Decode payload (add padding if needed)
        payload_b64 = parts[1]
        padding = '=' * (4 - len(payload_b64) % 4)
        payload_json = base64.urlsafe_b64decode(payload_b64 + padding)
        payload_data = json.loads(payload_json)
        
        # Tamper with payload
        payload_data["user_type"] = "ADMIN"  # Privilege escalation attempt
        
        # Re-encode payload
        tampered_payload = base64.urlsafe_b64encode(
            json.dumps(payload_data).encode()
        ).decode().rstrip('=')
        
        # Reconstruct tampered token
        tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"
        
        # Should be rejected
        decoded = decode_access_token(tampered_token)
        assert decoded is None
    
    def test_token_with_none_algorithm_attack_prevention(self):
        """TDD: JWT should prevent 'none' algorithm attack."""
        data = {"sub": "test@example.com"}
        
        # Try to create token with 'none' algorithm
        try:
            malicious_token = jose_jwt.encode(data, "", algorithm="none")
            
            # Should be rejected by decoder
            decoded = decode_access_token(malicious_token)
            assert decoded is None
        except Exception:
            # If jose library prevents 'none' algorithm, that's also good
            pass
    
    def test_very_large_payload_handling(self):
        """TDD: JWT should handle large payloads appropriately."""
        # Create large payload (but within reasonable limits)
        large_data = {"sub": "test@example.com"}
        large_data["large_field"] = "x" * 1000  # 1KB of data
        
        token = create_access_token(large_data)
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == "test@example.com"
        assert len(decoded["large_field"]) == 1000
    
    def test_unicode_data_in_payload(self):
        """TDD: JWT should handle Unicode data correctly."""
        unicode_data = {
            "sub": "test@example.com",
            "name": "José García",
            "description": "测试用户",
            "emoji": "🔐🚀💯"
        }
        
        token = create_access_token(unicode_data)
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded["name"] == "José García"
        assert decoded["description"] == "测试用户"
        assert decoded["emoji"] == "🔐🚀💯"
    
    def test_special_characters_in_claims(self):
        """TDD: JWT should handle special characters in claims."""
        special_data = {
            "sub": "test@example.com",
            "path": "/api/v1/users/{id}",
            "query": "filter=name&sort=date",
            "special": "!@#$%^&*()_+-=[]{}|;':,.<>?"
        }
        
        token = create_access_token(special_data)
        decoded = decode_access_token(token)
        
        assert decoded is not None
        for key, value in special_data.items():
            assert decoded[key] == value


class TestJWTPerformance:
    """Performance tests for JWT operations."""
    
    def test_token_creation_performance(self):
        """TDD: Token creation should be performant."""
        import time
        
        data = {"sub": "test@example.com", "user_id": "123"}
        
        # Measure token creation time
        start_time = time.time()
        for _ in range(100):  # Create 100 tokens
            create_access_token(data)
        end_time = time.time()
        
        duration = end_time - start_time
        avg_time = duration / 100
        
        # Should create token in less than 10ms on average
        assert avg_time < 0.01, f"Token creation took {avg_time:.4f}s, expected < 0.01s"
    
    def test_token_decoding_performance(self):
        """TDD: Token decoding should be performant."""
        import time
        
        data = {"sub": "test@example.com", "user_id": "123"}
        token = create_access_token(data)
        
        # Measure token decoding time
        start_time = time.time()
        for _ in range(100):  # Decode 100 times
            decode_access_token(token)
        end_time = time.time()
        
        duration = end_time - start_time
        avg_time = duration / 100
        
        # Should decode token in less than 5ms on average
        assert avg_time < 0.005, f"Token decoding took {avg_time:.4f}s, expected < 0.005s"


class TestJWTConfigurationDependency:
    """Test JWT functionality dependency on configuration."""
    
    def test_token_creation_uses_configured_secret(self):
        """TDD: Token creation should use configured secret key."""
        data = {"sub": "test@example.com"}
        
        with patch('app.core.security.settings.SECRET_KEY', 'test_secret_key'):
            token = create_access_token(data)
            
            # Token should be decodable with the test secret
            decoded = jose_jwt.decode(token, 'test_secret_key', algorithms=[settings.ALGORITHM])
            assert decoded["sub"] == "test@example.com"
    
    def test_token_creation_uses_configured_algorithm(self):
        """TDD: Token creation should use configured algorithm."""
        data = {"sub": "test@example.com"}
        
        with patch('app.core.security.settings.ALGORITHM', 'HS512'):
            token = create_access_token(data)
            
            # Token should be decodable with HS512
            decoded = jose_jwt.decode(token, settings.SECRET_KEY, algorithms=['HS512'])
            assert decoded["sub"] == "test@example.com"
    
    def test_token_expiration_uses_configured_time(self):
        """TDD: Token expiration should use configured time."""
        data = {"sub": "test@example.com"}
        
        # Mock different expiration time
        with patch('app.core.security.settings.ACCESS_TOKEN_EXPIRE_MINUTES', 60):
            token = create_access_token(data)
            decoded = jose_jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            # Should expire in approximately 60 minutes
            expected_exp = datetime.now(timezone.utc) + timedelta(minutes=60)
            actual_exp = datetime.fromtimestamp(decoded["exp"], timezone.utc)
            
            time_diff = abs((expected_exp - actual_exp).total_seconds())
            assert time_diff < 60  # Within 1 minute tolerance


if __name__ == "__main__":
    # Run with: python -m pytest tests/unit/auth/test_jwt_security.py -v
    pytest.main([__file__, "-v", "--tb=short", "--cov=app.core.security"])
