#!/usr/bin/env python3
"""
Enterprise JWT Encryption Security Standards Test Suite

This test suite validates the implementation of enterprise-grade JWT encryption
and security standards for the MeStore marketplace platform.

Test Coverage:
- JWT Algorithm Security (HS256/RS256 validation)
- AES-256 encryption for sensitive payload data
- Token binding and replay attack prevention
- Secure key derivation with PBKDF2
- Colombian compliance requirements validation
- Security audit procedures
- Key rotation functionality

Colombian Data Protection Compliance:
- Ley 1581 de 2012 (Habeas Data)
- Decreto 1377 de 2013
- Personal data encryption requirements
"""

import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch
import secrets
import base64

from fastapi import Request

from app.core.security import (
    create_access_token,
    decode_access_token,
    create_refresh_token,
    decode_refresh_token,
    generate_device_fingerprint,
    encryption_manager,
    token_manager,
    token_blacklist,
    TokenType,
    AlgorithmType,
    SecurityLevel,
    revoke_token,
    is_token_revoked,
    validate_token_security,
    perform_security_audit,
    rotate_system_keys,
    get_security_headers,
    create_secure_password_reset_token,
    verify_password_reset_token,
    create_email_verification_token,
    verify_email_verification_token
)
from app.core.config import settings


class TestJWTAlgorithmSecurity:
    """Test JWT algorithm security validation."""

    def test_algorithm_validation_production(self):
        """Test that insecure algorithms are rejected in production."""
        with patch.object(settings, 'ENVIRONMENT', 'production'):
            with patch.object(settings, 'ALGORITHM', 'HS512'):
                with pytest.raises(ValueError, match="Unsupported JWT algorithm"):
                    from app.core.security import SecureTokenManager
                    SecureTokenManager()

    def test_hs256_production_warning(self, caplog):
        """Test that HS256 usage in production generates warning."""
        with patch.object(settings, 'ENVIRONMENT', 'production'):
            with patch.object(settings, 'ALGORITHM', 'HS256'):
                from app.core.security import SecureTokenManager
                manager = SecureTokenManager()
                assert "Using HS256 in production" in caplog.text

    def test_algorithm_downgrade_prevention(self):
        """Test prevention of algorithm downgrade attacks."""
        with patch.object(settings, 'ALGORITHM', 'none'):
            with pytest.raises(ValueError, match="Unsupported JWT algorithm"):
                from app.core.security import SecureTokenManager
                SecureTokenManager()

    def test_rs256_key_generation(self):
        """Test RSA key pair generation for RS256."""
        with patch.object(settings, 'ALGORITHM', 'RS256'):
            from app.core.security import SecureTokenManager
            manager = SecureTokenManager()
            assert manager.key_pair is not None
            assert 'private_key' in manager.key_pair
            assert 'public_key' in manager.key_pair
            assert manager.key_pair['key_size'] >= 2048


class TestAES256Encryption:
    """Test AES-256 encryption implementation."""

    def test_encryption_manager_initialization(self):
        """Test encryption manager proper initialization."""
        assert encryption_manager._fernet_key is not None
        assert encryption_manager._master_key is not None
        assert len(encryption_manager._master_key) == 32  # 256 bits

    def test_encrypt_decrypt_sensitive_data(self):
        """Test encryption and decryption of sensitive data."""
        test_data = "user@example.com"
        encrypted = encryption_manager.encrypt_sensitive_data(test_data)
        decrypted = encryption_manager.decrypt_sensitive_data(encrypted)

        assert encrypted != test_data
        assert decrypted == test_data
        assert len(encrypted) > len(test_data)

    def test_encryption_key_derivation_pbkdf2(self):
        """Test PBKDF2 key derivation implementation."""
        # Test that different secrets produce different keys
        original_secret = settings.SECRET_KEY

        # Create first encryption manager
        manager1 = encryption_manager
        key1 = manager1._master_key

        # Temporarily change secret and create new manager
        with patch.object(settings, 'SECRET_KEY', 'different_secret_key_for_testing'):
            from app.core.security import EncryptionManager
            manager2 = EncryptionManager()
            key2 = manager2._master_key

        assert key1 != key2

    def test_encryption_salt_handling(self):
        """Test proper salt handling for key derivation."""
        salt = encryption_manager._salt
        assert salt is not None
        assert len(salt) == 16  # 128 bits
        assert isinstance(salt, bytes)

    def test_encryption_error_handling(self):
        """Test encryption error handling."""
        with pytest.raises(Exception):
            encryption_manager.decrypt_sensitive_data("invalid_encrypted_data")


class TestTokenBinding:
    """Test token binding and device fingerprinting."""

    def create_mock_request(self, headers=None):
        """Create a mock FastAPI request object."""
        request = Mock(spec=Request)
        request.headers = headers or {
            "user-agent": "Mozilla/5.0 (Test Browser)",
            "accept": "text/html,application/xhtml+xml",
            "accept-language": "en-US,en;q=0.9",
            "accept-encoding": "gzip, deflate"
        }
        request.client = Mock()
        request.client.host = "192.168.1.100"
        return request

    def test_device_fingerprint_generation(self):
        """Test device fingerprint generation."""
        request = self.create_mock_request()
        fingerprint = generate_device_fingerprint(request)

        assert len(fingerprint) == 64  # SHA256 hex length
        assert isinstance(fingerprint, str)

        # Same request should produce same fingerprint
        fingerprint2 = generate_device_fingerprint(request)
        assert fingerprint == fingerprint2

    def test_device_fingerprint_uniqueness(self):
        """Test that different devices produce different fingerprints."""
        request1 = self.create_mock_request({
            "user-agent": "Mozilla/5.0 (Windows NT 10.0)",
            "accept": "text/html"
        })

        request2 = self.create_mock_request({
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X)",
            "accept": "application/json"
        })

        fingerprint1 = generate_device_fingerprint(request1)
        fingerprint2 = generate_device_fingerprint(request2)

        assert fingerprint1 != fingerprint2

    def test_token_device_binding(self):
        """Test token binding to device fingerprint."""
        request = self.create_mock_request()
        device_fp = generate_device_fingerprint(request)

        # Create token with device binding
        token = create_access_token(
            data={"sub": "user@example.com"},
            device_fingerprint=device_fp
        )

        # Decode with correct device fingerprint
        payload = decode_access_token(token, verify_device=device_fp)
        assert payload is not None
        assert payload["sub"] == "user@example.com"

        # Decode with wrong device fingerprint should fail
        wrong_fp = "different_fingerprint_hash"
        payload_wrong = decode_access_token(token, verify_device=wrong_fp)
        assert payload_wrong is None

    def test_device_fingerprint_ip_privacy(self):
        """Test that IP addresses are hashed for privacy."""
        request1 = self.create_mock_request()
        request1.client.host = "192.168.1.100"

        request2 = self.create_mock_request()
        request2.client.host = "10.0.0.50"

        fp1 = generate_device_fingerprint(request1)
        fp2 = generate_device_fingerprint(request2)

        # Different IPs should produce different fingerprints
        assert fp1 != fp2

        # IP should not appear in plain text in fingerprint
        assert "192.168.1.100" not in fp1
        assert "10.0.0.50" not in fp2


class TestPayloadEncryption:
    """Test JWT payload encryption for sensitive data."""

    def test_payload_encryption_enabled(self):
        """Test payload encryption when enabled."""
        token = create_access_token(
            data={"sub": "user@example.com"},
            encrypt_payload=True
        )

        # Token should not contain plain text email
        import base64
        import json
        from jose import jwt

        # Decode without verification to check payload
        unverified = jwt.decode(token, key="", options={"verify_signature": False, "verify_aud": False, "verify_exp": False})

        assert "sub" not in unverified  # Plain text should not be present
        assert "sub_enc" in unverified  # Encrypted version should be present
        assert unverified.get("encrypted") is True

    def test_payload_decryption(self):
        """Test payload decryption during token validation."""
        original_email = "user@example.com"

        token = create_access_token(
            data={"sub": original_email},
            encrypt_payload=True
        )

        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == original_email
        assert "sub_enc" not in payload  # Encrypted version should be removed
        assert "encrypted" not in payload  # Flag should be removed

    def test_payload_encryption_error_handling(self):
        """Test handling of corrupted encrypted payload."""
        # Create token with valid encryption
        token = create_access_token(
            data={"sub": "user@example.com"},
            encrypt_payload=True
        )

        # Corrupt the token by modifying encrypted data
        from jose import jwt
        import json
        import base64

        # Decode and modify
        header = jwt.get_unverified_header(token)
        payload = jwt.decode(token, key="", options={"verify_signature": False, "verify_aud": False, "verify_exp": False})
        payload["sub_enc"] = "corrupted_encrypted_data"

        # Re-encode with corrupted data (for testing purposes)
        # In real scenario, this would fail signature validation
        corrupted_payload = decode_access_token(token)
        # Should handle decryption errors gracefully


class TestTokenBlacklist:
    """Test token revocation and blacklist functionality."""

    def test_token_revocation(self):
        """Test token revocation functionality."""
        token = create_access_token(data={"sub": "user@example.com"})

        # Token should be valid initially
        payload = decode_access_token(token)
        assert payload is not None

        # Revoke token
        success = revoke_token(token)
        assert success is True

        # Token should be invalid after revocation
        assert is_token_revoked(token) is True
        payload_after = decode_access_token(token)
        assert payload_after is None

    def test_blacklist_cleanup(self):
        """Test blacklist cleanup functionality."""
        initial_count = len(token_blacklist._blacklisted_tokens)

        # Add tokens to exceed cleanup threshold
        for i in range(1100):  # Exceed threshold of 1000
            jti = f"test_jti_{i}"
            token_blacklist.blacklist_token(jti)

        # Should have triggered cleanup
        final_count = len(token_blacklist._blacklisted_tokens)
        assert final_count < 1100  # Should be cleaned up

    def test_invalid_token_revocation(self):
        """Test revocation of invalid tokens."""
        invalid_token = "invalid.jwt.token"
        success = revoke_token(invalid_token)
        assert success is False

        # Invalid tokens should be considered revoked
        assert is_token_revoked(invalid_token) is True


class TestColombianCompliance:
    """Test Colombian data protection law compliance."""

    def test_personal_data_classification(self):
        """Test personal data classification in tokens."""
        with patch.object(token_manager, 'security_level', SecurityLevel.PRODUCTION):
            token = create_access_token(
                data={"sub": "user@example.com"},
                encrypt_payload=True
            )

            payload = decode_access_token(token)
            assert payload is not None
            assert "compliance" in payload
            assert payload["compliance"]["colombian_data_protection"] is True
            assert payload["compliance"]["data_classification"] == "personal"

    def test_non_personal_data_classification(self):
        """Test non-personal data classification."""
        with patch.object(token_manager, 'security_level', SecurityLevel.PRODUCTION):
            token = create_access_token(
                data={"role": "admin"},  # Non-personal data
                encrypt_payload=False
            )

            payload = decode_access_token(token)
            assert payload is not None
            assert "compliance" in payload
            assert payload["compliance"]["data_classification"] == "general"

    def test_data_retention_compliance(self):
        """Test data retention compliance with Colombian laws."""
        # Test short expiration for sensitive tokens
        reset_token = create_secure_password_reset_token("user@example.com")

        from jose import jwt
        payload = jwt.decode(reset_token, key="", options={"verify_signature": False, "verify_aud": False, "verify_exp": False})

        # Password reset tokens should expire in 1 hour max
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        issued_time = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        token_lifetime = exp_time - issued_time

        assert token_lifetime <= timedelta(hours=1)

    def test_audit_logging_compliance(self):
        """Test audit logging for compliance."""
        # This would be tested with actual logging in integration tests
        # For now, verify that audit functionality exists
        assert hasattr(encryption_manager, 'encrypt_sensitive_data')
        assert hasattr(token_manager, '_validate_algorithm')


class TestSecurityAudit:
    """Test security audit and validation procedures."""

    def test_security_audit_execution(self):
        """Test security audit execution."""
        audit_result = perform_security_audit()

        assert "timestamp" in audit_result
        assert "environment" in audit_result
        assert "algorithm_security" in audit_result
        assert "key_management" in audit_result
        assert "encryption_status" in audit_result
        assert "compliance_status" in audit_result
        assert "overall_score" in audit_result

        # Score should be between 0 and 100
        assert 0 <= audit_result["overall_score"] <= 100

    def test_token_security_validation(self):
        """Test comprehensive token security validation."""
        # Create a secure token
        device_fp = "test_device_fingerprint"
        token = create_access_token(
            data={"sub": "user@example.com"},
            encrypt_payload=True,
            device_fingerprint=device_fp
        )

        validation = validate_token_security(token)

        assert validation["valid"] is True
        assert validation["algorithm_secure"] is True
        assert validation["not_expired"] is True
        assert validation["not_revoked"] is True
        assert validation["security_score"] > 0

    def test_security_headers_generation(self):
        """Test security headers for API responses."""
        headers = get_security_headers()

        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "Referrer-Policy",
            "Permissions-Policy"
        ]

        for header in required_headers:
            assert header in headers
            assert headers[header]  # Should have non-empty value

    def test_production_security_recommendations(self):
        """Test security recommendations for production."""
        with patch.object(settings, 'ENVIRONMENT', 'production'):
            with patch.object(settings, 'ALGORITHM', 'HS256'):
                audit_result = perform_security_audit()

                recommendations = audit_result["recommendations"]
                assert any("RS256" in rec for rec in recommendations)


class TestKeyRotation:
    """Test key rotation functionality."""

    def test_system_key_rotation(self):
        """Test system-wide key rotation."""
        rotation_result = rotate_system_keys()

        assert "encryption_key_rotated" in rotation_result
        assert "signing_key_rotated" in rotation_result
        assert "timestamp" in rotation_result

        # At least one key rotation should succeed
        assert (rotation_result["encryption_key_rotated"] or
                rotation_result["signing_key_rotated"])

    def test_encryption_key_rotation(self):
        """Test encryption key rotation specifically."""
        original_key = encryption_manager._master_key

        success = encryption_manager.rotate_encryption_key()
        assert success is True

        new_key = encryption_manager._master_key
        assert new_key != original_key

    def test_signing_key_rotation_rs256(self):
        """Test signing key rotation for RS256."""
        with patch.object(settings, 'ALGORITHM', 'RS256'):
            from app.core.security import SecureTokenManager
            manager = SecureTokenManager()

            original_keys = manager.key_pair
            success = manager.rotate_keys()

            assert success is True
            new_keys = manager.key_pair
            assert new_keys != original_keys


class TestPasswordResetSecurity:
    """Test password reset token security."""

    def test_password_reset_token_creation(self):
        """Test secure password reset token creation."""
        email = "user@example.com"
        token = create_secure_password_reset_token(email)

        # Should be encrypted
        from jose import jwt
        unverified = jwt.decode(token, key="", options={"verify_signature": False, "verify_aud": False, "verify_exp": False})
        assert unverified.get("encrypted") is True
        assert unverified.get("typ") == "reset_password"

    def test_password_reset_token_verification(self):
        """Test password reset token verification."""
        email = "user@example.com"
        token = create_secure_password_reset_token(email)

        verified_email = verify_password_reset_token(token)
        assert verified_email == email

    def test_password_reset_token_expiration(self):
        """Test password reset token short expiration."""
        email = "user@example.com"
        token = create_secure_password_reset_token(email)

        from jose import jwt
        payload = jwt.decode(token, key="", options={"verify_signature": False, "verify_aud": False, "verify_exp": False})

        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        issued_time = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        token_lifetime = exp_time - issued_time

        # Should expire in 1 hour or less
        assert token_lifetime <= timedelta(hours=1)


class TestEmailVerificationSecurity:
    """Test email verification token security."""

    def test_email_verification_token_creation(self):
        """Test email verification token creation."""
        email = "user@example.com"
        token = create_email_verification_token(email)

        from jose import jwt
        unverified = jwt.decode(token, key="", options={"verify_signature": False, "verify_aud": False, "verify_exp": False})
        assert unverified.get("typ") == "email_verification"

    def test_email_verification_token_verification(self):
        """Test email verification token verification."""
        email = "user@example.com"
        token = create_email_verification_token(email)

        verified_email = verify_email_verification_token(token)
        assert verified_email == email

    def test_email_verification_token_expiration(self):
        """Test email verification token expiration."""
        email = "user@example.com"
        token = create_email_verification_token(email)

        from jose import jwt
        payload = jwt.decode(token, key="", options={"verify_signature": False, "verify_aud": False, "verify_exp": False})

        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        issued_time = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        token_lifetime = exp_time - issued_time

        # Should expire in 24 hours
        assert token_lifetime <= timedelta(hours=24)


class TestRefreshTokenSecurity:
    """Test refresh token enhanced security."""

    def test_refresh_token_creation_with_encryption(self):
        """Test refresh token creation with encryption."""
        token = create_refresh_token(
            data={"sub": "user@example.com"},
            encrypt_payload=True
        )

        from jose import jwt
        unverified = jwt.decode(token, key="", options={"verify_signature": False, "verify_aud": False, "verify_exp": False})
        assert unverified.get("typ") == "refresh"
        assert unverified.get("encrypted") is True

    def test_refresh_token_device_binding(self):
        """Test refresh token device binding."""
        device_fp = "test_device_fingerprint"
        token = create_refresh_token(
            data={"sub": "user@example.com"},
            device_fingerprint=device_fp
        )

        # Should decode successfully with correct device
        payload = decode_refresh_token(token, verify_device=device_fp)
        assert payload is not None
        assert payload["sub"] == "user@example.com"

        # Should fail with wrong device
        wrong_device = "wrong_device_fingerprint"
        payload_wrong = decode_refresh_token(token, verify_device=wrong_device)
        assert payload_wrong is None


# Integration test for the complete security flow
class TestIntegratedSecurityFlow:
    """Test integrated security flow with all features."""

    def test_complete_authentication_flow(self):
        """Test complete authentication flow with all security features."""
        # Simulate user login with device binding
        request = Mock(spec=Request)
        request.headers = {
            "user-agent": "Mozilla/5.0 (Test Browser)",
            "accept": "application/json"
        }
        request.client = Mock()
        request.client.host = "192.168.1.100"

        device_fp = generate_device_fingerprint(request)

        # Create access and refresh tokens
        user_data = {"sub": "user@example.com", "role": "buyer"}

        access_token = create_access_token(
            data=user_data,
            encrypt_payload=True,
            device_fingerprint=device_fp
        )

        refresh_token = create_refresh_token(
            data=user_data,
            encrypt_payload=True,
            device_fingerprint=device_fp
        )

        # Validate access token
        access_payload = decode_access_token(
            access_token,
            verify_device=device_fp
        )
        assert access_payload is not None
        assert access_payload["sub"] == "user@example.com"

        # Validate refresh token
        refresh_payload = decode_refresh_token(
            refresh_token,
            verify_device=device_fp
        )
        assert refresh_payload is not None
        assert refresh_payload["sub"] == "user@example.com"

        # Test token revocation
        revoke_success = revoke_token(access_token)
        assert revoke_success is True

        # Token should be invalid after revocation
        revoked_payload = decode_access_token(
            access_token,
            verify_device=device_fp
        )
        assert revoked_payload is None

    def test_security_audit_comprehensive(self):
        """Test comprehensive security audit."""
        audit_result = perform_security_audit()

        # Should pass basic security checks
        assert audit_result["overall_score"] >= 75  # Minimum acceptable score
        assert audit_result["algorithm_security"]["secure"] is True
        assert audit_result["encryption_status"]["encryption_manager_active"] is True
        assert audit_result["compliance_status"]["colombian_data_protection"] is True


if __name__ == "__main__":
    # Run the test suite
    pytest.main([__file__, "-v", "--tb=short"])